"""For scraping."""

import os
from dotenv import load_dotenv

from .dirs import ENV_PATH

load_dotenv(ENV_PATH)

# URLs
WEB_SEARCH_URL = "https://www.ebay.co.uk/sch/i.html"

# Proxies
PROXY_CONFIG = {
    "server": os.getenv("proxy_server"),
    "username": os.getenv("proxy_username"),
    "password": os.getenv("proxy_password"),
}
