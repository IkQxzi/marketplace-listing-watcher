"""Polling API for active listings."""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import requests

from alerts.core import Alerter
from api.listings import Listing, sort_listings
from api.params import (
    DatetimeRange,
    SearchEndpointPayload,
)
from api.schemas import ResponseMetadata, SearchEndpointResponse
from api.storage import (
    SearchEndpointSavePaths,
    get_latest_listing_timestamp,
    write_listings_to_data_path,
)
from config.api import SEARCH_ENDPOINT
from config.dirs import ACTIVE_DIR
from utils.misc import get_timestamp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
        self.save_paths = SearchEndpointSavePaths(
            payload_hash=hash(payload), base_dir=active_listing_dir
        )

    def get_latest_listings(
        self,
        access_token: str,
        ignore_warnings: bool = False,
    ) -> list[Listing]:
        """
        Query Search Endpoint for listings after a timestamp.\n
        Timestamp is the newer of the last listing timestamp and the payload filter timestamp.\n
        Write API responses and return list of Listing objects.
        """

        latest_timestamp = None
        if self.payload.filter.item_start_date:
            if self.payload.filter.item_start_date.upper_bd:
                raise NotImplementedError(
                    "Support for item start date ranges (specifically upper bd.) not yet implemented."
                )

            logging.warning(
                "Taking lower bd. of item start date for filter. Cannot handle upper bd."
            )
            latest_timestamp = self.payload.filter.item_start_date.lower_bd
            # TODO: if user hash is ahead of latest timestamp, use that

        if self.save_paths.data_path.exists():
            logging.debug(f"Existing data found at {self.save_paths.data_path}")
            (f"Existing data found at {self.save_paths.data_path}")
            if latest_timestamp:
                latest_timestamp = max(
                    get_latest_listing_timestamp(self.save_paths.data_path),
                    latest_timestamp,
                )

        resp = self._get_response_after_timestamp(access_token, latest_timestamp)

        sorted_listings = self.write_response_to_save_paths(self.save_paths, resp)

        return sorted_listings

    def _get_response_after_timestamp(
        self,
        access_token: str,
        latest_timestamp: datetime | None,
        ignore_warnings: bool = False,
    ) -> SearchEndpointResponse:
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

        cat_counts, cat_mappings = self._get_category_counts_and_mappings(
            item_summaries
        )

        # Infer category ID and name from most common
        cat_id = int(cat_counts.most_common(1)[0][0])
        cat_name = cat_mappings[cat_id]

        response = SearchEndpointResponse(
            metadata=metadata,
            item_summaries=item_summaries,
            search_value=self.payload.search_value,
            inferred_cat_id=cat_id,
            inferred_cat_name=cat_name,
            _raw_json=r_json,
        )

        return response

    def _get_category_counts_and_mappings(
        self, item_summaries: list[dict]
    ) -> tuple[Counter[str], defaultdict[int, str]]:
        """Parse categories of items,
        and return the counts of each category ID and the associated category name."""

        cat_counts = Counter()
        cat_mapping = defaultdict()

        for item in item_summaries:
            cat_info: list = item["categories"]

            for cat in cat_info:
                cat_id = int(cat["categoryId"])

                cat_counts[cat_id] += 1
                cat_mapping[cat_id] = cat["categoryName"]

        return cat_counts, cat_mapping

    def _dump_response(
        self, json_response: str, search_value: str, log_file_path: Path
    ) -> None:
        """Dump response to file. Useful for debugging."""

        with log_file_path.open(mode="w") as f:
            f.write(
                f"search_value: {search_value}\n json: {json.dumps(json_response, indent=4)}"
            )

    def write_response_to_save_paths(
        self, paths: SearchEndpointSavePaths, resp: SearchEndpointResponse
    ) -> list[Listing]:
        """
        Write the payload config, the data from response, metadata, the raw response to files.
        Listings written to data path are sorted newest first (at top of file).
        Returns the sorted listings.
        """

        with paths.raw_response_path.open(mode="a") as f:
            logging.debug(f"Writing raw response to {paths.raw_response_path}")
            json.dump(resp._raw_json, f, indent=2)

        sorted_listings = sort_listings(
            [Listing.model_validate(listing) for listing in resp.item_summaries]
        )

        write_listings_to_data_path(sorted_listings, paths.data_path)

        with paths.metadata_path.open(mode="w") as f:
            logging.debug(f"Writing metadata to {paths.metadata_path}")
            json.dump(asdict(resp.metadata), f, indent=2)

        # Only bother writing config if config not already present
        # Trusts hashing to enforce uniqueness
        if not paths.config_path.exists():
            with paths.config_path.open(mode="w") as f:
                logging.debug(f"Writing config to {paths.config_path}")
                json.dump(self.payload.model_dump(), f, indent=2)

        return sorted_listings
