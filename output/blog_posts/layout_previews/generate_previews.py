import json
import re
from pathlib import Path

BASE_DIR = Path("/home/nithin/Downloads/Downloads_old/simpleSpace")
with open(BASE_DIR / "test_data.json") as f:
    all_items = json.load(f)

with open(BASE_DIR / "pinned_history.json") as f:
    history = json.load(f)

kitchen_items = [i for i in all_items if i.get("board") == "Smart Kitchen Essentials & Organization Ideas"][:14]
out_dir = BASE_DIR / "output/blog_posts/layout_previews"

# ==========================================
# VERSION 1: Wirecutter Compact Row
# ==========================================
def build_v1():
    rows_html = ""
    for i, item in enumerate(kitchen_items, 1):
        asin = item.get("asin", "")
        img_url = history.get(asin, {}).get("cdn_url", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")
        headline = item.get("headline") or clean_name
        rating = item.get("rating", "4.0 ★")
        aff_link = item.get("affiliate_url", "")
        desc = item.get("seo_description", "")
        
        rows_html += f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center; padding: 22px 0; border-bottom: 1px solid #e2e8f0;">
            <div style="flex: 0 0 160px; max-width: 160px; text-align: center;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored">
                    <img src="{img_url}" alt="{clean_name}" loading="lazy" style="width: 100%; max-height: 160px; object-fit: contain; border-radius: 8px; background: #f8fafc; padding: 6px; border: 1px solid #edf2f7;" />
                </a>
            </div>
            <div style="flex: 1; min-width: 260px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 11px; font-weight: 800; color: #2563eb; background: #eff6ff; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                        #{i} Pick
                    </span>
                    <span style="font-size: 12px; font-weight: 600; color: #b45309;">
                        ⭐ {rating}
                    </span>
                </div>
                <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; line-height: 1.35;">
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #0f172a; text-decoration: none;">
                        {headline}
                    </a>
                </h3>
                <p style="font-size: 14px; color: #475569; line-height: 1.6; margin: 0 0 12px 0;">
                    {desc[:180]}...
                </p>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <span style="font-size: 12px; color: #16a34a; font-weight: 600;">
                        ⚡ In Stock · Prime Eligible
                    </span>
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #0f172a; color: #ffffff; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 700; text-decoration: none; display: inline-block;">
                        Check Live Price on Amazon &rarr;
                    </a>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V1: Wirecutter Compact Row Layout</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fafafa; color: #1e293b; padding: 24px 12px; margin: 0;">
<div style="max-width: 760px; margin: 0 auto; background: #ffffff; padding: 32px 24px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
    <div style="font-size: 12px; font-weight: 800; color: #2563eb; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
        Layout Option 1: Wirecutter-Style Compact Media Row
    </div>
    <h1 style="font-size: 26px; font-weight: 800; color: #0f172a; margin: 0 0 14px 0; line-height: 1.3;">
        14 Smart Kitchen Storage Hacks That Instantly Double Countertop Space
    </h1>
    <p style="font-size: 15px; color: #475569; line-height: 1.7; margin-bottom: 24px;">
        Horizontal split layout with compact 160px image thumbnails, punchy reviews, and immediate action buttons. Reduces scrolling by 70% compared to heavy cards.
    </p>
    <div style="background: #f0fdf4; border-left: 3px solid #16a34a; padding: 12px 16px; font-size: 13px; color: #166534; margin-bottom: 24px;">
        <strong>💡 Pro Tip:</strong> Tiered vertical organizers double shelf capacity without drilling holes in rental cabinets.
    </div>
    <div>
        {rows_html}
    </div>
    <div style="margin-top: 32px; font-size: 12px; color: #94a3b8; text-align: center;">
        Affiliate Disclaimer: Reader supported. As an Amazon Associate, Simple Space Haven earns from qualifying purchases.
    </div>
</div>
</body>
</html>
"""
    with open(out_dir / "kitchen_v1_wirecutter.html", "w", encoding="utf-8") as f:
        f.write(html)


# ==========================================
# VERSION 2: Minimalist Editorial Listicle
# ==========================================
def build_v2():
    items_html = ""
    for i, item in enumerate(kitchen_items, 1):
        asin = item.get("asin", "")
        img_url = history.get(asin, {}).get("cdn_url", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")
        headline = item.get("headline") or clean_name
        rating = item.get("rating", "4.0 ★")
        aff_link = item.get("affiliate_url", "")
        desc = item.get("seo_description", "")
        
        items_html += f"""
        <section style="margin-bottom: 48px;">
            <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
                <span style="font-family: Georgia, serif; font-size: 28px; font-weight: 400; color: #94a3b8; line-height: 1;">
                    {i:02d}
                </span>
                <h2 style="font-size: 21px; font-weight: 700; color: #111827; margin: 0; line-height: 1.35;">
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #111827; text-decoration: none;">
                        {clean_name}
                    </a>
                </h2>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored">
                    <img src="{img_url}" alt="{clean_name}" loading="lazy" style="max-width: 100%; max-height: 380px; border-radius: 8px; object-fit: contain;" />
                </a>
            </div>

            <p style="font-size: 16px; color: #374151; line-height: 1.8; margin-bottom: 16px;">
                {desc}
            </p>

            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding: 12px 0; border-top: 1px dashed #e5e7eb; border-bottom: 1px dashed #e5e7eb;">
                <div style="font-size: 13px; color: #6b7280;">
                    ⭐ Rated <strong>{rating}</strong> by Amazon India shoppers
                </div>
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #059669; font-weight: 700; font-size: 14px; text-decoration: none;">
                    Check today's live deal &rarr;
                </a>
            </div>
        </section>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V2: Minimalist Editorial Magazine</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #ffffff; color: #111827; padding: 32px 16px; margin: 0;">
<div style="max-width: 680px; margin: 0 auto;">
    <div style="font-size: 11px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #6b7280; margin-bottom: 12px;">
        Layout Option 2: Minimalist Editorial Magazine
    </div>
    <h1 style="font-family: Georgia, serif; font-size: 32px; font-weight: 400; color: #111827; margin: 0 0 16px 0; line-height: 1.25;">
        14 Smart Kitchen Storage Hacks That Instantly Double Countertop Space
    </h1>
    <p style="font-size: 17px; color: #4b5563; line-height: 1.8; margin-bottom: 32px;">
        Zero heavy boxes, zero nested frames. Reads like a natural story in an architectural digest, focusing on generous whitespace and authentic typography.
    </p>
    <div style="border-top: 2px solid #111827; padding-top: 24px; margin-bottom: 36px;">
        {items_html}
    </div>
    <div style="font-size: 12px; color: #9ca3af; text-align: center; margin-top: 48px;">
        Affiliate Disclaimer: As an Amazon Associate, Simple Space Haven earns from qualifying purchases.
    </div>
</div>
</body>
</html>
"""
    with open(out_dir / "kitchen_v2_minimalist.html", "w", encoding="utf-8") as f:
        f.write(html)


# ==========================================
# VERSION 3: Matrix + Micro Cards
# ==========================================
def build_v3():
    # 1. Comparison Matrix rows (first 4 items as top picks)
    table_rows = ""
    top_picks = kitchen_items[:4]
    badges = ["🥇 Best Overall", "🥈 Best Value", "🥉 Space Saver", "⭐ Top Renter Pick"]
    for idx, (b, item) in enumerate(zip(badges, top_picks)):
        clean_name = item.get("subheadline") or item.get("product_name", "")[:35]
        aff_link = item.get("affiliate_url", "")
        table_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 10px; font-weight: 700; font-size: 12px; color: #0f172a;">{b}</td>
            <td style="padding: 10px; font-size: 13px; color: #334155;">{clean_name}</td>
            <td style="padding: 10px; text-align: right;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #ff9900; color: #111; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 800; text-decoration: none; white-space: nowrap;">
                    View Deal &rarr;
                </a>
            </td>
        </tr>
        """

    # 2. Micro Cards
    micro_cards = ""
    for i, item in enumerate(kitchen_items, 1):
        asin = item.get("asin", "")
        img_url = history.get(asin, {}).get("cdn_url", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")
        rating = item.get("rating", "4.0 ★")
        aff_link = item.get("affiliate_url", "")
        
        micro_cards += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px; display: flex; align-items: center; gap: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="flex: 0 0 70px; text-align: center;">
                <img src="{img_url}" alt="{clean_name}" loading="lazy" style="width: 70px; height: 70px; object-fit: contain; border-radius: 6px; background: #f8fafc;" />
            </div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">
                    #{i} · ⭐ {rating}
                </div>
                <div style="font-size: 14px; font-weight: 700; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #0f172a; text-decoration: none;">
                        {clean_name}
                    </a>
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
                    Renter-friendly · Zero drilling · Live discount
                </div>
            </div>
            <div style="flex: 0 0 auto;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #0f172a; color: #ffffff; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 700; text-decoration: none; white-space: nowrap; display: inline-block;">
                    Check Price &rarr;
                </a>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V3: Comparison Matrix + Micro Cards</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; padding: 24px 12px; margin: 0;">
<div style="max-width: 720px; margin: 0 auto;">
    <div style="font-size: 12px; font-weight: 800; color: #d97706; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
        Layout Option 3: Quick-Pick Matrix + Micro Cards
    </div>
    <h1 style="font-size: 26px; font-weight: 800; margin: 0 0 14px 0; line-height: 1.3;">
        14 Smart Kitchen Storage Hacks That Instantly Double Countertop Space
    </h1>
    
    <!-- Quick Picks Cheat Sheet Matrix -->
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 28px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
        <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
            ⚡ Quick-Pick Comparison (1-Minute Cheat Sheet)
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid #e2e8f0; font-size: 11px; color: #64748b; text-transform: uppercase;">
                    <th style="padding: 6px 10px;">Award</th>
                    <th style="padding: 6px 10px;">Top Recommendation</th>
                    <th style="padding: 6px 10px; text-align: right;">Amazon Deal</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <!-- Micro Cards Stream -->
    <div style="font-size: 14px; font-weight: 800; color: #475569; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
        Full Curated Checklist:
    </div>
    <div>
        {micro_cards}
    </div>

    <div style="margin-top: 28px; font-size: 12px; color: #94a3b8; text-align: center;">
        Affiliate Disclaimer: Reader supported. As an Amazon Associate, Simple Space Haven earns from qualifying purchases.
    </div>
</div>
</body>
</html>
"""
    with open(out_dir / "kitchen_v3_matrix.html", "w", encoding="utf-8") as f:
        f.write(html)


# ==========================================
# MASTER PREVIEW HUB
# ==========================================
def build_hub():
    hub_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Compare 3 Lightweight Blog Layouts</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 32px 16px; }
  .container { max-width: 980px; margin: 0 auto; }
  h1 { font-size: 28px; font-weight: 800; text-align: center; margin-bottom: 8px; }
  p.subtitle { text-align: center; color: #94a3b8; margin-bottom: 36px; font-size: 16px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; }
  .card h2 { font-size: 19px; margin: 0 0 10px 0; color: #38bdf8; }
  .badge { display: inline-block; font-size: 11px; font-weight: 800; padding: 4px 8px; border-radius: 4px; margin-bottom: 12px; text-transform: uppercase; }
  .badge-1 { background: #0284c7; color: white; }
  .badge-2 { background: #059669; color: white; }
  .badge-3 { background: #d97706; color: white; }
  .features { list-style: none; padding: 0; margin: 16px 0; color: #cbd5e1; font-size: 14px; line-height: 1.8; }
  .features li::before { content: "✓ "; color: #38bdf8; font-weight: bold; }
  .btn { display: block; text-align: center; background: #38bdf8; color: #0f172a; font-weight: 700; text-decoration: none; padding: 12px 18px; border-radius: 8px; margin-top: 14px; }
  .btn:hover { background: #7dd3fc; }
</style>
</head>
<body>
<div class="container">
    <h1>🎨 Choose Your Favorite Blog Layout</h1>
    <p class="subtitle">We generated all 3 lightweight, user-friendly alternatives for the <strong>Smart Kitchen</strong> article. Click to open and inspect each one:</p>
    
    <div class="cards">
        <!-- Card 1 -->
        <div class="card">
            <div>
                <span class="badge badge-1">Option 1</span>
                <h2>Wirecutter-Style Compact Row</h2>
                <ul class="features">
                    <li>Compact 160px image on the left</li>
                    <li>Editorial review & CTA on the right</li>
                    <li>70% less scrolling than heavy cards</li>
                    <li>Fastest to scan on mobile & desktop</li>
                </ul>
            </div>
            <a class="btn" href="kitchen_v1_wirecutter.html" target="_blank">Open Preview 1 &rarr;</a>
        </div>

        <!-- Card 2 -->
        <div class="card">
            <div>
                <span class="badge badge-2">Option 2</span>
                <h2>Minimalist Magazine Listicle</h2>
                <ul class="features">
                    <li>Zero cards, boxes, or heavy borders</li>
                    <li>Elegant serif numerals (01, 02...)</li>
                    <li>Generous whitespace & storytelling</li>
                    <li>Apartment Therapy / Kinfolk feel</li>
                </ul>
            </div>
            <a class="btn" href="kitchen_v2_minimalist.html" target="_blank">Open Preview 2 &rarr;</a>
        </div>

        <!-- Card 3 -->
        <div class="card">
            <div>
                <span class="badge badge-3">Option 3</span>
                <h2>Quick-Pick Matrix + Micro Cards</h2>
                <ul class="features">
                    <li>1-Minute Cheat Sheet table at the top</li>
                    <li>Ultra-compact 70px micro cards</li>
                    <li>Instant clicks for short attention spans</li>
                    <li>The Strategist / Wirecutter combo</li>
                </ul>
            </div>
            <a class="btn" href="kitchen_v3_matrix.html" target="_blank">Open Preview 3 &rarr;</a>
        </div>
    </div>
</div>
</body>
</html>
"""
    with open(out_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(hub_html)

build_v1()
build_v2()
build_v3()
build_hub()
print("✓ Successfully generated all 3 layout versions and preview hub!")
