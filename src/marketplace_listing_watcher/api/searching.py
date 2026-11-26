"""Polling API for active listings."""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import requests

from marketplace_listing_watcher.alerts.core import Alerter
from marketplace_listing_watcher.api.listings import Listing, sort_listings
from marketplace_listing_watcher.api.params import (
    DatetimeRange,
    SearchEndpointPayload,
)
from marketplace_listing_watcher.api.schemas import (
    ResponseMetadata,
    SearchEndpointResponse,
)
from marketplace_listing_watcher.api.storage import (
    SearchEndpointSavePaths,
    read_latest_listing_timestamp,
    write_listings_to_data_path,
    write_payload_to_path,
)
from marketplace_listing_watcher.config.api import SEARCH_ENDPOINT
from marketplace_listing_watcher.config.dirs import ACTIVE_DIR
from marketplace_listing_watcher.utils.misc import get_timestamp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ListingSearcher:
    """
    Class to search for new listings.\n
    Requires:
    - A payload
    - An alerter
    Optional:
    - Active listing directory
    """

    def __init__(
        self,
        payload: SearchEndpointPayload,
        active_listing_dir: Path = ACTIVE_DIR,
    ) -> None:

        self.payload = payload
        self.save_paths = SearchEndpointSavePaths(
            payload_hash=hash(payload), base_dir=active_listing_dir
        )
        self.latest_timestamp: datetime | None = None

    def get_latest_listings_and_alert(
        self,
        access_token: str,
        alerter: Alerter | None = None,
        ignore_warnings: bool = False,
    ) -> list[Listing]:
        """
        Query Search Endpoint for listings after a timestamp.\n
        Alerts alerter if there is one.
        Timestamp is the newer of the last listing timestamp and the payload filter timestamp.\n
        Note that if there is a timestamp, the limit parameter of the payload will be ignored,
        because the API pads out the response with listings that do not respect the timestamp restriction.\n
        Write API responses and return list of Listing objects, sorted oldest first.\n
        """

        self._resolve_latest_timestamp()
        resp = self._get_response_after_latest_timestamp(access_token)
        sorted_listings = self.clean_listings(resp)

        if sorted_listings and alerter:
            alerter.alert(sorted_listings)

        # Skips writing to data if there are no listings
        self.write_response_to_save_paths(self.save_paths, resp, sorted_listings)

        return sorted_listings

    def _resolve_latest_timestamp(self) -> None:
        """
        Resolves the latest timestamp from the newer of the last listing fetched,
        or the payload's start date in its filter.
        """
        latest_timestamp_opts = []

        if self.payload.filter.item_start_date:
            if self.payload.filter.item_start_date.upper_bd:
                raise NotImplementedError(
                    "Support for item start date ranges (specifically upper bd.) not yet implemented."
                )

            logging.warning(
                "Taking lower bd. of item start date for filter. Cannot handle upper bd."
            )
            if self.payload.filter.item_start_date.lower_bd:
                latest_timestamp_opts.append(
                    self.payload.filter.item_start_date.lower_bd
                )
            # TODO: if user hash is ahead of latest timestamp, use that

        if self.save_paths.data_path.exists():
            logging.debug(f"Existing data found at {self.save_paths.data_path}")
            latest_timestamp_opts.append(
                read_latest_listing_timestamp(self.save_paths.data_path)
            )

        self.latest_timestamp = (
            max(latest_timestamp_opts) if latest_timestamp_opts else None
        )

    def _get_response_after_latest_timestamp(
        self,
        access_token: str,
        ignore_warnings: bool = False,
    ) -> SearchEndpointResponse:
        """
        Get all the listings after the latest timestamp from self attribute.\n
        """

        # To avoid modifying the original
        local_payload = self.payload.model_copy(deep=True)

        # May not work, may require frozen for hashing
        # Should use user-specified if it is newer than the latest timestamp
        if self.latest_timestamp:
            local_payload.filter.item_start_date = DatetimeRange(
                lower_bd=self.latest_timestamp
            )
            logging.debug(
                f"Requesting listings after timestamp: {self.latest_timestamp.isoformat()}"
            )

        headers = {
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            "Authorization": f"Bearer {access_token}",
        }

        r = requests.get(
            url=SEARCH_ENDPOINT,
            params=local_payload.model_dump(exclude_none=True, context="api"),
            headers=headers,
            timeout=10,
        )
        r_json = r.json()

        log_file_path = Path(f"temp_logs/{get_timestamp()}.txt")
        if r_json.get("warnings") and not ignore_warnings:
            self._dump_response(r_json, local_payload._search_value, log_file_path)
            raise RuntimeError(
                f"Warnings found in Search Endpoint response:\n{r_json.get('warnings')}"
            )

        if r_json.get("errors") and not ignore_warnings:
            self._dump_response(r_json, local_payload._search_value, log_file_path)
            raise RuntimeError(
                f"Errors found in Search Endpoint response:\n{r_json.get('errors')}"
            )

        metadata = ResponseMetadata(
            href=r_json["href"],
            total=r_json["total"],
            limit=r_json["limit"],
            offset=r_json["offset"],
            next=r_json.get("next"),
        )

        item_summaries = r_json.get("itemSummaries", {})

        if item_summaries:
            cat_counts, cat_mappings = self._get_category_counts_and_mappings(
                item_summaries
            )

            # Infer category ID and name from most common
            cat_id = int(cat_counts.most_common(1)[0][0])
            cat_name = cat_mappings[cat_id]
        else:
            cat_name = cat_id = None

        response = SearchEndpointResponse(
            metadata=metadata,
            item_summaries=item_summaries,
            search_value=local_payload._search_value,
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
                f"search_value: {search_value}\n response: {json.dumps(json_response, indent=4)}"
            )

    def clean_listings(self, resp: SearchEndpointResponse) -> list[Listing]:
        """Clean listings from response and return them."""

        listings = [Listing.model_validate(listing) for listing in resp.item_summaries]

        # Have to manually filter because API always pads out payload limit
        # Must be strict to not retrieve any stale
        if self.latest_timestamp:
            listings = [
                listing
                for listing in listings
                if listing.item_origin_date > self.latest_timestamp
            ]
        sort_listings(listings)

        return listings

    def write_response_to_save_paths(
        self,
        paths: SearchEndpointSavePaths,
        resp: SearchEndpointResponse,
        listings: list[Listing],
    ) -> None:
        """
        Write the payload config, cleaned listings, metadata, the raw response to files.\n
        Removes duplicate listings (which are always present from API padding out payload limit).\n
        Listings written to data path are sorted newest first (at top of file).\n
        """

        with paths.raw_response_path.open(mode="a") as f:
            logging.debug(f"Writing raw response to {paths.raw_response_path}")
            json.dump(resp._raw_json, f, indent=2)

        # Skip if there are no new listings
        if listings:
            write_listings_to_data_path(listings, paths.data_path)

        with paths.metadata_path.open(mode="w") as f:
            logging.debug(f"Writing metadata to {paths.metadata_path}")
            json.dump(asdict(resp.metadata), f, indent=2)

        # Only bother writing config if config not already present
        # Trusts hashing to enforce uniqueness
        if not paths.config_path.exists():
            write_payload_to_path(self.payload, paths.config_path)

        if listings:
            logging.info(
                f"Successfully wrote {len(listings)} listing{'s ' if len(listings) > 1 else ' '}to file: {paths.data_path}."
            )
        else:
            logging.info("No new listings found.")
