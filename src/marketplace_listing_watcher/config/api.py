"""API config."""

import os
from dotenv import load_dotenv

from .dirs import ENV_PATH

load_dotenv(ENV_PATH)

# Credentials
APP_ID = os.getenv("prd_app_id")
CERT_ID = os.getenv("prd_cert_id")
REFRESH_TOKEN = os.getenv("prd_refresh_token")

# Endpoints
BROWSE_ENDPOINT = "https://api.ebay.com/buy/browse/v1"
SEARCH_ENDPOINT = f"{BROWSE_ENDPOINT}/item_summary/search"
