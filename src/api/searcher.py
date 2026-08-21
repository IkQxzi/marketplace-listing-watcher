"""Polling API for active listings."""

import requests

"""Polling API for active listings."""

from collections import Counter, defaultdict
from pathlib import Path

import requests

from alerts.core import Alerter
from config.api import SEARCH_ENDPOINT
from utils.io import generate_log_path, write_to_dir

from .auth import get_access_token
from .core import SearchEndpointResponse


def log_response(api_response: SearchEndpointResponse, active_dir: Path) -> None:
    """Log API response to two files: one for item summaries, one for metadata, using category counts as file names."""

    item_dir = generate_log_path(
        active_dir,
        api_response.q,
        is_active=True,
        cat_id=api_response.inferred_cat_id,
        cat_name=api_response.inferred_cat_name,
    )

    write_to_dir(api_response.json_response, item_dir, file_ext="json")


class ListingSearcher:
    def __init__(self, alerter: Alerter) -> None:
        self.alerter = alerter

    def _parse_categories(
        self, item_summaries: list[dict]
    ) -> tuple[Counter[str], defaultdict[int, str]]:
        """Parse categories of items,
        and return the counts of each category ID and the associated category name."""

        cat_counts = Counter()
        cat_mapping = defaultdict()

        for item in item_summaries:
            cat_info: list = item["categories"]
            cat_info: list = item["categories"]

            for cat in cat_info:
                cat_id = int(cat["categoryId"])
                cat_id = int(cat["categoryId"])

                cat_counts[cat_id] += 1
                cat_mapping[cat_id] = cat["categoryName"]

                cat_mapping[cat_id] = cat["categoryName"]

        return cat_counts, cat_mapping

    def get_listings(
        self, access_token: str, config: SearchAPIConfig
    ) -> SearchEndpointResponse:
        """Query API (optionally restricting category) and return the JSON response."""

        headers = {
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
        }

        r = requests.get(
            url=SEARCH_ENDPOINT, params=config.to_dict(), headers=headers, timeout=10
        )
        r = requests.get(
            url=SEARCH_ENDPOINT, params=config.to_dict(), headers=headers, timeout=10
        )
        r_json = r.json()

        try:
            item_summaries: list[dict] = r.json()["itemSummaries"]
            item_summaries: list[dict] = r.json()["itemSummaries"]
        except KeyError:
            print(f"KeyError; r_json: {r_json}")
            print(f"KeyError; r_json: {r_json}")
            exit()

        cat_counts, cat_mappings = self._parse_categories(item_summaries)

        # Infer category ID and name from most common
        cat_id = int(cat_counts.most_common(1)[0][0])
        cat_name = cat_mappings[cat_id]

        # DEBUG
        for cat_id_str, cat_count in cat_counts.most_common():
            print(f"{(cat_id_str)}/{cat_mappings[int(cat_id_str)]}: {cat_count}")
            print(f"{(cat_id_str)}/{cat_mappings[int(cat_id_str)]}: {cat_count}")

        return SearchEndpointResponse(r_json, config.q, cat_id, cat_name)


# Example usage
if __name__ == "__main__":
    raise NotImplementedError

    from config.dirs import ACTIVE_DIR, TEMP_ACTIVE_DIR
if __name__ == "__main__":
    from alerts.discord import DiscordBot
    from config.alerts import DISCORD_WEBHOOK_URL
    from config.api import APP_ID, CERT_ID, REFRESH_TOKEN
    from config.dirs import TEMP_ACTIVE_DIR

    assert REFRESH_TOKEN and APP_ID and CERT_ID, "API credentials missing from .env"
    assert DISCORD_WEBHOOK_URL, "Discord webhook URL missing from .env"

    iphone_16_basic_conf = SearchAPIConfig(q="iphone 16", conditions=["NEW", "USED"])
    iphone_16_basic_conf = SearchAPIConfig(q="iphone 16", conditions=["NEW", "USED"])

    disc_bot = DiscordBot(DISCORD_WEBHOOK_URL)

    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)
    searcher = ListingSearcher(disc_bot)

    api_resp = searcher.get_listings(access_token, iphone_16_basic_conf)
    log_response(api_resp, TEMP_ACTIVE_DIR)
