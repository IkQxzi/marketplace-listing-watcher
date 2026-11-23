import logging
from datetime import UTC, datetime, timedelta

import pytest

from marketplace_listing_watcher.api import DatetimeRange, ListingSearcher, SearchEndpointPayload
from marketplace_listing_watcher.api.storage import read_listings_from_path, write_listings_to_data_path
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
    searcher.get_latest_listings_and_alert(access_token)


@pytest.mark.api
def test_excl_kwords(load_access_token, tmp_path):
    access_token = load_access_token()

    excl_kwords_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    excl_kwords_searcher = ListingSearcher(excl_kwords_payload, tmp_path)
    excl_kwords_listings = excl_kwords_searcher.get_latest_listings_and_alert(
        access_token
    )

    excl_kwords = EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS["q"].pop("excl_kwords")
    reg_payload = SearchEndpointPayload(**EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS)
    reg_searcher = ListingSearcher(reg_payload, tmp_path)
    reg_listings = reg_searcher.get_latest_listings_and_alert(access_token)

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


@pytest.mark.api
@pytest.mark.parametrize("depth", ["complex"])
def test_hash_does_not_change_after_repeat_search(
    load_access_token, form_payload_searcher_save_paths, depth
):
    access_token = load_access_token()
    payload, searcher, save_paths = form_payload_searcher_save_paths(depth)

    before_hash = hash(payload)
    before_dump = payload.model_dump()
    searcher.get_latest_listings_and_alert(access_token)
    after_hash = hash(searcher.payload)

    assert before_hash == after_hash, "Hash did not match after singular search"

    searcher.get_latest_listings_and_alert(access_token)
    assert before_hash == hash(searcher.payload), (
        "Hash did not match after repeat search."
    )


@pytest.mark.api
def test_payload_start_date_respected(load_access_token, get_params, tmp_path):
    access_token = load_access_token()
    start_date_lower = datetime.now(tz=UTC) - timedelta(days=30)
    params = get_params("simple")
    params["filter"] = params.get("filter", {}) | {
        "item_start_date": DatetimeRange(lower_bd=start_date_lower)
    }
    payload = SearchEndpointPayload(**params)
    searcher = ListingSearcher(payload, tmp_path)

    listings = searcher.get_latest_listings_and_alert(access_token)

    for listing in listings:
        assert listing.item_origin_date >= start_date_lower


@pytest.mark.parametrize("depth", ["simple", "complex"])
@pytest.mark.api
def test_only_new_listings_retrieved(
    load_access_token, form_payload_searcher_save_paths, depth
):

    access_token = load_access_token()
    payload, searcher, save_paths = form_payload_searcher_save_paths(depth)

    listings = searcher.get_latest_listings_and_alert(access_token)  # Oldest first

    # Index of the 75th percentile listing
    # So only 25% of listings are newer
    reference_listing_ind = 3 * (len(listings) // 4)
    reference_listing_timestamp = listings[reference_listing_ind].item_origin_date

    # Overwrite listings so newest 25% of listings are missing
    # Retain reference listing in file
    write_listings_to_data_path(
        listings[: reference_listing_ind + 1], save_paths.data_path, append=False
    )

    new_listings = searcher.get_latest_listings_and_alert(access_token)

    # Should be ONLY new listings (hence strict)
    are_listings_new = [
        listing.item_origin_date > reference_listing_timestamp
        for listing in new_listings
    ]

    if (
        are_listings_new.count(True) == 1
        and new_listings[are_listings_new.index(True)].item_origin_date
        == reference_listing_timestamp
    ):
        raise ValueError("Reference listing in new listings.")

    assert all(are_listings_new), "Stale listings in 'new listings'"

    written_listings = read_listings_from_path(save_paths.data_path)

    # Older listings should not be affected
    assert written_listings[0].item_origin_date == listings[0].item_origin_date, (
        "Oldest listing was overwritten!"
    )

    # Listings written to file must also be in oldest-first order
    # Note non-strict because sellers may list multiple items simultaneously
    written_listings_sorted = [
        written_listings[i].item_origin_date <= written_listings[i + 1].item_origin_date
        for i in range(len(written_listings) - 1)
    ]
    assert all(written_listings_sorted)
