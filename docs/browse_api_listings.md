Pretty comprehensive class for listings (includes many fields that will likely never see use):
```Python
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
    buying_options: list[buyingOption]
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
```

