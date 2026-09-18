"""Polling API for active listings."""

import requests

"""Polling API for active listings."""

from collections import Counter, defaultdict
from pathlib import Path

import requests
import json

from alerts.core import Alerter
from config.api import SEARCH_ENDPOINT
from utils.io import generate_log_path, write_to_dir
from utils.misc import get_timestamp

from .auth import get_access_token
from .core import SearchEndpointResponse, SearchEndpointPayload


def log_response(api_response: SearchEndpointResponse, active_dir: Path) -> None:
    """Log API response to file."""

    item_dir = generate_log_path(
        active_dir,
        api_response.search_value,
        is_active=True,
        cat_id=api_response.inferred_cat_id,
        cat_name=api_response.inferred_cat_name,
    )

    write_to_dir(api_response.json_response, item_dir, file_ext="json")


class ListingSearcher:
    def __init__(self, alerter: Alerter | None = None) -> None:
        if alerter:
            raise NotImplementedError

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
        self,
        access_token: str,
        payload: SearchEndpointPayload,
        ignore_warnings: bool = False,
    ) -> SearchEndpointResponse:
        """Query API (optionally restricting category) and return the JSON response."""

        headers = {
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
        }

        r = requests.get(
            url=SEARCH_ENDPOINT,
            params=payload.model_dump(exclude_none=True),
            headers=headers,
            timeout=10,
        )
        r_json = r.json()

        if "itemSummaries" not in r_json or (
            ("warnings" in r_json or "errors" in r_json) and not ignore_warnings
        ):
            log_file_path = Path(f"temp_logs/{get_timestamp()}.txt")
            self._dump_response(r_json, payload.search_value, log_file_path)
            raise RuntimeError(
                f"Unexpected Search Endpoint response, see {log_file_path!s} for more details."
            )

        item_summaries = r_json["itemSummaries"]

        cat_counts, cat_mappings = self._parse_categories(item_summaries)

        # Infer category ID and name from most common
        cat_id = int(cat_counts.most_common(1)[0][0])
        cat_name = cat_mappings[cat_id]

        # DEBUG
        # for cat_id_str, cat_count in cat_counts.most_common():
        #     print(f"{(cat_id_str)}/{cat_mappings[int(cat_id_str)]}: {cat_count}")

        return SearchEndpointResponse(
            json_response=r_json,
            search_value=payload.search_value,
            inferred_cat_id=cat_id,
            inferred_cat_name=cat_name,
        )

    def _dump_response(
        self, json_response: str, search_value: str, log_file_path: Path
    ) -> None:
        """Dump response to file. Useful for debugging."""

        with log_file_path.open(mode="w") as f:
            f.write(
                f"json: {json.dumps(json_response, indent=4)}\nsearch_value: {search_value}"
            )


# Example usage
if __name__ == "__main__":
    raise NotImplementedError

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
