'''Filtering listings using various criteria.'''

import pandas as pd
import numpy as np

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
    df: pd.DataFrame, banned_txt: list, case_sensitive = False
    ) -> pd.DataFrame:
    '''Remove listings containing the banned keywords.'''

    #generate banned text string from keywords
    keywords_list = "|".join(banned_txt)

    return df[~df['full_name'].str.contains(keywords_list, case=case_sensitive)]

def filter_by_price(
    upper_bound:float, lower_bound:float, df:pd.DataFrame
    ) -> pd.DataFrame:
    '''Remove listings above or below a certain price with specified upper/lower bounds'''

    return df[(df["price"] >= lower_bound) & (df["price"] <= upper_bound)]

def filter_by_standard_deviation(
        df:pd.DataFrame, n:int) -> pd.DataFrame:
    '''Remove listings that are n standard deviations away from the mean'''

    price_arr = df["price"]
    mean = np.mean(price_arr)
    sd = np.std(price_arr, ddof=1) #degrees of freedom = 1, this means it uses sample s.d. not population

    lower_bound = mean - (n*sd)
    upper_bound = mean + (n*sd)

    return df[(df["price"] >= lower_bound) & (df["price"] <= upper_bound)]

def filter_by_percentile(
        df:pd.DataFrame, lower_percentile:float, upper_percentile:float) -> pd.DataFrame:
    '''Remove listings that are outside a certain percentile range
    Percentile has to be a decimal e.g. 0,05'''

    price_arr = df["price"]
    lower_bound = price_arr.quantile(lower_percentile)
    upper_bound = price_arr.quantile(upper_percentile)

    return df[(df["price"] >= lower_bound) & (df["price"] <= upper_bound)]

def clean_listings(df: pd.DataFrame) -> pd.DataFrame:
    '''Call all the cleaning functions.'''

    raise NotImplementedError

