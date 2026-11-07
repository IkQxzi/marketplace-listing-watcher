import logging
import sys

import pytest

from api.auth import get_access_token
from config.api import APP_ID, CERT_ID, REFRESH_TOKEN

from .helpers import form_payload_searcher_save_paths

if not (REFRESH_TOKEN and APP_ID and CERT_ID):
    pytest.skip("No API creds, skipping live API tests.")

file_handler = logging.FileHandler("listings.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


@pytest.mark.api
@pytest.mark.parametrize("depth", ["simple", "complex"])
def test_searcher_no_files(depth):
    payload, searcher, save_paths = form_payload_searcher_save_paths(depth)

    for path in save_paths.item_dir.iterdir():
        path.unlink(missing_ok=True)
    save_paths.item_dir.rmdir()

    logging.debug(f"Listing searcher test data path: {save_paths.data_path}")

    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)
    resp = searcher.get_latest_listings(access_token)
