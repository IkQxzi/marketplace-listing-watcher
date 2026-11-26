"""API config."""

import os

from dotenv import load_dotenv

from .dirs import ENV_PATH, ROOT_DIR

load_dotenv(ENV_PATH)

# Credentials
APP_ID = os.getenv("prd_app_id")
CERT_ID = os.getenv("prd_cert_id")
REFRESH_TOKEN = os.getenv("prd_refresh_token")
ACCESS_TOKEN_PATH = ROOT_DIR / "token.json"
ACCESS_TOKEN_REFRESH_THRESHOLD = 60  # Seconds below which new requested

# Endpoints
BROWSE_ENDPOINT = "https://api.ebay.com/buy/browse/v1"
SEARCH_ENDPOINT = f"{BROWSE_ENDPOINT}/item_summary/search"
