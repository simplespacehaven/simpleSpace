"""
Simple Space Haven - Viral Multi-Post Blogger Engine
Rotates between Option 1 (Wirecutter Compact Row) and Option 3 (Quick-Pick Matrix + Micro-Cards).
Optimized with high-CTR, viral Pinterest & Google SEO title formulas (front-loaded keywords, 40-char mobile rule).
"""
import json
import re
from pathlib import Path
from config import BASE_DIR, OUTPUT_DIR, BLOG_URL, BRAND_NAME, AMAZON_TRACKING_ID

# Viral, high-CTR metadata tailored for Pinterest & Google SEO search algorithms
BOARD_METADATA = {
    "Smart Kitchen Essentials & Organization Ideas": {
        "slug": "genius-amazon-kitchen-hacks-double-space",
        "title": "Genius Amazon Kitchen Hacks That Instantly Double Countertop Space",
        "layout": "v1_wirecutter",  # Wirecutter Compact Row
        "intro": "When you live in a compact apartment or rental space, countertop real estate disappears in seconds. Instead of cramming cabinets or doing messy renovations, these viral, renter-friendly organizers from Amazon India unlock unused vertical storage, clear cluttered counters, and make small kitchens feel twice as big.",
        "tip": "Always prioritize tiered vertical organizers and sliding under-cabinet baskets. They transform dead vertical cabinet air into 2x usable storage space without drilling a single hole."
    },
    "Balcony Essentials & Decor for Small Spaces": {
        "slug": "amazon-balcony-finds-small-spaces",
        "title": "Amazon Balcony Finds That Make Tiny Spaces Feel Huge (Renter-Friendly)",
        "layout": "v3_matrix",  # Quick-Pick Matrix + Micro Cards
        "intro": "Even a tiny 4x4 balcony can become your personal morning coffee sanctuary or peaceful plant nook. With the right weather-durable space savers, railing planters, and warm ambient touches from Amazon India, you can turn overlooked outdoor corners into your home's favorite oasis on a budget.",
        "tip": "Use railing-mounted hanging planters and foldable bistro fixtures. They keep the entire floor clear for comfortable walking and easy cleaning."
    },
    "Small Bathroom Makeover": {
        "slug": "no-drill-small-bathroom-storage-hacks",
        "title": "No-Drill Bathroom Storage Hacks Every Renter Needs From Amazon",
        "layout": "v1_wirecutter",  # Wirecutter Compact Row
        "intro": "Small bathrooms quickly become chaotic with damp bottles, toiletries, and cleaning supplies cluttering every ledge. These rust-resistant, moisture-tested organizers from Amazon India create clean, spa-like order with zero drilling, keeping your vanity and shower stall spotless.",
        "tip": "Install waterproof corner suction caddies inside the shower. Corners are almost always wasted space that can easily hold 8–10 daily bottles."
    },
    "Bedroom Essentials": {
        "slug": "amazon-bedroom-closet-space-savers",
        "title": "Amazon Closet & Bedroom Space Savers That Are Actually Worth The Hype",
        "layout": "v3_matrix",  # Quick-Pick Matrix + Micro Cards
        "intro": "A peaceful bedroom requires visual calm. When wardrobe closets are bursting and bedroom corners are piled with extra bedding and seasonal clothes, space feels suffocating. These high-utility bedroom organizers from Amazon India reclaim your closet and under-bed space effortlessly.",
        "tip": "Pair airtight vacuum compression bags with under-bed wheeled bins to store 4x more winter duvets and extra pillows completely out of sight."
    },
    "Living Room Decor for Small Spaces": {
        "slug": "small-living-room-upgrades-amazon",
        "title": "Clever Small Living Room Hacks You Wish You Found Sooner",
        "layout": "v1_wirecutter",  # Wirecutter Compact Row
        "intro": "In small apartment living rooms, every piece of furniture and decor needs to earn its spot. Here are high-style, multi-functional home decor items from Amazon India that draw the eye upward, create elegant display areas, and keep clutter tucked away without making the room feel crowded.",
        "tip": "Mount floating wall display shelves at eye level. Drawing vertical sightlines makes ceiling heights feel higher and rooms feel significantly more open."
    }
}

# =========================================================================
# LAYOUT 1: WIRECUTTER-STYLE COMPACT MEDIA ROW (70% Less Scrolling, High CTR)
# =========================================================================
def render_v1_wirecutter(title, intro, tip, items, history, board_name):
    count = len(items)
    full_title = f"{count} {title}"
    
    rows_html = ""
    for i, item in enumerate(items, 1):
        asin = item.get("asin", "")
        img_url = history.get(asin, {}).get("cdn_url", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")
        headline = item.get("headline") or clean_name
        rating = item.get("rating", "4.0 ★")
        aff_link = item.get("affiliate_url", f"https://www.amazon.in/dp/{asin}?tag={AMAZON_TRACKING_ID}")
        desc = item.get("seo_description", "")
        
        rows_html += f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center; padding: 22px 0; border-bottom: 1px solid #e2e8f0;">
            <div style="flex: 0 0 160px; max-width: 160px; text-align: center;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored">
                    <img src="{img_url}" alt="{clean_name}" loading="lazy" style="width: 100%; max-height: 160px; object-fit: contain; border-radius: 8px; background: #f8fafc; padding: 6px; border: 1px solid #edf2f7; transition: transform 0.2s;" />
                </a>
            </div>
            <div style="flex: 1; min-width: 260px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 11px; font-weight: 800; color: #0d9488; background: #f0fdfa; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                        RANK #{i}
                    </span>
                    <span style="font-size: 12px; font-weight: 700; color: #854d0e; background: #fefce8; padding: 2px 8px; border-radius: 4px;">
                        ⭐ {rating}
                    </span>
                </div>
                <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; line-height: 1.35;">
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #0f172a; text-decoration: none;">
                        {headline}
                    </a>
                </h3>
                <div style="font-size: 13px; color: #64748b; margin-bottom: 8px; font-weight: 500;">
                    <strong>Item:</strong> {clean_name}
                </div>
                <p style="font-size: 14px; color: #475569; line-height: 1.6; margin: 0 0 12px 0;">
                    {desc[:190]}...
                </p>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <span style="font-size: 12px; color: #dc2626; font-weight: 700;">
                        ⚡ Live Amazon Deal Active
                    </span>
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #0f172a; color: #ffffff; padding: 9px 18px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none; display: inline-block;">
                        Check Live Price on Amazon &rarr;
                    </a>
                </div>
            </div>
        </div>
        """

    html = f"""<!-- Simple Space Haven - {full_title} (Wirecutter Style) -->
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.7; max-width: 760px; margin: 0 auto; padding: 20px 14px;">
    
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;">
        <span style="font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: #0d9488;">
            🌿 SIMPLE SPACE HAVEN • EDITORIAL ROUNDUP
        </span>
        <span style="font-size: 11px; font-weight: 600; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 10px;">
            ⏱️ 3 min read
        </span>
    </div>

    <h1 style="font-size: 27px; line-height: 1.3; font-weight: 800; color: #0f172a; margin: 0 0 16px 0; letter-spacing: -0.3px;">
        {full_title}
    </h1>

    <p style="font-size: 16px; color: #475569; line-height: 1.75; margin: 0 0 20px 0;">
        {intro}
    </p>

    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 14px 18px; margin-bottom: 28px;">
        <div style="font-size: 13px; font-weight: 700; color: #166534; margin-bottom: 2px;">
            💡 Pro Organizer Secret:
        </div>
        <div style="font-size: 13px; color: #1e293b; line-height: 1.55;">
            {tip}
        </div>
    </div>

    <div style="border-top: 2px solid #0f172a; margin-bottom: 20px;">
        {rows_html}
    </div>

    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-top: 36px;">
        <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0;">
            The Bottom Line on {board_name}
        </h3>
        <p style="font-size: 13px; color: #475569; line-height: 1.65; margin: 0;">
            Organizing small spaces doesn't require complex carpentry. Picking even one or two compact essentials above immediately frees up functional surface area and keeps clutter under control.
        </p>
    </div>

    <div style="margin-top: 28px; padding-top: 14px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center;">
        <strong>Affiliate Disclosure:</strong> As an Amazon Associate, Simple Space Haven earns from qualifying purchases. We only recommend products rated 4★+ with proven small-space utility.
    </div>
</div>
"""
    return html

# =========================================================================
# LAYOUT 3: QUICK-PICK COMPARISON MATRIX + MICRO-CARDS (Instant Click Engine)
# =========================================================================
def render_v3_matrix(title, intro, tip, items, history, board_name):
    count = len(items)
    full_title = f"{count} {title}"
    
    # 1. Quick-Pick Cheat Sheet (Top 4 items)
    top_picks = items[:4]
    badges = ["🥇 Top Overall Pick", "🥈 Best Budget Value", "🥉 Best Space Saver", "⭐ Top Renter Pick"]
    table_rows = ""
    for b, item in zip(badges, top_picks):
        asin = item.get("asin", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")[:36]
        aff_link = item.get("affiliate_url", f"https://www.amazon.in/dp/{asin}?tag={AMAZON_TRACKING_ID}")
        table_rows += f"""
        <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px 8px; font-weight: 800; font-size: 12px; color: #0f172a;">{b}</td>
            <td style="padding: 10px 8px; font-size: 13px; color: #334155; font-weight: 600;">{clean_name}</td>
            <td style="padding: 10px 8px; text-align: right;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #ff9900; color: #111111; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; text-decoration: none; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    Check Live Price &rarr;
                </a>
            </td>
        </tr>
        """

    # 2. Micro-Cards stream
    micro_cards = ""
    for i, item in enumerate(items, 1):
        asin = item.get("asin", "")
        img_url = history.get(asin, {}).get("cdn_url", "")
        clean_name = item.get("subheadline") or item.get("product_name", "")
        headline = item.get("headline") or clean_name
        rating = item.get("rating", "4.0 ★")
        aff_link = item.get("affiliate_url", f"https://www.amazon.in/dp/{asin}?tag={AMAZON_TRACKING_ID}")
        
        micro_cards += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 14px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);">
            <div style="flex: 0 0 76px; text-align: center;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored">
                    <img src="{img_url}" alt="{clean_name}" loading="lazy" style="width: 76px; height: 76px; object-fit: contain; border-radius: 6px; background: #f8fafc; padding: 4px; border: 1px solid #f1f5f9;" />
                </a>
            </div>
            <div style="flex: 1; min-width: 0;">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 2px;">
                    <span style="font-size: 10px; font-weight: 800; color: #b45309; background: #fefce8; padding: 2px 6px; border-radius: 3px;">
                        #{i} • ⭐ {rating}
                    </span>
                    <span style="font-size: 11px; color: #16a34a; font-weight: 700;">
                        ⚡ In Stock
                    </span>
                </div>
                <div style="font-size: 15px; font-weight: 700; color: #0f172a; line-height: 1.35; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="color: #0f172a; text-decoration: none;">
                        {headline}
                    </a>
                </div>
                <div style="font-size: 12px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {clean_name} · Renter-friendly & zero-drill
                </div>
            </div>
            <div style="flex: 0 0 auto;">
                <a href="{aff_link}" target="_blank" rel="nofollow sponsored" style="background: #0f172a; color: #ffffff; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 700; text-decoration: none; white-space: nowrap; display: inline-block;">
                    View Deal &rarr;
                </a>
            </div>
        </div>
        """

    html = f"""<!-- Simple Space Haven - {full_title} (Comparison Matrix Style) -->
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.7; max-width: 740px; margin: 0 auto; padding: 20px 14px;">
    
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;">
        <span style="font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: #d97706;">
            ⚡ SPEED GUIDE • QUICK-PICK PICKS
        </span>
        <span style="font-size: 11px; font-weight: 600; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 10px;">
            ⏱️ 2 min scan
        </span>
    </div>

    <h1 style="font-size: 27px; line-height: 1.3; font-weight: 800; color: #0f172a; margin: 0 0 16px 0; letter-spacing: -0.3px;">
        {full_title}
    </h1>

    <p style="font-size: 16px; color: #475569; line-height: 1.75; margin: 0 0 20px 0;">
        {intro}
    </p>

    <!-- Top 4 Cheat Sheet Comparison Matrix -->
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 28px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);">
        <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
            ⚡ 1-Minute Cheat Sheet: Top 4 Verified Amazon Finds
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid #e2e8f0; font-size: 11px; color: #64748b; text-transform: uppercase;">
                    <th style="padding: 6px 8px;">Category</th>
                    <th style="padding: 6px 8px;">Recommended Item</th>
                    <th style="padding: 6px 8px; text-align: right;">Amazon Link</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <div style="background: #fefce8; border: 1px solid #fef08a; border-left: 4px solid #eab308; border-radius: 8px; padding: 14px 18px; margin-bottom: 28px;">
        <div style="font-size: 13px; font-weight: 700; color: #854d0e; margin-bottom: 2px;">
            💡 Quick Styling Tip:
        </div>
        <div style="font-size: 13px; color: #1e293b; line-height: 1.55;">
            {tip}
        </div>
    </div>

    <!-- Complete Streamlined Micro-Cards List -->
    <div style="font-size: 14px; font-weight: 800; color: #334155; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
        All {count} Tested Picks (Ranked by Utility):
    </div>
    <div>
        {micro_cards}
    </div>

    <div style="margin-top: 28px; padding-top: 14px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center;">
        <strong>Affiliate Disclosure:</strong> As an Amazon Associate, Simple Space Haven earns from qualifying purchases.
    </div>
</div>
"""
    return html

def generate_blog_index(posts, index_file):
    cards_html = ""
    for p in posts:
        layout_badge = "Wirecutter Compact Row" if p["layout"] == "v1_wirecutter" else "Quick-Pick Matrix + Micro Cards"
        badge_color = "#0284c7" if p["layout"] == "v1_wirecutter" else "#d97706"
        cards_html += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <span style="background: #ecfdf5; color: #065f46; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 20px;">
                        {p['count']} Products
                    </span>
                    <span style="background: {badge_color}; color: #ffffff; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                        {layout_badge}
                    </span>
                </div>
                <h2 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 8px 0; line-height: 1.35;">
                    {p['title']}
                </h2>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 18px;">
                    📁 Board: {p['board']}
                </div>
            </div>
            <div>
                <a href="{p['slug']}.html" style="background: #0f172a; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-size: 13px; font-weight: 700; display: block; text-align: center;">
                    View & Copy Post HTML &rarr;
                </a>
            </div>
        </div>
        """

    master_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simple Space Haven — Blog Articles Dashboard</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 32px 16px; }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  .header {{ text-align: center; margin-bottom: 36px; }}
  .header h1 {{ font-size: 30px; font-weight: 800; margin: 0 0 8px 0; }}
  .header p {{ color: #64748b; font-size: 15px; margin: 0; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 20px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📌 Simple Space Haven — Curated Blog Articles</h1>
        <p>5 viral-optimized, lightweight blog listicles rotating between Wirecutter Rows & Quick-Pick Matrix layouts</p>
    </div>
    <div class="grid">
        {cards_html}
    </div>
</div>
</body>
</html>
"""
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(master_html)

def generate_blog_article():
    data_file = BASE_DIR / "test_data.json"
    if not data_file.exists():
        print("No test_data.json found.")
        return []

    with open(data_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    history_file = BASE_DIR / "pinned_history.json"
    history = {}
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    posts_dir = OUTPUT_DIR / "blog_posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    boards = {}
    for item in items:
        b = item.get("board", "Home Organization")
        boards.setdefault(b, []).append(item)

    print("==================================================")
    print("   SIMPLE SPACE HAVEN — VIRAL BLOG ENGINE")
    print("==================================================")
    print("Rotating between Option 1 (Wirecutter) & Option 3 (Matrix) with high-CTR titles:\n")

    generated_posts = []
    primary_html = None

    # Alternate/rotate layouts across boards
    layout_rotation = ["v1_wirecutter", "v3_matrix"]

    for idx, (board_name, board_items) in enumerate(boards.items()):
        assigned_layout = layout_rotation[idx % len(layout_rotation)]
        
        meta = BOARD_METADATA.get(board_name, {
            "slug": re.sub(r"[^a-zA-Z0-9]+", "-", board_name.lower()).strip("-"),
            "title": f"Smart {board_name} Organization Ideas",
            "layout": assigned_layout,
            "intro": f"Discover tested, renter-friendly products from Amazon India for {board_name}.",
            "tip": "Measure your spaces carefully before purchasing to ensure a flush, seamless fit."
        })

        chosen_layout = meta.get("layout", assigned_layout)
        batch_items = board_items[:15]

        if chosen_layout == "v3_matrix":
            post_html = render_v3_matrix(
                title=meta["title"],
                intro=meta["intro"],
                tip=meta["tip"],
                items=batch_items,
                history=history,
                board_name=board_name
            )
            layout_label = "Option 3: Quick-Pick Matrix"
        else:
            post_html = render_v1_wirecutter(
                title=meta["title"],
                intro=meta["intro"],
                tip=meta["tip"],
                items=batch_items,
                history=history,
                board_name=board_name
            )
            layout_label = "Option 1: Wirecutter Row"

        out_file = posts_dir / f"{meta['slug']}.html"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(post_html)

        print(f"  ✓ [{len(batch_items)} items | {layout_label}]")
        print(f"     File: {meta['slug']}.html")
        print(f"     Title: '{len(batch_items)} {meta['title']}'\n")

        generated_posts.append({
            "title": f"{len(batch_items)} {meta['title']}",
            "slug": meta["slug"],
            "file": out_file,
            "count": len(batch_items),
            "board": board_name,
            "layout": chosen_layout
        })

        if primary_html is None:
            primary_html = post_html

    index_file = posts_dir / "index.html"
    generate_blog_index(generated_posts, index_file)
    print(f"✓ Master Blog Dashboard: {index_file}")

    if primary_html:
        with open(OUTPUT_DIR / "blogger_post_draft.html", "w", encoding="utf-8") as f:
            f.write(primary_html)

    print(f"✓ Default draft updated: {OUTPUT_DIR / 'blogger_post_draft.html'}")
    print("==================================================")
    return generated_posts

if __name__ == "__main__":
    generate_blog_article()


