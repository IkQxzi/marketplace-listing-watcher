"""Core functionality for all alert systems."""

from datetime import datetime
from typing import Protocol

from marketplace_listing_watcher.api.listings import Listing


# Bot, SMS service, etc.
class Alerter(Protocol):
    # Returns status code
    def alert(self, listings: list[Listing], timestamp: datetime) -> int: ...
