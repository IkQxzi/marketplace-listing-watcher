"""Schemas describing API responses."""

from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel, computed_field


@dataclass
class ResponseMetadata:
    href: str
    total: int
    limit: int
    offset: int
    next: int | None


@dataclass
class SearchEndpointResponse:
    item_summaries: dict  # TODO: Document this better
    metadata: ResponseMetadata  # And this
    search_value: str
    inferred_cat_id: int
    inferred_cat_name: str
    _raw_json: Any | None = None
