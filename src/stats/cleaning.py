'''
Cleaning data from sold listings.
Includes functions which clean by calculation.
Does not incl. outlier-filtering.
'''

from dataclasses import dataclass

import pandas as pd
import numpy as np

from utils.misc import get_text_timestamp
from config.filters import FilterConfig


def drop_empty_records(df: pd.DataFrame) -> pd.DataFrame:
    '''Filter out errored/blank listings (usually the first 2).'''

    # The first 2 are usually redundant
    df = df[~(df['title'].str.lower() == 'shop on ebay')]
    
    # To prevent removed listings from affecting index
    df.reset_index(inplace=True, drop=True)

    return df


def remove_trailing_name_text(df: pd.DataFrame) -> pd.DataFrame:
    '''Clean the "Opens in a new window or tab" text from listing names.'''

    trailing_text = "Opens in a new window or tab"

    return df.assign(
        title= df['title'].str.removesuffix(trailing_text)
    )


def keep_records_containing(
    df: pd.DataFrame, filter_conf: FilterConfig,
    ) -> pd.DataFrame:
    
    '''
    Remove listings without this item name. 
    If unspecified, tries to infer from parent directory name.
    '''

    if not filter_conf.required_txts:
        raise NotImplementedError("Currently, inferring name from parent directory not supported.")
    
    txt = rf"\b({'|'.join(filter_conf.required_txts)})\b"
    df = df[df['title'].str.contains(txt, case=filter_conf.req_txts_case_sensitive)]

    return df


def remove_records_containing(
    df: pd.DataFrame, filter_conf: FilterConfig,
    ) -> pd.DataFrame:
    '''Remove listings containing the banned keywords.'''

    assert filter_conf.banned_txts, "Banned texts not specified in filter config!"

    txt = r'\b(' + '|'.join(filter_conf.banned_txts) + r')\b' #regex to filter out banned texts as separate words only

    # Param na unhandled so exceptions warn us of incomplete data
    df = df[~df['title'].str.contains(txt, case=filter_conf.ban_txt_case_sensitive)]

    return df


def conv_dates(df: pd.DataFrame) -> pd.DataFrame:
    '''Convert dates to datetime format Pandas uses.'''

    df['sold_date'] = pd.to_datetime(df['sold_date'])
    return df


def set_date_as_index(df: pd.DataFrame) -> pd.DataFrame:

    df.set_index('sold_date', inplace=True)
    return df


def replace_null_shipping_with_avg(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Replace null shipping values with the average shipping value for the df.
    Recommended to do after all other cleaning so averages are more accurate.
    '''

    avg_shipping = df['ship_price'].mean()

    df['ship_price'] = df['ship_price'].fillna(avg_shipping)
    return df


def sum_price_and_shipping(df: pd.DataFrame) -> pd.DataFrame:
    '''Combine price and shipping into new price col called total_price. Assumes both are full with no missing data or errors.'''

    df["total_price"] = df["ship_price"] + df["price"]

    return df