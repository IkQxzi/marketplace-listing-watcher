import logging
import time
from pathlib import Path

import typer

from marketplace_listing_watcher.alerts.discord import DiscordBot
from marketplace_listing_watcher.api import SearchEndpointPayload
from marketplace_listing_watcher.api.auth import get_access_token
from marketplace_listing_watcher.api.searching import ListingSearcher
from marketplace_listing_watcher.config.alerts import DISCORD_WEBHOOK_URL
from marketplace_listing_watcher.config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from marketplace_listing_watcher.config.dirs import TEMP_ACTIVE_DIR

logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_creds() -> None:
    if not REFRESH_TOKEN:
        raise ValueError("Refresh token missing from env.")

    if not APP_ID:
        raise ValueError("App ID missing from env.")

    if not CERT_ID:
        raise ValueError("Cert ID missing from env.")

    if not DISCORD_WEBHOOK_URL:
        raise ValueError("Discord webhook URL missing from env.")


def main(yaml_path: Path, api_limit: int = 5000) -> None:

    check_creds()
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    # Primitive "as much as possible", can make smarter later
    polling_interval = 24 * 60 * 60 / api_limit
    logging.info(f"Polling interval set to {polling_interval}s.")

    payload = SearchEndpointPayload.load_simple_yaml(yaml_path)
    logging.info("Loaded payload.")

    searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)

    bot = DiscordBot(DISCORD_WEBHOOK_URL)

    while True:
        listings = searcher.get_latest_listings_and_alert(access_token, bot)

        logging.info(f"Sleeping for {polling_interval} seconds.")
        time.sleep(polling_interval)


if __name__ == "__main__":
    typer.run(main)
