import pytest
from api.core import IntRange, SearchEndpointFilter


from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

# Importing the filter class and its supporting types from your module
from api.core import (
    _api_format_params,
    ConditionName,
    DatetimeRange,
    IntRange,
    SearchEndpointFilter,
    SearchEndpointQuery,
    SearchEndpointPayload,
)

from tests.api_core_params import EXAMPLE_FILTER_PARAMS, EXAMPLE_PAYLOAD_PARAMS

from datetime import datetime


def test_filter_instantiation():
    filter_instance = SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS)


def test_int_range():

    IntRange(lower_bd=1, upper_bd=5)
    IntRange(lower_bd=1)
    IntRange(lower_bd=1)
    with pytest.raises(ValueError):
        IntRange(lower_bd=5, upper_bd=1)


# Manual tests


def _test_filter_parametrisation():
    filter_instance = SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS)

    print(f"\nFilter: {filter_instance.to_param()}\n")


def _test_payload_serialisation():

    payload = SearchEndpointPayload(**EXAMPLE_PAYLOAD_PARAMS)
    print(f"\nPayload: {payload.to_payload()}\n")


if __name__ == "__main__":
    _test_filter_parametrisation()
    _test_payload_serialisation()
