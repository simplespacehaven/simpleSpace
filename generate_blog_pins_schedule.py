import csv
from datetime import datetime, timedelta
import random
from pathlib import Path

out_csv = Path("/home/nithin/Downloads/Downloads_old/simpleSpace/output/pinterest_blog_schedule.csv")

# 5 Live Articles & Hosted Hero Pins
campaigns = [
    {
        "title": "14 Genius Amazon Kitchen Hacks That Double Countertop Space",
        "media_url": "https://iili.io/nK8Cc4j.jpg",
        "board": "Smart Kitchen Essentials & Organization Ideas",
        "desc": "Living in a small apartment? Reclaim your kitchen countertop with these 14 renter-friendly Amazon India organizers. Zero drilling, easy setup, and top ratings. Tap the link to read the full guide and check today's live Amazon deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/14-genius-amazon-kitchen-hacks-that.html",
        "keywords": "Kitchen organization, Small kitchen storage, Rental friendly hacks, Amazon kitchen finds, Countertop space savers, Apartment living",
        "delay_hours": 10
    },
    {
        "title": "14 Amazon Balcony Finds That Make Tiny Spaces Feel Huge",
        "media_url": "https://iili.io/nKSdxql.jpg",
        "board": "Balcony Essentials & Decor for Small Spaces",
        "desc": "Even a tiny 4x4 balcony can become your dream morning coffee nook! Discover 14 weather-resistant, renter-friendly space savers, railing planters, and cozy lighting from Amazon India. Tap to read the full guide & check live deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/14-amazon-balcony-finds-that-make-tiny.html",
        "keywords": "Balcony decor, Small balcony ideas, Apartment balcony, Railing planters, Outdoor space savers, Rental friendly decor",
        "delay_hours": 16
    },
    {
        "title": "12 Amazon Bedroom & Closet Space Savers Worth The Hype",
        "media_url": "https://iili.io/nKSd11V.jpg",
        "board": "Bedroom Essentials",
        "desc": "Reclaim your closet and bedroom space! These 12 high-utility organizers from Amazon India maximize hanging space by 300% and keep seasonal blankets out of sight with zero hassle. Tap to read the full guide and check today's prices! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/12-amazon-closet-bedroom-space-savers.html",
        "keywords": "Bedroom organization, Small bedroom hacks, Closet organizers, Under bed storage, Apartment storage ideas, Minimalist living",
        "delay_hours": 34
    },
    {
        "title": "13 No-Drill Bathroom Storage Hacks Every Renter Needs From Amazon",
        "media_url": "https://iili.io/nKSxdRR.jpg",
        "board": "Small Bathroom Makeover",
        "desc": "Stop cluttering your small bathroom! These 13 rust-resistant, zero-drill organizers from Amazon India transform cramped showers and small vanities into spa-like order without damaging rental tiles. Tap to view the full guide & check deals! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/13-no-drill-bathroom-storage-hacks.html",
        "keywords": "Bathroom organization, Small bathroom hacks, No drill shower caddy, Rental bathroom makeover, Apartment living hacks",
        "delay_hours": 42
    },
    {
        "title": "12 Clever Small Living Room Hacks You Wish You Found Sooner",
        "media_url": "https://iili.io/nKSzYIp.jpg",
        "board": "Living Room Decor for Small Spaces",
        "desc": "Decorating a compact living room? Here are 12 space-conscious, aesthetic decor and storage solutions from Amazon India that make small apartments feel open, elegant, and clutter-free on a budget. Tap to read the full guide! #ad",
        "link": "https://simplespacehaven.blogspot.com/2026/09/12-clever-small-living-room-hacks-you.html",
        "keywords": "Living room decor, Small space living, Floating wall shelves, Apartment therapy, Budget home decor, Renter friendly hacks",
        "delay_hours": 58
    }
]

# Generate staggered schedule starting tomorrow morning
base_time = datetime(2026, 9, 11, 10, 15, 0)
rows = []

for c in campaigns:
    publish_dt = base_time + timedelta(hours=c["delay_hours"], minutes=random.randint(5, 45), seconds=random.randint(10, 50))
    # Keep within waking hours
    if publish_dt.hour >= 23 or publish_dt.hour < 8:
        publish_dt = datetime(publish_dt.year, publish_dt.month, publish_dt.day, 10, random.randint(10, 45), random.randint(10, 50))
        
    rows.append({
        "Title": c["title"],
        "Media URL": c["media_url"],
        "Pinterest board": c["board"],
        "Thumbnail": "",
        "Description": c["desc"],
        "Link": c["link"],
        "Publish date": publish_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Keywords": c["keywords"]
    })

fieldnames = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Generated Pinterest Blog Schedule CSV: {out_csv}")
for r in rows:
    print(f"  • [{r['Publish date']}] '{r['Title'][:40]}...' -> {r['Pinterest board']}")
