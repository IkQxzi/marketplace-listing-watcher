'''Filtering listings using various criteria.'''

from dataclasses import dataclass

import pandas as pd



@dataclass
class FilterConfig:
    required_txts: list[str] | None = None
    req_txts_case_sensitive: bool = False
    banned_txt: str | None = None
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
    '''Remove listings containing the banned text.'''

    assert filter_conf.banned_txt, "Banned text not specified in filter config!"

    return df[~df['full_name'].str.contains(filter_conf.banned_txt, case=filter_conf.ban_txt_case_sensitive)]


def clean_listings(df: pd.DataFrame) -> pd.DataFrame:
    '''Call all the cleaning functions.'''

    raise NotImplementedError
