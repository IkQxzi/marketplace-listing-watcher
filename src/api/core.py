'''Functionality and base classes for any part of API.'''

from dataclasses import dataclass
from typing import Any, Literal
import re

from utils.misc import snake_to_camel_case

@dataclass
class SearchAPIResponse:
    json_response: Any
    q: str
    inferred_cat_id: int
    inferred_cat_name: str


@dataclass(kw_only=True, frozen=True)
class SearchAPIConfig:
    '''
    Config for Search Endpoint.\n

    Note that bools can only be True or None, not False.\n

    Some params, like 'price' and 'bid_count' require strict formatting rules.
    They follow these rules:\n
    '..' used to separate bounds, examples:\n
    at least 1: '1..'\n
    up to 5: '..5'\n
    1 to 5: '1..5'\n
    '''

    # ---------- QUERY ----------
    q: str # Query (keywords)
    search_in_description: bool | None = None
    epid: int | None = None # eBay Product ID

    # ---------- CATEGORY ----------
    category_ids: list[int] | None = None
    exclude_category_ids: list[str] | None = None

    # ---------- PRICE ----------
    # See docstring for formatting rules
    price: str | None = None
    price_currency: str = 'GBP'

    # ---------- BUYING FORMAT ----------
    # See docstring for formatting rules
    bid_count: str | None = None
    buying_options: Literal['FIXED_PRICE', 'AUCTION', 'BEST_OFFER', 'CLASSIFIED_AD'] | None = None

    # ---------- CONDITION ----------
    # https://developer.ebay.com/api-docs/sell/static/metadata/condition-id-values.html
    conditions: Literal['NEW', 'USED', 'UNSPECIFIED'] | None = None
    condition_ids: int | None = None

    # ---------- DATE ----------
    # ISO date format
    item_end_date: str | None = None

    # ---------- REGION ----------
    # ISO 3166
    delivery_country: str = 'GB'
    item_location_country: str = 'GB'


    def _validate_bounded_param(self, filter: str) -> None:
        '''Check a param (namely price, bid_count) follows strict API format.'''

        filter_parts = filter.split('..')

        if len(filter_parts) >= 3:
            raise ValueError(f"Too many ellipses, invalid: {filter}")

        if any(part and not part.isdigit() for part in filter_parts):
            raise ValueError(f"Expected up to 2 ints separated by '..', not {filter}")

        # Allowing equal bounds for precise price-matching
        if all(filter_parts) and int(filter_parts[0]) > int(filter_parts[1]):
            raise ValueError(f"Lower bound cannot be greater than upper bound, invalid: {filter}\n"
                             f"{filter_parts[0]} is not less than {filter_parts[1]}")


    def __post_init__(self):

        # Check both follow strict format

        if self.bid_count:
            self._validate_bounded_param(self.bid_count)

        if self.price:
            self._validate_bounded_param(self.price)


    def to_dict(self) -> dict[str, Any]:
        '''Convert params to dict format Search Endpoint expects.'''

        return {
            snake_to_camel_case(k): v for k, v in self.__dict__.items() if v
        }
        
