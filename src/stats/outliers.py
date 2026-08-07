'''Cleaning listings using statistical methods.'''

from dataclasses import dataclass

import pandas as pd
import numpy as np

from utils.misc import get_text_timestamp

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