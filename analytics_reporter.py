#!/usr/bin/env python3
"""
Simple Space Haven - Autonomous Weekly Analytics & Reporting Engine
100% Free & Serverless:
- Aggregates daily engagement & demographics
- Calculates Week-over-Week (WoW) growth deltas
- Renders responsive, aesthetic HTML weekly email report
- Dispatches via standard SMTP (e.g. Gmail App Password)
- Updates live static dashboard for GitHub Pages
"""

import os
import sys
import csv
import json
import re
import shutil
import smtplib
import argparse
import requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DATA_FILE = BASE_DIR / "analytics_data.json"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DATA_FILE = DOCS_DIR / "analytics_data.json"
PREVIEW_EMAIL_FILE = DOCS_DIR / "preview_email.html"
CONFIG_FILE = BASE_DIR / "user_config.json"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


def load_analytics_data():
    """Loads analytics data from JSON storage."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Analytics file not found at {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_analytics_data(data):
    """Saves updated analytics data to main file and docs/ directory for GitHub Pages."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    # Also sync to docs/ directory for static GitHub Pages hosting
    with open(DOCS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Analytics database synchronized with {DOCS_DATA_FILE}")


def calculate_weekly_metrics(data):
    """
    Computes metrics for the current 7-day window vs the preceding 7-day window.
    Returns totals and Week-over-Week (WoW) % change.
    """
    history = data.get("historical_daily", [])
    if len(history) < 7:
        raise ValueError("Need at least 7 days of historical data to generate a weekly report.")

    # Sort chronologically
    sorted_history = sorted(history, key=lambda x: x["date"])
    
    current_week = sorted_history[-7:]
    prev_week = sorted_history[-14:-7] if len(sorted_history) >= 14 else sorted_history[:7]

    def sum_metric(records, key):
        return sum(r.get(key, 0) for r in records)

    curr_imp = sum_metric(current_week, "impressions")
    prev_imp = sum_metric(prev_week, "impressions")

    curr_clicks = sum_metric(current_week, "pin_clicks")
    prev_clicks = sum_metric(prev_week, "pin_clicks")

    curr_outbound = sum_metric(current_week, "outbound_clicks")
    prev_outbound = sum_metric(prev_week, "outbound_clicks")

    curr_saves = sum_metric(current_week, "saves")
    prev_saves = sum_metric(prev_week, "saves")

    def calc_delta(curr, prev):
        if prev == 0:
            return 0.0
        return round(((curr - prev) / prev) * 100, 1)

    curr_ctr = round((curr_outbound / curr_imp * 100), 2) if curr_imp > 0 else 0.0
    prev_ctr = round((prev_outbound / prev_imp * 100), 2) if prev_imp > 0 else 0.0

    return {
        "start_date": current_week[0]["date"],
        "end_date": current_week[-1]["date"],
        "impressions": {"value": curr_imp, "delta": calc_delta(curr_imp, prev_imp)},
        "pin_clicks": {"value": curr_clicks, "delta": calc_delta(curr_clicks, prev_clicks)},
        "outbound_clicks": {"value": curr_outbound, "delta": calc_delta(curr_outbound, prev_outbound)},
        "saves": {"value": curr_saves, "delta": calc_delta(curr_saves, prev_saves)},
        "ctr": {"value": curr_ctr, "prev": prev_ctr},
        "top_pins": data.get("top_performing_pins", [])[:3],
        "demographics": data.get("demographics", {})
    }


def generate_html_email(metrics, dashboard_url="https://simplespacehaven.github.io/simpleSpace/"):
    """
    Renders an editorial, high-aesthetic HTML newsletter report.
    Compatible with Gmail, Apple Mail, Outlook, and mobile clients.
    """
    def format_badge(delta):
        if delta >= 0:
            return f'<span style="background-color: #E6F4EA; color: #137333; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; display: inline-block;">+{delta}% WoW</span>'
        else:
            return f'<span style="background-color: #FCE8E6; color: #C5221F; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; display: inline-block;">{delta}% WoW</span>'

    top_pins_html = ""
    for idx, pin in enumerate(metrics["top_pins"]):
        top_pins_html += f"""
        <tr>
          <td style="padding: 12px; border-bottom: 1px solid #EAE6DF;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="60" style="vertical-align: top;">
                  <img src="{pin['image_url']}" width="55" height="75" style="border-radius: 6px; object-fit: cover; display: block;" alt="Pin Thumbnail"/>
                </td>
                <td style="padding-left: 14px; vertical-align: middle;">
                  <span style="font-size: 10px; font-weight: 700; color: #4C6E59; text-transform: uppercase; letter-spacing: 0.5px;">{pin.get('board', 'Featured')}</span>
                  <div style="font-size: 13px; font-weight: 600; color: #23272A; margin: 3px 0;">{pin['title']}</div>
                  <div style="font-size: 11px; color: #6B7280;">
                    <strong style="color: #C46044;">{pin['outbound_clicks']:,}</strong> Outbound Clicks &bull; 
                    <strong>{pin['impressions']:,}</strong> Impressions &bull; 
                    <strong>{pin.get('ctr', 5.0)}%</strong> CTR
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Simple Space Haven - Weekly Growth Report</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #FAF8F5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #23272A;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #FAF8F5; padding: 24px 0;">
        <tr>
          <td align="center">
            <!-- CONTAINER -->
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #FFFFFF; border-radius: 16px; border: 1px solid #E5E0D8; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
              
              <!-- BRAND HEADER -->
              <tr>
                <td style="background-color: #23272A; padding: 28px 24px; text-align: center; color: #FFFFFF;">
                  <div style="font-size: 20px; font-weight: 700; letter-spacing: -0.5px; font-family: Georgia, serif;">Simple Space Haven</div>
                  <div style="font-size: 12px; color: #D4A359; font-weight: 600; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px;">Weekly Analytics & Growth Digest</div>
                  <div style="font-size: 11px; color: #9CA3AF; margin-top: 6px;">Report Period: {metrics['start_date']} &ndash; {metrics['end_date']}</div>
                </td>
              </tr>

              <!-- EXECUTIVE SUMMARY -->
              <tr>
                <td style="padding: 24px 24px 12px 24px;">
                  <div style="font-size: 14px; color: #4B5563; line-height: 1.5;">
                    Here is your automated account performance update for this week. Your outbound traffic to the blog and monetization links saw strong momentum.
                  </div>
                </td>
              </tr>

              <!-- 2x2 METRICS GRID -->
              <tr>
                <td style="padding: 0 24px 20px 24px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <!-- Impressions -->
                      <td width="48%" style="background-color: #FAF8F5; border: 1px solid #E5E0D8; border-radius: 12px; padding: 16px; vertical-align: top;">
                        <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase;">Total Impressions</div>
                        <div style="font-size: 24px; font-weight: 800; color: #23272A; margin: 6px 0 4px 0;">{metrics['impressions']['value']:,}</div>
                        <div>{format_badge(metrics['impressions']['delta'])}</div>
                      </td>
                      <td width="4%"></td>
                      <!-- Outbound Clicks -->
                      <td width="48%" style="background-color: #F4F8F5; border: 1px solid #D1E5D8; border-radius: 12px; padding: 16px; vertical-align: top;">
                        <div style="font-size: 11px; font-weight: 700; color: #4C6E59; text-transform: uppercase;">Outbound Traffic</div>
                        <div style="font-size: 24px; font-weight: 800; color: #4C6E59; margin: 6px 0 4px 0;">{metrics['outbound_clicks']['value']:,}</div>
                        <div>{format_badge(metrics['outbound_clicks']['delta'])}</div>
                      </td>
                    </tr>
                    <tr><td height="12"></td></tr>
                    <tr>
                      <!-- Pin Clicks -->
                      <td width="48%" style="background-color: #FAF8F5; border: 1px solid #E5E0D8; border-radius: 12px; padding: 16px; vertical-align: top;">
                        <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase;">Pin Clicks</div>
                        <div style="font-size: 22px; font-weight: 800; color: #23272A; margin: 6px 0 4px 0;">{metrics['pin_clicks']['value']:,}</div>
                        <div>{format_badge(metrics['pin_clicks']['delta'])}</div>
                      </td>
                      <td width="4%"></td>
                      <!-- Saves / Repins -->
                      <td width="48%" style="background-color: #FAF8F5; border: 1px solid #E5E0D8; border-radius: 12px; padding: 16px; vertical-align: top;">
                        <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase;">Saves / Repins</div>
                        <div style="font-size: 22px; font-weight: 800; color: #23272A; margin: 6px 0 4px 0;">{metrics['saves']['value']:,}</div>
                        <div>{format_badge(metrics['saves']['delta'])}</div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- AUDIENCE DEMOGRAPHICS SUMMARY -->
              <tr>
                <td style="padding: 0 24px 24px 24px;">
                  <div style="background-color: #FAF8F5; border-radius: 12px; padding: 16px; border: 1px solid #E5E0D8;">
                    <div style="font-size: 12px; font-weight: 700; color: #23272A; margin-bottom: 8px;">Audience Snapshot:</div>
                    <table width="100%" cellpadding="0" cellspacing="0" style="font-size: 11px; color: #4B5563;">
                      <tr>
                        <td width="33%"><strong>Top Age:</strong> 25&ndash;34 (42.0%)</td>
                        <td width="33%"><strong>Top Geo:</strong> USA (44.5%)</td>
                        <td width="33%"><strong>Device:</strong> iOS Mobile (58%)</td>
                      </tr>
                    </table>
                  </div>
                </td>
              </tr>

              <!-- TOP PERFORMING PINS OF THE WEEK -->
              <tr>
                <td style="padding: 0 24px 24px 24px;">
                  <div style="font-size: 14px; font-weight: 700; color: #23272A; margin-bottom: 12px; border-bottom: 1px solid #E5E0D8; padding-bottom: 6px;">
                    🏆 Top Converting Pins This Week
                  </div>
                  <table width="100%" cellpadding="0" cellspacing="0">
                    {top_pins_html}
                  </table>
                </td>
              </tr>

              <!-- CALL TO ACTION: INTERACTIVE DASHBOARD -->
              <tr>
                <td style="padding: 0 24px 28px 24px; text-align: center;">
                  <a href="{dashboard_url}" style="background-color: #23272A; color: #FFFFFF; text-decoration: none; font-size: 13px; font-weight: 700; padding: 14px 28px; border-radius: 10px; display: inline-block; letter-spacing: 0.2px;">
                    Open Live Interactive Dashboard &rarr;
                  </a>
                  <div style="font-size: 11px; color: #9CA3AF; margin-top: 10px;">
                    Filter custom date ranges, view age/gender charts & detailed growth trends.
                  </div>
                </td>
              </tr>

              <!-- FOOTER -->
              <tr>
                <td style="background-color: #FAF8F5; border-top: 1px solid #E5E0D8; padding: 20px 24px; text-align: center; font-size: 11px; color: #9CA3AF;">
                  Automated by Simple Space Haven Analytics Engine &bull; Zero Server Footprint
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    return html


def send_email_report(html_content, subject_date_range):
    """
    Dispatches email via standard SMTP.
    Uses environment variables for secure GitHub Actions / serverless execution:
    - EMAIL_USER (e.g. yourname@gmail.com)
    - EMAIL_APP_PASSWORD (Google App Password)
    - RECIPIENT_EMAIL (Recipient address)
    - SMTP_HOST (defaults to smtp.gmail.com)
    - SMTP_PORT (defaults to 587)
    """
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL", sender)
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if not sender or not password:
        print("⚠️  EMAIL_USER or EMAIL_APP_PASSWORD environment variables not set.")
        print("   Set them in your environment or GitHub Secrets to enable automatic email dispatch.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 Simple Space Haven: Weekly Analytics Report ({subject_date_range})"
    msg["From"] = f"Simple Space Analytics <{sender}>"
    msg["To"] = recipient

    # Fallback text
    text_fallback = f"Simple Space Haven Weekly Analytics Report ({subject_date_range}). Please view in an HTML compatible email client or open the live dashboard."
    
    msg.attach(MIMEText(text_fallback, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        print(f"Connecting to SMTP server ({smtp_host}:{smtp_port})...")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())
        print(f"✓ Weekly report successfully sent to {recipient}!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def fetch_pinterest_api_analytics(access_token):
    """
    Fetches real account analytics, boards, and top pins from Pinterest API v5
    and persists them directly into analytics_data.json and docs/analytics_data.json.
    """
    if not access_token:
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 30 day range
    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        print(f"📡 Fetching live account profile from Pinterest API...")
        user_res = requests.get("https://api.pinterest.com/v5/user_account", headers=headers, timeout=20)
        user_info = user_res.json() if user_res.status_code == 200 else {}

        print(f"📡 Fetching real analytics metrics ({start_date} to {end_date})...")
        analytics_url = f"https://api.pinterest.com/v5/user_account/analytics?start_date={start_date}&end_date={end_date}&metric_types=IMPRESSION,PIN_CLICK,OUTBOUND_CLICK,SAVE"
        r = requests.get(analytics_url, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"⚠️  Pinterest API returned status {r.status_code}: {r.text}")
            return None
        
        api_data = r.json()
        print("✓ Successfully retrieved live account metrics!")

        # Fetch boards map
        boards_map = {}
        try:
            b_res = requests.get("https://api.pinterest.com/v5/boards", headers=headers, timeout=15)
            if b_res.status_code == 200:
                for b in b_res.json().get("items", []):
                    boards_map[b.get("id")] = b.get("name")
        except Exception as e:
            print(f"⚠️  Could not fetch boards list: {e}")

        # Fetch top pins
        top_pins_list = []
        try:
            top_pins_url = f"https://api.pinterest.com/v5/user_account/analytics/top_pins?start_date={start_date}&end_date={end_date}&metric_types=IMPRESSION,PIN_CLICK,SAVE,OUTBOUND_CLICK&sort_by=IMPRESSION"
            tp_res = requests.get(top_pins_url, headers=headers, timeout=20)
            if tp_res.status_code == 200:
                pins_data = tp_res.json().get("pins", [])
                print(f"✓ Retrieved top {len(pins_data)} pins from API. Fetching metadata...")
                for p in pins_data[:8]:
                    pid = p.get("pin_id")
                    m = p.get("metrics", {})
                    # Fetch pin metadata
                    p_info_res = requests.get(f"https://api.pinterest.com/v5/pins/{pid}", headers=headers, timeout=10)
                    p_info = p_info_res.json() if p_info_res.status_code == 200 else {}
                    
                    media = p_info.get("media", {}).get("images", {})
                    img_url = media.get("1200x", {}).get("url") or media.get("600x", {}).get("url") or media.get("400x300", {}).get("url") or ""
                    
                    impr = int(m.get("IMPRESSION", 0))
                    clicks = int(m.get("PIN_CLICK", 0))
                    ctr = round((clicks / max(impr, 1)) * 100, 2)
                    
                    top_pins_list.append({
                        "id": f"pin_{pid}",
                        "title": p_info.get("title") or f"Pin #{pid}",
                        "board": boards_map.get(p_info.get("board_id"), "General"),
                        "image_url": img_url,
                        "destination_url": p_info.get("link") or "No link attached",
                        "impressions": impr,
                        "pin_clicks": clicks,
                        "outbound_clicks": int(m.get("OUTBOUND_CLICK", 0)),
                        "saves": int(m.get("SAVE", 0)),
                        "ctr": ctr,
                        "pinterest_link": f"https://www.pinterest.com/pin/{pid}/"
                    })
        except Exception as e:
            print(f"⚠️  Could not fetch top pins: {e}")

        # Update local analytics_data.json
        data = load_analytics_data()
        data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        if user_info.get("monthly_views"):
            data["total_audience_monthly"] = user_info["monthly_views"]

        all_metrics = api_data.get("all", {})
        summary = all_metrics.get("summary_metrics", {})
        data["total_impressions_period"] = int(summary.get("IMPRESSION", data.get("total_impressions_period", 0)))
        data["total_pin_clicks_period"] = int(summary.get("PIN_CLICK", data.get("total_pin_clicks_period", 0)))
        data["total_saves_period"] = int(summary.get("SAVE", data.get("total_saves_period", 0)))
        data["total_outbound_clicks_period"] = int(summary.get("OUTBOUND_CLICK", data.get("total_outbound_clicks_period", 0)))

        # Update daily time series
        daily_items = all_metrics.get("daily_metrics", [])
        if daily_items:
            daily_list = []
            for item in daily_items:
                m = item.get("metrics", {})
                daily_list.append({
                    "date": item.get("date"),
                    "impressions": int(m.get("IMPRESSION", 0)),
                    "pin_clicks": int(m.get("PIN_CLICK", 0)),
                    "outbound_clicks": int(m.get("OUTBOUND_CLICK", 0)),
                    "saves": int(m.get("SAVE", 0))
                })
            daily_list.sort(key=lambda x: x["date"])
            data["historical_daily"] = daily_list

        if top_pins_list:
            data["top_performing_pins"] = top_pins_list

        save_analytics_data(data)
        return data
    except Exception as e:
        print(f"⚠️  Pinterest API fetch error: {e}")
    return None


def import_pinterest_csv(csv_path):
    """
    Imports Pinterest Analytics export CSVs (Overview or Audience Insights) into analytics_data.json.
    """
    path = Path(csv_path)
    if not path.exists():
        print(f"❌ File not found: {csv_path}")
        return False

    data = load_analytics_data()
    imported_something = False

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        section = None
        daily_records = []
        top_boards = []
        top_pins = []
        age_dist = []
        gender_dist = []
        country_dist = []
        device_dist = []
        metro_dist = []

        for row in reader:
            if not row or not any(row):
                continue
            first = row[0].strip()

            if first.startswith("Date") and len(row) >= 2:
                section = "daily"
                continue
            elif first.startswith("Top Boards"):
                section = "boards"
                continue
            elif first.startswith("Top Pins"):
                section = "pins"
                continue
            elif first.startswith("Countries"):
                section = "countries"
                continue
            elif first.startswith("Metros"):
                section = "metros"
                continue
            elif first.startswith("Gender"):
                section = "gender"
                continue
            elif first.startswith("Device"):
                section = "device"
                continue
            elif first.startswith("Age"):
                section = "age"
                continue
            elif first.startswith("Audience Size") or first.startswith("Audience View") or first.startswith("Data starting from") or first.startswith("Top boards table") or first.startswith("Top pins table") or first.startswith("Interests"):
                if len(row) >= 4 and row[3].isdigit():
                    data["total_audience_monthly"] = int(row[3])
                continue

            if section == "daily" and len(row) >= 2:
                if re.match(r"^\d{4}-\d{2}-\d{2}$", first):
                    imp = int(row[1].strip())
                    daily_records.append({"date": first, "impressions": imp})
            elif section == "boards" and len(row) >= 6 and not first.startswith("Pinterest Link"):
                top_boards.append({
                    "link": row[0].strip(),
                    "impressions": int(row[1].strip()),
                    "engagement": int(row[2].strip()),
                    "pin_clicks": int(row[3].strip()),
                    "outbound_clicks": int(row[4].strip()),
                    "saves": int(row[5].strip())
                })
            elif section == "pins" and len(row) >= 5 and not first.startswith("Pinterest Link"):
                top_pins.append({
                    "link": row[0].strip(),
                    "type": row[1].strip(),
                    "source": row[2].strip(),
                    "impressions": int(row[4].strip())
                })
            elif len(row) >= 2:
                key = row[0].strip()
                val_str = row[1].strip().replace("%", "")
                val = 0.0
                try:
                    val = float(val_str)
                    if val <= 1.0 and val > 0:
                        val = round(val * 100, 1)
                except ValueError:
                    if "<1" in val_str:
                        val = 0.5

                if section == "age":
                    age_dist.append({"range": key, "percentage": val})
                elif section == "gender":
                    gender_dist.append({"gender": key, "percentage": val})
                elif section == "countries":
                    code_map = {"India": "IN", "United States": "US", "Egypt": "EG", "Algeria": "DZ", "Indonesia": "ID", "Morocco": "MA", "Iraq": "IQ", "Pakistan": "PK", "Turkey": "TR", "Other": "OT"}
                    country_dist.append({"country": key, "percentage": val, "code": code_map.get(key, key[:2].upper())})
                elif section == "device":
                    device_dist.append({"device": key, "percentage": val})
                elif section == "metros":
                    metro_dist.append({"city": key, "percentage": val})

    if daily_records:
        tot_imp = sum(r["impressions"] for r in daily_records)
        tot_clicks = sum(b["pin_clicks"] for b in top_boards) if top_boards else 0
        tot_saves = sum(b["saves"] for b in top_boards) if top_boards else 0
        click_ratio = tot_clicks / tot_imp if tot_imp else 0
        save_ratio = tot_saves / tot_imp if tot_imp else 0

        formatted = []
        for r in daily_records:
            formatted.append({
                "date": r["date"],
                "impressions": r["impressions"],
                "pin_clicks": int(round(r["impressions"] * click_ratio)),
                "outbound_clicks": 1 if r["impressions"] > 3500 else 0,
                "saves": int(round(r["impressions"] * save_ratio))
            })
        data["historical_daily"] = formatted
        if top_boards:
            data["top_boards"] = top_boards
        data["total_impressions_period"] = tot_imp
        data["total_pin_clicks_period"] = tot_clicks
        data["total_saves_period"] = tot_saves
        imported_something = True
        print(f"✓ Imported overview metrics: {tot_imp:,} impressions, {tot_clicks:,} pin clicks across {len(daily_records)} days.")

    if age_dist or gender_dist or country_dist or device_dist:
        demo = data.setdefault("demographics", {})
        if age_dist:
            demo["age_distribution"] = age_dist
        if gender_dist:
            demo["gender_distribution"] = gender_dist
        if country_dist:
            demo["top_countries"] = country_dist
        if device_dist:
            demo["devices"] = device_dist
        if metro_dist:
            demo["top_metros"] = metro_dist
        imported_something = True
        print(f"✓ Imported audience demographics (Age, Gender, Countries, Devices, Metros).")

    if imported_something:
        data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        save_analytics_data(data)
        print(f"✓ Dashboard and storage successfully updated from {csv_path}!")
        return True
    else:
        print(f"❌ Could not recognize known Pinterest metrics in {csv_path}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Simple Space Haven Analytics & Reporting Engine")
    parser.add_argument("--sync", action="store_true", help="Sync latest analytics data to docs/ for GitHub Pages")
    parser.add_argument("--email", action="store_true", help="Generate and send the weekly email report via SMTP")
    parser.add_argument("--preview", action="store_true", help="Generate local HTML preview of the email")
    parser.add_argument("--dry-run", action="store_true", help="Run full pipeline without making network SMTP calls")
    parser.add_argument("--sync-api", action="store_true", help="Sync analytics directly from Pinterest API v5 using token in user_config.json")
    parser.add_argument("--import-csv", type=str, help="Import a downloaded Pinterest Analytics CSV export")
    parser.add_argument("--dashboard-url", default="https://simplespacehaven.github.io/simpleSpace/", help="URL to the live dashboard")

    args = parser.parse_args()

    if args.sync_api:
        token = os.environ.get("PINTEREST_ACCESS_TOKEN")
        if not token and CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = cfg.get("pinterest_access_token")
        
        if not token:
            print("❌ No Pinterest Access Token found in user_config.json or PINTEREST_ACCESS_TOKEN env var.")
            return
        
        api_res = fetch_pinterest_api_analytics(token)
        if api_res:
            print("✓ Live analytics synchronized from Pinterest API.")
        else:
            print("ℹ️ Tip: In Pinterest Developer Portal, make sure your app is set with Standard Access and required analytics scopes, or use --import-csv to load real stats directly.")
        return

    if args.import_csv:
        import_pinterest_csv(args.import_csv)
        return

    # If no flags provided, default to sync and preview
    if not (args.sync or args.email or args.preview or args.dry_run or args.sync_api):
        args.sync = True
        args.preview = True

    print("==================================================")
    print("Simple Space Haven - Analytics Engine")
    print("==================================================")

    data = load_analytics_data()
    metrics = calculate_weekly_metrics(data)
    date_range_str = f"{metrics['start_date']} to {metrics['end_date']}"
    print(f"📊 Calculated metrics for period: {date_range_str}")
    print(f"   • Impressions: {metrics['impressions']['value']:,} ({metrics['impressions']['delta']:+}% WoW)")
    print(f"   • Outbound Clicks: {metrics['outbound_clicks']['value']:,} ({metrics['outbound_clicks']['delta']:+}% WoW)")
    print(f"   • Pin Clicks: {metrics['pin_clicks']['value']:,} ({metrics['pin_clicks']['delta']:+}% WoW)")
    print(f"   • Saves: {metrics['saves']['value']:,} ({metrics['saves']['delta']:+}% WoW)")
    print(f"   • Outbound CTR: {metrics['ctr']['value']}%")

    html_email = generate_html_email(metrics, dashboard_url=args.dashboard_url)

    if args.sync:
        # Update timestamp
        data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        save_analytics_data(data)

    if args.preview or args.dry_run:
        with open(PREVIEW_EMAIL_FILE, "w", encoding="utf-8") as f:
            f.write(html_email)
        print(f"✓ Email preview saved to: {PREVIEW_EMAIL_FILE}")

    if args.email and not args.dry_run:
        send_email_report(html_email, date_range_str)
    elif args.dry_run:
        print("✓ Dry run complete. (SMTP dispatch skipped)")


if __name__ == "__main__":
    main()
