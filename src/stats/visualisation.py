'''Visualisation of prices and other data.'''

import pandas as pd
import matplotlib.pyplot as plt

# TODO: Put prices in different bins
def show_price_hist(df: pd.DataFrame, bin_size: float | None = None) -> None:
    '''
    Display the price data in a histogram.
    Works on price column, so combining with shipping recommended.
    '''

    if bin_size:
        raise NotImplementedError("Need to put prices in bins")

    df['price'].hist()
    plt.show()
