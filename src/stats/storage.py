'''Storing/retrieving stats data.'''

from utils.io import write_df_to_dir, read_multiple_df
from utils.misc import get_timestamp
from utils.config import TEMP_STATS_DIR

import pandas as pd

def save_stats(df:pd.DataFrame, product_name:str, col:str) -> None:
    '''Takes a dataframe and saves the summary stats for it in a CSV.'''

    #TODO: decide properly on which stats to save here 
    #TODO: maybe pass directory here as well

    data = df[col].describe().to_dict() #get summary stats
    stats_df = pd.DataFrame(data, index=[0])

    stats_df["timestamp"] = get_timestamp()
    stats_df["column_name"] = col

    file_path = TEMP_STATS_DIR / product_name

    write_df_to_dir(stats_df, file_path)


def read_all_stats(product_name:str, col:str) -> pd.DataFrame:
    '''Takes a product and column name and returns DF with all stats'''

    directory = TEMP_STATS_DIR / product_name

    data = read_multiple_df(directory)
    data = data[data["column_name"] == col]

    return data


def read_recent_stats(product_name:str) -> pd.DataFrame:
    '''Takes a product name and returns DF with most recent stats'''

    directory = TEMP_STATS_DIR / product_name
    
    data = read_multiple_df(directory)
    data = data.sort_values(by="timestamp")

    return data.tail(1) #return first (most recent) row