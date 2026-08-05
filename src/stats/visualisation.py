'''Visualisation of prices and other data.'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def show_price_hist(
        df: pd.DataFrame, 
        bin_size: float | None = None, 
        dist_values: object | None = None,
        lines: object | None = None
        ) -> None:
    
    '''
    Display the price data in a histogram.
    Works on price column, so combining with shipping recommended.
    Draws distribution over prices if specified, and also quartiles (if specified).
    '''

    if bin_size: #create bins
        min_val = df["price"].min()
        max_val = df["price"].max()
        bins = np.arange(min_val, max_val + bin_size, bin_size)

        df["price"].hist(bins=bins)

    else:
        df["price"].hist()

    if dist_values: #plot distribution using values
        scale_factor = len(df) * bin_size
        scaled_y = dist_values["y"] * scale_factor

        plt.plot(dist_values["x"], scaled_y)

    if lines: # plot array of lines, e.g. mean, median
        colours = plt.get_cmap("rainbow")
        num_lines = len(lines)
        
        for i, (key, val) in enumerate(lines.items()):
            # calculate normalized float between 0 and 1 for each line
            colour_fraction = i / max(1, num_lines - 1)
            
            plt.axvline(x=val, label=key, color=colours(colour_fraction))
        
        plt.legend()

    plt.show()
