import csv
import time

from api.auth import get_access_token
from api.core import SearchEndpointSavePaths
from api.params import SearchEndpointPayload
from api.searching import ListingSearcher
from config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from config.dirs import TEMP_ACTIVE_DIR
from tests.api_core_params import (
    EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS,
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
)


def form_payload_searcher_save_paths() -> tuple[
    SearchEndpointPayload, ListingSearcher, SearchEndpointSavePaths
]:

    payload = SearchEndpointPayload(**SIMPLE_EXAMPLE_PAYLOAD_PARAMS)
    searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)
    save_paths = SearchEndpointSavePaths(
        payload_hash=hash(payload), base_dir=TEMP_ACTIVE_DIR
    )
    return payload, searcher, save_paths


def test_searcher_no_files():

    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    payload, searcher, save_paths = form_payload_searcher_save_paths()

    # First test without any pre-existing data
    for path in save_paths.item_dir.iterdir():
        path.unlink(missing_ok=True)
    save_paths.item_dir.rmdir()

    print(f"Listing searcher test data path: {save_paths.data_path}")

    try:
        df = searcher.get_latest_listings(access_token)
    except Exception as e:
        e.add_note("Error occurred during first call to get latest listings.")
        raise

    # To test if repeats work
    for _ in range(2):
        try:
            df = searcher.get_latest_listings(access_token)
        except Exception as e:
            e.add_note("Error occurred during repeat-calls to get latest listings.")
            raise


def test_searcher_with_files():
    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    payload, searcher, save_paths = form_payload_searcher_save_paths()

    # Create mock csv

    for path in save_paths.item_dir.iterdir():
        path.unlink(missing_ok=True)

    # Matches timestamp format from API
    mock_data = [
        ["price", "shipping_price", "currency", "timestamp"],
        ["40.00", "5.00", "GBP", "2026-09-14T17:56:42.000Z"],
    ]
    save_paths.item_dir.mkdir(parents=True, exist_ok=True)
    with save_paths.data_path.open(mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(mock_data)

    searcher.get_latest_listings(access_token)


# TODO: add logging again
def test_excl_kwords():
    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

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
        time.sleep(1)  # For timestamp offset
        raise ValueError("excl. kword found in listing titles.")
