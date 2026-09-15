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
import json
import shutil
import smtplib
import argparse
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DATA_FILE = BASE_DIR / "analytics_data.json"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DATA_FILE = DOCS_DIR / "analytics_data.json"
PREVIEW_EMAIL_FILE = DOCS_DIR / "preview_email.html"

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


def generate_html_email(metrics, dashboard_url="https://simplespacehaven.github.io/analytics/"):
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


def main():
    parser = argparse.ArgumentParser(description="Simple Space Haven Analytics & Reporting Engine")
    parser.add_argument("--sync", action="store_true", help="Sync latest analytics data to docs/ for GitHub Pages")
    parser.add_argument("--email", action="store_true", help="Generate and send the weekly email report via SMTP")
    parser.add_argument("--preview", action="store_true", help="Generate local HTML preview of the email")
    parser.add_argument("--dry-run", action="store_true", help="Run full pipeline without making network SMTP calls")
    parser.add_argument("--dashboard-url", default="https://simplespacehaven.github.io/analytics/", help="URL to the live dashboard")

    args = parser.parse_args()

    # If no flags provided, default to sync and preview
    if not (args.sync or args.email or args.preview or args.dry_run):
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
