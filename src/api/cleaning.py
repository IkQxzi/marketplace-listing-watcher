"""Cleaning raw API response into clean listing objects."""

from pydantic import BaseModel, computed_field

from .schemas import SearchEndpointResponse


class Listing(BaseModel):
    """Class for an individual listing."""

    price: float
    shipping_price: float

    @computed_field
    @property
    def total_price(self) -> float:
        return self.price + self.shipping_price

    ...


def clean_listings(response: SearchEndpointResponse) -> list[Listing]:
    """Clean the API response and return a list of Listing objects"""
    raise NotImplementedError
