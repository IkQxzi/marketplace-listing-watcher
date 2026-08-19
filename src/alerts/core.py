"""Core functionality for all alert systems."""

from typing import Protocol, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ActiveListingInfo:
    title: str
    price: float
    url: str
    percentile: float
    timestamp: str  # Match to API response type
    extra_info: str


# Bot, SMS service, etc.
class Alerter(Protocol):
    # Returns status code
    def alert(self, list_info: ActiveListingInfo) -> int: ...


# Create later, Discord has specific formats
def create_message(list_info: ActiveListingInfo) -> str:
    raise NotImplementedError
