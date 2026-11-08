"""Some filter params for testing (see api/params.py)."""

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
