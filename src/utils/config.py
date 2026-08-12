from pathlib import Path
from dotenv import load_dotenv
import os


# Up 2 levels
ROOT_DIR = Path(__file__).parent.parent.parent

# Directories ---------

# dirs
CONFIG_DIR = ROOT_DIR / "configs"
LOG_DIR = ROOT_DIR / "logs"
SOLD_DIR = LOG_DIR / "sold"
ACTIVE_DIR = LOG_DIR / "active" # /search/catId_catName

ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

# Temporary dirs
temp_html_path_str = os.getenv('test_html_path') # Optional for testing
if temp_html_path_str:
    TEMP_HTML_PATH = Path(temp_html_path_str)
TEMP_LOG_DIR = ROOT_DIR / "temp_logs"
TEMP_SOLD_DIR = TEMP_LOG_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_LOG_DIR / "active"
TEMP_STATS_DIR = TEMP_LOG_DIR / "stats"

# API ---------

# API URLs
API_URL = "https://api.ebay.com/buy/browse/v1"
API_SEARCH_URL = f"{API_URL}/item_summary/search"

# API Credentials
APP_ID = os.getenv('prd_app_id')
CERT_ID = os.getenv('prd_cert_id')
REFRESH_TOKEN = os.getenv('prd_refresh_token')

# Scraping ---------

# Regular URLs
WEB_SEARCH_URL = "https://www.ebay.co.uk/sch/i.html"

# Proxies
PROXY_CONFIG = {
    'server': os.getenv('proxy_server'),
    'username': os.getenv('proxy_username'),
    'password': os.getenv('proxy_password')
}
