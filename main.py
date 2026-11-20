import logging
import time
from pathlib import Path

import typer

from api import SearchEndpointPayload
from api.auth import get_access_token
from api.searching import ListingSearcher
from config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from config.dirs import TEMP_ACTIVE_DIR

logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main(yaml_path: Path, api_limit: int = 5000) -> None:

    if not REFRESH_TOKEN:
        raise ValueError("Refresh token missing from env.")

    if not APP_ID:
        raise ValueError("App ID missing from env.")

    if not CERT_ID:
        raise ValueError("Cert ID missing from env.")

    polling_interval = 24 * 60 * 60 / api_limit

    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    payload = SearchEndpointPayload.load_simple_yaml(yaml_path)
    logging.info("Loaded payload.")
    searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)

    while True:
        listings = searcher.get_latest_listings(access_token)
        logging.info(f"Sleeping for {polling_interval} seconds.")
        time.sleep(polling_interval)


if __name__ == "__main__":
    typer.run(main)
