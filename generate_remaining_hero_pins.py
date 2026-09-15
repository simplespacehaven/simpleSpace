import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import autopilot
from config import BASE_DIR, OUTPUT_DIR, FONTS_DIR

out_dir = OUTPUT_DIR / "pins"
out_dir.mkdir(parents=True, exist_ok=True)

def make_hero_cover(bg_cdn_url, title_lines, badge_text, dest_file):
    # Fetch base image
    r = requests.get(bg_cdn_url, timeout=15)
    base_img = Image.open(BytesIO(r.content)).convert("RGBA")
    
    # 1000 x 1500 canvas
    canvas = Image.new("RGBA", (1000, 1500), (255, 255, 255, 255))
    
    # Resize base image to cover bottom/middle
    base_w, base_h = base_img.size
    scale = max(1000 / base_w, 1100 / base_h)
    new_w, new_h = int(base_w * scale), int(base_h * scale)
    base_resized = base_img.resize((new_w, new_h), Image.LANCZOS)
    
    # Crop to 1000x1100
    crop_x = (new_w - 1000) // 2
    crop_y = (new_h - 1100) // 2
    cropped = base_resized.crop((crop_x, crop_y, crop_x + 1000, crop_y + 1100))
    canvas.paste(cropped, (0, 400))
    
    # Elegant cream top card
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (1000, 430)], fill="#FAF8F5")
    
    # Decorative border frame
    draw.rectangle([(30, 30), (970, 400)], outline="#D4AF37", width=3)
    draw.rectangle([(40, 40), (960, 390)], outline="#E5D9C5", width=1)
    
    # Fonts
    font_title = ImageFont.truetype(str(FONTS_DIR / "PlayfairDisplay-Bold.ttf"), 68)
    font_badge = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Bold.ttf"), 28)
    font_sub = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Regular.ttf"), 22)
    
    # Draw Title Lines
    y_text = 65
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        w = bbox[2] - bbox[0]
        draw.text(((1000 - w) // 2, y_text), line, fill="#1A202C", font=font_title)
        y_text += 78
        
    # Badge Pill (Golden)
    badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = badge_bbox[2] - badge_bbox[0]
    pill_w = bw + 40
    pill_x = (1000 - pill_w) // 2
    pill_y = y_text + 15
    draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + 48)], radius=24, fill="#C59B27")
    draw.text((pill_x + 20, pill_y + 8), badge_text, fill="#FFFFFF", font=font_badge)
    
    # Brand Watermark at Bottom Bar
    draw.rectangle([(0, 1430), (1000, 1500)], fill="#1A202C")
    wm_text = "SIMPLE SPACE HAVEN • CURATED ROOM GUIDE"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=font_sub)
    ww = wm_bbox[2] - wm_bbox[0]
    draw.text(((1000 - ww) // 2, 1450), wm_text, fill="#E2E8F0", font=font_sub)
    
    # Save RGB
    canvas.convert("RGB").save(dest_file, "JPEG", quality=95)
    print(f"✓ Created: {dest_file}")
    cdn = autopilot.upload_pin_to_cdn(dest_file)
    print(f"  CDN: {cdn}")
    return cdn

# Bathroom
bath_cdn = make_hero_cover(
    "https://iili.io/ndE5ziv.jpg",
    ["13 NO-DRILL", "BATHROOM HACKS", "FOR SMALL SPACES"],
    "RENTER ESSENTIALS",
    out_dir / "hero_bathroom_blog_pin.jpg"
)

# Living Room
living_cdn = make_hero_cover(
    "https://iili.io/ndE5wbe.jpg",
    ["12 CLEVER SMALL", "LIVING ROOM HACKS", "YOU NEED TO TRY"],
    "SPACE SAVERS",
    out_dir / "hero_living_room_blog_pin.jpg"
)

print(f"BATHROOM_CDN={bath_cdn}")
print(f"LIVING_CDN={living_cdn}")
