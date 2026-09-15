"""
Simple Space Haven - Autopilot Amazon Finder & Pin Batcher
Automatically finds 4+ star products under price threshold on Amazon,
checks pinned_history.json to guarantee ZERO duplicates,
creates multi-style curiosity pins (Editorial, Callout, Curated),
uploads to CDN (0 MB local disk footprint), updates master ledger,
and outputs the Pinterest Bulk Schedule CSV.
"""
import sys
import time
import json
import csv
import re
import random
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    BASE_DIR, OUTPUT_DIR, PINS_DIR, BASE_IMAGES_DIR,
    AMAZON_TRACKING_ID, BRAND_NAME, CURRENCY_SYMBOL,
    DEFAULT_MAX_PRICE, DEFAULT_MIN_RATING,
    BOARD_TAXONOMY, NICHE_DATA, load_niche_data
)
from pin_generator import create_pin
from blog_generator import generate_blog_article
from master_ledger import sync_master_records, purge_local_images

def upload_pin_to_cdn(image_path):
    """Uploads styled pin to a public high-speed CDN so Pinterest cloud can download it."""
    try:
        with open(image_path, "rb") as f:
            r = requests.post("https://freeimage.host/api/1/upload", data={
                "key": "6d207e02198a847aa98d0a2a901485a5",
                "action": "upload",
                "format": "json"
            }, files={"source": f}, timeout=25)
            if r.status_code == 200:
                data = r.json()
                return data.get("image", {}).get("url")
    except Exception as e:
        print(f"Warning: CDN upload failed ({e}), falling back to local filename.")
    return None

HISTORY_FILE = BASE_DIR / "pinned_history.json"

def generate_human_schedule(count, start_dt=None):
    """
    Generates realistic, organic human posting timestamps:
    - Never uses sharp rounded hours like 12:00 or 12:30.
    - Adds natural human jitter (e.g. 65-105 minutes + random seconds).
    - Respects active waking hours (08:00 AM - 11:15 PM).
    - Automatically sleeps at night and resumes the next morning.
    """
    if not start_dt:
        start_dt = datetime.now() + timedelta(minutes=random.randint(18, 38), seconds=random.randint(10, 52))
        
    current_dt = start_dt
    schedule = []
    
    for _ in range(count):
        gap_minutes = random.randint(65, 105)
        gap_seconds = random.randint(14, 58)
        current_dt += timedelta(minutes=gap_minutes, seconds=gap_seconds)
        
        # If time enters sleeping hours (past 11:15 PM or before 8:00 AM), move to next morning
        if current_dt.hour >= 23 or current_dt.hour < 8:
            if current_dt.hour >= 23:
                next_day = current_dt.date() + timedelta(days=1)
            else:
                next_day = current_dt.date()
                
            rand_m = random.randint(15, 50)
            rand_s = random.randint(10, 55)
            current_dt = datetime(next_day.year, next_day.month, next_day.day, 8, rand_m, rand_s)
            
        schedule.append(current_dt.strftime("%Y-%m-%d %H:%M:%S"))
        
    return schedule

def get_next_schedule_start():
    """Calculates the start time for the next batch following the previous scheduled batch."""
    csv_file = OUTPUT_DIR / "pinterest_bulk_schedule.csv"
    if csv_file.exists():
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                dates = [r["Publish date"] for r in reader if r.get("Publish date")]
                if dates:
                    latest_dt = max(datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates)
                    if latest_dt > datetime.now():
                        next_day = latest_dt.date() + timedelta(days=1)
                        rand_m = random.randint(18, 45)
                        rand_s = random.randint(10, 50)
                        return datetime(next_day.year, next_day.month, next_day.day, 8, rand_m, rand_s)
        except Exception:
            pass
    return None

def open_in_browser(file_path):
    """Opens a file in the default browser in a cross-platform manner."""
    try:
        import platform
        import subprocess
        system = platform.system()
        if system == "Linux":
            subprocess.run(["xdg-open", str(file_path)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin":
            subprocess.run(["open", str(file_path)], check=False)
        elif system == "Windows":
            os.startfile(str(file_path))
    except Exception:
        pass

def generate_pin_gallery(rows, out_file):
    """Creates a beautiful, single-page responsive HTML gallery for reviewing all pins at once."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{BRAND_NAME} — Visual Pin Review Gallery</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f4f3ef;
    margin: 0;
    padding: 30px;
    color: #222;
  }}
  .header {{
    text-align: center;
    margin-bottom: 40px;
  }}
  .header h1 {{
    margin: 0 0 10px;
    font-size: 28px;
    color: #1a1a1a;
  }}
  .header p {{
    margin: 0;
    font-size: 16px;
    color: #666;
  }}
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 30px;
    max-width: 1400px;
    margin: 0 auto;
  }}
  .pin-card {{
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
  }}
  .pin-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
  }}
  .pin-img-wrap {{
    position: relative;
    width: 100%;
    background: #eee;
  }}
  .pin-img-wrap img {{
    width: 100%;
    height: auto;
    display: block;
    aspect-ratio: 2 / 3;
    object-fit: cover;
  }}
  .pin-info {{
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-grow: 1;
  }}
  .pin-board {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: #c44d34;
    letter-spacing: 0.5px;
  }}
  .pin-title {{
    font-size: 15px;
    font-weight: 600;
    color: #222;
    line-height: 1.4;
  }}
  .pin-date {{
    font-size: 13px;
    color: #4c6e59;
    font-weight: 600;
    margin-top: auto;
    padding-top: 8px;
    border-top: 1px solid #f0f0f0;
  }}
  .pin-link {{
    margin-top: 4px;
    font-size: 13px;
  }}
  .pin-link a {{
    color: #0066c0;
    text-decoration: none;
    font-weight: 600;
  }}
  .pin-link a:hover {{
    text-decoration: underline;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>📌 {BRAND_NAME} — Visual Pin Review Gallery</h1>
  <p>All {len(rows)} pins formatted, hosted, and scheduled across the week</p>
</div>
<div class="gallery">
"""
    for idx, r in enumerate(rows, 1):
        html_content += f"""
  <div class="pin-card">
    <div class="pin-img-wrap">
      <img src="{r.get('Media URL', '')}" alt="Pin {idx}" loading="lazy">
    </div>
    <div class="pin-info">
      <div class="pin-board">#{idx:02d} • {r.get('Pinterest board', '')}</div>
      <div class="pin-title">{r.get('Title', '')}</div>
      <div class="pin-date">📅 Publish: {r.get('Publish date', '')}</div>
      <div class="pin-link"><a href="{r.get('Link', '')}" target="_blank">View Amazon Item ↗</a></div>
    </div>
  </div>
"""
    html_content += """
</div>
</body>
</html>
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Visual Review Gallery updated: {out_file}")

SESSION_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def search_amazon_candidates(session, query, board_name, board_cfg, history, max_price=999, min_rating=3.8):
    query_enc = query.replace(" ", "+")
    # Natural search URL with organic search engine referer
    url = f"https://www.amazon.in/s?k={query_enc}&ref=nb_sb_noss"
    headers = SESSION_HEADERS.copy()
    headers["Referer"] = random.choice([
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://duckduckgo.com/"
    ])
    
    # Always use a fresh clean session to avoid bot-check cookie carryover
    s = requests.Session()
    try:
        r = s.get(url, headers=headers, timeout=12)
        if r.status_code != 200 or len(r.text) < 5000:
            headers["Referer"] = "https://www.google.co.in/"
            s = requests.Session()
            r = s.get(url, headers=headers, timeout=12)
            if r.status_code != 200 or len(r.text) < 5000:
                return []
    except Exception as e:
        print(f"Network error searching '{query}': {e}")
        return []
        
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.find_all("div", {"data-component-type": "s-search-result"})
    candidates = []
    
    for it in items:
        asin = it.get("data-asin")
        if not asin or len(asin) != 10 or asin in history:
            continue
            
        h2 = it.find("h2")
        raw_title = h2.get_text(strip=True) if h2 else ""
        if not raw_title or len(raw_title) < 15:
            continue
            
        # Price Check
        price_elem = it.find("span", class_="a-price-whole")
        if not price_elem:
            continue
        try:
            price_val = int(price_elem.get_text(strip=True).replace(",", "").replace(".", ""))
        except ValueError:
            continue
            
        if price_val > max_price or price_val < 149:
            continue
            
        # Rating Check
        rating_elem = it.find("span", class_="a-icon-alt")
        rating_text = rating_elem.get_text(strip=True) if rating_elem else "4.2 out of 5 stars"
        match = re.search(r"(\d+\.\d+)", rating_text)
        star_num = float(match.group(1)) if match else 4.0
        
        if star_num < min_rating:
            continue
            
        # Image (Transform thumbnail into 1500px Ultra-HD master URL)
        img_elem = it.find("img", class_="s-image")
        raw_img_url = img_elem.get("src") if img_elem else None
        if not raw_img_url:
            continue
            
        hd_img_url = re.sub(r"\._[A-Z0-9_,]+_\.", "._SL1500_.", raw_img_url)
        img_url = hd_img_url
            
        # Clean title for pin display
        clean_title = re.sub(r"[,\-|].*", "", raw_title).strip()
        if len(clean_title) < 15:
            clean_title = raw_title[:60].strip()
            
        candidates.append({
            "asin": asin,
            "raw_title": raw_title,
            "clean_title": clean_title,
            "price_inr": f"{CURRENCY_SYMBOL}{price_val}",
            "star_num": star_num,
            "rating_str": f"{star_num:.1f} ★",
            "img_url": img_url,
            "board": board_name,
            "badge": board_cfg.get("badge", "MUST-HAVE"),
            "headline_prefix": board_cfg.get("headline_prefix", "Genius Hack"),
            "topics": board_cfg.get("topics", []),
            "hooks": board_cfg.get("hooks", []),
            "affiliate_url": f"https://www.amazon.in/dp/{asin}?tag={AMAZON_TRACKING_ID}"
        })
        
    return candidates

def run_autopilot(total_pins_target=5, max_price=None, min_rating=None, niche_id=None, purge_local=True, continue_schedule=False):
    if niche_id:
        niche = load_niche_data(niche_id)
        boards_dict = niche.get("boards", {})
        niche_title = niche.get("niche_name", niche_id)
    else:
        boards_dict = BOARD_TAXONOMY
        niche_title = NICHE_DATA.get("niche_name", "Active Niche")
        
    max_price = max_price or DEFAULT_MAX_PRICE
    min_rating = min_rating or DEFAULT_MIN_RATING
    
    print("==================================================")
    print(f"  {BRAND_NAME.upper()} — SMART AUTOPILOT PIN ENGINE")
    print(f"  Niche: {niche_title}")
    print(f"  Target: {total_pins_target} Fresh Pins | Rating >= {min_rating}★ | Price < {CURRENCY_SYMBOL}{max_price}")
    print("==================================================")
    
    history = load_history()
    print(f"📊 Currently tracked in database: {len(history)} products (will NOT duplicate)")
    
    session = requests.Session()
    collected_products = []
    
    # Balanced Round-robin across boards and queries
    boards_list = list(boards_dict.items())
    if not boards_list:
        print("❌ Error: No boards configured for this niche.")
        return
        
    max_queries_per_board = max(len(b[1].get("queries", [])) for b in boards_list)
    max_cycles = max(200, max_queries_per_board * len(boards_list) * 8)
    board_idx = 0
    
    while len(collected_products) < total_pins_target and board_idx < max_cycles:
        b_name, b_cfg = boards_list[board_idx % len(boards_list)]
        queries = b_cfg.get("queries", [])
        if not queries:
            board_idx += 1
            continue
            
        q_idx = (board_idx // len(boards_list)) % len(queries)
        query = queries[q_idx]
        
        print(f"\n🔍 Exploring board: '{b_name}' | Query: '{query}'...")
        candidates = search_amazon_candidates(
            session, query, b_name, b_cfg, history, max_price, min_rating
        )
        
        # Take max 2 per board per cycle to distribute across all boards!
        added_this_board = 0
        for cand in candidates:
            if cand["asin"] not in [c["asin"] for c in collected_products] and cand["asin"] not in history:
                print(f"  ✓ Found fresh product: {cand['clean_title'][:45]} ({cand['price_inr']}, {cand['rating_str']})")
                collected_products.append(cand)
                added_this_board += 1
                if len(collected_products) >= total_pins_target or added_this_board >= 2:
                    break
                    
        time.sleep(1.2)
        board_idx += 1
        
    if not collected_products:
        print("No new products found meeting criteria.")
        return
        
    print(f"\n🎉 Successfully found {len(collected_products)} fresh, verified products!")
    print("\n[Step 2/4] Generating styled curiosity pins & uploading to CDN...")
    
    # Generate humanized organic posting schedule (randomized jitter, active waking hours)
    start_dt = get_next_schedule_start() if continue_schedule else None
    if start_dt:
        print(f"📅 Continuing schedule from previous batch! Next pin drops: {start_dt}")
    human_schedule = generate_human_schedule(len(collected_products), start_dt=start_dt)
    
    processed_items = []
    csv_rows = []
    
    for idx, p in enumerate(collected_products, 1):
        asin = p["asin"]
        pid = f"auto_{asin}"
        img_dest = BASE_IMAGES_DIR / f"{pid}.jpg"
        
        # Download product photo
        try:
            r_img = session.get(p["img_url"], headers=SESSION_HEADERS, timeout=15)
            with open(img_dest, "wb") as f:
                f.write(r_img.content)
        except Exception as e:
            print(f"Failed to download image for {asin}: {e}")
            continue
            
        # Select dynamic psychological hook
        hooks = p.get("hooks", [])
        if hooks:
            chosen_headline = hooks[(idx - 1) % len(hooks)]
        else:
            chosen_headline = f"{p['headline_prefix']} You Need For Small Apartments"
            
        item_data = {
            "id": pid,
            "asin": asin,
            "product_name": p["raw_title"][:100],
            "category": p["badge"],
            "board": p["board"],
            "headline": chosen_headline,
            "subheadline": p["clean_title"],
            "badge": p["badge"],
            "rating": f"{p['rating_str']} (Top Rated)",
            "cta": "Check Today's Price  >",
            "price_inr": p["price_inr"],
            "affiliate_url": p["affiliate_url"],
            "seo_title": f"{chosen_headline} | {p['clean_title']}",
            "seo_description": f"Reclaim your home space with {p['clean_title']}! Rated {p['rating_str']} on Amazon India. Renter friendly, easy installation, zero drilling required. Tap the link to view real customer reviews and check today's deal on Amazon.",
            "keywords": p["topics"]
        }
        
        # 1. Generate Pin Image with Auto-Rotating Styles (Editorial, Callout, Curated)
        out_pin = PINS_DIR / f"{pid}_pinterest.jpg"
        create_pin(item_data, img_dest, out_pin, style="auto")
        
        # 2. Upload to CDN
        cdn_url = upload_pin_to_cdn(out_pin) or p["img_url"]
        
        # 3. Add to CSV with Organic Humanized Publish Date
        time_str = human_schedule[idx - 1]
        topics_str = ", ".join(p["topics"])
        
        csv_rows.append({
            "Title": item_data["seo_title"],
            "Media URL": cdn_url,
            "Pinterest board": item_data["board"],
            "Thumbnail": "",
            "Description": item_data["seo_description"],
            "Link": item_data["affiliate_url"],
            "Publish date": time_str,
            "Keywords": topics_str
        })
        
        # 4. Save to history database (with CDN URL for permanent record)
        history[asin] = {
            "title": p["clean_title"],
            "board": p["board"],
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "price": p["price_inr"],
            "rating": p["rating_str"],
            "link": p["affiliate_url"],
            "cdn_url": cdn_url
        }
        processed_items.append(item_data)
        print(f"[{idx}/{len(collected_products)}] ✓ Pin ready & hosted: {cdn_url}")
        time.sleep(1.0)
        
    # Save updated history
    save_history(history)
    
    # Save Pinterest CSV (Combine with existing batch when continue_schedule is active)
    csv_file = OUTPUT_DIR / "pinterest_bulk_schedule.csv"
    existing_rows = []
    if continue_schedule and csv_file.exists():
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_rows = [r for r in reader if r.get("Title")]
        except Exception:
            existing_rows = []
            
    combined_csv_rows = existing_rows + csv_rows
    fieldnames = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_csv_rows)
        
    # Update Blogger article draft
    test_data_file = BASE_DIR / "test_data.json"
    existing_blog_items = []
    if continue_schedule and test_data_file.exists():
        try:
            with open(test_data_file, "r", encoding="utf-8") as f:
                existing_blog_items = json.load(f)
        except Exception:
            existing_blog_items = []
    combined_blog_items = existing_blog_items + processed_items
    with open(test_data_file, "w", encoding="utf-8") as f:
        json.dump(combined_blog_items, f, indent=2, ensure_ascii=False)
    generate_blog_article()
    
    # Generate Visual Review Gallery (Single-page review for all pins)
    gallery_file = OUTPUT_DIR / "pin_gallery.html"
    generate_pin_gallery(combined_csv_rows, gallery_file)
    open_in_browser(gallery_file)
    
    # Sync permanent master ledger
    print("\n[Step 4/4] Updating Permanent Master Ledger & Managing Disk Storage...")
    sync_master_records()
    
    # Auto-purge local images to keep disk at 0 MB
    if purge_local:
        print("\n🗑️ Auto-purging temporary local images (0 MB local footprint)...")
        purge_local_images()
    
    print("\n==================================================")
    print(f"🎉 AUTOPILOT FINISHED!")
    print(f"📊 Added {len(processed_items)} brand-new products to history database.")
    print(f"📄 Pinterest Bulk Schedule CSV: {csv_file}")
    print(f"📑 Master Ledger Record: {OUTPUT_DIR / 'master_pin_records.csv'}")
    print("👉 Just open Pinterest and drop this CSV file!")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Number of pins to discover and generate")
    parser.add_argument("--niche", type=str, default=None, help="Niche ID (e.g. home_organization, tech_gadgets)")
    parser.add_argument("--continue", "--next-batch", dest="continue_schedule", action="store_true", help="Continue schedule from the end of the previous batch")
    parser.add_argument("--keep-local", action="store_true", help="Keep local temporary image copies on disk")
    args = parser.parse_args()
    run_autopilot(total_pins_target=args.count, niche_id=args.niche, purge_local=not args.keep_local, continue_schedule=args.continue_schedule)
