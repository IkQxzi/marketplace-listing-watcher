"""Polling API for active listings."""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import requests

from alerts.core import Alerter
from config.api import SEARCH_ENDPOINT
from config.dirs import ACTIVE_DIR, TEMP_ACTIVE_DIR
from utils.io import generate_save_path
from utils.misc import get_timestamp

from .auth import get_access_token
from .core import SearchEndpointSavePaths
from .params import DatetimeRange, SearchEndpointPayload
from .schemas import ResponseMetadata, SearchEndpointRawResponse


def _log_response(
    payload: SearchEndpointPayload,
    api_response: SearchEndpointRawResponse,
    active_dir: Path,
) -> None:
    """Log API response to file."""

    item_dir = generate_save_path(
        log_dir=active_dir,
        item_name=payload.search_value,
        is_active=True,
        cat_id=api_response.inferred_cat_id,
        cat_name=api_response.inferred_cat_name,
    )

    json_path = item_dir / f"{hash(payload)!s}.json"
    print(f"json_path: {json_path}")

    with json_path.open(mode="w") as f:
        json.dump(api_response.raw_json, f)


class ListingSearcher:
    """Class to search for new listings."""

    def __init__(
        self,
        payload: SearchEndpointPayload,
        active_listing_dir: Path = ACTIVE_DIR,
        alerter: Alerter | None = None,
    ) -> None:
        if alerter:
            raise NotImplementedError

        self.payload = payload
        self.active_listing_dir = active_listing_dir

    def get_latest_listings(
        self,
        access_token: str,
        ignore_warnings: bool = False,
    ) -> SearchEndpointRawResponse:
        """
        Read timestamp of latest listings from one of the files specified in `core.py`\n
        Query Search Endpoint for listings after timestamp.\n
        Write and return the raw response from API.
        """

        if self.payload.filter.item_start_date or self.payload.filter.item_end_date:
            # TODO: if user hash is ahead of latest timestamp, use that
            raise NotImplementedError(
                "Support for item start/end date ranges not yet implemented."
            )

        # TODO: change test path
        save_paths = SearchEndpointSavePaths(
            payload_hash=hash(self.payload), base_dir=self.active_listing_dir
        )

        latest_timestamp = None
        if save_paths.data_path.exists():
            latest_timestamp = self._get_latest_timestamp(save_paths.data_path)

        return self._get_listings_after(access_token, latest_timestamp)

    def _get_listings_after(
        self,
        access_token: str,
        latest_timestamp: datetime | None,
        ignore_warnings: bool = False,
    ) -> SearchEndpointRawResponse:
        """
        Get all the listings after the latest timestamp specified.
        """

        # May not work, may require frozen for hashing
        # Should use user-specified if it is newer than the latest timestamp
        if latest_timestamp:
            self.payload.filter.item_start_date = DatetimeRange(
                lower_bd=latest_timestamp
            )

        headers = {
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
        }

        r = requests.get(
            url=SEARCH_ENDPOINT,
            params=self.payload.model_dump(exclude_none=True),
            headers=headers,
            timeout=10,
        )
        r_json = r.json()

        if "itemSummaries" not in r_json or (
            ("warnings" in r_json or "errors" in r_json) and not ignore_warnings
        ):
            log_file_path = Path(f"temp_logs/{get_timestamp()}.txt")
            self._dump_response(r_json, self.payload.search_value, log_file_path)
            raise RuntimeError(
                f"Unexpected Search Endpoint response, see {log_file_path} for more details."
            )

        metadata = ResponseMetadata(
            href=r_json["href"],
            total=r_json["total"],
            limit=r_json["limit"],
            offset=r_json["offset"],
            next=r_json.get("next"),
        )

        item_summaries = r_json["itemSummaries"]

        cat_counts, cat_mappings = self._parse_categories(item_summaries)

        # Infer category ID and name from most common
        cat_id = int(cat_counts.most_common(1)[0][0])
        cat_name = cat_mappings[cat_id]

        response = SearchEndpointRawResponse(
            metadata=metadata,
            item_summaries=item_summaries,
            search_value=self.payload.search_value,
            inferred_cat_id=cat_id,
            inferred_cat_name=cat_name,
            raw_json=r_json,
        )

        return response

    def _get_latest_timestamp(self, data_path: Path) -> datetime:
        with data_path.open(mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            timestamp_ind = list(next(reader)).index("timestamp")
            latest_timestamp = datetime.fromisoformat(list(next(reader))[timestamp_ind])

        if not isinstance(latest_timestamp, datetime):
            raise ValueError(
                "Timestamp from ListingSearcher._get_latest_timestamp() is not datetime object."
            )

        return latest_timestamp  # TODO: convert to datetime

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
