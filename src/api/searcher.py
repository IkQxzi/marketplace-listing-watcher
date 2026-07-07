
from pprint import pprint
from bs4 import BeautifulSoup

import os
import requests
import time
import json
from collections import Counter, defaultdict

from utils.config import API_SEARCH_URL, TEMP_ACTIVE_DIR
from utils.misc import get_timestamp
from utils.io import write_to_dir

def _log_response(r_json, item_name: str, cat_counts: Counter, cat_mappings: defaultdict) -> None:
    '''Log API response to two files: one for item summaries, one for metadata, using category counts as file names.'''
    
    cat_id = cat_counts.most_common(1)[0][0]
    cat_name = cat_mappings[cat_id]

    item_dir = f"{TEMP_ACTIVE_DIR}\\{cat_id}_{cat_name}\\{item_name}"
    write_to_dir(r_json, item_dir, file_ext='json')


def _parse_categories(item_summaries: list[dict]) -> tuple[Counter, defaultdict]:
    '''Parse categories of items,
    and return the counts of each category ID and the associated category name.'''

    cat_counts = Counter()
    cat_mapping = defaultdict()

    for item in item_summaries:
        
        cat_info: list = item['categories']

        for cat in cat_info:

            cat_id = cat['categoryId']

            cat_counts[cat_id] += 1
            cat_mapping[cat_id] = cat['categoryName']
    
    return cat_counts, cat_mapping


def search_item(access_token: str, item_name: str, limit: int = 50, category_id: int | None = None, 
                log_response: bool = False):
    '''Query for an active search and return the JSON response.'''


    params: dict[str, str | int] = {
        'q': item_name, # parens + comma for or, spc for and
        'limit': limit, # no. of items
        'offset': 0
    }

    if category_id: 
        params['category_ids'] = category_id

    headers = {
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_GB',
        'Authorization': f'Bearer {access_token}'
    }

    r = requests.get(url=API_SEARCH_URL, params=params, headers=headers, timeout=10)
    r_json = r.json()
    
    try:
        item_summaries: list[dict] = r.json()['itemSummaries']
    except KeyError:
        print(f'KeyError; r_json: {r_json}')
        exit()
        
    cat_counts, cat_mappings = _parse_categories(item_summaries)
    
    if log_response:        
        _log_response(r_json, item_name, cat_counts, cat_mappings)

    # debug
    for cat_id, cat_count in cat_counts.most_common():
        print(f'{cat_id}/{cat_mappings[cat_id]}: {cat_count}')

    return r_json


