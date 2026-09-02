from api.core import SearchEndpointQuery, SearchEndpointFilter, IntRange, DatetimeRange

from datetime import datetime


EXAMPLE_FILTER_PARAMS = {
    # Query Settings
    "search_in_description": True,
    # Price & Currency
    "price": IntRange(lower_bd=10, upper_bd=100),
    "price_currency": "GBP",
    # Condition (mutually exclusive: conditions is populated, precise_conditions is None)
    "conditions": ["NEW", "USED"],
    "precise_conditions": None,
    # Buying Format
    "bid_count": IntRange(lower_bd=1, upper_bd=20),
    "buying_options": "FIXED_PRICE",
    # Dates (satisfies: item_start_date.lower_bd >= item_end_date.upper_bd)
    "item_start_date": DatetimeRange(
        lower_bd=datetime(2026, 8, 15, 12, 0),
        upper_bd=datetime(2026, 8, 20, 12, 0),
    ),
    "item_end_date": DatetimeRange(
        lower_bd=datetime(2026, 8, 1, 12, 0),
        upper_bd=datetime(2026, 8, 10, 12, 0),
    ),
    # Seller Settings (sellers joined length is well below 250 characters)
    "sellers": [10111213, 20212223, 30313233],
    "seller_account_types": "BUSINESS",
    # Region
    "delivery_country": "GB",
}

EXAMPLE_PAYLOAD_PARAMS = {
    "q": SearchEndpointQuery(q=["iphone 17"], join_method="AND"),
    "auto_correct": "KEYWORD",
    "limit": 50,
    "filter": SearchEndpointFilter(**EXAMPLE_FILTER_PARAMS),
}
