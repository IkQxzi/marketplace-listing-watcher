"""Functions common to multiple tests."""

import copy
from collections.abc import Callable
from typing import Literal

import pytest

from api import ListingSearcher, SearchEndpointPayload, SearchEndpointSavePaths
from api.auth import get_access_token
from config.api import APP_ID, CERT_ID, REFRESH_TOKEN
from config.dirs import TEMP_ACTIVE_DIR
from tests.data.api.payloads import (
    COMPLEX_EXAMPLE_PAYLOAD_PARAMS,
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
)

Depth = Literal["simple", "complex"]


@pytest.fixture
def get_params() -> Callable[..., dict]:
    def _resolve_params(depth: Depth = "complex", **overrides):
        if depth == "simple":
            return {**copy.deepcopy(SIMPLE_EXAMPLE_PAYLOAD_PARAMS), **overrides}
        elif depth == "complex":
            return {**copy.deepcopy(COMPLEX_EXAMPLE_PAYLOAD_PARAMS), **overrides}
        raise ValueError(f"Unexpected depth: {depth}")

    return _resolve_params


@pytest.fixture
def form_payload(get_params) -> Callable[..., SearchEndpointPayload]:
    def _resolve_payload(depth: Depth = "complex", **overrides):
        return SearchEndpointPayload(**get_params(depth, **overrides))

    return _resolve_payload


@pytest.fixture
def form_payload_searcher_save_paths(
    form_payload,
) -> Callable[
    ..., tuple[SearchEndpointPayload, ListingSearcher, SearchEndpointSavePaths]
]:

    def _resolve_payload_searcher_save_paths(depth: Depth = "complex", **overrides):

        payload = form_payload(depth, **overrides)
        searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)
        save_paths = SearchEndpointSavePaths(
            payload_hash=hash(payload), base_dir=TEMP_ACTIVE_DIR
        )
        return payload, searcher, save_paths

    return _resolve_payload_searcher_save_paths


@pytest.fixture
def load_access_token() -> Callable[..., str]:

    def _resolve_access_token():
        if not (REFRESH_TOKEN and APP_ID and CERT_ID):
            return None
        return get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    return _resolve_access_token
