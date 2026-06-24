from pathlib import Path

# Up 2 levels
ROOT_DIR = Path.cwd()   

# dirs
CONFIG_DIR = ROOT_DIR / "configs"
LOG_DIR = ROOT_DIR / "logs"
SOLD_DIR = LOG_DIR / "sold"
ACTIVE_DIR = LOG_DIR / "active" # /search/catId_catName
ENV_PATH = ROOT_DIR / "used.env"

# temp dirs
TEMP_LOG_DIR = ROOT_DIR / "temp_logs"
TEMP_SOLD_DIR = TEMP_LOG_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_LOG_DIR / "active"

# API URLs
API_URL = "https://api.ebay.com/buy/browse/v1"
SEARCH_URL = f"{API_URL}/item_summary/search"