import json
import pytest

# Importing the filter class and its supporting types from your module
from api.core import (
    IntRange,
    SearchEndpointFilter,
    SearchEndpointQuery,
    SearchEndpointPayload,
)

from tests.api_core_params import (
    EXAMPLE_FILTER_PARAMS,
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
    COMPLEX_EXAMPLE_PAYLOAD_PARAMS,
    EXAMPLE_QUERY_PARAMS,
)


def test_filter_instantiation():
    filter_instance = SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS)


def test_int_range():

    IntRange(lower_bd=1, upper_bd=5)
    IntRange(lower_bd=1)
    IntRange(upper_bd=1)
    with pytest.raises(ValueError):
        IntRange(lower_bd=5, upper_bd=1)


def test_query_serialisation():
    query = SearchEndpointQuery(**EXAMPLE_QUERY_PARAMS)
    print(f"\nQuery: '{query.model_dump()}'\n")


def test_filter_serialisation():
    filter_instance = SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS)
    print(f"\nFilter: {filter_instance.model_dump()}\n")


def test_payload_serialisation():

    payload = SearchEndpointPayload(**SIMPLE_EXAMPLE_PAYLOAD_PARAMS)
    print(f"\nPayload: {payload.model_dump(exclude_none=True)}\n")


def test_payload_hashing():
    payload = SearchEndpointPayload(**COMPLEX_EXAMPLE_PAYLOAD_PARAMS)
    base_hash = hash(payload)

    payload_copy = SearchEndpointPayload(**COMPLEX_EXAMPLE_PAYLOAD_PARAMS.copy())
    assert hash(payload_copy) == base_hash, "Copied params do not result in same hash."

    mixed_payload_params = COMPLEX_EXAMPLE_PAYLOAD_PARAMS.copy()
    mixed_payload_params["q"]["kwords"] = reversed(
        COMPLEX_EXAMPLE_PAYLOAD_PARAMS["q"]["kwords"]
    )
    mixed_payload_params["q"]["excl_kwords"] = reversed(
        COMPLEX_EXAMPLE_PAYLOAD_PARAMS["q"]["excl_kwords"]
    )
    mixed_payload_params["filter"]["conditions"] = reversed(
        COMPLEX_EXAMPLE_PAYLOAD_PARAMS["filter"]["conditions"]
    )
    mixed_payload_params["filter"]["buying_options"] = reversed(
        COMPLEX_EXAMPLE_PAYLOAD_PARAMS["filter"]["buying_options"]
    )

    mixed_payload = SearchEndpointPayload(**mixed_payload_params)

    assert hash(mixed_payload) == hash(payload), (
        "Different ordered lists do not result in same hash."
        f"\nBase payload _hashable_model_dump: \n{json.dumps(payload._hashable_model_dump, indent=2)}\n"
        f"\nMixed payload _hashable_model_dump: \n{json.dumps(mixed_payload._hashable_model_dump, indent=2)}"
    )


if __name__ == "__main__":
    test_filter_serialisation()
    test_payload_serialisation()
