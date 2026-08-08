'''Polling API for active listings.'''

import requests

from dataclasses import dataclass
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from config.dirs import ACTIVE_DIR, TEMP_ACTIVE_DIR
from config.api import SEARCH_ENDPOINT, APP_ID, CERT_ID, REFRESH_TOKEN
from utils.io import write_to_dir, generate_log_path
from api.auth import get_access_token

@dataclass
class APIResponse:
    json_response: Any
    item_name: str
    cat_id: int
    cat_name: str


def log_response(api_response: APIResponse, active_dir: Path) -> None:
    '''Log API response to two files: one for item summaries, one for metadata, using category counts as file names.'''
    
    item_dir = generate_log_path(
        active_dir, api_resp.item_name, is_active=True, cat_id=api_resp.cat_id, cat_name=api_resp.cat_name
        )
    write_to_dir(api_resp.json_response, item_dir, file_ext='json')


def _parse_categories(item_summaries: list[dict]) -> tuple[Counter[str], defaultdict[int, str]]:
    '''Parse categories of items,
    and return the counts of each category ID and the associated category name.'''

    cat_counts = Counter()
    cat_mapping = defaultdict()

    for item in item_summaries:
        
        cat_info: list = item['categories']

        for cat in cat_info:

            cat_id = int(cat['categoryId'])

            cat_counts[cat_id] += 1
            cat_mapping[cat_id] = cat['categoryName']
    
    return cat_counts, cat_mapping


def search_item(
        access_token: str, item_name: str, limit: int = 50, category_id: int | None = None, 
        log_response: bool = False
    ) -> APIResponse:

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

    r = requests.get(url=SEARCH_ENDPOINT, params=params, headers=headers, timeout=10)
    r_json = r.json()
    
    try:
        item_summaries: list[dict] = r.json()['itemSummaries']
    except KeyError:
        print(f'KeyError; r_json: {r_json}')
        exit()
        
    cat_counts, cat_mappings = _parse_categories(item_summaries)

    # Infer category ID and name from most common
    cat_id = int(cat_counts.most_common(1)[0][0])
    cat_name = cat_mappings[cat_id]

    # DEBUG
    for cat_id_str, cat_count in cat_counts.most_common():
        print(f'{(cat_id_str)}/{cat_mappings[int(cat_id_str)]}: {cat_count}')

    return APIResponse(r_json, item_name, cat_id, cat_name)


# Example usage
if __name__ == '__main__':

    assert REFRESH_TOKEN and APP_ID and CERT_ID, "API credentials missing from .env"

    item = 'iphone 16'
    access_token = get_access_token(REFRESH_TOKEN, APP_ID, CERT_ID)

    api_resp = search_item(access_token, item, log_response=True)
    log_response(api_resp, TEMP_ACTIVE_DIR)

