'''Core functionality for all alert systems.'''

from typing import Protocol, Any
from dataclasses import dataclass


@dataclass
class ActiveListingInfo:
    title: str
    price: float
    url: str
    percentile: float
    timestamp: str # Match to API response type
    extra_info: str


# Bot, SMS service, etc.
class Alerter(Protocol):

    def build_message(self, list_info: ActiveListingInfo) -> Any:
        ...

    # Returns status code
    def alert(self, message: Any) -> int:
        ...


# Create later, Discord has specific formats
def create_message(list_info: ActiveListingInfo) -> str:
    raise NotImplementedError
