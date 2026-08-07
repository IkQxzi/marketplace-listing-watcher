'''Various filters to be used across scraper, data-cleaning, API.'''

from dataclasses import dataclass


@dataclass
class FilterConfig:
    required_txts: list[str] | None = None
    req_txts_case_sensitive: bool = False
    banned_txts: list[str] | None = None
    ban_txt_case_sensitive: bool = False
