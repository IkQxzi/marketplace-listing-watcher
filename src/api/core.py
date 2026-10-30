"""Functionality and base classes for any part of API."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchEndpointSavePaths:
    item_dir: Path
    data_path: Path
    metadata_path: Path
    config_path: Path
    raw_response_path: Path
