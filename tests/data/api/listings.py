from datetime import datetime

from api.listings import Listing

EXAMPLE_LISTING_ARGS = {
    "title": "Some title",
    "item_id": "some id",
    "buying_options": ["FIXED_PRICE"],
    "has_coupons": False,
    "condition": "NEW",
    "item_origin_date": datetime.now().isoformat(),
    "item_creation_date": datetime.now().isoformat(),
    "href": "https://example.com",
    "web_url": "https://example.com",
    "seller": {
        "username": "some dodgy seller",
        "feedback_percentage": 100,
        "feedback_score": 10_000,
    },
    "shipping_price": 10,
    "price": 100,
    "itemLocation": {"country": "GB"},
    "priority_listing": False,
}

EXAMPLE_LISTING = Listing(**EXAMPLE_LISTING_ARGS)
