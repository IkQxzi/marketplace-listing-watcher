'''Filtering listings using various criteria.'''

import pandas as pd

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
    df: pd.DataFrame, required_txt: str | None = None, case_sensitive = False
    ) -> pd.DataFrame:
    
    '''
    Remove listings without this item name. 
    If unspecified, tries to infer from parent directory name.
    '''

    if not required_txt:
        raise NotImplementedError("Currently, inferring name from parent directory not supported.")
    
    # Non case-sensitive
    return df[df['full_name'].str.contains(required_txt, case=case_sensitive)]


def remove_records_containing(
    df: pd.DataFrame, banned_txt: str, case_sensitive = False
    ) -> pd.DataFrame:
    '''Remove listings containing the banned text.'''

    return df[~df['full_name'].str.contains(banned_txt, case=case_sensitive)]


def clean_listings(df: pd.DataFrame) -> pd.DataFrame:
    '''Call all the cleaning functions.'''

    raise NotImplementedError
