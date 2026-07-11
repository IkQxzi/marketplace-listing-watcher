'''
Universal I/O functions.
Note that utf-8 encoding is required to support emojis.
'''

from pandas import DataFrame

from pathlib import Path
import os
import json

from utils.misc import get_timestamp


def get_latest_search_json(directory: Path, search: str) -> Path:
    '''Get the Path object of the latest json for a given search in a given directory.'''

    search_json_gen = Path(directory).rglob(f"{search}/*.json")
    latest_search = max(f for f in search_json_gen)
    
    return latest_search


def _confirm_dir_exists(directory: str) -> None:
    '''Create a directory if it does not exist, otherwise do nothing.'''

    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_dir(content, directory: str, file_ext: str) -> None:
    '''
    Log content to a directory, with the filename being a timestamp ending in specified file extension.\n
    Creates directory if it does not exist.
    '''

    _confirm_dir_exists(directory)

    file_path = f'{directory}/{get_timestamp()}'

    # Ensure no dot in ext
    if file_ext[0] == '.':
        file_ext = file_ext[1:]
    
    print(f'Saving file to {file_path}.{file_ext}')
    
    if file_ext == 'json':
        with open(f'{file_path}.{file_ext}', 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4)
        return
    
    with open(f'{file_path}.{file_ext}', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return
        

def write_df_to_dir(df: DataFrame, directory: str) -> None:

    _confirm_dir_exists(directory)

    df_path = f"{directory}/{get_timestamp()}.csv" 
    df.to_csv(df_path)

    print(f'Saved df to path: {df_path}')
