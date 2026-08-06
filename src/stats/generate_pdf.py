import numpy as np
from scipy import stats

def pdf_normal(
        params: object, max:float, min:float, array_size: int = 500) -> object:
    '''Returns object of values (x and y) to draw normal curve.'''

    x_vals = np.linspace(min-100, max+100, array_size) #generate list of x-values
    y_vals = stats.norm.pdf(x=x_vals, loc=params["mean"], scale=params["std"])

    return {
        "x":x_vals,
        "y":y_vals
    }

def pdf_lognormal(
        params: object, max:float, min:float, array_size: int = 500) -> object:
    '''Returns object of values (x and y) to draw normal curve.'''

    x_vals = np.linspace(min-100, max+100, array_size) #generate list of x-values
    y_vals = stats.lognorm.pdf(x=x_vals, loc=params["loc"], scale=params["scale"], s=params["shape"])

    return {
        "x":x_vals,
        "y":y_vals
    }