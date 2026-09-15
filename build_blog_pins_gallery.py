import csv
from pathlib import Path
import autopilot

out_gallery = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/blog_pins_gallery.html")
out_csv = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/pinterest_blog_schedule.csv")
out_csv_all = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/pinterest_blog_schedule_all5.csv")

pins_data = [
    {
        "status": "already_added",
        "status_label": "✓ Already Added on Pinterest",
        "badge_color": "#16a34a",
        "title": "14 Genius Amazon Kitchen Hacks That Double Countertop Space",
        "media_url": "https://iili.io/nK8Cc4j.jpg",
        "local_img": "pins/hero_kitchen_blog_pin.jpg",
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "desc": "Living in a small apartment? Reclaim your kitchen countertop with these 14 renter-friendly Amazon India organizers. Zero drilling, easy setup, and top ratings. Tap the link to read the full guide and check today's live Amazon deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/14-genius-amazon-kitchen-hacks-that.html",
        "publish_date": "Added Manually",
        "keywords": "Kitchen organization, Small kitchen storage, Rental friendly hacks, Amazon kitchen finds, Countertop space savers"
    },
    {
        "status": "already_added",
        "status_label": "✓ Already Added on Pinterest",
        "badge_color": "#16a34a",
        "title": "14 Amazon Balcony Finds That Make Tiny Spaces Feel Huge",
        "media_url": "https://iili.io/nKSdxql.jpg",
        "local_img": "pins/hero_balcony_blog_pin.jpg",
        "board": "Balcony Essentials & Decor for Small Spaces",
        "desc": "Even a tiny 4x4 balcony can become your dream morning coffee nook! Discover 14 weather-resistant, renter-friendly space savers, railing planters, and cozy lighting from Amazon India. Tap to read the full guide & check live deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/14-amazon-balcony-finds-that-make-tiny.html",
        "publish_date": "Added Manually",
        "keywords": "Balcony decor, Small balcony ideas, Apartment balcony, Railing planters, Outdoor space savers, Rental friendly decor"
    },
    {
        "status": "already_added",
        "status_label": "✓ Already Added on Pinterest",
        "badge_color": "#16a34a",
        "title": "12 Amazon Bedroom & Closet Space Savers Worth The Hype",
        "media_url": "https://iili.io/nKSd11V.jpg",
        "local_img": "pins/hero_bedroom_blog_pin.jpg",
        "board": "Bedroom Essentials",
        "desc": "Reclaim your closet and bedroom space! These 12 high-utility organizers from Amazon India maximize hanging space by 300% and keep seasonal blankets out of sight with zero hassle. Tap to read the full guide and check today's prices! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/12-amazon-closet-bedroom-space-savers.html",
        "publish_date": "Added Manually",
        "keywords": "Bedroom organization, Small bedroom hacks, Closet organizers, Under bed storage, Apartment storage ideas"
    },
    {
        "status": "ready_for_csv",
        "status_label": "⏳ Ready in CSV Schedule",
        "badge_color": "#d97706",
        "title": "13 No-Drill Bathroom Storage Hacks Every Renter Needs From Amazon",
        "media_url": "https://iili.io/nKSWjup.jpg",
        "local_img": "pins/hero_bathroom_blog_pin.jpg",
        "board": "Small Bathroom Makeover",
        "desc": "Stop cluttering your small bathroom! These 13 rust-resistant, zero-drill organizers from Amazon India transform cramped showers and small vanities into spa-like order without damaging rental tiles. Tap to view the full guide & check deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/13-no-drill-bathroom-storage-hacks.html",
        "publish_date": "2026-09-11 15:45:22",
        "keywords": "Bathroom organization, Small bathroom hacks, No drill shower caddy, Rental bathroom makeover, Apartment living hacks"
    },
    {
        "status": "ready_for_csv",
        "status_label": "⏳ Ready in CSV Schedule",
        "badge_color": "#d97706",
        "title": "12 Clever Small Living Room Hacks You Wish You Found Sooner",
        "media_url": "https://iili.io/nKSWent.jpg",
        "local_img": "pins/hero_living_room_blog_pin.jpg",
        "board": "Living Room Decor for Small Spaces",
        "desc": "Decorating a compact living room? Here are 12 space-conscious, aesthetic decor and storage solutions from Amazon India that make small apartments feel open, elegant, and clutter-free on a budget. Tap to read the full guide! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/12-clever-small-living-room-hacks-you.html",
        "publish_date": "2026-09-12 11:20:15",
        "keywords": "Living room decor, Small space living, Floating wall shelves, Apartment therapy, Budget home decor, Renter friendly hacks"
    }
]

# 1. Generate Visual HTML Review Gallery
cards_html = ""
for idx, p in enumerate(pins_data, 1):
    cards_html += f"""
    <div class="pin-card">
        <div class="pin-img-wrap">
            <img src="{p['media_url']}" alt="{p['title']}" loading="lazy" />
            <div class="badge" style="background: {p['badge_color']};">{p['status_label']}</div>
        </div>
        <div class="pin-info">
            <div class="pin-board">#{idx:02d} • {p['board']}</div>
            <div class="pin-title">{p['title']}</div>
            <div class="pin-meta">
                <span>📅 <strong>Schedule:</strong> {p['publish_date']}</span>
            </div>
            <div class="pin-link">
                <a href="{p['link']}" target="_blank">🔗 View Destination Blog Post &rarr;</a>
            </div>
        </div>
    </div>
    """

gallery_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simple Space Haven — Blog Pins Visual Review</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f4f3ef;
    margin: 0;
    padding: 32px 16px;
    color: #1e293b;
  }}
  .header {{
    text-align: center;
    max-width: 800px;
    margin: 0 auto 36px;
  }}
  .header h1 {{
    margin: 0 0 8px;
    font-size: 30px;
    font-weight: 800;
    color: #0f172a;
  }}
  .header p {{
    margin: 0;
    font-size: 16px;
    color: #64748b;
  }}
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
    gap: 28px;
    max-width: 1400px;
    margin: 0 auto;
  }}
  .pin-card {{
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    display: flex;
    flex-direction: column;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .pin-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.1);
  }}
  .pin-img-wrap {{
    position: relative;
    width: 100%;
    background: #e2e8f0;
  }}
  .pin-img-wrap img {{
    width: 100%;
    height: auto;
    display: block;
    aspect-ratio: 2 / 3;
    object-fit: cover;
  }}
  .badge {{
    position: absolute;
    top: 12px;
    left: 12px;
    color: #ffffff;
    font-size: 11px;
    font-weight: 800;
    padding: 5px 12px;
    border-radius: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .pin-info {{
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-grow: 1;
  }}
  .pin-board {{
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    color: #0d9488;
    letter-spacing: 0.5px;
  }}
  .pin-title {{
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.4;
  }}
  .pin-meta {{
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
  }}
  .pin-link {{
    margin-top: auto;
    padding-top: 12px;
    border-top: 1px solid #f1f5f9;
  }}
  .pin-link a {{
    color: #2563eb;
    text-decoration: none;
    font-weight: 700;
    font-size: 13px;
  }}
  .pin-link a:hover {{
    text-decoration: underline;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>📌 Simple Space Haven — Visual Blog Pins Review</h1>
  <p>Preview all 5 Hero Blog Pins before scheduling the remaining 2 to Pinterest</p>
</div>
<div class="gallery">
  {cards_html}
</div>
</body>
</html>
"""

with open(out_gallery, "w", encoding="utf-8") as f:
    f.write(gallery_html)
print(f"✓ Visual Review HTML generated: {out_gallery}")

# 2. Write CSV with the 2 pending pins (Bathroom and Living Room)
pending_pins = [p for p in pins_data if p["status"] == "ready_for_csv"]
fieldnames = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for p in pending_pins:
        writer.writerow({
            "Title": p["title"],
            "Media URL": p["media_url"],
            "Pinterest board": p["board"],
            "Thumbnail": "",
            "Description": p["desc"],
            "Link": p["link"],
            "Publish date": p["publish_date"],
            "Keywords": p["keywords"]
        })
print(f"✓ Generated 2-Pin Schedule CSV: {out_csv}")

# 3. Also write full 5-pin CSV for reference
with open(out_csv_all, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for p in pins_data:
        writer.writerow({
            "Title": p["title"],
            "Media URL": p["media_url"],
            "Pinterest board": p["board"],
            "Thumbnail": "",
            "Description": p["desc"],
            "Link": p["link"],
            "Publish date": p["publish_date"],
            "Keywords": p["keywords"]
        })
print(f"✓ Generated All 5-Pin Master CSV: {out_csv_all}")

# Open gallery in default browser
autopilot.open_in_browser(out_gallery)
