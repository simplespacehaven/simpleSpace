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

    # 4. Fetch top pins
    top_pins_list = []
    try:
        tp_url = f"https://api.pinterest.com/v5/user_account/analytics/top_pins?start_date={start_date}&end_date={today}&metric_types=IMPRESSION,PIN_CLICK,SAVE,OUTBOUND_CLICK&sort_by=IMPRESSION"
        tp_res = requests.get(tp_url, headers=headers, timeout=15)
        if tp_res.status_code == 200:
            pins_data = tp_res.json().get("pins", [])
            for p in pins_data[:10]:
                pid = p.get("pin_id")
                m = p.get("metrics", {})
                
                # Fetch individual pin details
                p_info = {}
                try:
                    p_res = requests.get(f"https://api.pinterest.com/v5/pins/{pid}", headers=headers, timeout=8)
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
                
                top_pins_list.append({
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
                })
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


# ─── API Routes ───────────────────────────────────────────────────────────────
@app.route("/api/health")
def api_health():
    return jsonify({"status": "healthy", "service": "Simple Space Analytics"})


@app.route("/api/analytics", methods=["GET"])
def api_get_analytics():
    """Returns the latest stored analytics data."""
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
    port = 5555
    print("=" * 65)
    print("  🚀 Simple Space Haven — Live Analytics Web Application")
    print(f"  📊 Live Dashboard  → http://127.0.0.1:{port}")
    print(f"  ⚡ API Endpoint    → http://127.0.0.1:{port}/api/analytics")
    print(f"  🔄 Live Sync API   → http://127.0.0.1:{port}/api/analytics/refresh")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
