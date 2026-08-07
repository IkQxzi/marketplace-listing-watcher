'''Evaluating and analysing the data.'''

import pandas as pd
import scipy.stats


def get_empirical_percentile(df: pd.DataFrame, col: str, value: float) -> float:
    '''Get the percentile (0-100) of a given value in a column in a df.'''

    # Strict results in empirical percentile
    return scipy.stats.percentileofscore(df[col], score=value, kind='strict') * 100