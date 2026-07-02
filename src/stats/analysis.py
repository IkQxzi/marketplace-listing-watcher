
import pandas as pd

import json 
from pathlib import Path

from utils.config import TEMP_ACTIVE_DIR

def do_stats(data_file: Path) -> None:
    
    with data_file.open('r') as f:
        df = pd.read_json(f)

        breakpoint()


'''
Create df from latest data
Get outliers
Display good listings
'''