import requests
import base64


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
        "Authorization": f"Basic {base64.b64encode((f'{app_id}:{cert_id}').encode('utf-8')).decode('utf-8')}",
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


def get_access_token(refresh_token: str, app_id: str, cert_id: str) -> str:
    """
    Get access token (expiry: 2 hours) using refresh token.
    You can find your details at https://developer.ebay.com/my/keys
    Args:
    refresh_token -- Your refresh token acquired from get_refresh_token()
    app_id -- The App ID (Client ID) displayed on your Ebay keyset page.
    cert_id -- The Cert ID (Client Secret) displayed on your Ebay keyset page.
    """

    oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        # b64 expects bytes-like object
        "Authorization": f"Basic {base64.b64encode((f'{app_id}:{cert_id}').encode('utf-8')).decode('utf-8')}",
    }

    # Can also narrow scopes with this
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    r = requests.post(url=oauth_url, headers=headers, data=data)

    # is a Python dict
    r_json = r.json()
    if r.ok:
        print("Access token acquired succesfully.\n")
    else:
        print(f"There was an error! Status code: {r.status_code}.")
        print(f"The response from the server:\n {r.content}")

    return r_json["access_token"]
