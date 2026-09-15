"""
Simple Space Haven — Quota-Free Local Motion Pin Generator
==========================================================
Renders viral 9:16 vertical motion pins (1080x1920 MP4) locally on your machine
using FFmpeg and Pillow. 100% quota-free, zero API costs, runs completely offline.
"""

import math
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from config import FONTS_DIR, OUTPUT_DIR

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
out_dir = OUTPUT_DIR / "videos"
out_dir.mkdir(parents=True, exist_ok=True)

def generate_motion_pin(
    src_img_path,
    title_lines,
    badge_text,
    sub_text,
    output_filename,
    duration=5,
    fps=30
):
    W, H = 1080, 1920
    total_frames = fps * duration
    out_path = out_dir / output_filename
    
    bg_raw = Image.open(src_img_path).convert("RGB")
    bw, bh = bg_raw.size
    base_scale = max(W / bw, H / bh) * 1.15
    base_w, base_h = int(bw * base_scale), int(bh * base_scale)
    bg_large = bg_raw.resize((base_w, base_h), Image.LANCZOS)
    
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-an",
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "20",
        str(out_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    font_title = ImageFont.truetype(str(FONTS_DIR / "PlayfairDisplay-Bold.ttf"), 68)
    font_badge = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Bold.ttf"), 28)
    font_sub = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Regular.ttf"), 24)
    font_cta = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Bold.ttf"), 26)
    font_brand = ImageFont.truetype(str(FONTS_DIR / "Montserrat-Bold.ttf"), 19)
    
    print(f"🎬 Rendering {output_filename} ({total_frames} frames)...")
    
    for i in range(total_frames):
        progress = i / float(total_frames)
        ease = 0.5 * (1 - math.cos(progress * math.pi))
        
        # Ken Burns smooth zoom & gentle pan
        current_zoom = 1.0 + (0.08 * ease)
        curr_w = int(W * current_zoom)
        curr_h = int(H * current_zoom)
        crop_x = int((base_w - curr_w) / 2)
        crop_y = int((base_h - curr_h) / 2 + (ease * 36))
        frame_bg = bg_large.crop((crop_x, crop_y, crop_x + curr_w, crop_y + curr_h)).resize((W, H), Image.BILINEAR).convert("RGBA")
        
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Top Card slide-in (first 0.7 seconds)
        slide_prog = min(1.0, i / (fps * 0.7))
        card_ease = 1 - math.pow(1 - slide_prog, 3)
        target_card_y = 120
        current_card_y = int(-360 + (target_card_y + 360) * card_ease)
        
        card_w, card_h = 920, 480
        card_x = (W - card_w) // 2
        
        if slide_prog > 0:
            shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(shadow)
            s_draw.rounded_rectangle(
                [(card_x - 10, current_card_y + 12), (card_x + card_w + 10, current_card_y + card_h + 20)],
                radius=28, fill=(0, 0, 0, int(120 * slide_prog))
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(16))
            frame_bg = Image.alpha_composite(frame_bg, shadow)
            
            card_box = [(card_x, current_card_y), (card_x + card_w, current_card_y + card_h)]
            draw.rounded_rectangle(card_box, radius=24, fill=(255, 253, 249, 248))
            draw.rounded_rectangle(card_box, radius=24, outline=(197, 155, 39, 255), width=3)
            inner_box = [(card_x + 12, current_card_y + 12), (card_x + card_w - 12, current_card_y + card_h - 12)]
            draw.rounded_rectangle(inner_box, radius=16, outline=(228, 220, 205, 255), width=1)
            
            # Badge Pill with gentle pulse
            pulse = math.sin(progress * math.pi * 4) * 0.05
            b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
            bw_text = b_bbox[2] - b_bbox[0]
            pill_w = int((bw_text + 44) * (1.0 + pulse))
            pill_h = 44
            pill_x = (W - pill_w) // 2
            pill_y = current_card_y + 36
            draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=22, fill=(197, 155, 39, 255))
            tb = draw.textbbox((0, 0), badge_text, font=font_badge)
            draw.text(((W - (tb[2]-tb[0])) // 2, pill_y + 7), badge_text, fill=(255, 255, 255, 255), font=font_badge)
            
            # Title typography
            y_text = pill_y + pill_h + 24
            for line in title_lines:
                t_bbox = draw.textbbox((0, 0), line, font=font_title)
                tw = t_bbox[2] - t_bbox[0]
                draw.text(((W - tw) // 2, y_text), line, fill=(26, 32, 44, 255), font=font_title)
                y_text += 76
                
            # Subtitle
            s_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
            sw = s_bbox[2] - s_bbox[0]
            draw.text(((W - sw) // 2, current_card_y + card_h - 52), sub_text, fill=(100, 116, 139, 255), font=font_sub)
        
        # Animated Bouncing Bottom CTA
        bounce_y = int(math.sin(progress * math.pi * 6) * 8)
        cta_y = 1720 + bounce_y
        cta_w, cta_h = 680, 72
        cta_x = (W - cta_w) // 2
        draw.rounded_rectangle([(cta_x, cta_y), (cta_x + cta_w, cta_y + cta_h)], radius=36, fill=(26, 32, 44, 240))
        draw.rounded_rectangle([(cta_x, cta_y), (cta_x + cta_w, cta_y + cta_h)], radius=36, outline=(197, 155, 39, 255), width=2)
        cta_str = "👆 TAP TO VIEW LIST & DEALS →"
        cb = draw.textbbox((0, 0), cta_str, font=font_cta)
        cw = cb[2] - cb[0]
        draw.text(((W - cw) // 2, cta_y + 18), cta_str, fill=(255, 255, 255, 255), font=font_cta)
        
        # Header bar
        draw.rectangle([(0, 0), (W, 55)], fill=(26, 32, 44, 230))
        brand_text = "SIMPLE SPACE HAVEN • HOME & LIVING"
        bb = draw.textbbox((0, 0), brand_text, font=font_brand)
        draw.text(((W - (bb[2]-bb[0])) // 2, 16), brand_text, fill=(241, 245, 249, 255), font=font_brand)
        
        frame = Image.alpha_composite(frame_bg, overlay).convert("RGB")
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"✓ Video ready: {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    return out_path

if __name__ == "__main__":
    generate_motion_pin(
        src_img_path="/home/nithin/.gemini/antigravity-cli/brain/8028d642-ba34-4773-befe-c9a605d26c35/kitchen_hacks_pin_1789064326587.jpg",
        title_lines=["14 GENIUS KITCHEN", "SPACE SAVERS", "FOR SMALL COUNTERS"],
        badge_text="⚡ 14 VIRAL AMAZON FINDS",
        sub_text="RENTER-FRIENDLY • NO DRILL • UNDER ₹999",
        output_filename="motion_pin_kitchen_demo.mp4"
    )
