from bs4 import BeautifulSoup
from pprint import pprint

from pathlib import Path
from dotenv import load_dotenv
import os
import requests

from api.auth import get_refresh_token, get_access_token
from api import search_item
from webscraper.scraper import ListingScraper, ListingParser
from utils.config import ENV_PATH, TEMP_ACTIVE_DIR, TEMP_HTML_PATH
from utils.io import get_latest_search_json
from stats.analysis import do_stats


def load_env_vars():
    
    load_dotenv(ENV_PATH)
    app_id = os.getenv('prd_app_id')
    cert_id = os.getenv('prd_cert_id')
    refresh_token = os.getenv('prd_refresh_token')

    assert app_id and cert_id and refresh_token, "Missing credentials."

    return app_id, cert_id, refresh_token

def load_discord_webhook_url():
    
    load_dotenv(ENV_PATH)
    url = os.getenv("discord_webhook_url")

    return url

def webhook_test():
    print(load_discord_webhook_url())

def search_test():

    app_id, cert_id, refresh_token = load_env_vars()
    assert app_id and cert_id and refresh_token 
    access_token = get_access_token(refresh_token, app_id, cert_id)


    item = 'iphone 16 case'
    category_id = 0
    limit = 200
    log_response = True

    print(f"Searching for: '{item}'\n")

    r_json = search_item(access_token, item, limit, category_id, log_response)
    # pprint(r_json)

    item_summaries = r_json['itemSummaries']
    print(f'\nNo. of items: {len(item_summaries)}')


def stats_test():

    data_file = get_latest_search_json(TEMP_ACTIVE_DIR, 'iphone 17')
    do_stats(data_file)


def scraper_test():

    raise NotImplementedError

    scraper = CamoufoxScraper(headless=False)
    scraper.get_sold_listings_info(item="iphone 16", condition="new")


def html_test():

    parser = ListingParser()
    ListingParser()
    

def main():
    scraper_test()
    # webhook_test()

if __name__ == '__main__':
    main() 