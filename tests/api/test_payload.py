"""Testing payload from api/params.py"""

import random
import json

from api import SearchEndpointPayload


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
