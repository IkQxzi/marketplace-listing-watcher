"""Various filters to be used across parser, data-cleaning, API."""

from pydantic import BaseModel, Field
from dataclasses import dataclass

@dataclass
class FilterConfig:
    required_txts: list[str] | None = None
    req_txts_case_sensitive: bool = False
    banned_txts: list[str] | None = None
    ban_txt_case_sensitive: bool = False


class LLMOutputFilters(BaseModel):
    required_keywords: list[str] = Field(description="Words that must appear in the title to match the exact target model.")
    banned_keywords: list[str] = Field(description="Words to exclude: tier variants, wrong storage, accessories, damage, locks.")
    min_reasonable_price: float = 0.0 #sets this as default value
    product_name: str
