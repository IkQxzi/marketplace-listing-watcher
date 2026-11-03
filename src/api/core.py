"""Functionality and base classes for any part of API."""

from pathlib import Path
from typing import Self

from pydantic import BaseModel, computed_field, field_validator, model_validator

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
        return self.item_dir / "data.csv"

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

    # Different from data path to not overwrite good data if failed
    @computed_field
    @property
    def fail_path(self) -> Path:
        return self.item_dir / f"{self._timestamp}_fail.json"

    @model_validator(mode="after")
    def create_dirs(self) -> Self:

        self.item_dir.mkdir(parents=True, exist_ok=True)
        return self
