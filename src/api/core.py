"""Functionality and base classes for any part of API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, BaseModel, computed_field, model_validator
from config.dirs import ACTIVE_DIR
from utils.misc import get_timestamp

# ---------------------------- Dataclasses ----------------------------


class SearchEndpointSavePaths(BaseModel):
    payload_hash: int
    base_dir: Path = ACTIVE_DIR

    @computed_field
    @property
    def item_dir(self) -> Path:
        return self.base_dir / str(self.payload_hash)

    @computed_field
    @property
    def data_path(self) -> Path:
        return self.item_dir / "data.json"

    @computed_field
    @property
    def metadata_path(self) -> Path:
        return self.item_dir / "metadata.json"

    @computed_field
    @property
    def config_path(self) -> Path:
        return self.item_dir / "config.json"

    @computed_field
    @property
    def raw_response_path(self) -> Path:
        return self.item_dir / f"{get_timestamp()}_raw.json"

    @model_validator(mode="after")
    def create_dirs(self) -> Self:

        self.item_dir.mkdir(parents=True, exist_ok=True)
        return self


# ---------------------------- Custom Types ----------------------------
# TODO: add PostCode
# itemId
# marketplaceId

Price = Annotated[float, Field(ge=0)]
Currency = Annotated[str, Field(min_length=3, max_length=3)]  # TODO: verify ISO 4127
CountryCode = Annotated[str, Field(min_length=2, max_length=2)]  # TODO; verify ISO wtv
Percentage = Annotated[float, Field(ge=0, le=100)]
Epid = Annotated[str, Field(min_length=11, max_length=11)]
