"""Functionality and base classes for any part of API."""

from pydantic import BaseModel

from dataclasses import dataclass
from typing import Any, Literal, get_args
from datetime import datetime

import re

from utils.misc import snake_to_camel_case


@dataclass
class SearchAPIResponse:
    json_response: Any
    q: str
    inferred_cat_id: int
    inferred_cat_name: str


class SearchAPIConfig(BaseModel):
    """
    Config for Search Endpoint.\n

    Note that bools can only be True or None, not False.\n

    Some params, like 'price' and 'bid_count' require strict formatting rules.
    They follow these rules:\n
    '..' used to separate bounds, examples:\n
    at least 1: '1..'\n
    up to 5: '..5'\n
    1 to 5: '1..5'\n
    """

    # ---------- QUERY ----------
    q: str  # Query (keywords)
    search_in_description: bool | None = None
    epid: int | None = None  # eBay Product ID

    # ---------- PRICE ----------
    # See docstring for formatting rules
    price: str | None = None
    price_currency: str = "GBP"

    # ---------- DATE ----------
    # ISO date format
    item_end_date: str | None = None
    item_start_date: str | None = None

    # ---------- CATEGORY ----------
    category_ids: list[int] | None = None
    exclude_category_ids: list[str] | None = None

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: str | None = None
    buying_options: (
        Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"] | None
    ) = None

    # ---------- CONDITION ----------
    # https://developer.ebay.com/api-docs/sell/static/metadata/condition-id-values.html
    conditions: list[Literal["NEW", "USED", "UNSPECIFIED"]] | None = None
    condition_ids: int | None = None

    # ---------- SELLER ----------
    seller_account_types: Literal["INDIVIDUAL", "BUSINESS"] | None = None

    # ---------- REGION ----------
    # ISO 3166
    delivery_country: str = "GB"
    item_location_country: str = "GB"

    def __post_init__(self):

        # Check both follow strict format

        if self.bid_count:
            self._validate_bounded_param(self.bid_count)

        if self.price:
            self._validate_bounded_param(self.price)

        # Check dates are ISO format
        if self.item_start_date:
            try:
                datetime.fromisoformat(self.item_start_date)
            except ValueError as e:
                raise e

        if self.item_end_date:
            try:
                datetime.fromisoformat(self.item_end_date)
            except ValueError as e:
                raise e

        raise NotImplementedError(
            "Conversion of all param types to str not implemented yet."
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert params to dict format Search Endpoint expects."""

        return {snake_to_camel_case(k): v for k, v in self.__dict__.items() if v}

    def _validate_bounded_param(self, param: str) -> None:
        """
        Check a param (namely price, bid_count) follows strict API format.\n
        Raise error if not.
        """

        param_parts = param.split("..")

        if len(param_parts) >= 3:
            raise ValueError(f"Too many ellipses, invalid: {param}")

        if any(part and not part.isdigit() for part in param_parts):
            raise ValueError(f"Expected up to 2 ints separated by '..', not {param}")

        # Allowing equal bounds for precise price-matching
        if all(param_parts) and int(param_parts[0]) > int(param_parts[1]):
            raise ValueError(
                f"Lower bound cannot be greater than upper bound, invalid: {param}\n"
                f"{param_parts[0]} is not less than {param_parts[1]}"
            )
