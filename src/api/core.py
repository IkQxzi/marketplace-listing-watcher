"""Functionality and base classes for any part of API."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated, Any, Literal, Self
from collections.abc import Mapping
from abc import ABC, abstractmethod

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    model_serializer,
    field_validator,
    ConfigDict,
    AliasGenerator,
)
from pydantic.alias_generators import to_camel

from utils.misc import snake_to_camel_case


@dataclass
class SearchEndpointResponse:
    json_response: Any
    q: SearchEndpointQuery
    inferred_cat_id: int
    inferred_cat_name: str


type _Singular = str | int | float | bool


def _join_list(items: list[str] | list[int | float]) -> str:
    """
    Join a list (of uniform type) according to Search Endpoint format:
    list[str]: pipe separated, wrapped in curly braces.
    list[int]: comma separated
    with pipes and wrap it in curly braces.
    """

    if any(type(s) is not type(items[0]) for s in items):
        raise ValueError(f"Elements in list are not a uniform type!\nlist:{items}")

    if type(items[0]) is str:
        return "{" + "|".join(s for s in items) + "}"  # type: ignore

    if type(items[0]) in [int, float]:
        return ",".join(str(s) for s in items)

    raise ValueError(
        f"List contains unsupported type. Encountered type: {type(items[0])} {type(items[0]) is int}"
    )


# Generic type to know when joining is not required
# TODO: use in _comma_join_dict()
# not useful bc strs need to be curly wrapped but not ints,
# going to leave here jic
type _Singular_ = str | int | float | bool


def _join_dict_with_char(dct: dict, char: str = "&") -> str:
    """Join a dict with colons between keys & values, and specified char between entries."""

    formatted = {}

    for k, v in dct.items():
        if isinstance(v, list):
            formatted[k] = _join_list(v)
        elif isinstance(v, bool):
            formatted[k] = str(v).lower()  # API expects 'true', not 'True'
        else:
            formatted[k] = str(v)

    return char.join(f"{k}:{v}" for k, v in formatted.items())


# TODO: Why note use __dict__?
def _api_format_params(
    instance: object, dict_join_char: str = "&", return_dict: bool = False
) -> str | dict[str, str]:
    """Format the attributes of an instance into 1 string."""

    if dict_join_char != "&" and return_dict:
        raise ValueError(
            "Tried to join dict with a char but also specified to return dict instead of str."
        )

    api_dict: dict[str, str] = {}

    # Attr names or aliases
    attr_dict = instance.__dict__

    # If instance is a param obj,
    # use aliases instead of internal attr names
    if isinstance(instance, SearchEndpointParam):
        for key in attr_dict.copy():
            alias = instance.__class__.model_fields[key].serialization_alias
            if alias:
                attr_dict[alias] = attr_dict.pop(key)

    for attr, val in attr_dict.items():
        if not val:  # Can omit None items in API
            continue

        if isinstance(val, SearchEndpointParam):
            # Can't use recursion because SearchEndointQuery has special list joining rules
            api_dict[attr] = val.to_param()

        elif isinstance(val, list):
            api_dict[attr] = _join_list(val)

        elif isinstance(val, dict):
            api_dict[attr] = _join_dict_with_char(val)

        elif isinstance(val, bool):
            api_dict[attr] = str(val).lower()  # API expects 'true', not 'True'

        elif isinstance(val, str | int | float):
            api_dict[attr] = str(val)

        else:
            raise NotImplementedError(f"Unexpected type {type(val)}: {attr}: {val}")

    if return_dict:
        return api_dict

    return _join_dict_with_char(api_dict, dict_join_char)


class SearchEndpointParam(ABC, BaseModel):
    @abstractmethod
    def to_param(self) -> str:
        """Convert class to param format Search Endpoint expects."""
        _api_format_params(self)


def _range_to_str(lower_bd: str | int | None, upper_bd: str | int | None) -> str:
    """Convert a range to a str with optional vals."""

    l = lower_bd if lower_bd is not None else ""
    u = upper_bd if lower_bd is not None else ""

    return f"{l}..{u}"


# TODO: handle non-BST
def format_datetime(v: datetime | None) -> str | None:
    """
    Format datetime objects to format API expects.
    Assumes that datetime is specified in UK BST, converts to UTC.
    """

    if v:
        v = v - timedelta(hours=1)  # Convert to UTC
        return f"{v.isoformat()}Z"

    return v


class RangeParam[T: (int, datetime)](BaseModel):
    lower_bd: T | None = None
    upper_bd: T | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if self.lower_bd is None and self.upper_bd is None:
            raise ValueError("At least one bound must be specified.")

        if (
            self.lower_bd is not None
            and self.upper_bd is not None
            and self.lower_bd >= self.upper_bd
        ):
            raise ValueError("Lower bound must be less than upper bound.")

        return self


class IntRange(RangeParam[int]):
    @field_validator("lower_bd", "upper_bd")
    @classmethod
    def check_gt_zero(cls, v: int) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Bounds must be greater than 0.")

        return v

    @model_serializer
    def serialize(self) -> str:
        return _range_to_str(self.lower_bd, self.upper_bd)


class DatetimeRange(RangeParam[datetime]):
    # Maybe check that the date is not before today,
    # if API does not support that.

    @model_serializer
    def serialize(self) -> str:
        return _range_to_str(
            format_datetime(self.lower_bd), format_datetime(self.upper_bd)
        )


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
    """
    Filters which are used by SearchEndpointPayload.\n
    Some conditions unique to the 'apparel' category have been omitted.
    """

    # TODO: check that I can still instantiate by name and not by alias
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        serialize_by_alias=True,
    )

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
    precise_conditions: Annotated[
        list[ConditionName] | None, Field(serialization_alias="ConditionIds")
    ] = None  # TODO: convert to id

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: IntRange | None = None
    buying_options: (
        list[Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"]] | None
    ) = None

    # ---------- DATE ----------
    # TODO: verify dates are ebay format
    item_end_date: DatetimeRange | None = None
    item_start_date: DatetimeRange | None = None

    # ---------- SELLER ----------
    sellers: list[str] | None
    seller_account_types: list[Literal["INDIVIDUAL", "BUSINESS"]] | None = None

    # ---------- REGION ----------
    # TODO: research if item_location_region/country are required
    # ISO 3166
    # item_location_country: str = "GB"
    delivery_country: str = "GB"

    # TODO: Validate that price is not fixed with bid count
    @model_validator(mode="after")
    def validate_params(self) -> "SearchEndpointFilter":

        if self.precise_conditions:
            raise NotImplementedError(
                "Conversion of precise_conditions to ConditionIds not implemented."
            )

        if self.item_start_date or self.item_end_date:
            raise NotImplementedError(
                "Item start & end dates are not implemented properly."
            )

        if self.price and not self.price_currency:
            raise ValueError("price requires price_currency to be specified.")

        if self.conditions and self.precise_conditions:
            raise ValueError("Use only one of: conditions, precise_conditions.")

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

        return _api_format_params(self, dict_join_char=",")


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
        if self.join_method == "AND":
            return " ".join(self.q)

        if self.join_method == "OR":
            return (
                "(" + ", ".join(self.q) + ")"
            )  # Has a space as well as comma in docs for some reason

        raise ValueError()


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
    # Search Endpoint requires this to be wrapped in square brackets for ragebait reasons
    auto_correct: Literal["KEYWORD"] | None = None
    category_ids: list[int] | None = None
    epid: int | None = None  # eBay Product ID
    gtin: int | None = None  # UPC, EAN, ISBN
    limit: Annotated[int, Field(ge=1, le=200)] = 50
    offset: int = 0

    # TODO: link to thing
    fieldgroups: Literal[
        "ASPECT_REFINEMENTS",
        "CATEGORY_REFINEMENTS",
        "CONDITION_REFINEMENTS",
        "EXTENDED",
        "MATCHING_ITEMS",
        "FULL",
    ] = "MATCHING_ITEMS"  # Maybe set to None
    filter: SearchEndpointFilter | None = None

    # Maybe offset, limit will have an issue
    # See: https://developer.ebay.com/develop/api/buy/browse_api#buy-browse_api-item_summary-search:~:text=of%20items%20returned.-,Note,-%3A%20The%20value
    @model_validator(mode="after")
    def check_params(self) -> "SearchEndpointPayload":

        if self.q and (self.epid or self.gtin):
            raise ValueError("When q is specified, epid and gtin cannot be used.")

        if self.aspect_filter and (
            not self.category_ids
            or self.category_ids != self.aspect_filter.get("category_id")
        ):
            raise ValueError(
                "If aspect filter specififed, category ID must be specified in both aspect filter and base payload class."
            )

        return self

    def to_payload(self) -> dict:
        return _api_format_params(self, return_dict=True)


if __name__ == "__main__":
    some_int_rg = IntRange(lower_bd=1, upper_bd=5)
    assert isinstance(some_int_rg, SearchEndpointParam)
