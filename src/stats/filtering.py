'''Filtering listings using various criteria.'''

from dataclasses import dataclass

import pandas as pd
import numpy as np

from utils.misc import get_text_timestamp


@dataclass
class FilterConfig:
    required_txts: list[str] | None = None
    req_txts_case_sensitive: bool = False
    banned_txts: list[str] | None = None
    ban_txt_case_sensitive: bool = False


def drop_empty_records(df: pd.DataFrame) -> pd.DataFrame:
    '''Filter out errored/blank listings (usually the first 2).'''

    # The first 2 are usually redundant
    df = df[~(df['full_name'].str.lower() == 'shop on ebay')]
    
    # To prevent removed listings from affecting index
    df.reset_index(inplace=True, drop=True)

    return df


def remove_trailing_name_text(df: pd.DataFrame) -> pd.DataFrame:
    '''Clean the "Opens in a new window or tab" text from listing names.'''

    trailing_text = "Opens in a new window or tab"

    return df.assign(
        full_name= df['full_name'].str.removesuffix(trailing_text)
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
    
    # Remove sequentially
    for txt in filter_conf.required_txts:
        df = df[df['full_name'].str.contains(txt, case=filter_conf.req_txts_case_sensitive)]

    return df


def remove_records_containing(
    df: pd.DataFrame, filter_conf: FilterConfig,
    ) -> pd.DataFrame:
    '''Remove listings containing the banned keywords.'''

    assert filter_conf.banned_txts, "Banned texts not specified in filter config!"

    df["name_lower"] = df["full_name"].str.lower() #create new column with lowercase titles
    txt = r'\b(' + '|'.join(filter_conf.banned_txts) + r')\b' #regex to filter out banned texts as separate words only

    df = df[~df['name_lower'].str.contains(txt, case=False, na=False)]

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

    return df[~df['full_name'].str.contains(keywords_list, case=case_sensitive)]

def clean_listings(df: pd.DataFrame) -> pd.DataFrame:
    '''Call all the cleaning functions.'''

    raise NotImplementedError

