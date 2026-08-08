'''
Full data pipeline from file to ready-to-analyse data.
Use before experimentation in personal notebooks.
'''

import pandas as pd

from pathlib import Path

from utils.io import read_df_from_path
from config.filters import FilterConfig
from stats.cleaning import (
    drop_empty_records, remove_trailing_name_text, 
    keep_records_containing, remove_records_containing, 
    remove_trailing_name_text, conv_dates, set_date_as_index,
    replace_null_shipping_with_avg, sum_price_and_shipping
    )


def get_cleaned_df(csv_path: Path, filter_conf: FilterConfig) -> pd.DataFrame:
    '''Load & return cleaned df.'''

    raw_df = read_df_from_path(csv_path)

    clean_df = (
    raw_df
    .pipe(drop_empty_records)
    .pipe(remove_trailing_name_text)
    .pipe(keep_records_containing, filter_conf)
    .pipe(remove_records_containing, filter_conf)
    .pipe(conv_dates)
    .pipe(set_date_as_index)
    .pipe(replace_null_shipping_with_avg)
    .pipe(sum_price_and_shipping)
    )

    assert len(set(clean_df['id'])) == len(list(clean_df['id'])), "IDs of cleaned df are non-unique!"

    return clean_df
