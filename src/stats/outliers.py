'''Removing outliers from data using statistical methods'''

from dataclasses import dataclass

import pandas as pd
import numpy as np

from utils.misc import get_text_timestamp


def filter_by_price(
    df:pd.DataFrame, upper_bound: float, lower_bound: float, col: str
    ) -> pd.DataFrame:
    '''Remove listings above or below a certain threshold within a column.'''

    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    

def filter_by_std(
    df:pd.DataFrame, n:int, col: str
    ) -> pd.DataFrame:

    '''Remove listings that are n standard deviations away from the mean in a specific column.'''

    price_arr = df[col]
    mean = np.mean(price_arr)
    sd = np.std(price_arr, ddof=1) #degrees of freedom = 1, this means it uses sample s.d. not population

    lower_bound = mean - (n*sd)
    upper_bound = mean + (n*sd)

    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    

def filter_by_percentile(
        df:pd.DataFrame, lower_percentile:float, upper_percentile:float, col: str) -> pd.DataFrame:
    '''Remove listings that are outside a certain percentile range for a certain column.
    Percentile is between 0 and 1.'''

    price_arr = df[col]
    lower_bound = price_arr.quantile(lower_percentile)
    upper_bound = price_arr.quantile(upper_percentile)

    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]