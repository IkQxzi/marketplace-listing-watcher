import pytest

from api.core import SearchEndpointPayload
from api.searcher import ListingSearcher, log_response
from api.auth import get_access_token
from config.api import REFRESH_TOKEN, APP_ID, CERT_ID
from config.dirs import TEMP_ACTIVE_DIR

import time
from tests.api_core_params import (
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
    COMPLEX_EXAMPLE_PAYLOAD_PARAMS,
    EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS,
)


def test_listing_searcher():
    payload = SearchEndpointPayload(**SIMPLE_EXAMPLE_PAYLOAD_PARAMS)
    searcher = ListingSearcher()

    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)
    response = searcher.get_listings(access_token, payload)

    log_response(response, TEMP_ACTIVE_DIR)


def test_excl_kwords():
    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    searcher = ListingSearcher()
    excl_kwords_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    excl_kwords_response = searcher.get_listings(access_token, excl_kwords_payload)

    excl_kwords = EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS["q"].pop("excl_kwords")
    regular_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    reg_response = searcher.get_listings(access_token, regular_payload)

    reg_listing_titles = [
        listing["title"] for listing in reg_response.json_response["itemSummaries"]
    ]

    # eBay is case-insensitive
    # eBay only checks if whole word is found (hence space)
    if all(
        f"{kword} " not in " ".join(reg_listing_titles).lower() for kword in excl_kwords
    ):
        log_response(reg_response, TEMP_ACTIVE_DIR)
        raise ValueError(
            "excl. kwords are not found in regular search, test is ambiguous."
        )

    excl_kwords_listing_titles = [
        listing["title"]
        for listing in excl_kwords_response.json_response["itemSummaries"]
    ]

    if any(
        f"{kword} " in " ".join(excl_kwords_listing_titles).lower()
        for kword in excl_kwords
    ):
        log_response(reg_response, TEMP_ACTIVE_DIR)
        time.sleep(1)  # For timestamp offset
        log_response(excl_kwords_response, TEMP_ACTIVE_DIR)
        raise ValueError("excl. kword found in listing titles.")

    log_response(reg_response, TEMP_ACTIVE_DIR)
    time.sleep(1)  # For timestamp offset
    log_response(excl_kwords_response, TEMP_ACTIVE_DIR)
