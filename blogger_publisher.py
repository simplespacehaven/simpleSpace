#!/usr/bin/env python3
"""
Simple Space Haven - Autonomous Blogger Email Publisher
Publishes high-converting HTML articles directly to Blogger via secure Gmail SMTP.
"""
import os
import sys
import json
import smtplib
import time
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
BLOG_POSTS_DIR = OUTPUT_DIR / "blog_posts"
CONFIG_FILE = BASE_DIR / "blogger_credentials.json"
HISTORY_FILE = BASE_DIR / "blogger_published_history.json"

DEFAULT_CREDS = {
    "sender_email": "simplespacehaven@gmail.com",
    "app_password": "lehvrbsoymfsgumr",
    "blogger_email": "simplespacehaven.space9872@blogger.com"
}

def load_credentials():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CREDS, f, indent=2)
    return DEFAULT_CREDS

def load_published_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_published_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def send_blog_post_to_blogger(title, html_content, creds=None):
    creds = creds or load_credentials()
    sender = creds["sender_email"]
    pwd = creds["app_password"].replace(" ", "")
    blogger_to = creds["blogger_email"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = sender
    msg["To"] = blogger_to

    # Attach rich HTML part
    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)

    print(f"📧 Sending '{title}' to Blogger ({blogger_to})...")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, pwd)
    server.sendmail(sender, blogger_to, msg.as_string())
    server.quit()
    print("✓ Successfully sent! Blogger is publishing the post immediately.")
    return True

def publish_file(html_path, creds=None):
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"❌ File not found: {html_path}")
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Extract title from HTML comment or H1
    import re
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if title_match:
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
    else:
        title = html_path.stem.replace("-", " ").title()

    send_blog_post_to_blogger(title, html, creds)
    
    # Record history
    history = load_published_history()
    history[html_path.name] = {
        "title": title,
        "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file": str(html_path)
    }
    save_published_history(history)
    return True

def publish_all_pending():
    history = load_published_history()
    files = list(BLOG_POSTS_DIR.glob("*.html"))
    files = [f for f in files if f.name != "index.html"]
    
    # Check kitchen already published manually
    if "genius-amazon-kitchen-hacks-double-space.html" not in history:
        history["genius-amazon-kitchen-hacks-double-space.html"] = {
            "title": "14 Genius Amazon Kitchen Hacks That Instantly Double Countertop Space",
            "published_at": "Manual via UI",
            "file": "genius-amazon-kitchen-hacks-double-space.html"
        }
        save_published_history(history)

    pending = [f for f in files if f.name not in history]
    if not pending:
        print("All blog posts are already published!")
        return

    print(f"🚀 Found {len(pending)} pending blog posts to publish automatically:\n")
    creds = load_credentials()
    for f in pending:
        publish_file(f, creds)
        time.sleep(3)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        publish_all_pending()
    elif len(sys.argv) > 2 and sys.argv[1] == "--file":
        publish_file(sys.argv[2])
    else:
        # Publish all pending by default
        publish_all_pending()
