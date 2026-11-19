"""Testing payload from api/params.py"""

from datetime import datetime

import random

import yaml

from api import SearchEndpointPayload
from config.dirs import FILTER_DIR


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
    regular_yml = yaml.safe_load((FILTER_DIR / "regular_example.yml").open("r"))
    minimal_yml = yaml.safe_load((FILTER_DIR / "minimal_example.yml").open("r"))

    reg_payload = SearchEndpointPayload.load_simple_yaml(regular_yml)
    assert reg_payload.q.kwords == regular_yml["query"]["include"]
    assert reg_payload.q.excl_kwords == regular_yml["query"]["exclude"]
    assert reg_payload.filter.price.lower_bd == regular_yml["price"]["lower_bound"]
    assert reg_payload.filter.price.upper_bd == regular_yml["price"]["upper_bound"]
    assert all(s in reg_payload.filter.conditions for s in ["NEW", "USED"])
    assert reg_payload.filter.item_start_date.lower_bd == datetime(
        day=19, month=11, year=2026
    )
    assert all(
        s in reg_payload.filter.buying_options
        for s in ["AUCTION", "BEST_OFFER", "FIXED_PRICE"]
    )

    minimal_payload = SearchEndpointPayload.load_simple_yaml(minimal_yml)
    assert all(s in minimal_payload.q.kwords for s in regular_yml["query"]["include"])
    assert not minimal_payload.q.excl_kwords
    assert minimal_payload.filter.price.lower_bd == regular_yml["price"]["lower_bound"]
    assert minimal_payload.filter.price.upper_bd == regular_yml["price"]["upper_bound"]
    assert not minimal_payload.filter.conditions
    assert minimal_payload.filter.item_start_date.lower_bd == datetime(
        day=19, month=11, year=2026
    )
    assert not minimal_payload.filter.buying_options
