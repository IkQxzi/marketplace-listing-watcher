'''
Calculations involving listing prices.
The calculations performed here do not include visualisation or filtering.
'''

import pandas as pd
import numpy as np
from scipy import stats


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