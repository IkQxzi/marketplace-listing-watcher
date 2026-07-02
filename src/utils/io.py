from pathlib import Path
import os
import json

from utils.misc import get_timestamp


def get_latest_search_json(directory: Path, search: str) -> Path:
    '''Get the Path object of the latest json for a given search in a given directory.'''

    search_json_gen = Path(directory).rglob(f"{search}/*.json")
    latest_search = max(f for f in search_json_gen)
    
    return latest_search


def log_file(content, directory: str, is_json = False) -> None:
    '''Log a file to a directory, with the filename being a timestamp.'''

    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = get_timestamp()
    file_path = f'{directory}/{timestamp}'

    if is_json:
        with open(f'{file_path}.json', 'w') as f:
            json.dump(content, f, indent=4)
        return
    
    with open(f'{file_path}.txt', 'w') as f:
        f.write(content)
    
    return
        