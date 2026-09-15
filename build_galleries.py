import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. BUILD BLOG PINS GALLERY
blog_cards = [
    {
        "title": "15 Genius Amazon Kitchen Hacks That Instantly Double Countertop Space",
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "slug": "genius-amazon-kitchen-hacks-double-space.html",
        "pin_img": "https://iili.io/nqHTmUF.jpg",
        "badge": "KITCHEN SPACE SAVER",
        "count": "15 Items",
        "desc": "Living in a small apartment? Reclaim your kitchen countertop with these 15 renter-friendly Amazon India organizers. Zero drilling, easy setup, and top ratings.",
        "link": "blog_posts/genius-amazon-kitchen-hacks-double-space.html"
    },
    {
        "title": "15 Amazon Balcony Finds That Make Tiny Spaces Feel Huge (Renter-Friendly)",
        "board": "Balcony Essentials & Decor for Small Spaces",
        "slug": "amazon-balcony-finds-small-spaces.html",
        "pin_img": "https://iili.io/nqHuJDv.jpg",
        "badge": "BALCONY MAKEOVER",
        "count": "15 Items",
        "desc": "Even a tiny 4x4 balcony can become your dream morning coffee nook! 15 weather-resistant, renter-friendly space savers, railing planters, and cozy lighting.",
        "link": "blog_posts/amazon-balcony-finds-small-spaces.html"
    },
    {
        "title": "15 No-Drill Bathroom Storage Hacks Every Renter Needs From Amazon",
        "board": "Small Bathroom Makeover",
        "slug": "no-drill-small-bathroom-storage-hacks.html",
        "pin_img": "https://iili.io/nqHu3Vp.jpg",
        "badge": "BATHROOM MUST-HAVE",
        "count": "15 Items",
        "desc": "Stop cluttering your small bathroom! 15 rust-resistant, zero-drill organizers from Amazon India transform cramped showers into spa-like order.",
        "link": "blog_posts/no-drill-small-bathroom-storage-hacks.html"
    },
    {
        "title": "15 Amazon Closet & Bedroom Space Savers That Are Actually Worth The Hype",
        "board": "Bedroom Essentials",
        "slug": "amazon-bedroom-closet-space-savers.html",
        "pin_img": "https://iili.io/nqHunJn.jpg",
        "badge": "WARDROBE SPACE SAVER",
        "count": "15 Items",
        "desc": "Reclaim your closet and bedroom space! 15 high-utility organizers from Amazon India maximize hanging space by 300% and keep blankets out of sight.",
        "link": "blog_posts/amazon-bedroom-closet-space-savers.html"
    },
    {
        "title": "15 Clever Small Living Room Hacks You Wish You Found Sooner",
        "board": "Living Room Decor for Small Spaces",
        "slug": "small-living-room-upgrades-amazon.html",
        "pin_img": "https://iili.io/nqHuxOG.jpg",
        "badge": "LIVING ROOM ESSENTIALS",
        "count": "15 Items",
        "desc": "Decorating a compact living room? 15 space-conscious, aesthetic decor and storage solutions from Amazon India that make small apartments feel open and elegant.",
        "link": "blog_posts/small-living-room-upgrades-amazon.html"
    }
]

cards_html = ""
for b in blog_cards:
    cards_html += f"""
    <div class="blog-card">
      <a href="{b['link']}" class="pin-preview-link" title="Click to open {b['title']}">
        <img src="{b['pin_img']}" alt="{b['title']}" loading="lazy">
        <div class="overlay-hint">
          <span class="overlay-btn">📖 Click To Open Article ➔</span>
        </div>
      </a>
      <div class="card-body">
        <div class="card-meta">
          <span class="board-badge">{b['board']}</span>
          <span class="item-count">{b['count']}</span>
        </div>
        <a href="{b['link']}" class="card-title">{b['title']}</a>
        <p class="card-desc">{b['desc']}</p>
        <div class="card-actions">
          <a href="{b['link']}" class="btn-read">Read Full Article ({b['count']}) ➔</a>
          <a href="{b['pin_img']}" target="_blank" class="btn-pin">View Pin 🔍</a>
        </div>
      </div>
    </div>
"""

blog_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simple Space Haven — Blog Pins & Article Hub</title>
<style>
  :root {{
    --primary: #181b1e;
    --accent-gold: #d4af37;
    --accent-terracotta: #c44d34;
    --bg-page: #f6f5f1;
    --card-bg: #ffffff;
    --text-dark: #1e293b;
    --text-muted: #64748b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-page);
    color: var(--text-dark);
    padding: 40px 20px 80px;
  }}
  .container {{ max-width: 1360px; margin: 0 auto; }}
  .header {{ text-align: center; margin-bottom: 48px; }}
  .header .badge {{
    display: inline-block;
    background: var(--primary);
    color: var(--accent-gold);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 20px;
    margin-bottom: 12px;
  }}
  .header h1 {{ font-size: 34px; font-weight: 800; color: var(--primary); margin-bottom: 10px; }}
  .header p {{ font-size: 17px; color: var(--text-muted); max-width: 680px; margin: 0 auto; }}
  .nav-bar {{ display: flex; justify-content: center; gap: 16px; margin-bottom: 40px; }}
  .nav-btn {{
    padding: 10px 22px;
    border-radius: 25px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s;
  }}
  .nav-btn.active, .nav-btn:hover {{ background: var(--primary); color: #ffffff; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 36px; }}
  .blog-card {{
    background: var(--card-bg);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border: 1px solid #edebe4;
    transition: transform 0.25s, box-shadow 0.25s;
    display: flex;
    flex-direction: column;
  }}
  .blog-card:hover {{ transform: translateY(-6px); box-shadow: 0 16px 36px rgba(0,0,0,0.12); }}
  .pin-preview-link {{ display: block; position: relative; overflow: hidden; background: #1e293b; }}
  .pin-preview-link img {{ width: 100%; aspect-ratio: 2 / 3; object-fit: cover; display: block; }}
  .overlay-hint {{
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.4);
    opacity: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.2s ease;
  }}
  .pin-preview-link:hover .overlay-hint {{ opacity: 1; }}
  .overlay-btn {{
    background: #ffffff;
    color: var(--primary);
    font-weight: 700;
    padding: 12px 24px;
    border-radius: 30px;
    font-size: 15px;
  }}
  .card-body {{ padding: 24px; display: flex; flex-direction: column; flex-grow: 1; }}
  .card-meta {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .board-badge {{
    background: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 6px;
  }}
  .item-count {{ background: #fef3c7; color: #92400e; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px; }}
  .card-title {{ font-size: 19px; font-weight: 700; line-height: 1.35; color: var(--primary); margin-bottom: 10px; text-decoration: none; }}
  .card-title:hover {{ color: var(--accent-terracotta); }}
  .card-desc {{ font-size: 14px; color: var(--text-muted); line-height: 1.55; margin-bottom: 20px; flex-grow: 1; }}
  .card-actions {{ display: flex; gap: 12px; margin-top: auto; }}
  .btn-read {{
    flex: 1;
    background: var(--accent-terracotta);
    color: #ffffff;
    text-align: center;
    padding: 12px 18px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 14px;
    text-decoration: none;
  }}
  .btn-read:hover {{ background: #a83822; }}
  .btn-pin {{
    background: #f8fafc;
    color: #334155;
    border: 1px solid #e2e8f0;
    padding: 12px 16px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 13px;
    text-decoration: none;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge">EDITORIAL BLOG HUB</div>
    <h1>Simple Space Haven — Blog Pin Reviews</h1>
    <p>Click any pin image or "Read Full Article" to immediately open and review the live formatted HTML blog guide.</p>
  </div>
  
  <div class="nav-bar">
    <a href="blog_pins_gallery.html" class="nav-btn active">📌 Blog Pins Gallery (6 Articles)</a>
    <a href="pin_gallery.html" class="nav-btn">🛍️ Normal Product Pins Gallery (128 Pins)</a>
    <a href="blog_posts/index.html" class="nav-btn">📑 All Blog Articles Index</a>
  </div>

  <div class="grid">
    {cards_html}
  </div>
</div>
</body>
</html>
"""

with open(OUTPUT_DIR / "blog_pins_gallery.html", "w", encoding="utf-8") as f:
    f.write(blog_html)
print("✓ Generated: output/blog_pins_gallery.html")

# 2. BUILD NORMAL PRODUCT PINS GALLERY
with open(BASE_DIR / "pinned_history.json", "r", encoding="utf-8") as f:
    history = json.load(f)

boards = sorted(list(set(d.get("board", "General") for d in history.values() if d.get("board"))))

filter_buttons_html = f"""<button class="filter-btn active" onclick="filterBoard('all', this)">All Boards ({len(history)})</button>\n"""
for b in boards:
    b_count = sum(1 for d in history.values() if d.get("board") == b)
    filter_buttons_html += f"""<button class="filter-btn" onclick="filterBoard('{b}', this)">{b} ({b_count})</button>\n"""

prod_cards_html = ""
for asin, d in history.items():
    b = d.get("board", "General")
    title = d.get("title", "")
    price = d.get("price", "₹499")
    rating = d.get("rating", "4.2 ★")
    cdn = d.get("cdn_url", "")
    aff_link = d.get("link", f"https://www.amazon.in/dp/{asin}?tag=simplespaceha-21")
    if not cdn:
        continue
    
    prod_cards_html += f"""
    <div class="pin-card" data-board="{b}">
      <div class="pin-img-box">
        <a href="{aff_link}" target="_blank">
          <img src="{cdn}" alt="{title}" loading="lazy">
        </a>
      </div>
      <div class="pin-info">
        <span class="board-tag">{b}</span>
        <div class="pin-title" title="{title}">{title}</div>
        <div class="price-rating">
          <span class="price">{price}</span>
          <span class="rating">⭐ {rating}</span>
        </div>
        <a href="{aff_link}" target="_blank" class="btn-aff">Check Deal on Amazon ➔</a>
      </div>
    </div>
"""

prod_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simple Space Haven — Normal Product Pins Gallery (128 Pins)</title>
<style>
  :root {{
    --primary: #181b1e;
    --accent-gold: #d4af37;
    --accent-terracotta: #c44d34;
    --bg-page: #f6f5f1;
    --card-bg: #ffffff;
    --text-dark: #1e293b;
    --text-muted: #64748b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-page);
    color: var(--text-dark);
    padding: 40px 20px 80px;
  }}
  .container {{ max-width: 1440px; margin: 0 auto; }}
  .header {{ text-align: center; margin-bottom: 36px; }}
  .header .badge {{
    display: inline-block;
    background: var(--primary);
    color: var(--accent-gold);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 20px;
    margin-bottom: 12px;
  }}
  .header h1 {{ font-size: 34px; font-weight: 800; color: var(--primary); margin-bottom: 10px; }}
  .header p {{ font-size: 16px; color: var(--text-muted); }}
  .nav-bar {{ display: flex; justify-content: center; gap: 16px; margin-bottom: 32px; }}
  .nav-btn {{
    padding: 10px 22px;
    border-radius: 25px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s;
  }}
  .nav-btn.active, .nav-btn:hover {{ background: var(--primary); color: #ffffff; }}
  .filters {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-bottom: 36px; }}
  .filter-btn {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #475569;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .filter-btn.active, .filter-btn:hover {{
    background: var(--accent-terracotta);
    color: #ffffff;
    border-color: var(--accent-terracotta);
  }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 28px; }}
  .pin-card {{
    background: var(--card-bg);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    border: 1px solid #edebe4;
    display: flex;
    flex-direction: column;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .pin-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.12); }}
  .pin-img-box {{ position: relative; background: #0f172a; }}
  .pin-img-box img {{ width: 100%; aspect-ratio: 2 / 3; object-fit: cover; display: block; }}
  .pin-info {{ padding: 18px; display: flex; flex-direction: column; flex-grow: 1; }}
  .board-tag {{
    font-size: 11px;
    font-weight: 700;
    color: #0284c7;
    background: #f0f9ff;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    margin-bottom: 8px;
    align-self: flex-start;
  }}
  .pin-title {{
    font-size: 15px;
    font-weight: 700;
    line-height: 1.35;
    color: var(--primary);
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .price-rating {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }}
  .price {{ font-size: 16px; font-weight: 800; color: #15803d; }}
  .rating {{ font-size: 13px; font-weight: 700; color: #b45309; background: #fefce8; padding: 2px 8px; border-radius: 4px; }}
  .btn-aff {{
    margin-top: auto;
    background: var(--primary);
    color: #ffffff;
    text-align: center;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
  }}
  .btn-aff:hover {{ background: var(--accent-terracotta); }}
</style>
<script>
function filterBoard(bName, btn) {{
  const cards = document.querySelectorAll(".pin-card");
  const btns = document.querySelectorAll(".filter-btn");
  btns.forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  cards.forEach(c => {{
    if (bName === "all" || c.dataset.board === bName) {{
      c.style.display = "flex";
    }} else {{
      c.style.display = "none";
    }}
  }});
}}
</script>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge">PRODUCT PINS DATABASE</div>
    <h1>Simple Space Haven — Normal Product Pins ({len(history)} Total)</h1>
    <p>All product pins generated for Amazon India affiliate products across 6 boards with permanent CDN image hosting.</p>
  </div>
  
  <div class="nav-bar">
    <a href="blog_pins_gallery.html" class="nav-btn">📌 Blog Pins Gallery (6 Articles)</a>
    <a href="pin_gallery.html" class="nav-btn active">🛍️ Normal Product Pins Gallery ({len(history)} Pins)</a>
    <a href="blog_posts/index.html" class="nav-btn">📑 All Blog Articles Index</a>
  </div>

  <div class="filters">
    {filter_buttons_html}
  </div>

  <div class="grid">
    {prod_cards_html}
  </div>
</div>
</body>
</html>
"""

with open(OUTPUT_DIR / "pin_gallery.html", "w", encoding="utf-8") as f:
    f.write(prod_html)
print("✓ Generated: output/pin_gallery.html")
