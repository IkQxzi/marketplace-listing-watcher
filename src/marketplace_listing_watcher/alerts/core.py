"""Core functionality for all alert systems."""

from typing import Protocol

from marketplace_listing_watcher.api.listings import Listing


# Bot, SMS service, etc.
class Alerter(Protocol):
    # Returns status code
    def alert(self, listings: list[Listing]) -> int: ...


# Create later, Discord has specific formats
def create_message(listings: list[Listing]) -> str:
    raise NotImplementedError
