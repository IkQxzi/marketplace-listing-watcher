"""Functionality and base classes for any part of API."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Self

from pydantic import BaseModel, computed_field, field_validator, model_validator

from api.listings import Listing
from config.dirs import ACTIVE_DIR
from utils.misc import get_timestamp

# ---------------------------- Dataclasses ----------------------------


class SearchEndpointSavePaths(BaseModel):
    payload_hash: int
    base_dir: Path = ACTIVE_DIR

    _timestamp: str = get_timestamp()

    @field_validator("base_dir", mode="after")
    def create_base_dir(cls, v: Path) -> Path:
        if not v.exists():
            v.mkdir(parents=True)

        return v

    @computed_field
    @property
    def item_dir(self) -> Path:
        return self.base_dir / str(self.payload_hash)

    @computed_field
    @property
    def data_path(self) -> Path:
        return self.item_dir / "data.jsonl"  # yh we use jsonl now

    # Unique to each request
    @computed_field
    @property
    def metadata_path(self) -> Path:
        return self.item_dir / f"{self._timestamp}_metadata.json"

    @computed_field
    @property
    def config_path(self) -> Path:
        return self.item_dir / "config.json"

    @computed_field
    @property
    def raw_response_path(self) -> Path:
        return self.item_dir / f"{self._timestamp}_raw.json"

    @model_validator(mode="after")
    def create_dirs(self) -> Self:

        self.item_dir.mkdir(parents=True, exist_ok=True)
        return self


# ---------------------------- Saving ----------------------------
def write_listings_to_data_path(
    listings: list[Listing], data_path: Path, append=True
) -> None:
    """
    Write listings to data path specified.\n
    Defaults to appending, set append = False to overwrite.\n
    Does not sort the listings or remove duplicates.\n
    """
    listing_jsons = [Listing.model_dump_json(listing) for listing in listings]

    mode = "a" if append else "w"
    with data_path.open(mode) as f:
        logging.debug(f"Writing data to {data_path}")
        f.write("\n".join(listing_jsons) + "\n")


# ---------------------------- Loading ----------------------------


def read_listings_from_path(data_path: Path, count: int | None = None) -> list[Listing]:
    """Load a number of listings from data path. Loads top down."""

    with data_path.open(mode="r", encoding="utf-8") as f:
        all_listings = [
            Listing.model_validate_json(clean_line)
            for line in f.readlines()
            if (clean_line := line.strip())
        ]

        # TODO: rewrite to actually be more efficient
        if count:
            return all_listings[-count:]

        return all_listings


def read_latest_listing_timestamp(data_path: Path, oldest_first=True) -> datetime:
    """
    Gets latest timestamp from newest listing at data path.\n
    Defaults to oldest first.
    """

    # TODO: use seek() to jump to end
    with data_path.open(mode="r", encoding="utf-8") as f:
        if oldest_first:
            latest_listing_json = f.readlines()[-1].strip()
        else:
            latest_listing_json = f.readline().strip()

        # Should ensure datetime on its own
        latest_timestamp = Listing.model_validate_json(
            latest_listing_json
        ).item_creation_date
        logging.debug(f"Latest timestamp requested: {latest_timestamp.isoformat()}")

    return latest_timestamp
