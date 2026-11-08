import logging
from time import sleep

import pytest

from api import ListingSearcher, SearchEndpointPayload
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

    for path in save_paths.item_dir.iterdir():
        path.unlink(missing_ok=True)
    save_paths.item_dir.rmdir()

    logging.debug(f"Listing searcher test data path: {save_paths.data_path}")

    access_token = load_access_token()
    resp = searcher.get_latest_listings(access_token)


@pytest.mark.api
def test_excl_kwords(load_access_token, form_payload):
    access_token = load_access_token()

    excl_kwords_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    excl_kwords_searcher = ListingSearcher(excl_kwords_payload)
    excl_kwords_response = excl_kwords_searcher._get_listings_after(
        access_token, latest_timestamp=None
    )

    excl_kwords = EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS["q"].pop("excl_kwords")
    reg_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    reg_searcher = ListingSearcher(reg_payload)
    reg_response = reg_searcher._get_listings_after(access_token, latest_timestamp=None)

    reg_listing_titles = [
        listing["title"] for listing in reg_response._raw_json["itemSummaries"]
    ]

    # eBay is case-insensitive
    # eBay only checks if whole word is found (hence space)
    if all(
        f"{kword} " not in " ".join(reg_listing_titles).lower() for kword in excl_kwords
    ):
        raise ValueError(
            "excl. kwords are not found in regular search, test is ambiguous."
        )

    excl_kwords_listing_titles = [
        listing["title"] for listing in excl_kwords_response._raw_json["itemSummaries"]
    ]

    if any(
        f"{kword} " in " ".join(excl_kwords_listing_titles).lower()
        for kword in excl_kwords
    ):
        sleep(1)  # For timestamp offset
        raise ValueError("excl. kword found in listing titles.")
