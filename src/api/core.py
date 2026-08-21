"""Functionality and base classes for any part of API."""

from types import MappingProxyType
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


class RangeParam[T: (int, datetime)](SearchEndpointParam):
    """Class for some arbitrary (int or datetime) param in Search Endpoint which requires a range.
    At least one of: lower_bd, upper_bd required (or both)."""

    lower_bd: T | None = None
    upper_bd: T | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> "RangeParam":

        if not (self.lower_bd or self.upper_bd):
            raise ValueError("At least one of min, max required.")

        if self.lower_bd and self.upper_bd and not (self.lower_bd < self.upper_bd):
            raise ValueError(
                f"lower_b must be less than upper_bd.\n min:{self.lower_bd} !< max:{self.upper_bd}."
            )

        return self

    def to_param(self) -> str:
        raise NotImplementedError


class IntRange(RangeParam[int]):
    """Generic class for some range of ints."""

    lower_bd: Annotated[int, Field(ge=0)] | None = None
    upper_bd: Annotated[int, Field(ge=0)] | None = None


class DatetimeRange(RangeParam[datetime]):
    """Generic class for some range of datetimes."""

    pass


type ConditionName = Literal[
    "NEW",
    "NEW_OTHER",
    "NEW_WITH_DEFECTS",
    "CERTIFIED_REFURBISHED",
    "EXCELLENT_REFURBISHED",
    "VERY_GOOD_REFURBISHED",
    "GOOD_REFURBISHED",
    "SELLER_REFURBISHED",
    "LIKE_NEW",
    "USED_EXCELLENT",
    "USED_VERY_GOOD",
    "USED_GOOD",
    "USED_ACCEPTABLE",
    "FOR_PARTS_OR_NOT_WORKING",
]

_CONDITION_ID_MAP: dict[ConditionName, int] = {
    "NEW": 1000,
    "NEW_OTHER": 1500,
    "NEW_WITH_DEFECTS": 1750,
    "CERTIFIED_REFURBISHED": 2000,
    "EXCELLENT_REFURBISHED": 2010,
    "VERY_GOOD_REFURBISHED": 2020,
    "GOOD_REFURBISHED": 2030,
    "SELLER_REFURBISHED": 2500,
    "LIKE_NEW": 2750,
    "USED_EXCELLENT": 3000,
    "USED_VERY_GOOD": 4000,
    "USED_GOOD": 5000,
    "USED_ACCEPTABLE": 6000,
    "FOR_PARTS_OR_NOT_WORKING": 7000,
}


class SearchEndpointFilter(SearchEndpointParam):
    # Some conditions unique to 'apparel' category omitted

    # ---------- QUERY SETTINGS ----------
    search_in_description: Literal[True] | None = None

    # ---------- PRICE ----------
    price: IntRange
    price_currency: str = "GBP"

    # ---------- CONDITION ----------
    conditions: list[Literal["NEW", "USED", "UNSPECIFIED"]] | None = (
        None  # TODO: pipe separate
    )
    # Converted to ConditionIds for API
    precise_conditions: list[ConditionName] | None = None  # TODO: convert to id

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: IntRange | None = None
    buying_options: (
        Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"] | None
    ) = None

    # ---------- DATE ----------
    # TODO: verify dates are ebay format
    item_end_date: DatetimeRange | None = None
    item_start_date: DatetimeRange | None = None

    # ---------- SELLER ----------
    sellers: list[int] | None
    seller_account_types: Literal["INDIVIDUAL", "BUSINESS"] | None = None

    # ---------- REGION ----------
    # TODO: research if item_location_region/country are required
    # ISO 3166
    # item_location_country: str = "GB"
    delivery_country: str = "GB"

    @model_validator(mode="after")
    def validate_params(self) -> "SearchEndpointFilter":

        if self.price and not self.price_currency:
            raise ValueError("price requires price_currency to be specified.")

        if self.conditions and self.precise_conditions:
            raise ValueError("Use only one of: conditions, precise_conditions.")

        # start: between 2 - 3 aug
        # end: between 4-5 aug

        # invalid: start 3-4 aug, end 1-2 aug
        # invalid: start 3..aug, end ..2 aug
        # start: ..5 aug, end

        if (
            self.item_start_date
            and self.item_end_date
            and self.item_start_date.lower_bd
            and self.item_end_date.upper_bd
            and self.item_start_date.lower_bd < self.item_end_date.upper_bd
        ):
            raise ValueError(
                "lower_bd of item_start_date cannot be < upper_bd of item_end_date."
            )

        if self.sellers and len("|".join(str(s) for s in self.sellers)) > 250:
            raise ValueError(
                f"Length of joined sellers list must be < 250. Got {len('|'.join(str(s) for s in self.sellers))}"
            )

        return self

    def to_param(self) -> str:
        raise NotImplementedError


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

    # AND: "kw1 kw2"
    # OR: "(kw1, kw2)"


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
