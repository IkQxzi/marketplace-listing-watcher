"""Functions common to multiple tests."""

from typing import Literal

from api import ListingSearcher, SearchEndpointPayload, SearchEndpointSavePaths
from config.dirs import TEMP_ACTIVE_DIR

from .api_core_params import (
    SIMPLE_EXAMPLE_PAYLOAD_PARAMS,
    COMPLEX_EXAMPLE_PAYLOAD_PARAMS,
)

type Depth = Literal["simple, complex"]


def form_payload(depth: Depth) -> SearchEndpointPayload:
    if depth == "simple":
        return SearchEndpointPayload(**SIMPLE_EXAMPLE_PAYLOAD_PARAMS)

    return SearchEndpointPayload(**COMPLEX_EXAMPLE_PAYLOAD_PARAMS)


def form_payload_searcher_save_paths(
    depth: Depth,
) -> tuple[SearchEndpointPayload, ListingSearcher, SearchEndpointSavePaths]:

    payload = form_payload(depth)
    searcher = ListingSearcher(payload, TEMP_ACTIVE_DIR)
    save_paths = SearchEndpointSavePaths(
        payload_hash=hash(payload), base_dir=TEMP_ACTIVE_DIR
    )
    return payload, searcher, save_paths
