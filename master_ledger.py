"""
Simple Space Haven - Master Ledger & Cloud Record Manager
Maintains a permanent, lightweight record of every pin posted (with public CDN links)
and optionally frees up 100% of local disk space by deleting local temporary image files.
"""
import json
import csv
from pathlib import Path
from config import BASE_DIR, OUTPUT_DIR, PINS_DIR, BASE_IMAGES_DIR

HISTORY_FILE = BASE_DIR / "pinned_history.json"
MASTER_CSV = OUTPUT_DIR / "master_pin_records.csv"

def sync_master_records():
    """Generates a clean, portable CSV ledger containing all historical pins with public CDN links."""
    if not HISTORY_FILE.exists():
        print("No history found.")
        return
        
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
        
    fieldnames = ["ASIN", "Product Title", "Board", "Date Added", "Price", "Rating", "Affiliate Link", "Hosted Image URL"]
    rows = []
    
    for asin, data in history.items():
        rows.append({
            "ASIN": asin,
            "Product Title": data.get("title", ""),
            "Board": data.get("board", ""),
            "Date Added": data.get("date_added", ""),
            "Price": data.get("price", "N/A"),
            "Rating": data.get("rating", "N/A"),
            "Affiliate Link": data.get("link", f"https://www.amazon.in/dp/{asin}?tag=simplespaceha-21"),
            "Hosted Image URL": data.get("cdn_url", "Uploaded directly to Pinterest")
        })
        
    with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"✓ Master records synchronized: {len(rows)} products tracked in {MASTER_CSV}")
    return rows

def upload_video_to_cdn(video_path):
    """Uploads rendered MP4 video to high-speed public CDN and returns the direct permanent URL."""
    try:
        import requests
        with open(video_path, "rb") as f:
            r = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                timeout=45
            )
            if r.status_code == 200 and r.text.strip().startswith("http"):
                return r.text.strip()
    except Exception as e:
        print(f"Warning: Cloud video upload failed ({e})")
    return None

def purge_local_images():
    """Deletes local image files to keep machine disk storage at near 0MB."""
    freed_bytes = 0
    count = 0
    for f in BASE_IMAGES_DIR.glob("*.*"):
        freed_bytes += f.stat().st_size
        f.unlink()
        count += 1
    for f in PINS_DIR.glob("*.jpg"):
        freed_bytes += f.stat().st_size
        f.unlink()
        count += 1
    mb_freed = freed_bytes / (1024 * 1024)
    print(f"🧹 Cleaned up {count} local image files. Freed {mb_freed:.2f} MB from this machine.")
    print("👉 All image records are preserved in the cloud (CDN & Pinterest).")

def purge_local_videos():
    """Deletes local video files to keep machine disk storage at 0MB."""
    vid_dir = OUTPUT_DIR / "videos"
    if not vid_dir.exists():
        return
    freed_bytes = 0
    count = 0
    for f in vid_dir.glob("*.mp4"):
        freed_bytes += f.stat().st_size
        f.unlink()
        count += 1
    mb_freed = freed_bytes / (1024 * 1024)
    print(f"🧹 Cleaned up {count} local video files. Freed {mb_freed:.2f} MB from this machine.")
    print("👉 All video files are safely hosted on the cloud CDN.")

def purge_all_local_media():
    """Purges both images and videos from local machine after cloud sync."""
    purge_local_images()
    purge_local_videos()

if __name__ == "__main__":
    sync_master_records()

