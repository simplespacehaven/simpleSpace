#!/usr/bin/env python3
"""
Simple Space Haven - Winning Horse Multiplier Engine
==================================================
Transforms a proven viral winning product into 3 high-converting Pinterest A/B test variations:
1. Deal Hunter (Price & Prime Callout badge)
2. Renter Hack (Problem-solver / No-drill benefit frame)
3. Curated Checklist (Social proof listicle with high save rate)
"""

import os
import io
import csv
import urllib.request
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent.resolve()
FONTS_DIR = BASE_DIR / "assets" / "fonts"
OUTPUT_DIR = BASE_DIR / "output" / "winner_batches"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PIN_W = 1000
PIN_H = 1500

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", Image.BICUBIC))

def get_font(font_name, size):
    font_path = FONTS_DIR / font_name
    if font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            pass
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def fetch_image(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=12).read()
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        print(f"Fetch image error: {e}")
        # Return fallback aesthetic background
        img = Image.new("RGB", (PIN_W, PIN_H), color=(245, 245, 242))
        return img

def create_deal_hunter_pin(base_img, title, price_text="Under ₹999"):
    """Angle A: High-Contrast Price & Prime Deal Badge"""
    canvas = Image.new("RGB", (PIN_W, PIN_H), (255, 255, 255))
    
    # Scale and center-crop image to cover canvas
    img_ratio = base_img.width / base_img.height
    target_ratio = PIN_W / PIN_H
    if img_ratio > target_ratio:
        new_h = PIN_H
        new_w = int(PIN_H * img_ratio)
    else:
        new_w = PIN_W
        new_h = int(PIN_W / img_ratio)
    
    resized = base_img.resize((new_w, new_h), RESAMPLE_FILTER)
    left = (new_w - PIN_W) // 2
    top = (new_h - PIN_H) // 2
    canvas.paste(resized.crop((left, top, left + PIN_W, top + PIN_H)), (0, 0))

    # Add dark gradient overlay at top and bottom for readability
    overlay = Image.new("RGBA", (PIN_W, PIN_H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    # Top badge banner
    ov_draw.rectangle([(50, 60), (PIN_W - 50, 150)], fill=(230, 0, 35, 240)) # Pinterest Red Pill
    
    # Bottom card
    ov_draw.rounded_rectangle([(40, PIN_H - 430), (PIN_W - 40, PIN_H - 50)], radius=28, fill=(15, 23, 42, 230))
    
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Top Badge Text
    font_badge = get_font("Montserrat-Bold.ttf", 42)
    badge_str = f"VERIFIED DEAL: {price_text.upper()}"
    bbox = draw.textbbox((0, 0), badge_str, font=font_badge)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_W - tw) // 2, 85), badge_str, fill=(255, 255, 255), font=font_badge)

    # Card Title
    font_title = get_font("Poppins-ExtraBold.ttf", 52)
    font_sub = get_font("Montserrat-Bold.ttf", 34)
    font_cta = get_font("Montserrat-Bold.ttf", 36)

    lines = wrap_text(title, font_title, PIN_W - 140, draw)[:2]
    cur_y = PIN_H - 390
    for line in lines:
        draw.text((80, cur_y), line, fill=(255, 255, 255), font=font_title)
        cur_y += 68

    # Rating
    draw.text((80, cur_y + 15), "★ 4.8 / 5.0  Top Rated Amazon Find", fill=(251, 191, 36), font=font_sub)

    # Bottom CTA Pill
    ov_draw2 = Image.new("RGBA", (PIN_W, PIN_H), (0, 0, 0, 0))
    ImageDraw.Draw(ov_draw2).rounded_rectangle([(80, PIN_H - 140), (PIN_W - 80, PIN_H - 75)], radius=18, fill=(230, 0, 35, 255))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), ov_draw2).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    
    cta_text = "TAP TO VIEW ON AMAZON >>"
    bbox_cta = draw.textbbox((0, 0), cta_text, font=font_cta)
    draw.text(((PIN_W - (bbox_cta[2] - bbox_cta[0])) // 2, PIN_H - 128), cta_text, fill=(255, 255, 255), font=font_cta)

    return canvas

def create_renter_hack_pin(base_img, title):
    """Angle B: Renter-Friendly / No-Drill Solution Story"""
    canvas = Image.new("RGB", (PIN_W, PIN_H), (250, 248, 245))
    
    # Scale base image into upper hero frame
    hero_h = 950
    img_ratio = base_img.width / base_img.height
    new_w = PIN_W - 80
    new_h = int(new_w / img_ratio)
    if new_h < hero_h:
        new_h = hero_h
        new_w = int(hero_h * img_ratio)
    
    resized = base_img.resize((new_w, new_h), RESAMPLE_FILTER)
    cropped = resized.crop(((new_w - (PIN_W - 80)) // 2, (new_h - hero_h) // 2, (new_w + (PIN_W - 80)) // 2, (new_h + hero_h) // 2))
    
    canvas.paste(cropped, (40, 120))

    # Add stylish frames and badges
    overlay = Image.new("RGBA", (PIN_W, PIN_H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # Renter Badge at Top
    ov_draw.rounded_rectangle([(60, 45), (PIN_W - 60, 105)], radius=14, fill=(5, 150, 105, 255)) # Emerald Green

    # Bottom White Info Card
    ov_draw.rounded_rectangle([(40, 1080), (PIN_W - 40, PIN_H - 45)], radius=24, fill=(255, 255, 255, 255), outline=(229, 231, 235), width=2)

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Top Badge Text
    font_badge = get_font("Montserrat-Bold.ttf", 36)
    badge_str = "RENTER HACK: ZERO DAMAGE / NO GLUE"
    bbox = draw.textbbox((0, 0), badge_str, font=font_badge)
    draw.text(((PIN_W - (bbox[2] - bbox[0])) // 2, 58), badge_str, fill=(255, 255, 255), font=font_badge)

    # Bottom Card Content
    font_title = get_font("Poppins-ExtraBold.ttf", 46)
    font_bullets = get_font("Montserrat-Bold.ttf", 30)

    lines = wrap_text(title, font_title, PIN_W - 140, draw)[:2]
    y = 1115
    for l in lines:
        draw.text((70, y), l, fill=(17, 24, 39), font=font_title)
        y += 60

    # 3 Checkmarks
    bullets = [
        "+ 100% Washable & All-Weather Proof",
        "+ Easy 5-Minute Roll-Out (No Landlord Issues)",
        "+ Instant Luxury Balcony Upgrade"
    ]
    y += 15
    for b in bullets:
        draw.text((70, y), b, fill=(5, 150, 105), font=font_bullets)
        y += 48

    # Tap link brand footnote
    font_foot = get_font("Montserrat-Regular.ttf", 26)
    draw.text((70, PIN_H - 90), "@simplespacehaven  •  Tap pin for Amazon direct link >>", fill=(107, 114, 128), font=font_foot)

    return canvas

def create_listicle_checklist_pin(base_img, title, board="Balcony"):
    """Angle C: Curated 3-Item Listicle / Checklist Layout"""
    canvas = Image.new("RGB", (PIN_W, PIN_H), (248, 249, 250))
    draw = ImageDraw.Draw(canvas)

    # Header Card
    font_header_tag = get_font("Montserrat-Bold.ttf", 30)
    font_header_main = get_font("PlayfairDisplay-Bold.ttf", 54)

    # Clean Dark Header
    draw.rectangle([(0, 0), (PIN_W, 230)], fill=(17, 24, 39))
    draw.text((60, 45), f"SMART SPACE MAKEOVER  •  2026 EDITION", fill=(217, 119, 6), font=font_header_tag)
    draw.text((60, 95), "3 Essentials Every Small Space Needs", fill=(255, 255, 255), font=font_header_main)

    # Hero Image in Middle
    hero_h = 780
    img_ratio = base_img.width / base_img.height
    new_w = PIN_W - 100
    new_h = int(new_w / img_ratio)
    if new_h < hero_h:
        new_h = hero_h
        new_w = int(hero_h * img_ratio)
    
    resized = base_img.resize((new_w, new_h), RESAMPLE_FILTER)
    cropped = resized.crop(((new_w - (PIN_W - 100)) // 2, (new_h - hero_h) // 2, (new_w + (PIN_W - 100)) // 2, (new_h + hero_h) // 2))
    canvas.paste(cropped, (50, 260))

    # Bottom 3 Numbered Badges
    items = [
        ("#01", title[:42] + "..."),
        ("#02", "Railing Hanging Planter Pots"),
        ("#03", "Warm Solar Fairy Vine Lights")
    ]

    cur_y = 1070
    font_num = get_font("Montserrat-Bold.ttf", 28)
    font_item = get_font("Poppins-Bold.ttf", 32)

    for num, item_title in items:
        # Card
        draw.rounded_rectangle([(50, cur_y), (PIN_W - 50, cur_y + 85)], radius=16, fill=(255, 255, 255), outline=(229, 231, 235), width=2)
        # Number badge
        draw.rounded_rectangle([(65, cur_y + 15), (145, cur_y + 70)], radius=10, fill=(230, 0, 35))
        draw.text((80, cur_y + 24), num, fill=(255, 255, 255), font=font_num)
        # Item text
        draw.text((165, cur_y + 24), item_title, fill=(17, 24, 39), font=font_item)
        cur_y += 105

    # Footer CTA
    font_cta = get_font("Montserrat-Bold.ttf", 28)
    draw.text((60, PIN_H - 100), "SAVE THIS PIN  •  Direct product link inside >>", fill=(107, 114, 128), font=font_cta)

    return canvas


def generate_winning_horse_pack(pin_id, title, board, image_url, destination_url):
    """
    Generates all 3 A/B test variations, saves images, and produces ready schedule CSV.
    """
    batch_dir = OUTPUT_DIR / f"horse_{pin_id}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching base image for horse {pin_id}...")
    base_img = fetch_image(image_url)

    # 1. Deal Hunter
    pin1 = create_deal_hunter_pin(base_img, title, "Under ₹999")
    p1_path = batch_dir / "variation_1_deal_hunter.jpg"
    pin1.save(p1_path, quality=95)

    # 2. Renter Hack
    pin2 = create_renter_hack_pin(base_img, title)
    p2_path = batch_dir / "variation_2_renter_hack.jpg"
    pin2.save(p2_path, quality=95)

    # 3. Curated Listicle
    pin3 = create_listicle_checklist_pin(base_img, title, board)
    p3_path = batch_dir / "variation_3_listicle.jpg"
    pin3.save(p3_path, quality=95)

    # Create CSV Schedule
    csv_path = batch_dir / "pinterest_winning_batch_schedule.csv"
    now = datetime.datetime.now()
    dates = [
        (now + datetime.timedelta(days=1, hours=9, minutes=30)).strftime("%Y-%m-%d %H:%M:00"),
        (now + datetime.timedelta(days=2, hours=13, minutes=30)).strftime("%Y-%m-%d %H:%M:00"),
        (now + datetime.timedelta(days=3, hours=18, minutes=30)).strftime("%Y-%m-%d %H:%M:00")
    ]

    base_domain = os.environ.get("RENDER_EXTERNAL_URL", "https://simplespace.onrender.com").rstrip("/")

    variations = [
        {
            "angle": "Deal Hunter (Price & Prime)",
            "title": f"Amazon Deal: {title} (Verified Prime)",
            "desc": f"Verified Amazon Deal on {title}. Best small space solution with Prime delivery. Tap link to check price and discount on Amazon! #amazonfinds #deals #{board.lower().replace(' ', '').replace('&', '')}",
            "filename": "variation_1_deal_hunter.jpg",
            "file_path": str(p1_path),
            "web_url": f"/output/winner_batches/horse_{pin_id}/variation_1_deal_hunter.jpg",
            "full_image_url": f"{base_domain}/output/winner_batches/horse_{pin_id}/variation_1_deal_hunter.jpg",
            "date": dates[0]
        },
        {
            "angle": "Renter Hack (No-Drill Setup)",
            "title": f"Renter-Friendly Hack: {title} (Zero Damage)",
            "desc": f"Apartment & Renter Safe: {title}. 100% reversible, no damage, quick setup for small spaces. Tap link for direct details! #renterfriendly #apartmenthacks #smallspaces",
            "filename": "variation_2_renter_hack.jpg",
            "file_path": str(p2_path),
            "web_url": f"/output/winner_batches/horse_{pin_id}/variation_2_renter_hack.jpg",
            "full_image_url": f"{base_domain}/output/winner_batches/horse_{pin_id}/variation_2_renter_hack.jpg",
            "date": dates[1]
        },
        {
            "angle": "Curated 3-Item Listicle",
            "title": f"3 Small Space Must-Haves: {title} & More",
            "desc": f"3 smart upgrades that instantly double small space storage and aesthetic. Save this pin for home decor inspiration! Direct link in pin. #homemakeover #minimalspace #storageideas",
            "filename": "variation_3_listicle.jpg",
            "file_path": str(p3_path),
            "web_url": f"/output/winner_batches/horse_{pin_id}/variation_3_listicle.jpg",
            "full_image_url": f"{base_domain}/output/winner_batches/horse_{pin_id}/variation_3_listicle.jpg",
            "date": dates[2]
        }
    ]

    # Write Pinterest CSV bulk schema with full public URL for direct bulk importer
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
        for v in variations:
            writer.writerow([
                v["title"],
                v["full_image_url"],
                board,
                v["full_image_url"],
                v["desc"],
                destination_url,
                v["date"],
                "small space decor, apartment hacks, amazon home finds, viral pin"
            ])

    return {
        "status": "success",
        "pin_id": pin_id,
        "title": title,
        "board": board,
        "affiliate_link": destination_url,
        "csv_download_url": f"/output/winner_batches/horse_{pin_id}/pinterest_winning_batch_schedule.csv",
        "variations": variations
    }
