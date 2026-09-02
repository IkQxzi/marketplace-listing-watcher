from api.core import SearchEndpointQuery, SearchEndpointFilter, IntRange, DatetimeRange

from datetime import datetime


EXAMPLE_FILTER_PARAMS = {
    # Query Settings
    "search_in_description": True,
    # Price & Currency
    "price": IntRange(lower_bd=200, upper_bd=700),
    "price_currency": "GBP",
    # Condition (mutually exclusive: conditions is populated, precise_conditions is None)
    "conditions": ["NEW", "USED"],
    # Buying Format
    "buying_options": ["FIXED_PRICE"],
    # Dates (satisfies: item_start_date.lower_bd >= item_end_date.upper_bd)
    "item_start_date": DatetimeRange(
        lower_bd=f"{datetime.isoformat(datetime(2026, 8, 1, 12, 0))}Z",
        upper_bd=f"{datetime.isoformat(datetime(2026, 8, 2, 12, 0))}Z",
    ),
    "item_end_date": DatetimeRange(
        lower_bd=f"{datetime.isoformat(datetime(2026, 8, 3, 12, 0))}Z",
        upper_bd=f"{datetime.isoformat(datetime(2026, 8, 4, 12, 0))}Z",
    ),
    # Seller Settings (sellers joined length is well below 250 characters)
    "sellers": ["ukphonehub"],
    "seller_account_types": ["BUSINESS"],
    # Region
    "delivery_country": "GB",
}

EXAMPLE_PAYLOAD_PARAMS = {
    "q": SearchEndpointQuery(q=["iphone 17"], join_method="AND"),
    "auto_correct": "KEYWORD",
    "limit": 50,
    "filter": SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS),
}
