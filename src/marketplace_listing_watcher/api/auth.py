import base64
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests

from marketplace_listing_watcher.config.api import (
    ACCESS_TOKEN_PATH,
    ACCESS_TOKEN_REFRESH_THRESHOLD,
)

logger = logging.getLogger()


def get_refresh_token(oauth_url, app_id: str, cert_id: str) -> str:
    """
    Get refresh token (expiry: 18 months) using the branded Oauth URL.
    You can find your details at https://developer.ebay.com/my/keys
    Args:
    auth_url -- The URL Ebay directs you to, after using your branded Oauth sign-in found under 'User Access Tokens' section of Keyset.
    app_id -- The App ID (Client ID) displayed on your Ebay keyset page.
    cert_id -- The Cert ID (Client Secret) displayed on your Ebay keyset page.
    """

    print("Retrieving refresh token...", flush=True)

    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        # b64 expects bytes-like object
        "Authorization": f"Basic {base64.b64encode((f'{app_id}:{cert_id}').encode()).decode('utf-8')}",
    }

    code = oauth_url.split("code=")[1].rstrip("&expires_in=299")
    data = {
        "grant_type": "authorization_code",
        "code": code,
    }

    r = requests.post(url, headers=headers, data=data)

    if r.ok:
        print("Refresh token acquired.", flush=True)
    else:
        print(f"There was an error! Status code: {r.status_code}.")
        print(f"The response from the server:\n {r.content}")

    r_json = r.json()
    return r_json["refresh_token"]


def _request_access_token_info(refresh_token: str, app_id: str, cert_id: str) -> str:
    """Retrieve access token info (expiry etc. included)"""

    OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        # b64 expects bytes-like object
        "Authorization": f"Basic {base64.b64encode((f'{app_id}:{cert_id}').encode()).decode('utf-8')}",
    }

    # Can also narrow scopes with this
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    r = requests.post(url=OAUTH_URL, headers=headers, data=data)
    r.raise_for_status()
    logging.info("Access token acquired succesfully.\n")

    return r.json()


def _write_access_token_info(path: Path, access_token_info: dict) -> None:
    """Writes expiry datetime also."""

    if not path.exists():
        path.touch()

    expires_at = (
        datetime.now() + timedelta(seconds=access_token_info["expires_in"])
    ).isoformat()
    json.dump({**access_token_info, "expires_at": expires_at}, path.open("w"))


def _read_access_token_info(path: Path) -> dict | None:
    if not path.exists():
        return
    return json.load(path.open("r"))


def get_access_token(refresh_token: str, app_id: str, cert_id: str) -> str:
    """
    Get access token (expiry: 2 hours) using refresh token, and cache to local json file.
    If exists, do not poll oauth endpoint.
    You can find your details at https://developer.ebay.com/my/keys
    Args:
    refresh_token -- Your refresh token acquired from get_refresh_token()
    app_id -- The App ID (Client ID) displayed on your Ebay keyset page.
    cert_id -- The Cert ID (Client Secret) displayed on your Ebay keyset page.
    """

    token_info = _read_access_token_info(ACCESS_TOKEN_PATH)
    if (
        not token_info
        or datetime.now() - datetime.fromisoformat(token_info["expires_at"])
        <= ACCESS_TOKEN_REFRESH_THRESHOLD
    ):
        token_info = _request_access_token_info(refresh_token, app_id, cert_id)
        _write_access_token_info(ACCESS_TOKEN_PATH, token_info)

    return token_info["access_token"]
