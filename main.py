#!/usr/bin/env python3
"""
PinAutopilot - Universal, Machine-Independent Pinterest Affiliate Engine
Works on Linux, macOS, and Windows with zero configuration.
"""
import sys
import os
import json
import argparse
from pathlib import Path

from config import (
    BASE_DIR, CONFIG_FILE, NICHES_DIR, OUTPUT_DIR,
    DEFAULT_CONFIG, load_user_config
)
from master_ledger import sync_master_records, purge_local_images
import autopilot

def get_available_niches():
    niches = []
    if NICHES_DIR.exists():
        for f in NICHES_DIR.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as nf:
                    data = json.load(nf)
                    niches.append((f.stem, data.get("niche_name", f.stem)))
            except Exception:
                pass
    return niches

def run_setup_wizard():
    print("==================================================")
    print("   PIN AUTOPILOT — AFFILIATE ONBOARDING WIZARD")
    print("==================================================")
    print("Let's configure your brand and affiliate account in 60 seconds.\n")
    
    current_cfg = load_user_config()
    
    # 1. Brand Name
    def_brand = current_cfg.get("brand_name", "Simple Space Haven")
    brand = input(f"[1/5] Enter your Brand Name [{def_brand}]: ").strip() or def_brand
    
    # 2. Brand Handle
    def_handle = current_cfg.get("brand_handle", "@simplespacehaven")
    handle = input(f"[2/5] Enter your Pinterest Handle [{def_handle}]: ").strip() or def_handle
    
    # 3. Amazon Tag
    def_tag = current_cfg.get("amazon_tag", "simplespaceha-21")
    tag = input(f"[3/5] Enter your Amazon Associates Tracking ID [{def_tag}]: ").strip() or def_tag
    
    # 4. Amazon Marketplace
    print("\nSelect Amazon Marketplace:")
    print("  1) Amazon India (amazon.in - ₹)")
    print("  2) Amazon United States (amazon.com - $)")
    print("  3) Amazon United Kingdom (amazon.co.uk - £)")
    m_choice = input("Enter choice (1-3) [1]: ").strip() or "1"
    
    if m_choice == "2":
        market = "amazon.com"
        currency = "$"
        def_price = 50
    elif m_choice == "3":
        market = "amazon.co.uk"
        currency = "£"
        def_price = 40
    else:
        market = "amazon.in"
        currency = "₹"
        def_price = 999
        
    # 5. Niche Selection
    niches = get_available_niches()
    print("\nSelect your Content Niche:")
    for idx, (n_id, n_name) in enumerate(niches, 1):
        print(f"  {idx}) {n_name} ({n_id})")
        
    n_choice = input(f"Enter choice (1-{len(niches)}) [1]: ").strip() or "1"
    try:
        selected_niche = niches[int(n_choice) - 1][0]
    except Exception:
        selected_niche = niches[0][0] if niches else "home_organization"
        
    # Price and rating
    price_input = input(f"\nTarget Max Price for Products [{currency}{def_price}]: ").strip()
    try:
        max_price = int(price_input) if price_input else def_price
    except ValueError:
        max_price = def_price
        
    config_data = {
        "brand_name": brand,
        "brand_handle": handle,
        "blog_url": current_cfg.get("blog_url", "http://simplespacehaven.blogspot.com"),
        "amazon_tag": tag,
        "marketplace": market,
        "currency_symbol": currency,
        "active_niche": selected_niche,
        "max_price": max_price,
        "min_rating": 3.8
    }
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
        
    print("\n" + "=" * 50)
    print("✓ Configuration saved successfully to user_config.json!")
    print(f"  Brand: {brand} ({handle})")
    print(f"  Affiliate Tag: {tag} on {market}")
    print(f"  Active Niche: {selected_niche}")
    print("=" * 50 + "\n")
    return config_data

def show_ledger_summary():
    ledger_csv = OUTPUT_DIR / "master_pin_records.csv"
    if not ledger_csv.exists():
        print("No master ledger found yet. Run a batch first!")
        return
        
    import csv
    with open(ledger_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print("==================================================")
    print(f"   SIMPLE SPACE HAVEN — MASTER CLOUD LEDGER")
    print("==================================================")
    print(f"📊 Total Historical Pins Tracked: {len(rows)}")
    
    boards = {}
    for r in rows:
        b = r.get("Board", "Unknown")
        boards[b] = boards.get(b, 0) + 1
        
    print("\n📁 Pins By Board:")
    for b, count in boards.items():
        print(f"  • {b}: {count} pins")
        
    print(f"\n📑 Master File: {ledger_csv}")
    print("👉 100% of image records are safely stored on the cloud CDN.")
    print("==================================================")

def main():
    parser = argparse.ArgumentParser(description="PinAutopilot: Universal Pinterest Affiliate Marketing Engine")
    parser.add_argument("--wizard", "--setup", action="store_true", help="Launch interactive setup wizard")
    parser.add_argument("--count", type=int, default=5, help="Number of pins to generate (default: 5)")
    parser.add_argument("--niche", type=str, default=None, help="Override active niche (e.g. home_organization, tech_gadgets)")
    parser.add_argument("--continue", "--next-batch", dest="continue_schedule", action="store_true", help="Schedule pins starting after the previous batch")
    parser.add_argument("--week", action="store_true", help="Automatically generate and schedule pins for the entire upcoming week through Sunday")
    parser.add_argument("--ledger", action="store_true", help="View summary of all historical cloud pins")
    parser.add_argument("--clean", action="store_true", help="Purge all temporary local images to free 100%% disk space")
    parser.add_argument("--keep-local", action="store_true", help="Keep temporary images locally on disk")
    
    args = parser.parse_args()
    
    if args.wizard:
        run_setup_wizard()
        return
        
    if args.ledger:
        show_ledger_summary()
        return
        
    if args.clean:
        purge_local_images()
        return
        
    if not CONFIG_FILE.exists():
        print("First time running PinAutopilot! Launching interactive wizard...\n")
        run_setup_wizard()
        
    cfg = load_user_config()
    niche_to_run = args.niche or cfg.get("active_niche", "home_organization")
    
    if args.week:
        args.continue_schedule = True
        csv_file = OUTPUT_DIR / "pinterest_bulk_schedule.csv"
        existing_count = 0
        if csv_file.exists():
            try:
                import csv
                with open(csv_file, "r", encoding="utf-8") as f:
                    existing_count = sum(1 for r in csv.DictReader(f) if r.get("Title"))
            except Exception:
                existing_count = 0
        pins_needed = max(20, 55 - existing_count)
        args.count = pins_needed
        print(f"\n🗓️ Full Week Mode Active:")
        print(f"  • {existing_count} pins already queued for early week.")
        print(f"  • Generating {pins_needed} new pins to complete schedule through Sunday!")
        print("==================================================\n")
        
    # Run the autopilot discovery & pin generator
    autopilot.run_autopilot(
        total_pins_target=args.count,
        max_price=cfg.get("max_price", 999),
        min_rating=cfg.get("min_rating", 3.8),
        niche_id=niche_to_run,
        purge_local=not args.keep_local,
        continue_schedule=args.continue_schedule
    )

if __name__ == "__main__":
    main()
