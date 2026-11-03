#!/usr/bin/env python3
"""
Simple Space Analytics Web Application Server
============================================
Lightweight Flask backend connecting the Analytics Dashboard (docs/index.html)
to the live Pinterest API v5.

Features:
- Full CORS support (avoids all browser cross-origin fetch issues)
- Live on-demand Pinterest API sync (/api/analytics/refresh)
- Serves the clean performance analysis dashboard on http://127.0.0.1:5555
- Retains PinAutopilot generation pipeline endpoints (/api/run, /api/stream)
"""

import os
import sys
import json
import queue
import datetime
import threading
import subprocess
from pathlib import Path
import requests
from flask import Flask, Response, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).parent.resolve()
DOCS_DIR = BASE_DIR / "docs"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_FILE = BASE_DIR / "user_config.json"
DATA_FILE = BASE_DIR / "analytics_data.json"
DOCS_DATA_FILE = DOCS_DIR / "analytics_data.json"
PIPELINE_STATE_FILE = OUTPUT_DIR / "pipeline_state.json"

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/*": {"origins": "*"}})

# ─── Global State ─────────────────────────────────────────────────────────────
_log_queue: queue.Queue = queue.Queue()
_is_running: bool = False
_run_lock = threading.Lock()
_current_proc: subprocess.Popen | None = None


def get_pinterest_token():
    token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    if not token and (BASE_DIR / ".env").exists():
        try:
            for line in (BASE_DIR / ".env").read_text(encoding="utf-8").splitlines():
                if line.startswith("PINTEREST_ACCESS_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
        except Exception:
            pass
    if not token and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                token = json.load(f).get("pinterest_access_token")
        except Exception:
            pass
    return token


def load_cached_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading analytics data: {e}")
    return {}


def sync_pinterest_live():
    """Queries Pinterest API v5 directly and updates analytics_data.json."""
    token = get_pinterest_token()
    if not token:
        raise ValueError("No Pinterest access token found in user_config.json")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Fetch user account info
    u_res = requests.get("https://api.pinterest.com/v5/user_account", headers=headers, timeout=15)
    user_info = u_res.json() if u_res.status_code == 200 else {}

    # 2. Fetch 30-day analytics
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=30)
    a_url = f"https://api.pinterest.com/v5/user_account/analytics?start_date={start_date}&end_date={today}&metric_types=IMPRESSION,PIN_CLICK,OUTBOUND_CLICK,SAVE"
    a_res = requests.get(a_url, headers=headers, timeout=20)
    if a_res.status_code != 200:
        raise RuntimeError(f"Pinterest Analytics API error ({a_res.status_code}): {a_res.text}")
    analytics_payload = a_res.json()

    # 3. Fetch boards
    boards_map = {}
    try:
        b_res = requests.get("https://api.pinterest.com/v5/boards", headers=headers, timeout=10)
        if b_res.status_code == 200:
            for b in b_res.json().get("items", []):
                boards_map[b.get("id")] = b.get("name")
    except Exception as e:
        print(f"Board fetch warning: {e}")

    # 4. Fetch top pins (Top 30 Performing Pins with Concurrent Fetching)
    top_pins_list = []
    try:
        from concurrent.futures import ThreadPoolExecutor
        tp_url = f"https://api.pinterest.com/v5/user_account/analytics/top_pins?start_date={start_date}&end_date={today}&metric_types=IMPRESSION,PIN_CLICK,SAVE,OUTBOUND_CLICK&sort_by=IMPRESSION&num_of_pins=30"
        tp_res = requests.get(tp_url, headers=headers, timeout=15)
        if tp_res.status_code == 200:
            pins_data = tp_res.json().get("pins", [])[:30]

            def fetch_single_pin(p):
                pid = p.get("pin_id")
                m = p.get("metrics", {})
                p_info = {}
                try:
                    p_res = requests.get(f"https://api.pinterest.com/v5/pins/{pid}", headers=headers, timeout=6)
                    if p_res.status_code == 200:
                        p_info = p_res.json()
                except Exception:
                    pass

                media = p_info.get("media", {}).get("images", {})
                img_url = media.get("1200x", {}).get("url") or media.get("600x", {}).get("url") or media.get("400x300", {}).get("url") or ""
                impr = int(m.get("IMPRESSION", 0))
                clicks = int(m.get("PIN_CLICK", 0))
                outbound = int(m.get("OUTBOUND_CLICK", 0))
                saves = int(m.get("SAVE", 0))
                ctr = round((clicks / max(impr, 1)) * 100, 2)
                return {
                    "id": f"pin_{pid}",
                    "pin_id": pid,
                    "title": p_info.get("title") or f"Pin #{pid}",
                    "board": boards_map.get(p_info.get("board_id"), "General"),
                    "image_url": img_url,
                    "destination_url": p_info.get("link") or "",
                    "has_link": bool(p_info.get("link")),
                    "impressions": impr,
                    "pin_clicks": clicks,
                    "outbound_clicks": outbound,
                    "saves": saves,
                    "ctr": ctr,
                    "pinterest_link": f"https://www.pinterest.com/pin/{pid}/"
                }

            with ThreadPoolExecutor(max_workers=10) as executor:
                top_pins_list = list(executor.map(fetch_single_pin, pins_data))
    except Exception as e:
        print(f"Top pins warning: {e}")

    # Build updated data object
    data = load_cached_data()
    data["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    data["account_username"] = user_info.get("username", "simplespacehaven")
    data["business_name"] = user_info.get("business_name", "Simple Space Haven")
    data["profile_image"] = user_info.get("profile_image", "")
    data["follower_count"] = user_info.get("follower_count", 0)
    data["pin_count"] = user_info.get("pin_count", 0)
    data["board_count"] = user_info.get("board_count", 0)
    data["total_audience_monthly"] = user_info.get("monthly_views", data.get("total_audience_monthly", 0))

    summary = analytics_payload.get("all", {}).get("summary_metrics", {})
    data["total_impressions_period"] = int(summary.get("IMPRESSION", 0))
    data["total_pin_clicks_period"] = int(summary.get("PIN_CLICK", 0))
    data["total_saves_period"] = int(summary.get("SAVE", 0))
    data["total_outbound_clicks_period"] = int(summary.get("OUTBOUND_CLICK", 0))

    daily_items = analytics_payload.get("all", {}).get("daily_metrics", [])
    if daily_items:
        daily_list = []
        for item in daily_items:
            m = item.get("metrics", {})
            daily_list.append({
                "date": item.get("date"),
                "impressions": int(m.get("IMPRESSION", 0)),
                "pin_clicks": int(m.get("PIN_CLICK", 0)),
                "outbound_clicks": int(m.get("OUTBOUND_CLICK", 0)),
                "saves": int(m.get("SAVE", 0))
            })
        daily_list.sort(key=lambda x: x["date"])
        data["historical_daily"] = daily_list

    if top_pins_list:
        data["top_performing_pins"] = top_pins_list

    # Save to disk
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    with open(DOCS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


# ─── Static & Dashboard Routes ────────────────────────────────────────────────
@app.route("/")
def index():
    """Serves the clean performance analytics dashboard."""
    return send_file(DOCS_DIR / "index.html")


@app.route("/analytics_data.json")
def serve_data_json():
    return send_file(DATA_FILE)


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(BASE_DIR / "assets", filename)


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


def suggest_product_link(title):
    t = (title or "").lower()
    if 'grass' in t:
        return "https://www.amazon.in/dp/B0BWDPDXJD?tag=simplespaceha-21"
    elif 'mandir' in t or 'temple' in t:
        return "https://www.amazon.in/dp/B08RF1JC8Y?tag=simplespaceha-21"
    elif 'bistro' in t:
        return "https://www.amazon.in/s?k=balcony+bistro+set+chairs+and+table&tag=simplespaceha-21"
    elif 'thali' in t or 'thaali' in t:
        return "https://www.amazon.in/dp/B0FZV94JR4?tag=simplespaceha-21"
    elif 'chair' in t:
        return "https://www.amazon.in/s?k=foldable+study+chair+with+writing+pad&tag=simplespaceha-21"
    elif 'planter' in t:
        return "https://www.amazon.in/s?k=balcony+railing+planters&tag=simplespaceha-21"
    import urllib.parse
    clean = "+".join(title.split()[:4])
    return f"https://www.amazon.in/s?k={urllib.parse.quote_plus(clean)}&tag=simplespaceha-21"


# ─── API Routes ───────────────────────────────────────────────────────────────
@app.route("/api/health")
def api_health():
    return jsonify({"status": "healthy", "service": "Simple Space Analytics"})


@app.route("/api/analytics", methods=["GET"])
def api_get_analytics():
    """Calls Pinterest API live on every load to ensure true real-time metrics."""
    try:
        data = sync_pinterest_live()
        return jsonify(data)
    except Exception as e:
        print(f"Live sync warning, using cache: {e}")
        data = load_cached_data()
        return jsonify(data)


@app.route("/api/analytics/refresh", methods=["GET", "POST"])
def api_refresh_analytics():
    """Triggers an immediate live fetch from the Pinterest API v5."""
    try:
        fresh_data = sync_pinterest_live()
        return jsonify({"status": "success", "data": fresh_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/audit", methods=["GET"])
def api_audit():
    """Scans all top pins and audits their affiliate link health and profit leaks."""
    data = load_cached_data()
    pins = data.get("top_performing_pins", [])
    audited = []
    total_lost_clicks = 0
    for p in pins:
        dest = p.get("destination_url") or ""
        has_dest = bool(dest and dest.lower() != "no link attached" and dest.startswith("http"))
        is_amazon = any(dom in dest.lower() for dom in ["amazon.in", "amazon.com", "amzn.to", "amzn.in", "link.amazon"])
        has_tag = ("tag=simplespaceha-21" in dest) or ("simplespac00e-20" in dest) or ("link.amazon" in dest) or ("amzn.to" in dest) or ("amzn.in" in dest)
        
        if not has_dest:
            status = "CRITICAL_MISSING"
            msg = "No link attached! Viewers have no way to purchase."
        elif is_amazon and has_tag:
            status = "HEALTHY"
            msg = "Active verified Amazon affiliate link attached."
        elif is_amazon and not has_tag:
            status = "MISSING_TAG"
            msg = "Amazon link attached, but missing your affiliate tracking tag."
        else:
            status = "HEALTHY"
            msg = f"Active destination link attached."
            
        clicks = p.get("pin_clicks", 0)
        outbound = p.get("outbound_clicks", 0)
        lost = max(0, clicks - outbound) if (status in ["CRITICAL_MISSING", "MISSING_TAG"]) else 0
        total_lost_clicks += lost
        
        audited.append({
            "id": p.get("id"),
            "pin_id": p.get("pin_id"),
            "title": p.get("title"),
            "board": p.get("board"),
            "image_url": p.get("image_url"),
            "destination_url": dest,
            "status": status,
            "status_message": msg,
            "impressions": p.get("impressions", 0),
            "pin_clicks": clicks,
            "outbound_clicks": outbound,
            "lost_clicks": lost,
            "suggested_link": suggest_product_link(p.get("title", "")),
            "pinterest_link": p.get("pinterest_link")
        })
        
    est_lost_revenue = round(total_lost_clicks * 0.03 * 45) # 3% conv, ₹45 avg comm
    return jsonify({
        "status": "success",
        "total_audited": len(audited),
        "total_lost_clicks": total_lost_clicks,
        "estimated_lost_commission_inr": est_lost_revenue,
        "pins": audited
    })


@app.route("/api/winners", methods=["GET"])
def api_winners():
    """Identifies viral horse pins and matches dynamic Amazon search categories."""
    data = load_cached_data()
    pins = data.get("top_performing_pins", [])
    winners = []
    from amazon_trend_hunter import clean_product_keyword
    for p in pins:
        impr = p.get("impressions", 0)
        clicks = p.get("pin_clicks", 0)
        if impr >= 1000 or clicks >= 40:
            title = p.get("title", "")
            pid = p.get("pin_id") or (p.get("id", "").replace("pin_", ""))
            batch_dir = OUTPUT_DIR / "winner_batches" / f"horse_{pid}"
            has_batch = (batch_dir / "pinterest_amazon_bestsellers_schedule.csv").exists()
            dyn_keyword = clean_product_keyword(title)
            winners.append({
                "rank": len(winners) + 1,
                "pin_id": pid,
                "title": title,
                "clean_keyword": dyn_keyword,
                "board": p.get("board"),
                "image_url": p.get("image_url"),
                "destination_url": p.get("destination_url") or "",
                "impressions": impr,
                "pin_clicks": clicks,
                "saves": p.get("saves", 0),
                "has_batch": has_batch,
                "suggested_link": suggest_product_link(title),
                "angles": [
                    {
                        "type": "Amazon Bestseller",
                        "headline": f"Top Rated {dyn_keyword}",
                        "desc": "Real Amazon Bestseller with 4★+ rating, high review velocity, and Prime delivery."
                    },
                    {
                        "type": "Frequently Bought Together",
                        "headline": "Complementary Solution",
                        "desc": "Matching product from this exact category to capture multi-item basket conversion."
                    },
                    {
                        "type": "Budget Impulse Gem",
                        "headline": "Under ₹999 Find",
                        "desc": "High-conversion affordable essential with highest organic click-through rate."
                    }
                ]
            })
    return jsonify({"status": "success", "winners": winners})


@app.route("/api/winners/generate", methods=["GET", "POST"])
def api_generate_winner_pack():
    """Dynamically searches Amazon India for real bestsellers matching this winning horse."""
    pin_id = request.args.get("pin_id")
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        pin_id = body.get("pin_id") or pin_id

    if not pin_id:
        return jsonify({"status": "error", "message": "pin_id is required"}), 400

    data = load_cached_data()
    pins = data.get("top_performing_pins", [])
    target_pin = None
    for p in pins:
        pid = p.get("pin_id") or (p.get("id", "").replace("pin_", ""))
        if pid == pin_id:
            target_pin = p
            break

    from amazon_trend_hunter import hunt_bestsellers_for_horse
    title = target_pin.get("title", "Smart Space Decor") if target_pin else "Smart Balcony Decor"
    board = target_pin.get("board", "Balcony Essentials & Decor for Small Spaces") if target_pin else "Balcony Essentials & Decor for Small Spaces"

    try:
        pack = hunt_bestsellers_for_horse(pin_id, title, board)
        return jsonify(pack)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/publisher/queue", methods=["GET"])
def api_publisher_queue():
    """Returns local schedule CSV batches ready for drip distribution."""
    output_dir = BASE_DIR / "output"
    csvs = list(output_dir.glob("pinterest_*schedule.csv"))
    batches = []
    for c in csvs:
        try:
            with open(c, "r", encoding="utf-8") as f:
                lines = len(f.readlines()) - 1
            batches.append({
                "filename": c.name,
                "pin_count": max(0, lines),
                "modified": datetime.datetime.fromtimestamp(c.stat().st_mtime).strftime("%b %d, %H:%M")
            })
        except Exception:
            pass
    batches.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify({
        "status": "success",
        "batches": batches[:8],
        "token_scope": "pins:read, boards:read, user_accounts:read (Trial Access Active)",
        "write_scope_ready": False
    })


# ─── Retained Pipeline Routes (For automated pin generation) ──────────────────
@app.route("/api/status")
def api_status():
    return jsonify({"is_running": _is_running})


@app.route("/api/state")
def api_state():
    if PIPELINE_STATE_FILE.exists():
        try:
            return jsonify(json.loads(PIPELINE_STATE_FILE.read_text(encoding="utf-8")))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "NO_PREVIOUS_RUN"})


@app.route("/api/cancel", methods=["POST"])
def api_cancel():
    global _current_proc
    if _current_proc and _is_running:
        _current_proc.terminate()
        return jsonify({"status": "cancelled"})
    return jsonify({"status": "nothing_running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5555))
    print("=" * 65)
    print("  🚀 Simple Space Haven — Live Analytics Web Application")
    print(f"  📊 Live Dashboard  → http://0.0.0.0:{port}")
    print(f"  ⚡ API Endpoint    → http://0.0.0.0:{port}/api/analytics")
    print(f"  🔄 Live Sync API   → http://0.0.0.0:{port}/api/analytics/refresh")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
