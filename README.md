# 📌 PinAutopilot — Universal Pinterest Affiliate Engine

An autonomous, machine-independent Pinterest affiliate marketing pipeline. Designed to operate like a modern editorial media brand (rather than a spam bot) with **0 MB local disk footprint**.

## 🚀 Key Features

* **Universal & Cross-Platform:** Bundled open-source fonts (*Playfair Display* & *Montserrat*). Runs natively on **Windows, macOS, and Linux** with zero OS-specific dependencies.
* **Niche-Agnostic & Pluggable:** Supports any affiliate niche via modular JSON configs (`niches/home_organization.json`, `niches/tech_gadgets.json`, etc.).
* **Multi-Style Dynamic Pin Generator:** Rotates between 3 viral layout engines:
  1. *Editorial Minimalist* (Playfair luxury serif, frosted-glass card, magazine look)
  2. *Renter Hack / Feature Callout* (High-contrast curiosity badge, hero shadow frame)
  3. *Curated Checklist* (Multi-bullet social proof, high save-rate listicle layout)
* **Zero Local Disk Footprint:** Automatically uploads pins to a permanent cloud CDN and wipes local scratch images so your hard drive stays clean.
* **Permanent Master Cloud Ledger:** Logs every ASIN, product title, board, price, rating, affiliate link, and clickable CDN URL to `output/master_pin_records.csv`.
* **Exact Pinterest Bulk CSV Schema:** Generates ready-to-upload CSVs with 10 official Pinterest taxonomy keywords and staggered publishing dates.

---

## ⚡ 60-Second Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Setup Wizard (First-Time Only)
```bash
python main.py --wizard
```
The wizard will guide you through:
- Brand Name & Pinterest Handle
- Amazon Associates Tag & Marketplace (`amazon.in`, `amazon.com`, `amazon.co.uk`)
- Content Niche Selection
- Price ceiling & minimum rating

### 3. Generate Pins
```bash
# Generate 10 fresh pins
python main.py --count 10

# Generate 5 pins for a specific niche
python main.py --count 5 --niche tech_gadgets
```

### 4. Upload to Pinterest
1. Go to [Pinterest Bulk Pin Creator](https://in.pinterest.com/settings/bulk-create-pins/)
2. Drag and drop `output/pinterest_bulk_schedule.csv`
3. Pinterest automatically schedules your pins!

---

## 🛠️ Handy Commands

* **Check Your Master Ledger:**
  ```bash
  python main.py --ledger
  ```
* **Purge Local Images (Free 100% Disk Space):**
  ```bash
  python main.py --clean
  ```
* **Keep Local Images (Optional Debugging):**
  ```bash
  python main.py --count 5 --keep-local
  ```

---

## 📊 Autonomous Analytics & Weekly Email Dashboard

A 100% free, cloud-native reporting system running on GitHub Actions & GitHub Pages:

* **Interactive Online Dashboard (`docs/index.html`)**:
  * Date range selector (Last 7d, 14d, 30d, All history, Custom range).
  * Impressions, Pin Clicks, Outbound Clicks to Blog/Amazon, Saves & Outbound CTR %.
  * Audience demographics: Age distribution, Top Countries, Gender & Device splits.
  * Top converting pins leaderboard.
* **Weekly Email Digest (`analytics_reporter.py`)**:
  * Automatically sent every Monday morning via standard SMTP (Gmail App Password).
  * Summarizes Week-over-Week (+% / -%) deltas and links directly to the live dashboard.

### Local Testing & Preview:
```bash
# Preview the weekly email in your browser & sync metrics
python analytics_reporter.py --preview

# Test dry-run of full reporting pipeline
python analytics_reporter.py --dry-run
```

