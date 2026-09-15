import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
PINS_DIR = OUTPUT_DIR / "pins"
BASE_IMAGES_DIR = BASE_DIR / "base_images"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
NICHES_DIR = BASE_DIR / "niches"
CONFIG_FILE = BASE_DIR / "user_config.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PINS_DIR.mkdir(parents=True, exist_ok=True)
BASE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)
NICHES_DIR.mkdir(parents=True, exist_ok=True)

# Machine-Independent Bundled Fonts
FONT_POPPINS_EXTRABOLD = str(FONTS_DIR / "Poppins-ExtraBold.ttf")
FONT_POPPINS_BOLD = str(FONTS_DIR / "Poppins-Bold.ttf")
FONT_OSWALD_BOLD = str(FONTS_DIR / "Oswald-Bold.ttf")
FONT_SERIF_BOLD = str(FONTS_DIR / "PlayfairDisplay-Bold.ttf")
FONT_SANS_BOLD = str(FONTS_DIR / "Montserrat-Bold.ttf")
FONT_SANS_REGULAR = str(FONTS_DIR / "Montserrat-Regular.ttf")

# High-Visibility Defaults
FONT_BOLD = FONT_POPPINS_EXTRABOLD
FONT_REGULAR = FONT_POPPINS_BOLD

# Default settings
DEFAULT_CONFIG = {
    "brand_name": "Simple Space Haven",
    "brand_handle": "@simplespacehaven",
    "blog_url": "http://simplespacehaven.blogspot.com",
    "amazon_tag": "simplespaceha-21",
    "marketplace": "amazon.in",
    "currency_symbol": "₹",
    "active_niche": "home_organization",
    "max_price": 999,
    "min_rating": 3.8
}

def load_user_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(data)
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

USER_CFG = load_user_config()

BRAND_NAME = USER_CFG.get("brand_name", "Simple Space Haven")
BRAND_HANDLE = USER_CFG.get("brand_handle", "@simplespacehaven")
BLOG_URL = USER_CFG.get("blog_url", "http://simplespacehaven.blogspot.com")
AMAZON_TRACKING_ID = USER_CFG.get("amazon_tag", "simplespaceha-21")
MARKETPLACE = USER_CFG.get("marketplace", "amazon.in")
CURRENCY_SYMBOL = USER_CFG.get("currency_symbol", "₹")
ACTIVE_NICHE = USER_CFG.get("active_niche", "home_organization")
DEFAULT_MAX_PRICE = USER_CFG.get("max_price", 999)
DEFAULT_MIN_RATING = USER_CFG.get("min_rating", 3.8)

def load_niche_data(niche_id=None):
    nid = niche_id or ACTIVE_NICHE
    niche_file = NICHES_DIR / f"{nid}.json"
    if niche_file.exists():
        with open(niche_file, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback to home_organization if specified not found
    fallback = NICHES_DIR / "home_organization.json"
    if fallback.exists():
        with open(fallback, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"boards": {}}

NICHE_DATA = load_niche_data()
BOARD_TAXONOMY = NICHE_DATA.get("boards", {})

# Editorial Color Palettes (Aesthetic, Warm Minimalist, High CTR)
COLORS = {
    "bg_light": (250, 248, 245),       # Warm off-white / alabaster
    "card_bg": (255, 255, 255),        # Pure white
    "primary_dark": (35, 39, 42),      # Soft charcoal black for headlines
    "accent_sage": (76, 110, 89),       # Muted sage green (earthy home vibe)
    "accent_terracotta": (196, 96, 68), # Warm rust / terracotta for badges
    "accent_gold": (212, 163, 89),     # Soft warm gold for highlight
    "text_muted": (100, 105, 110),     # Subtitle gray
    "border_light": (230, 226, 220),   # Subtle divider
    "star_color": (245, 166, 35),      # Star rating yellow
    "glass_bg": (255, 255, 255, 235),  # Frosted glass overlay
    "editorial_cream": (246, 243, 238) # Editorial magazine cream
}
