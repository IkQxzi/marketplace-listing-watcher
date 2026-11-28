from marketplace_listing_watcher.config.llm import GEMINI_API_KEY
import logging
import time
from pathlib import Path
from typing import Annotated

import typer

from marketplace_listing_watcher.llm.generation import GeminiClient
from marketplace_listing_watcher.alerts.discord import DiscordBot
from marketplace_listing_watcher.api import SearchEndpointPayload
from marketplace_listing_watcher.api.auth import get_access_token
from marketplace_listing_watcher.api.searching import ListingSearcher
from marketplace_listing_watcher.api.storage import load_payload_from_json_path
from marketplace_listing_watcher.config.alerts import DISCORD_WEBHOOK_URL
from marketplace_listing_watcher.config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from marketplace_listing_watcher.config.dirs import TEMP_ACTIVE_DIR

logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = typer.Typer()


def _check_creds() -> None:
    if not REFRESH_TOKEN:
        raise ValueError("Refresh token missing from env.")

    if not APP_ID:
        raise ValueError("App ID missing from env.")

    if not CERT_ID:
        raise ValueError("Cert ID missing from env.")

    if not DISCORD_WEBHOOK_URL:
        raise ValueError("Discord webhook URL missing from env.")


def _calculate_polling_interval(api_key_daily_limit: int = 5000) -> float:
    # Primitive "as much as possible", can make smarter later
    polling_interval = 24 * 60 * 60 / api_key_daily_limit
    logging.info(f"Polling interval set to {polling_interval}s.")
    return polling_interval


def get_listings_on_loop(
    searcher: ListingSearcher,
    access_token: str,
    bot: DiscordBot,
    polling_interval: float,
) -> None:
    """Retrieve latest listings on a loop, indefinitely."""
    while True:
        breakpoint()
        listings = searcher.get_latest_listings_and_alert(access_token, bot)

        logging.info(f"Sleeping for {polling_interval} seconds.")
        time.sleep(polling_interval)


@app.callback(invoke_without_command=True)
def main(
    generate: Annotated[
        str,
        typer.Option(
            "-g", "--generate", help="Natural language to generate a payload from."
        ),
    ] = "",
    json_path_str: Annotated[
        str,
        typer.Option(
            "--json",
            "-j",
            help="Path to json file containing payload params."
            "Cannot be used with yaml path.",
            show_default=False,
        ),
    ] = "",
    yaml_path_str: Annotated[
        str,
        typer.Option(
            "--simple",
            "-s",
            "--yaml",
            "-y",
            help="Path to yaml file containing simple payload options."
            "Cannot be used with json path.",
            show_default=False,
        ),
    ] = "",
    api_key_daily_limit: Annotated[
        int,
        typer.Option(
            "--daily-limit",
            "-d",
            help="Daily request limit for the eBay API key in env.",
        ),
    ] = 5000,
) -> None:

    _check_creds()
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    polling_interval = _calculate_polling_interval(api_key_daily_limit)

    if not (generate or json_path_str or yaml_path_str):
        raise ValueError(
            "One of generate (-j [text]) json_path (-j [path]) or yaml_path (-s|-y [path]) must be specified."
        )

    if json_path_str and yaml_path_str:
        raise ValueError(
            "Only one of json_path (-j) or yaml_path (-s|-y) must be specified."
        )

    if json_path_str:
        json_path = Path(json_path_str).resolve()
        payload = load_payload_from_json_path(json_path)
    if yaml_path_str:
        yaml_path = Path(yaml_path_str).resolve()
        payload = SearchEndpointPayload.load_simple_yaml(yaml_path)
    if generate:
        if not GEMINI_API_KEY:
            raise ValueError()
        client = GeminiClient(generate, GEMINI_API_KEY, access_token)
        payload = client.generate_payload()

    logging.info("Loaded payload.")

    searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)

    bot = DiscordBot(DISCORD_WEBHOOK_URL)

    get_listings_on_loop(searcher, access_token, bot, polling_interval)
