"""Functionality and base classes for any part of API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import Field

# ---------------------------- Dataclasses ----------------------------


@dataclass
class SearchEndpointSavePaths:
    item_dir: Path
    data_path: Path
    metadata_path: Path
    config_path: Path
    raw_response_path: Path


# ---------------------------- Custom Types ----------------------------
# TODO: add PostCode
# itemId
# marketplaceId

Price = Annotated[float, Field(ge=0)]
Currency = Annotated[str, Field(min_length=3, max_length=3)]  # TODO: verify ISO 4127
CountryCode = Annotated[str, Field(min_length=2, max_length=2)]  # TODO; verify ISO wtv
Percentage = Annotated[float, Field(ge=0, le=100)]
Epid = Annotated[str, Field(min_length=11, max_length=11)]
