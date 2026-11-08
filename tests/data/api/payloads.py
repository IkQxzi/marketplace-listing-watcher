"""Some payload params for testing (see api/params.py)."""

SIMPLE_EXAMPLE_PAYLOAD_PARAMS = {
    "q": {
        "kwords": ["laptop", "thinkpad"],
        "join_method": "AND",
    },
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
        "delivery_country": "GB",
    },
}

COMPLEX_EXAMPLE_PAYLOAD_PARAMS = {
    "q": {
        "kwords": ["laptop", "thinkpad"],
        "excl_kwords": ["case", "accessory"],
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

EXAMPLE_EXCL_KWORDS_PAYLOAD_PARAMS = {
    "q": {
        "kwords": ["laptop", "thinkpad"],
        "excl_kwords": ["case", "accessory", "t480", "ssd"],
        "join_method": "AND",
    },
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
        "delivery_country": "GB",
    },
}
