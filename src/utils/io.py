'''
Universal I/O functions.
Note that utf-8 encoding is required to support emojis.
'''

from pandas import DataFrame, read_csv

import json
from pathlib import Path

from utils.misc import get_timestamp


# TODO: Rewrite this to not require is_active flag (pass in sold/active as log_dir)
def generate_log_path(
    log_dir: Path, item_name: str, is_active: bool,
    cat_id: int | None = None, cat_name: str | None = None
    ) -> Path:

    '''Generate path for use in saving for scraper/API.'''
    
    if is_active:
        base_path = log_dir / "active"
    else:
        base_path = log_dir / "sold"
    
    if cat_id or cat_name:
        assert cat_id and cat_name, "Generating log path requires both cat ID and name."

        base_path = base_path / f"{cat_id}_{cat_name}"
    
    final_path = base_path / item_name

    return final_path


def get_latest_search_json(directory: Path, search: str) -> Path:
    '''Get the Path object of the latest json for a given search in a given directory.'''

    search_json_gen = Path(directory).rglob(f"{search}/*.json")
    latest_search = max(f for f in search_json_gen)
    
    return latest_search


def read_df_from_path(data_file: Path) -> DataFrame:
    '''Read df from a file, assuming first col. is index'''
    
    with data_file.open('r', encoding='utf-8') as f:
        df = read_csv(f, index_col=0)

    return df


def write_to_dir(content: str, dir: Path, file_ext: str) -> None:
    '''
    Log content to a directory, with the filename being a timestamp ending in specified file extension.\n
    Creates directory if it does not exist.
    '''

    # Ensure file_ext begins with dot
    if file_ext[0] != '.':
        file_ext = '.' + file_ext

    # Create file
    dir.mkdir(parents=True, exist_ok=True)
    file_path = (dir / get_timestamp()).with_suffix(file_ext)

    print(f'Writing to file: {str(file_path)}')

    if file_ext == '.json':
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(content, f, indent=4)
        return

    with file_path.open('w', encoding='utf-8') as f:
        f.write(content)
        
    return

def write_df_to_dir(df: DataFrame, dir: Path) -> None:
    '''Write df to directory, creating dir if it does not exist.'''

    dir.mkdir(parents=True, exist_ok=True)
    df_path = (dir / get_timestamp()).with_suffix('.csv') 

    df.to_csv(df_path)

    print(f'Saved df to path: {df_path}')
