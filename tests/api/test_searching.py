from api.listings import Listing
from api.storage import get_listings_from_path, write_listings_to_data_path
import json
import logging
from datetime import UTC, datetime, timedelta
from time import sleep

import pytest

from api import DatetimeRange, ListingSearcher, SearchEndpointPayload
from api.listings import (
    sort_listings,
)
from tests.data.api.payloads import EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS

logger = logging.getLogger(__name__)


@pytest.mark.api
@pytest.mark.parametrize("depth", ["simple", "complex"])
def test_searcher_raises_no_errors(
    load_access_token,
    form_payload_searcher_save_paths,
    depth,
):
    payload, searcher, save_paths = form_payload_searcher_save_paths(depth)

    logging.debug(f"Listing searcher test data path: {save_paths.data_path}")

    access_token = load_access_token()
    searcher.get_latest_listings(access_token)


@pytest.mark.api
def test_excl_kwords(load_access_token, tmp_path):
    access_token = load_access_token()

    excl_kwords_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    excl_kwords_searcher = ListingSearcher(excl_kwords_payload, tmp_path)
    excl_kwords_listings = excl_kwords_searcher.get_latest_listings(access_token)

    excl_kwords = EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS["q"].pop("excl_kwords")
    reg_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    reg_searcher = ListingSearcher(reg_payload, tmp_path)
    reg_listings = reg_searcher.get_latest_listings(access_token)

    reg_listing_titles = [listing.title for listing in reg_listings]

    # eBay is case-insensitive
    # eBay only checks if whole word is found (hence space)
    if all(
        f"{kword} " not in " ".join(reg_listing_titles).lower() for kword in excl_kwords
    ):
        raise ValueError(
            "excl. kwords are not found in regular search, test is ambiguous."
        )

    excl_kwords_listing_titles = [listing.title for listing in excl_kwords_listings]

    if any(
        f"{kword} " in " ".join(excl_kwords_listing_titles).lower()
        for kword in excl_kwords
    ):
        raise ValueError("excl. kword found in listing titles.")


def test_hash_does_not_change_after_searching(
    load_access_token, form_payload_searcher_save_paths
):
    access_token = load_access_token()
    payload, searcher, save_paths = form_payload_searcher_save_paths()

    before_hash = hash(payload)
    resp = searcher.get_latest_listings(access_token)
    after_hash = hash(searcher.payload)

    assert before_hash == after_hash


def test_payload_start_date_respected(load_access_token, get_params, tmp_path):
    access_token = load_access_token()
    start_date_lower = datetime.now(tz=UTC) - timedelta(days=30)
    params = get_params("simple")
    params["filter"] = params.get("filter", {}) | {
        "item_start_date": DatetimeRange(lower_bd=start_date_lower)
    }
    payload = SearchEndpointPayload(**params)
    searcher = ListingSearcher(payload, tmp_path)

    resp = searcher.get_latest_listings(access_token)

    sorted_listings = _sort_listings(resp)

    for listing in sorted_listings:
        assert _get_listing_creation_datetime(listing) >= start_date_lower


@pytest.mark.skip
def test_only_new_listings_retrieved(
    load_access_token, form_payload_searcher_save_paths
):

    access_token = load_access_token()
    payload, searcher, save_paths = form_payload_searcher_save_paths()

    resp = searcher.get_latest_listings(access_token)
    listing_dicts: list[dict] = json.load(
        save_paths.data_path.open(mode="r", encoding="utf-8")
    )

    # slice list from some index like 25% thru
    # get the timestamp there
    # overwrite file with slice
    # modify metadata
    # search again -> assert that the listings in response are not in the file already

    # general plan:
    # from clean files: get latest listings
    # delete some
    # use deleted timestamp to update the metadata to an older time
    # search again -> assert that the listings in response are not in the file already
