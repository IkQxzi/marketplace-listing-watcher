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
    mu = mean.
    std = standard deviation. '''

    mu, std = stats.norm.fit(df["price"])

    return {
        "mu":mu,
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


def calculate_simple_stats(df:pd.DataFrame) -> object:
    '''Calculate simple stats from dataframe and return as an object: mean, min, q1, median, q3, max'''

    prices = df["price"]

    q0 = prices.quantile(0)
    q1 = prices.quantile(0.25)
    q2 = prices.quantile(0.50)
    q3 = prices.quantile(0.75)
    q4 = prices.quantile(1)

    mean = np.mean(prices)

    return {
        "mean":mean,
        "min":q0,
        "q1":q1,
        "median":q2,
        "q3":q3,
        "max":q4
    }