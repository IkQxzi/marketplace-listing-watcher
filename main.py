from bs4 import BeautifulSoup
from pprint import pprint

from dotenv import load_dotenv
import os
import requests

from api.auth import get_refresh_token, get_access_token
from utils.config import ENV_PATH
from api import search_item


def load_env_vars():
    
    load_dotenv(ENV_PATH)
    app_id = os.getenv('prd_app_id')
    cert_id = os.getenv('prd_cert_id')
    refresh_token = os.getenv('prd_refresh_token')

    return app_id, cert_id, refresh_token


def test_search():


    app_id, cert_id, refresh_token = load_env_vars()
    assert app_id and cert_id and refresh_token 
    access_token = get_access_token(refresh_token, app_id, cert_id)


    item = 'iphone 17 case'
    category_id = 0
    limit = 200
    log_response = False
    category_name = 'phones'

    print(f"Searching for: '{item}'\n")

    r_json = search_item(access_token, item, limit, category_id, log_response, category_name)
    # pprint(r_json)

    item_summaries = r_json['itemSummaries']
    print(f'\nNo. of items: {len(item_summaries)}')


def main():

    pass


if __name__ == '__main__':
    main() 