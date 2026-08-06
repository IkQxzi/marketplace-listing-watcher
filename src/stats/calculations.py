'''Calculations involving listing prices.'''

import pandas as pd
import numpy as np
from scipy import stats
def combine_price_with_shipping(df: pd.DataFrame) -> pd.DataFrame:
    '''Combine price and shipping into one price col called total_price. Assumes both are full with no missing data or errors.'''

    df["total_price"] = df["ship_price"] + df["price"]

    return df


def fit_to_normal(df:pd.DataFrame) -> object:
    '''Fit the dataframe price distribution to the normal distribution and output the parameters as an object.
    mean = mean.
    std = standard deviation. '''

    mean, std = stats.norm.fit(df["price"])

    return {
        "mean":mean,
        "std":std
    }


def fit_to_lognormal(df:pd.DataFrame) -> object:
    '''Fit the dataframe price distribution to the lognormal distribution and output the parameters as an object.
    shape = how skewed the data is.
    loc = floor (min value), set to 0.
    scale = median of distribution. '''

    shape, loc, scale = stats.lognorm.fit(df["price"], floc=0)

    return {
        "shape":shape,
        "loc":loc,
        "scale":scale
    }