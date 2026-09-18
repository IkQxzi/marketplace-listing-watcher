"""Cleaning raw API response into clean listing objects."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FileUrl, HttpUrl, computed_field

from .constants import ConditionId, ConditionName, buyingOption
from .core import CountryCode, Currency, Percentage, Price, Epid
from .schemas import SearchEndpointResponse


# TODO: possibly allow CamelCase instantiation
class Listing(BaseModel):
    """
    Class for an individual listing.\n
    Search Endpoint gives price after discounts (see MarketingInfo for original price).\n
    Note that a list of category names is omitted,
    as this may be implemented as a separate mapping somewhere else.\n
    """

    # So classes defined lower in file can be type-hinted to
    model_config = ConfigDict(defer_build=True)

    # ---------- IDs ----------
    item_id: str
    legacy_item_id: int
    marketplace_id: str
    epid: Epid

    # ---------- Price/Purchasing ----------
    # TODO: implement conversion to GBP always
    price: Price  # After discounts
    currency: Currency
    buying_options = list[buyingOption]
    unit_pricing_measure: Literal["Unit"] | None = None
    unit_price: Price | None = None
    has_coupons: bool

    # ---------- Condition ----------
    condition: ConditionName
    condition_id: ConditionId

    # ---------- Dates ----------
    item_origin_date: datetime
    item_creation_date: datetime

    # ---------- URLs ----------
    href: HttpUrl
    web_url: HttpUrl
    thumbnail_image_urls: list[FileUrl]
    image_urls: list[FileUrl]  # Most listings only have 1 image
    group_href: HttpUrl | None

    # ---------- Shipping ----------
    shipping_price: Price  # TODO alias: shipping_cost
    shipping_price_type: str  # TODO: find Literals

    # ---------- Categories ----------
    category_ids: list[int]
    leaf_category_ids: list[int]

    # ---------- Location ----------
    postcode: str  # Is censored, pretty sure
    country_code: CountryCode

    # ---------- Seller ----------
    seller: Seller

    # ---------- Misc. ----------
    priority_listing: bool
    item_group_type: Literal["SELLER_DEFINED_VARIATIONS"] | None

    @computed_field
    @property
    def total_price(self) -> float:
        return self.price + self.shipping_price

    ...


class Seller(BaseModel):
    username: str
    feedback_percentage: Percentage
    feedback_Score: Annotated[int, Field(ge=0)]
    account_type: Literal["BUSINESS", "INDIVIDUAL"]
    price_treatment: Literal["MARKDOWN"] | None


class MarketingInfo(BaseModel):
    original_price: Annotated[float, Field(ge=0)]
    currency: Currency
    discount_percentage: Percentage
    price_treatment: str  # TODO: implement Literal["MARKDOWN"]


def clean_listings(response: SearchEndpointResponse) -> list[Listing]:
    """Clean the API response and return a list of Listing objects"""
    raise NotImplementedError
