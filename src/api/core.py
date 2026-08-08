'''Functionality and base classes for any part of API.'''

from dataclasses import dataclass
from typing import Any


@dataclass
class APIResponse:
    json_response: Any
    item_name: str
    cat_id: int
    cat_name: str
