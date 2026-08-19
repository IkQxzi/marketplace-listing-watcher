"""Parsing sold listings."""

import pandas as pd
from bs4 import BeautifulSoup, Tag

from pathlib import Path

from config.dirs import LOG_DIR
from utils.io import generate_log_path, write_to_dir, write_df_to_dir


class ListingParser:
    def __init__(self, save_df=True, log_dir: Path = LOG_DIR) -> None:
        self.log_dir = log_dir
        self.save_df = save_df

    # TODO: Use more robust parsing
    def parse_sold_listings_html(
        self, item_name: str | None, html: str | Path
    ) -> pd.DataFrame:
        """
        Convert html of sold listings page into dataframe and return.
        Also logs df by default (see __init__ arguments).
        """

        # Try to infer item name from directory structure
        if not item_name:
            assert isinstance(html, Path), (
                f"Parameter html must be a Path object where item name is unspecified."
            )

            item_name = str(html.parent.name)
            print(f"Warning: item_name not specified, inferred as: {item_name}")

        # Handle both path and str
        if isinstance(html, Path):
            with html.open(encoding="utf-8") as html_f:
                soup = BeautifulSoup(html_f, "html.parser")
        else:
            soup = BeautifulSoup(html, "html.parser")

        parsed_items = []
        listings = soup.find_all(class_="su-card-container")  # add main page items
        second_listings = soup.find_all(class_="su-grid__item")

        if len(second_listings) > len(
            listings
        ):  # checking for different ebay website formats
            listings = second_listings

        for listing in listings:  # parse data
            # name
            name = self._safe_get_element_text(
                listing,
                classes=".su-item-card__title, .s-card__title, .su-item-card__header",
            )

            # url of item page
            url_el = listing.select_one(".s-card__link, .su-item-card__title")
            url = (
                url_el["href"].strip() if url_el and url_el.has_attr("href") else "N/A"
            )  # type: ignore

            # extract item id from url
            try:
                id = url.split("/itm/")[1].split("?")[0]
            except IndexError:
                id = "N/A"

            price = self._safe_get_element_text(
                listing, classes=".su-item-card__price, .s-card__price"
            )

            price_list = price.split(" ")
            price = price_list[-1]

            if price != "N/A":
                price = self._clean_price_str(price)

            # Not in fn to get ship price because it may be useful later
            listing_infos = listing.select(
                selector="div.s-card__attribute-row span.su-styled-text.secondary.large:not(large-1, s-card__price strikethrough)"
            )

            ship_price: str | float = self._get_ship_price(listing_infos)

            img_container = listing.select_one(
                ".su-card-container__media, .s-card__link, .su-image"
            )
            img_el = img_container.select_one("img") if img_container else None
            img_url = img_el["src"] if img_el and img_el.has_attr("src") else "N/A"

            # now parse big subtitle - contains condition, official item name, etc
            subtitle = self._safe_get_element_text(
                listing, classes=".su-item-card__subtitle, .s-card__subtitle"
            )

            # parse the sold substitle to extract sold date aswkk

            sold_date = self._safe_get_element_text(
                listing, classes=".s-card__caption, .su-styled-text.positive.default"
            )

            # TODO: explain what is going on here
            if sold_date != "N/A":
                sold_date = sold_date[6:]

            # Subtitle is made up of multiple parts separated by '.'

            # subtitle could really contain anything in any order.
            # ive seen GB for phones, phone name, company name, condition, etc, in different orders so cant reliably parse it here

            item_dict = {
                "title": name,
                "url": url,
                "id": id,
                "price": price,
                "ship_price": ship_price,
                "img_url": img_url,
                "sold_date": sold_date,
                "extra-info": subtitle,
            }

            parsed_items.append(item_dict)

        parsed_items_df = pd.DataFrame(parsed_items)

        if self.save_df:
            dir = generate_log_path(self.log_dir, item_name, is_active=False)
            write_df_to_dir(parsed_items_df, dir)

        return parsed_items_df

    def _safe_get_element_text(
        self, element: Tag, classes: str, fallback: str = "N/A"
    ) -> str:
        """Get the stripped text of an element if it exists, with fallback."""

        sub_element = element.select_one(classes)
        return rf"{sub_element.text.strip()}" if sub_element else fallback

    def _get_ship_price(
        self, listing_infos: list[Tag], fallback: str = "N/A"
    ) -> float | str:
        """Return the raw string from the element containing the shipping price information, with fallback."""

        if len(listing_infos) == 0:
            return fallback

        # There are multiple elements with identical classes,
        # so searching text is necessary
        for info in listing_infos:
            # +£<amount> is its own element
            if "+£" in info.text:
                raw_ship_str = info.text.strip().removesuffix(" delivery")
                return float(raw_ship_str[2:])

            # Otherwise, Free Delivery
            elif "free delivery" in info.text.lower():
                return float(0)

        return fallback

    # TODO: fix, fragile and depends on strange character being present
    def _clean_price_str(self, price_str: str) -> str:

        replacements = str.maketrans({"£": "", ",": ""})
        cleaned_price_str = price_str[1:].translate(
            replacements
        )  # First char is strange

        return cleaned_price_str
