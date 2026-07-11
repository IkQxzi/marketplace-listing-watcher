from pathlib import Path
from dotenv import load_dotenv
import os


# Up 2 levels
ROOT_DIR = Path.cwd()   

# dirs
CONFIG_DIR = ROOT_DIR / "configs"
LOG_DIR = ROOT_DIR / "logs"
SOLD_DIR = LOG_DIR / "sold"
ACTIVE_DIR = LOG_DIR / "active" # /search/catId_catName
ENV_PATH = ROOT_DIR / "used.env"

# For unique paths
load_dotenv(ENV_PATH)

# temp dirs
if os.getenv('test_html_path'):
    TEMP_HTML_PATH = os.getenv('test_html_path')

TEMP_LOG_DIR = ROOT_DIR / "temp_logs"
TEMP_SOLD_DIR = TEMP_LOG_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_LOG_DIR / "active"

# API URLs
API_URL = "https://api.ebay.com/buy/browse/v1"
API_SEARCH_URL = f"{API_URL}/item_summary/search"

# Regular URLs
WEB_SEARCH_URL = "https://www.ebay.co.uk/sch/i.html"