"""
Handling listings from Browse API and related functions.
e.g. cleaning raw API response into clean listing objects.
For now, is quite minimal, only enough to run the API loop.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PlainValidator,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

from api import (
    ConditionName,
)
from core.types import CountryCode, Currency, Percentage, Price, buyingOption


# TODO: possibly allow CamelCase instantiation
class Listing(BaseModel):
    """
    Class for an individual listing.\n
    Search Endpoint gives price after discounts (will implement marketing_info for original price).\n
    Note that a list of category names is omitted,
    as this may be implemented as a separate mapping somewhere else.\n
    """

    # So classes defined lower in file can be type-hinted to
    model_config = ConfigDict(
        defer_build=True,
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
    )

    # ---------- IDs/Name ----------
    title: str
    item_id: str

    # ---------- Price/Purchasing ----------
    # TODO: implement conversion to GBP always
    price: Annotated[
        Price | None, Field(validation_alias=AliasPath("price", "value"))
    ] = None  # After discounts, can be either this or bid price
    bid_price: Annotated[
        Price | None, Field(validation_alias=AliasPath("currentBidPrice", "value"))
    ] = None
    buying_options: list[buyingOption]
    has_coupons: Annotated[bool, Field(validation_alias=AliasPath("availableCoupons"))]

    # ---------- Condition ----------
    condition: Annotated[ConditionName, PlainValidator(lambda v: v.upper())]

    # ---------- Dates ----------
    def to_dt(v: str) -> datetime:
        return datetime.fromisoformat(v)

    item_origin_date: datetime
    item_creation_date: datetime

    # ---------- URLs ----------
    href: Annotated[HttpUrl, Field(validation_alias=AliasPath("itemHref"))]
    web_url: Annotated[HttpUrl, Field(validation_alias=AliasPath("itemWebUrl"))]

    # ---------- Shipping ----------
    pickup_options: list[dict] | None = None  # Must be specified if no pickup option
    shipping_price: Annotated[
        float | None,
        Field(
            validation_alias=AliasPath("shippingOptions", 0, "shippingCost", "value")
        ),
    ] = None  # TODO alias: shipping_cost

    # ---------- Location ----------
    postcode: Annotated[
        str | None, Field(validation_alias=AliasPath("itemLocation", "postalCode"))
    ] = None  # Is censored: LD1***
    country_code: Annotated[
        CountryCode, Field(validation_alias=AliasPath("itemLocation", "country"))
    ]

    # ---------- Seller ----------
    seller: Seller

    # ---------- Misc. ----------
    priority_listing: bool

    @model_validator(mode="after")
    def ensure_shipping_or_pickup(self) -> Self:
        """Ensure there is a shipping price, or a pickup option"""
        if self.shipping_price is None and not self.pickup_options:
            raise ValueError("Neither shipping price nor pickup options found.")
        return self

    @model_validator(mode="after")
    def ensure_price(self) -> Self:
        """Ensure either bid price or fixed price are present."""

        if not (self.price or self.bid_price):
            raise ValueError("Both price and bid price not present!")

        return self

    @computed_field
    @property
    def total_price(self) -> Price:
        total = self.price if self.price else self.bid_price
        if self.shipping_price:
            total += self.shipping_price
        return total

    @field_validator("item_creation_date", "item_origin_date", mode="before")
    @classmethod
    def convert_to_datetime(cls, v: str) -> datetime:
        return datetime.fromisoformat(v)

    @field_serializer("item_creation_date", "item_origin_date", mode="plain")
    def convert_dt_to_str(self, v: datetime) -> str:
        return datetime.isoformat(v)

    @field_serializer("href", "web_url", mode="plain")
    def convert_http_url_to_str(self, v: HttpUrl) -> str:
        return str(v)


class Seller(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, validate_by_alias=True, validate_by_name=True
    )

    username: str
    feedback_percentage: Percentage
    feedback_score: Annotated[
        int, Field(ge=0)
    ]  # Have no idea what the scale of this is yet
    account_type: Annotated[
        Literal["BUSINESS", "INDIVIDUAL"],
        Field(validation_alias=AliasPath("sellerAccountType")),
    ]


class MarketingInfo(BaseModel):
    original_price: Annotated[float, Field(ge=0)]
    currency: Currency
    discount_percentage: Percentage


def sort_listings(listings: list[Listing]) -> list[Listing]:
    listings.sort(key=lambda listing: listing.item_creation_date, reverse=True)
    return listings
