"""Testing payload from api/params.py"""

import random
import pytest
from datetime import UTC, datetime, timedelta

import yaml

from marketplace_listing_watcher.api import SearchEndpointPayload
from marketplace_listing_watcher.config.dirs import FILTER_DIR


def test_identical_payloads_match_hashes(form_payload):

    payload = form_payload()
    payload_copy = form_payload()

    assert hash(payload) == hash(payload_copy)


def test_different_list_orders_match_hashes(get_params, form_payload):

    params = get_params()

    # Try to keep comprehensive
    params["q"]["kwords"] = params["q"]["kwords"][::-1]
    params["q"]["excl_kwords"] = params["q"]["excl_kwords"][::-1]
    params["filter"]["conditions"] = params["filter"]["conditions"][::-1]
    params["filter"]["buying_options"] = params["filter"]["buying_options"][::-1]

    payload = form_payload()
    reversed_payload = SearchEndpointPayload(**params)

    assert hash(payload) == hash(reversed_payload)


def test_random_casing_match_hashes(get_params, form_payload):

    def _randomise_case(l: list[str]) -> list[str]:
        return [
            "".join([c.upper() if random.choice((0, 1)) else c for c in s]) for s in l
        ]

    params = get_params()
    params["q"]["kwords"] = _randomise_case(params["q"]["kwords"])
    params["q"]["excl_kwords"] = _randomise_case(params["q"]["excl_kwords"])

    payload = form_payload()
    randomised_payload = SearchEndpointPayload(**params)

    assert hash(randomised_payload) == hash(payload)


def test_simple_yaml_loading():
    regular_yml_path = FILTER_DIR / "regular_example.yml"
    minimal_yml_path = FILTER_DIR / "minimal_example.yml"
    regular_yml = yaml.safe_load((regular_yml_path).open("r"))
    minimal_yml = yaml.safe_load((minimal_yml_path).open("r"))

    ref_datetime = datetime(day=19, month=11, year=2026, tzinfo=UTC)

    # Check that all things loaded into payload correctly
    reg_payload = SearchEndpointPayload.load_simple_yaml(regular_yml_path)
    assert reg_payload.q.kwords == regular_yml["query"]["include"]
    assert reg_payload.q.excl_kwords == regular_yml["query"]["exclude"]
    assert reg_payload.filter.price.lower_bd == regular_yml["price"]["lower_bound"]
    assert reg_payload.filter.price.upper_bd == regular_yml["price"]["upper_bound"]
    assert all(s in reg_payload.filter.conditions for s in ["NEW", "USED"])
    assert reg_payload.filter.item_start_date.lower_bd == ref_datetime
    assert all(
        s in reg_payload.filter.buying_options
        for s in ["AUCTION", "BEST_OFFER", "FIXED_PRICE"]
    )

    # Subtract a few s to eliminate accuracy error
    cur_ref_datetime = datetime.now().astimezone(tz=UTC) - timedelta(seconds=5)
    minimal_payload = SearchEndpointPayload.load_simple_yaml(minimal_yml_path)
    assert all(s in minimal_payload.q.kwords for s in minimal_yml["query"]["include"])
    assert not minimal_payload.q.excl_kwords
    assert minimal_payload.filter.price.lower_bd == minimal_yml["price"]["lower_bound"]
    assert minimal_payload.filter.price.upper_bd == minimal_yml["price"]["upper_bound"]
    assert not minimal_payload.filter.conditions

    # Default behaviour without item start date is to fetch only new listings
    assert minimal_payload.filter.item_start_date.lower_bd > cur_ref_datetime
    assert not minimal_payload.filter.buying_options


@pytest.mark.skip
def test_payload_serialisation(form_payload):
    payload: SearchEndpointPayload = form_payload()

    print(payload.model_dump_json())
