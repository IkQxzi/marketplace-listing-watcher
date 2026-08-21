"""Functionality and base classes for any part of API."""

from pydantic import BaseModel
"""Functionality and base classes for any part of API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Literal
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, model_validator, field_validator

from utils.misc import snake_to_camel_case



@dataclass
class SearchEndpointResponse:
    json_response: Any
    q: str
    inferred_cat_id: int
    inferred_cat_name: str


class SearchEndpointParam(ABC, BaseModel):
    @abstractmethod
    def to_param(self) -> str:
        """Convert class to param format Search Endpoint expects."""
        ...


class IntRange(SearchEndpointParam):
    """
    Class for some param in Search Endpoint which requires a range.
    At least one of: min, max required (or both).
    """

    min: Annotated[int | None, Field(ge=0)] = None
    max: Annotated[int | None, Field(ge=0)] = None

    @model_validator(mode="after")
    def validate_bounds(self) -> "IntRange":
        if not (self.min or self.max):
            raise ValueError("At least one of min, max required.")

        if self.min and self.max and not (self.min < self.max):
            raise ValueError(f"Min must be less than max.\n min:{min} !< max:{max}.")

        return self

    def to_param(self) -> str:
        "Returns format: [min..max]"

        param_str = ".."

        if self.min:
            param_str = f"{self.min}{param_str}"

        if self.max:
            param_str = f"{param_str}{self.max}"

        return f"[{param_str}]"


class SearchEndpointFilter(SearchEndpointParam):
    # ---------- QUERY SETTINGS ----------
    search_in_description: Literal[True] | None = None

    # ---------- PRICE ----------
    price: IntRange  # TODO: requires price_currency
    price_currency: str = "GBP"

    # ---------- CONDITION ----------
    # https://developer.ebay.com/api-docs/sell/static/metadata/condition-id-values.html
    conditions: list[Literal["NEW", "USjED", "UNSPECIFIED"]] | None = None
    condition_ids: int | None = None  # TODO: implement some dict to translate these

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: IntRange | None = None
    buying_options: (
        Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"] | None
    ) = None

    # ---------- DATE ----------
    item_end_date: datetime | None = None
    item_start_date: datetime | None = None

    # ---------- SELLER ----------
    sellers: list[int] | None  # TODO: len < 250
    seller_account_types: Literal["INDIVIDUAL", "BUSINESS"] | None = None

    # ---------- REGION ----------
    # TODO: research if item_location_region/country are required
    # ISO 3166
    # item_location_country: str = "GB"
    delivery_country: str = "GB"


class SearchEndpointQuery(SearchEndpointParam):
    q: list[str]
    join_method: Literal["AND", "OR"]

    @field_validator("q")
    @classmethod
    def validate_query(cls, v: list[str]) -> list[str]:
        if len(" ".join(v)) > 100:
            raise ValueError("Combined length of query + spaces must be <=100.")

        return v

    def to_param(self) -> str:
        raise NotImplementedError

    # Ensure len(q) <= 100
    # AND: "kw1 kw2"
    # OR: "(kw1, kw2)"


class SearchAPIConfig(BaseModel):
    """
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
    """

    # ---------- QUERY ----------
    q: str  # Query (keywords)
    search_in_description: bool | None = None
    epid: int | None = None  # eBay Product ID
    q: str  # Query (keywords)
    category_ids: list[int] | None = None
    epid: int | None = None  # eBay Product ID

    # ---------- FILTER ----------
    search_in_description: Literal[True] | None = None

    # ---------- PRICE ----------
    # See docstring for formatting rules
    price: str | None = None
    price_currency: str = "GBP"
    price_currency: str = "GBP"

    # ---------- DATE ----------
    # ISO date format
    item_end_date: str | None = None
    item_start_date: str | None = None

    # ---------- CATEGORY ----------
    exclude_category_ids: list[str] | None = None

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: str | None = None
    buying_options: (
        Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"] | None
    ) = None
    buying_options: (
        Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"] | None
    ) = None

    # ---------- CONDITION ----------
    # https://developer.ebay.com/api-docs/sell/static/metadata/condition-id-values.html
    conditions: list[Literal["NEW", "USED", "UNSPECIFIED"]] | None = None
    conditions: list[Literal["NEW", "USED", "UNSPECIFIED"]] | None = None
    condition_ids: int | None = None

    # ---------- SELLER ----------
    seller_account_types: Literal["INDIVIDUAL", "BUSINESS"] | None = None

    # ---------- REGION ----------k
    # ISO 3166
    delivery_country: str = "GB"
    item_location_country: str = "GB"
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
        raise NotImplementedError(
            "Conversion of all param types to str not implemented yet."
        )

    def to_api_format(self) -> dict[str, str | int | bool]:
        """Convert params to dict and make their format clean."""

    def to_dict(self) -> dict[str, Any]:
        """Convert params to dict format Search Endpoint expects."""
        param_dict = self._to_dict()

        return {snake_to_camel_case(k): v for k, v in self.__dict__.items() if v}
        # Join lists with pipe
        return {
            k: "|".join(v) if isinstance(v, list) else v for k, v in param_dict.items()
        }

    def _to_dict(self) -> dict[str, Any]:
        """Convert params to dict format Search Endpoint expects."""

        return {snake_to_camel_case(k): v for k, v in self.__dict__.items() if v}

    def _validate_bounded_param(self, param: str) -> None:
        """
        """
        Check a param (namely price, bid_count) follows strict API format.\n
        Raise error if not.
        """
        """

        param_parts = param.split("..")
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

            raise ValueError(
                f"Lower bound cannot be greater than upper bound, invalid: {param}\n"
                f"{param_parts[0]} is not less than {param_parts[1]}"
            )


class SearchEndpointPayload(BaseModel):
    """
    All params for the Search Endpoint of the Browse API.
    """

    # epid and q are exclusive

    q: SearchEndpointQuery

    # Match any aspects of the items that are specific to that item
    # TODO: eg ...
    # Get by ...
    aspect_filter: dict[str, str | int] | None = None
    auto_correct: Literal["Keyword"] | None = None
    category_ids: list[int] | None = None
    epid: int | None = None  # eBay Product ID
    gtin: int | None = None  # UPC, EAN, ISBN
    limit: Annotated[int, Field(ge=1, le=200)] = 50
    offset: int = 0  # Must be a perfect divisor of limit
    # TODO: validate perfect divisor

    # TODO: link to thing
    fieldgroups: Literal[
        "ASPECT_REFINEMENTS",
        "CATEGORY_REFINEMENTS",
        "CONDITION_REFINEMENTS",
        "EXTENDED",
        "MATCHING_ITEMS",
        "FULL",
    ] = "MATCHING_ITEMS"
    filter: SearchEndpointFilter | None = None
