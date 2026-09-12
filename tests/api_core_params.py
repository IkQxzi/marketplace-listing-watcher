from api.core import SearchEndpointQuery, SearchEndpointFilter, IntRange, DatetimeRange

from datetime import datetime


EXAMPLE_FILTER_PARAMS = {
    "search_in_description": True,
    "price": {
        "lower_bd": 50,
        "upper_bd": 300,
    },
    "price_currency": "GBP",
    "conditions": ["NEW", "USED"],
    "bid_count": {
        "lower_bd": 1,
        "upper_bd": 5,
    },
    "buying_options": ["FIXED_PRICE", "AUCTION"],
    "seller_account_types": ["BUSINESS"],
    "delivery_country": "GB",
}

EXAMPLE_PAYLOAD_PARAMS = {
    "q": {
        "q": ["laptop", "thinkpad"],
        "join_method": "AND",
    },
    "category_ids": [177],
    "limit": 50,
    "offset": 0,
    "fieldgroups": "MATCHING_ITEMS",
    "filter": {
        "search_in_description": True,
        "price": {
            "lower_bd": 150,
            "upper_bd": 600,
        },
        "price_currency": "GBP",
        "conditions": ["NEW", "USED"],
        "bid_count": {
            "lower_bd": 1,
            "upper_bd": 10,
        },
        "buying_options": ["FIXED_PRICE", "AUCTION"],
        "seller_account_types": ["BUSINESS"],
        "delivery_country": "GB",
    },
}
