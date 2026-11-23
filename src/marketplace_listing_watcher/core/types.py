"""Custom types for use with both sold listings from web interface and active listings from API."""

from typing import Annotated, Literal

from pydantic import Field

# TODO: add PostCode
# itemId
# marketplaceId

# Better to go here for easier sold listing filtering later
type buyingOption = Literal["FIXED_PRICE", "AUCTION", "BEST_OFFER", "CLASSIFIED_AD"]

Price = Annotated[float, Field(ge=0)]
Currency = Annotated[str, Field(min_length=3, max_length=3)]  # TODO: verify ISO 4127
CountryCode = Annotated[str, Field(min_length=2, max_length=2)]  # TODO; verify ISO wtv
Percentage = Annotated[float, Field(ge=0, le=100)]
Epid = Annotated[str, Field(min_length=11, max_length=11)]
