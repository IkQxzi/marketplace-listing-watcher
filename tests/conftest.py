"""Functions common to multiple tests."""

import copy
from collections.abc import Callable
from typing import Literal

import pytest

from api import ListingSearcher, SearchEndpointPayload, SearchEndpointSavePaths
from api.auth import get_access_token
from config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from tests.data.api.payloads import (
    COMPLEX_EXAMPLE_PAYLOAD_PARAMS,
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
)

Depth = Literal["simple", "complex"]


@pytest.fixture
def get_params() -> Callable[..., dict]:
    def _resolve_params(depth: Depth = "complex"):
        if depth == "simple":
            return copy.deepcopy(SIMPLE_EXAMPLE_PAYLOAD_PARAMS)
        elif depth == "complex":
            return copy.deepcopy(COMPLEX_EXAMPLE_PAYLOAD_PARAMS)
        else:
            raise ValueError(f"Unexpected depth: {depth}")

    return _resolve_params


@pytest.fixture
def form_payload(get_params) -> Callable[..., SearchEndpointPayload]:
    def _resolve_payload(depth: Depth = "complex"):
        return SearchEndpointPayload(**get_params(depth))

    return _resolve_payload


@pytest.fixture
def form_payload_searcher_save_paths(
    form_payload, tmp_path
) -> Callable[
    ..., tuple[SearchEndpointPayload, ListingSearcher, SearchEndpointSavePaths]
]:

    def _resolve_payload_searcher_save_paths(depth: Depth = "complex"):

        payload = form_payload(depth)
        searcher = ListingSearcher(payload, tmp_path)
        save_paths = searcher.save_paths
        return payload, searcher, save_paths

    return _resolve_payload_searcher_save_paths


@pytest.fixture
def load_access_token() -> Callable[..., str]:

    def _resolve_access_token():
        if not (REFRESH_TOKEN and APP_ID and CERT_ID):
            return None
        return get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    return _resolve_access_token
