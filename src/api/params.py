"""Parameter classes for use with the Search Endpoint."""

from __future__ import annotations

import hashlib
import urllib.parse
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self

from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    SerializerFunctionWrapHandler,
    computed_field,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.alias_generators import to_camel

from .constants import _CONDITION_ID_MAP, ConditionName

# ---------------------------- Helper Functions ----------------------------


def _pipe_join_curly_wrap_sorted(v: list[str]) -> str:
    "Join list with pipes and wrap in curly braces after sorting."
    return "{" + "|".join(sorted(v)) + "}"


def _comma_colon_join_dict(d: dict[str, Any]):
    return ",".join(f"{k}:{v}" for k, v in d.items() if v is not None)


# ---------------------------- Payload ----------------------------


# May not need serialization logic due to way params are handled by requests.get() automatically
class SearchEndpointPayload(BaseModel):
    """
    All params for the Search Endpoint of the Browse API.
    When epid or gtin are used, q must be empty.
    epid and gtin can be used together.
    If aspect filter specififed, category ID must be specified in both aspect filter and payload.
    """

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, defer_build=True
    )

    filter: SearchEndpointFilter

    # epid and q are exclusive
    q: SearchEndpointQuery | None = None

    # Match any aspects of the items that are specific to that item
    # TODO: eg ...
    # Get by ...
    aspect_filter: (
        Annotated[
            dict[str, PipeSepStrList | CommaSepNumList],
            PlainSerializer(_comma_colon_join_dict),
        ]
        | None
    ) = None
    # Search Endpoint requires this to be wrapped in square brackets for ragebait reasons
    auto_correct: Literal["KEYWORD"] | None = None
    category_ids: (
        Annotated[
            list[int],
            PlainSerializer(
                lambda v: ",".join(str(x) for x in sorted(v)), return_type=str
            ),
        ]
        | None
    ) = None
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

    @computed_field
    @property
    def search_value(self) -> str:
        v = ""
        if self.q:
            v += self.q.model_dump()

        if self.epid:
            v += str(self.epid)

        if self.gtin:
            v += str(self.gtin)

        return v

    @field_validator("category_ids")
    @classmethod
    def ensure_one_category(cls, v: list[int] | None) -> list[int] | None:
        if v and len(v) > 1:
            raise ValueError("API expects max. one category.")

    def __hash__(self) -> int:
        """
        Generate a hash for the instance.
        Does not sort lists, assumes that any BaseModel params have handled sorting themselves.
        """

        url = urllib.parse.urlencode(self.model_dump())
        return int.from_bytes(hashlib.md5(url.encode()).digest())

    # Maybe offset, limit will have an issue
    # See: https://developer.ebay.com/develop/api/buy/browse_api#buy-browse_api-item_summary-search:~:text=of%20items%20returned.-,Note,-%3A%20The%20value
    @model_validator(mode="after")
    def check_params(self) -> Self:

        if not (self.q or self.epid or self.gtin):
            raise ValueError("One of: q, epid, gtin must be specified.")

        # But epid, gtin can be used together
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


# ---------------------------- Generic Types ----------------------------

PipeSepStrList = Annotated[
    list[str],
    PlainSerializer(_pipe_join_curly_wrap_sorted, return_type=str),
]

CommaSepNumList = Annotated[
    list[int | float], PlainSerializer(lambda v: ",".join(sorted(v)), return_type=str)
]

# API expects 'true', not 'True'
LowercaseBool = Annotated[Literal[True], PlainSerializer(lambda v: str(v).lower())]

LowercaseList = Annotated[
    list[str],
    PlainSerializer(lambda v: sorted([s.lower() for s in v]), return_type=list),
]


# ---------------------------- Base Classes ----------------------------


class SearchPayloadParam(BaseModel, ABC):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @abstractmethod
    def serialize(self) -> str: ...

    if TYPE_CHECKING:

        def model_dump(self, *args: Any, **kwargs: Any) -> str:  # type: ignore[override]
            return ""


class _RangeParam[T: (int, datetime)](BaseModel):
    lower_bd: T | None = None
    upper_bd: T | None = None

    def _range_to_str(
        self, lower_bd: str | int | None, upper_bd: str | int | None
    ) -> str:
        """Convert a bound range to a str."""

        l = lower_bd if lower_bd is not None else ""
        u = upper_bd if upper_bd is not None else ""

        return f"[{l}..{u}]"

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


# ---------------------------- Param Classes ----------------------------


class IntRange(_RangeParam[int], SearchPayloadParam):
    @field_validator("lower_bd", "upper_bd")
    @classmethod
    def check_gt_zero(cls, v: int) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Bounds must be greater than 0.")

        return v

    @model_serializer
    def serialize(self) -> str:
        return super()._range_to_str(self.lower_bd, self.upper_bd)


class DatetimeRange(_RangeParam[datetime], SearchPayloadParam):
    # Maybe check that the date is not before today,
    # if API does not support that.

    # TODO: handle non-BST
    def format_datetime(self, v: datetime | None) -> str | None:
        """
        Format datetime objects to format API expects.
        Naively assumes that datetime is specified in UK BST, converts to UTC.
        """

        if v:
            v = v - timedelta(hours=1)  # Convert to UTC
            return f"{v.isoformat()}Z"

        return v

    @model_serializer
    def serialize(self) -> str:
        return super()._range_to_str(
            self.format_datetime(self.lower_bd), self.format_datetime(self.upper_bd)
        )


class SearchEndpointFilter(SearchPayloadParam):
    """
    Filters which are used by SearchEndpointPayload.\n
    Some conditions unique to the 'apparel' category have been omitted.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        serialize_by_alias=True,
    )

    # ---------- QUERY SETTINGS ----------
    search_in_description: LowercaseBool | None = None

    # ---------- PRICE ----------
    price: IntRange
    price_currency: str = "GBP"

    # ---------- CONDITION ----------
    conditions: (
        Annotated[
            list[Literal["NEW", "USED", "UNSPECIFIED"]],
            PlainSerializer(_pipe_join_curly_wrap_sorted),
        ]
        | None
    ) = None

    # Converted to ConditionIds for API
    precise_conditions: Annotated[list[ConditionName] | None, Field(exclude=True)] = (
        None
    )

    # ---------- BUYING FORMAT ----------
    bid_count: IntRange | None = None
    buying_options: (
        Annotated[
            list[Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"]],
            PlainSerializer(_pipe_join_curly_wrap_sorted),
        ]
        | None
    ) = None

    # ---------- DATE ----------
    item_end_date: DatetimeRange | None = None
    item_start_date: DatetimeRange | None = None

    # ---------- SELLER ----------
    sellers: (
        Annotated[LowercaseList, PlainSerializer(_pipe_join_curly_wrap_sorted)] | None
    ) = None
    seller_account_types: (
        Annotated[
            list[Literal["INDIVIDUAL", "BUSINESS"]],
            PlainSerializer(_pipe_join_curly_wrap_sorted),
        ]
        | None
    ) = None

    # ---------- REGION ----------
    # TODO: research if item_location_region/country are required
    # ISO 3166
    # item_location_country: str = "GB"
    delivery_country: str = "GB"

    @model_validator(mode="after")
    def validate_params(self) -> Self:

        if self.buying_options == "FIXED_PRICE" and self.bid_count:
            raise ValueError("Cannot specify bid count with fixed price.")

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

    @computed_field
    @property
    def condition_ids(self) -> list[int] | None:
        if self.precise_conditions:
            return [_CONDITION_ID_MAP[name] for name in self.precise_conditions]
        return None

    @model_serializer(mode="wrap")
    def serialize(self, handler: SerializerFunctionWrapHandler) -> str:

        data: dict[str, Any] = handler(self)
        return _comma_colon_join_dict(data)


class SearchEndpointQuery(SearchPayloadParam):
    kwords: LowercaseList
    excl_kwords: LowercaseList | None = None
    join_method: Literal["AND", "OR"]

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        # +2 for the first ' -' in between them
        if (
            len(" ".join(self.kwords))
            + (len(" -".join(self.excl_kwords)) + 2 if self.excl_kwords else 0)
            > 100
        ):
            raise ValueError("Combined length of query + spaces must be <=100.")

        return self

    @model_serializer(mode="wrap")
    def serialize(self, handler: SerializerFunctionWrapHandler) -> str:
        data: dict[str, Any] = handler(self)

        query = ""

        if self.join_method == "AND":
            query = " ".join(data["kwords"])

        if self.join_method == "OR":
            # Has a space as well as comma in docs for some reason
            query = "(" + ", ".join(data["kwords"]) + ")"

        if self.excl_kwords:
            query += f" -{' -'.join(data['excl_kwords'])}"

        return query
