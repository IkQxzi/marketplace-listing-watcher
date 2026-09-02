from api.core import SearchEndpointPayload
from api.searcher import ListingSearcher, log_response
from api.auth import get_access_token
from config.api import REFRESH_TOKEN, APP_ID, CERT_ID
from config.dirs import TEMP_ACTIVE_DIR

from tests.api_core_params import EXAMPLE_PAYLOAD_PARAMS


def test_listing_searcher():
    payload = SearchEndpointPayload(**EXAMPLE_PAYLOAD_PARAMS)
    searcher = ListingSearcher()

    assert REFRESH_TOKEN and APP_ID and CERT_ID
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)
    response = searcher.get_listings(access_token, payload)

    log_response(response, TEMP_ACTIVE_DIR)
