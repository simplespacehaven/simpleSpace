import csv
from datetime import datetime, timedelta
from pathlib import Path

# 5 Published Blog URLs
BLOG_URLS = {
    "kitchen": "https://simplespacehaven.blogspot.com/2026/09/14-genius-amazon-kitchen-hacks-that.html",
    "balcony": "https://simplespacehaven.blogspot.com/2026/09/14-amazon-balcony-finds-that-make-tiny.html",
    "bathroom": "https://simplespacehaven.blogspot.com/2026/09/13-no-drill-bathroom-storage-hacks.html",
    "bedroom": "https://simplespacehaven.blogspot.com/2026/09/12-amazon-closet-bedroom-space-savers.html",
    "living_room": "https://simplespacehaven.blogspot.com/2026/09/12-clever-small-living-room-hacks-you.html"
}

# 15 Verified Pins (3 Multi-Angle Pins per Blog)
PINS = [
    # KITCHEN (Board: Smart Kitchen Essentials & Organization Ideas)
    {
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "title": "15 Genius Amazon Kitchen Hacks That Instantly Double Countertop Space",
        "angle": "Editorial Roundup",
        "media_url": "https://iili.io/nqHTmUF.jpg",
        "link": BLOG_URLS["kitchen"],
        "desc": "Living in a small apartment? Reclaim your kitchen countertop with these 15 renter-friendly Amazon India organizers. Zero drilling, easy setup, and top ratings. Tap to read the full curated guide & live deals! #ad",
        "keywords": "Kitchen organization, Small kitchen storage, Rental friendly hacks, Amazon kitchen finds, Countertop space savers, Apartment living"
    },
    {
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "title": "Smart Under-Sink & Countertop Space Savers for Small Rental Kitchens",
        "angle": "Problem-Solver",
        "media_url": "https://iili.io/ndzlz2R.jpg",
        "link": BLOG_URLS["kitchen"],
        "desc": "Struggling with cramped kitchen counters? Tiered sliding under-sink organizers and spice racks transform dead vertical space into 2x storage without drilling. Tap to view our top Amazon picks! #ad",
        "keywords": "Kitchen storage, Under sink organizer, Small space living, Amazon India finds, Rental friendly decor"
    },
    {
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "title": "Aesthetic Amazon Kitchen Organizers That Keep Counters Spotless",
        "angle": "Budget & Aesthetic",
        "media_url": "https://iili.io/ndzl124.jpg",
        "link": BLOG_URLS["kitchen"],
        "desc": "Keep spices, oils, and pantry staples beautifully organized on a budget! Discover top-rated 3-tier kitchen racks from Amazon India that look luxury in compact kitchens. Tap to explore! #ad",
        "keywords": "Pantry organization, Spice rack, Small kitchen hacks, Kitchen decor, Amazon finds India"
    },

    # BALCONY (Board: Balcony Essentials & Decor for Small Spaces)
    {
        "board": "Balcony Essentials & Decor for Small Spaces",
        "title": "15 Amazon Balcony Finds That Make Tiny Spaces Feel Huge (Renter-Friendly)",
        "angle": "Editorial Roundup",
        "media_url": "https://iili.io/nqHuJDv.jpg",
        "link": BLOG_URLS["balcony"],
        "desc": "Even a tiny 4x4 balcony can become your dream morning coffee nook! Discover 15 weather-resistant, renter-friendly space savers, railing planters, and cozy lighting from Amazon India. Tap to view the full guide! #ad",
        "keywords": "Balcony decor, Small balcony ideas, Apartment balcony, Railing planters, Outdoor space savers, Rental friendly decor"
    },
    {
        "board": "Balcony Essentials & Decor for Small Spaces",
        "title": "How to Turn a Tiny Apartment Balcony Into a Cozy Coffee Oasis",
        "angle": "Cozy Nook & Aesthetic",
        "media_url": "https://iili.io/nd0Di8u.jpg",
        "link": BLOG_URLS["balcony"],
        "desc": "Transform your outdoor space with zero construction! Heavy-duty railing pot holders and vertical plant stands keep your balcony floor clear and open for relaxing. Tap to view prices on Amazon! #ad",
        "keywords": "Balcony makeover, Railing plant holder, Vertical garden, Apartment therapy, Small space living"
    },
    {
        "board": "Balcony Essentials & Decor for Small Spaces",
        "title": "Must-Have Railing Planters & Vertical Space Savers from Amazon",
        "angle": "Vertical Storage",
        "media_url": "https://iili.io/nd1JJSI.jpg",
        "link": BLOG_URLS["balcony"],
        "desc": "Love plants but short on floor space? Hang your garden vertically with these durable, rust-proof railing stands and planters from Amazon India. Tap to read the full guide & check deals! #ad",
        "keywords": "Plant stands, Hanging flower pots, Balcony gardening, Renter friendly hacks, Outdoor decor"
    },

    # BATHROOM (Board: Small Bathroom Makeover)
    {
        "board": "Small Bathroom Makeover",
        "title": "15 No-Drill Bathroom Storage Hacks Every Renter Needs From Amazon",
        "angle": "Editorial Roundup",
        "media_url": "https://iili.io/nqHu3Vp.jpg",
        "link": BLOG_URLS["bathroom"],
        "desc": "Stop cluttering your small bathroom! These 15 rust-resistant, zero-drill organizers from Amazon India transform cramped showers into spa-like order without damaging rental tiles. Tap to view the guide! #ad",
        "keywords": "Bathroom organization, Small bathroom hacks, No drill shower caddy, Rental bathroom makeover, Apartment living hacks"
    },
    {
        "board": "Small Bathroom Makeover",
        "title": "Zero-Drill Suction & Corner Shower Organizers for Rental Apartments",
        "angle": "Problem-Solver",
        "media_url": "https://iili.io/nd1J7ob.jpg",
        "link": BLOG_URLS["bathroom"],
        "desc": "Clear shower bottle clutter with zero tile damage! Heavy-duty suction and adhesive bathroom shelves that hold shampoo bottles securely and never rust. Tap to check today's live deals! #ad",
        "keywords": "Shower caddy, Bathroom shelf no drill, Renter safe bathroom, Small apartment hacks, Amazon finds"
    },
    {
        "board": "Small Bathroom Makeover",
        "title": "Aesthetic Adhesive Bathroom Shelves That Give Luxury Spa Vibes",
        "angle": "Spa Vibes & Aesthetic",
        "media_url": "https://iili.io/nd1Rmpn.jpg",
        "link": BLOG_URLS["bathroom"],
        "desc": "Turn bathroom clutter into calm hotel luxury! Sleek aluminum floating shower shelves and vanity organizers that install in seconds. Tap to see the full list of top-rated Amazon picks! #ad",
        "keywords": "Bathroom makeover, Aesthetic bathroom, Floating shelves, No drill organizer, Amazon India"
    },

    # BEDROOM (Board: Bedroom Essentials)
    {
        "board": "Bedroom Essentials",
        "title": "7 Amazon Closet & Bedroom Space Savers That Are Actually Worth The Hype",
        "angle": "Editorial Roundup",
        "media_url": "https://iili.io/nd1tyAb.jpg",
        "link": BLOG_URLS["bedroom"],
        "desc": "Reclaim your closet and bedroom space! These 7 high-utility organizers from Amazon India maximize wardrobe capacity by 300% and keep clutter out of sight with zero hassle. Tap to read the guide! #ad",
        "keywords": "Bedroom organization, Small bedroom hacks, Closet organizers, Under bed storage, Apartment storage ideas, Minimalist living"
    },
    {
        "board": "Bedroom Essentials",
        "title": "How to Triple Small Closet Space with Foldable Wardrobe Organizers",
        "angle": "Closet 3x Capacity",
        "media_url": "https://iili.io/ndGuFY7.jpg",
        "link": BLOG_URLS["bedroom"],
        "desc": "Closet bursting with clothes? Modular foldable wardrobe organizers with sturdy handles keep folded shirts, jeans, and accessories neat and visible. Tap through to view prices on Amazon! #ad",
        "keywords": "Closet makeover, Wardrobe organizer, Small bedroom ideas, Closet organization hacks, Amazon finds"
    },
    {
        "board": "Bedroom Essentials",
        "title": "Genius Collapsible Fabric Storage Cubes for Clean Bedroom Organization",
        "angle": "Under-Bed & Modular",
        "media_url": "https://iili.io/ndGTDpn.jpg",
        "link": BLOG_URLS["bedroom"],
        "desc": "Keep extra blankets, linens, and off-season clothes dust-free and compact! High-density fabric storage cubes that fit perfectly on closet shelves and under bed frames. Tap to explore! #ad",
        "keywords": "Storage cubes, Blanket organizer, Bedroom essentials, Minimalist home, Amazon India"
    },

    # LIVING ROOM (Board: Living Room Decor for Small Spaces)
    {
        "board": "Living Room Decor for Small Spaces",
        "title": "15 Clever Small Living Room Hacks You Wish You Found Sooner",
        "angle": "Editorial Roundup",
        "media_url": "https://iili.io/nd1DIxR.jpg",
        "link": BLOG_URLS["living_room"],
        "desc": "Decorating a compact living room? Here are 15 space-conscious, aesthetic decor and storage solutions from Amazon India that make small apartments feel open, elegant, and clutter-free on a budget. Tap to read! #ad",
        "keywords": "Living room decor, Small space living, Floating wall shelves, Apartment therapy, Budget home decor, Renter friendly hacks"
    },
    {
        "board": "Living Room Decor for Small Spaces",
        "title": "Clever Floating Wall Shelves That Maximize Vertical Living Room Space",
        "angle": "Vertical Storage",
        "media_url": "https://iili.io/nd1DaJn.jpg",
        "link": BLOG_URLS["living_room"],
        "desc": "Draw the eyes upward and keep floors clear! Modern clear and wooden floating wall shelves that showcase your favorite books, plants, and art with zero bulk. Tap to check live Amazon prices! #ad",
        "keywords": "Floating shelves, Small living room, Wall decor, Vertical storage, Apartment hacks"
    },
    {
        "board": "Living Room Decor for Small Spaces",
        "title": "Small Apartment Living Room Upgrades That Look High-End on a Budget",
        "angle": "Budget Luxury",
        "media_url": "https://iili.io/ndE5wbe.jpg",
        "link": BLOG_URLS["living_room"],
        "desc": "You do not need expensive renovations to give your small living room a designer aesthetic. Discover minimalist acrylic display shelves and accent storage from Amazon India. Tap to view the full guide! #ad",
        "keywords": "Home decor ideas, Apartment living, Aesthetic living room, Budget interior design, Amazon finds"
    }
]

# Stagger dates across next 3 days (Sep 14, Sep 15, Sep 16)
start_dt = datetime(2026, 9, 14, 9, 0, 0)
rows = []
gallery_items = []

for idx, p in enumerate(PINS):
    day_offset = idx // 5 # 0 (Sep 14), 1 (Sep 15), 2 (Sep 16)
    slot = idx % 5
    hours = [9, 12, 15, 18, 20]
    
    pub_dt = (start_dt + timedelta(days=day_offset)).replace(
        hour=hours[slot],
        minute=15 + (idx * 7) % 35,
        second=10
    )
    
    rows.append({
        "Title": p["title"],
        "Media URL": p["media_url"],
        "Pinterest board": p["board"],
        "Thumbnail": "",
        "Description": p["desc"],
        "Link": p["link"],
        "Publish date": pub_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Keywords": p["keywords"]
    })
    
    gallery_items.append({
        "title": p["title"],
        "board": p["board"],
        "angle": p["angle"],
        "media_url": p["media_url"],
        "link": p["link"],
        "pub_date": pub_dt.strftime("%b %d, %Y - %I:%M %p"),
        "desc": p["desc"]
    })

# Write CSV files
out_csv = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/pinterest_blog_multiplier_schedule.csv")
ready_csv = Path("/home/nithin/Downloads/pinterest_blog_multiplier_schedule_ready.csv")

fieldnames = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]

for dest in [out_csv, ready_csv]:
    with open(dest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"✓ Created clean CSV with {len(rows)} pins at: {ready_csv}")

# Build Visual Gallery
gallery_html = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/blog_multiplier_pins_gallery.html")

cards_html = ""
for it in gallery_items:
    cards_html += f"""
    <div class="pin-card" data-board="{it['board']}">
        <div class="pin-img-wrapper">
            <img src="{it['media_url']}" alt="{it['title']}" loading="lazy" />
            <span class="pin-badge">{it['angle']}</span>
        </div>
        <div class="pin-info">
            <div class="pin-board-tag">{it['board']}</div>
            <h3 class="pin-title">{it['title']}</h3>
            <p class="pin-desc">{it['desc']}</p>
            <div class="pin-meta">
                <span class="meta-time">📅 {it['pub_date']}</span>
            </div>
            <a href="{it['link']}" target="_blank" class="blog-link-btn">
                <span>Read Linked Blog Post</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </a>
        </div>
    </div>
    """

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Space Haven • 15 Blog Multiplier Pins (Verified)</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #0d1117;
            --bg-card: #161b22;
            --border-card: #30363d;
            --gold-accent: #d4af37;
            --gold-glow: rgba(212, 175, 55, 0.15);
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            padding: 40px 20px;
        }}
        .header {{
            max-width: 1300px;
            margin: 0 auto 30px;
            text-align: center;
        }}
        .header h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.4rem;
            color: #ffffff;
            margin-bottom: 10px;
        }}
        .header p {{
            color: var(--text-muted);
            font-size: 1.05rem;
            max-width: 750px;
            margin: 0 auto 20px;
        }}
        .stats-bar {{
            display: inline-flex;
            gap: 20px;
            background: var(--bg-card);
            padding: 12px 24px;
            border-radius: 40px;
            border: 1px solid var(--border-card);
            margin-bottom: 30px;
            font-size: 0.9rem;
        }}
        .stats-bar span {{ color: var(--gold-accent); font-weight: 700; }}
        .grid {{
            max-width: 1300px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 30px;
        }}
        .pin-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .pin-card:hover {{
            transform: translateY(-4px);
            border-color: var(--gold-accent);
            box-shadow: 0 10px 25px var(--gold-glow);
        }}
        .pin-img-wrapper {{
            position: relative;
            width: 100%;
            background: #000;
        }}
        .pin-img-wrapper img {{
            width: 100%;
            display: block;
            aspect-ratio: 2 / 3;
            object-fit: cover;
        }}
        .pin-badge {{
            position: absolute;
            top: 14px;
            right: 14px;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 20px;
            background: #d4af37;
            color: #111;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .pin-info {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }}
        .pin-board-tag {{
            font-size: 0.78rem;
            color: var(--gold-accent);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .pin-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            line-height: 1.4;
            color: #ffffff;
            margin-bottom: 10px;
        }}
        .pin-desc {{
            font-size: 0.86rem;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 16px;
            flex-grow: 1;
        }}
        .pin-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 12px;
            border-top: 1px solid var(--border-card);
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-bottom: 16px;
        }}
        .blog-link-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: rgba(212, 175, 55, 0.12);
            color: var(--gold-accent);
            border: 1px solid var(--gold-accent);
            padding: 10px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .blog-link-btn:hover {{
            background: var(--gold-accent);
            color: #111;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Simple Space Haven • 15 Blog Multiplier Pins (Verified)</h1>
        <p>3 Multi-Angle High-CTR Pins per Published Cornerstone Blog. Staggered across the next 3 days on Pinterest.</p>
        <div class="stats-bar">
            <div>Total Pins: <span>15</span></div>
            <div>Articles Targeted: <span>5</span></div>
            <div>Days Scheduled: <span>Sep 14 – Sep 16</span></div>
            <div>Verified Products: <span>100% Home & Decor</span></div>
        </div>
    </div>
    
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""

with open(gallery_html, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"✓ Created Visual Gallery at: {gallery_html}")
