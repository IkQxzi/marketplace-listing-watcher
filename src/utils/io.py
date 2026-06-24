from pathlib import Path


def get_latest_search_json(directory: Path, search: str) -> Path:
    '''Get the Path object of the latest json for a given search in a given directory.'''

    search_json_gen = Path(directory).rglob(f"{search}/*.json")
    latest_search = max(f for f in search_json_gen)
    
    return latest_search
