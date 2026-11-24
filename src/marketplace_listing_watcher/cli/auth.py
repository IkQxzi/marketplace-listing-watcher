import argparse
import os

from marketplace_listing_watcher.api.auth import get_refresh_token
from marketplace_listing_watcher.config.api import APP_ID, CERT_ID
from marketplace_listing_watcher.config.dirs import ENV_PATH


def update_refresh():

    if not APP_ID:
        raise KeyError("APP_ID not found in env")

    if not CERT_ID:
        raise KeyError("CERT_ID not found in env")

    try:
        OAUTH_SUCCESS_URL = os.environ["OAUTH_SUCCESS_URL"]
    except KeyError as e:
        e.add_note("OAUTH_SUCCESS_URL not found in env")
        raise

    print(OAUTH_SUCCESS_URL)

    refresh_token = get_refresh_token(OAUTH_SUCCESS_URL, APP_ID, CERT_ID)

    with ENV_PATH.open("a") as f:
        f.write(f"\n{refresh_token=}\n")
