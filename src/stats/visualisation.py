'''Generation of distributions and visualisation of prices and other data.'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from dataclasses import dataclass
from stats.distributions import LognormalParams, NormalParams

@dataclass(frozen=True)
class DistributionPoints:
	x: list[float]
	y: list[float]

def pdf_normal(
        params: NormalParams, max:float, min:float, array_size: int = 500) -> DistributionPoints:
    '''Returns object of values (x and y) to draw normal curve.'''

    x_vals = np.linspace(min-100, max+100, array_size) #generate list of x-values
    y_vals = stats.norm.pdf(x=x_vals, loc=params.mean, scale=params.std)

    return DistributionPoints(x=x_vals, y=y_vals)


def pdf_lognormal(
        params: LognormalParams, max:float, min:float, array_size: int = 500) -> DistributionPoints:
    '''Returns object of values (x and y) to draw normal curve.'''

    x_vals = np.linspace(min-100, max+100, array_size) #generate list of x-values
    y_vals = stats.lognorm.pdf(x=x_vals, loc=params.loc, scale=params.scale, s=params.shape)

    return DistributionPoints(x=x_vals, y=y_vals)


def show_price_hist(
        df: pd.DataFrame, 
        bin_size: float | None = None, 
        dist_values: DistributionPoints | None = None,
        lines: dict | None = None
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
        scaled_y = dist_values.y * scale_factor

        plt.plot(dist_values.x, scaled_y)

    if lines: # plot array of lines, e.g. mean, median
        colours = plt.get_cmap("rainbow")
        num_lines = len(lines)
        
        for i, (key, val) in enumerate(lines.items()):
            # calculate normalized float between 0 and 1 for each line
            colour_fraction = i / max(1, num_lines - 1)
            
            plt.axvline(x=val, label=key, color=colours(colour_fraction))
        
        plt.legend()

    plt.show()

# Examples
def _example_visualisation(cleaned_df: pd.DataFrame) -> None:

    from .distributions import fit_to_lognormal, fit_to_normal

    simple_stats = cleaned_df["price"].describe()
    normal_params = fit_to_normal(cleaned_df)
    lognormal_params = fit_to_lognormal(cleaned_df)

    print(simple_stats)

    max = simple_stats["max"]
    min = simple_stats["min"]
    mean = simple_stats["mean"]
    std = normal_params.std

    lines_to_include = {
        "mean": mean,
        "mean+std": mean+std,
        "mean-std": mean-std,
        "q1": simple_stats["25%"],
        "q3": simple_stats["75%"],
    }

    normal_pdf = pdf_normal(normal_params, max=max, min=min)
    lognormal_pdf = pdf_lognormal(lognormal_params, max=max, min=min)

    show_price_hist(cleaned_df, dist_values=lognormal_pdf, lines=lines_to_include, bin_size=25)
    print(cleaned_df)

