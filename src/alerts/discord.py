"""Discord bot implementations."""

import logging
from typing import Any

import requests

from api import Listing

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DiscordBot:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def alert(self, listings: list[Listing]) -> int:
        """Build and send the messages containing all the listings."""

        message = self._build_message(listings)
        status_code = self._send_message(message)

        return status_code

    def _build_message(self, listings: list[Listing]) -> dict[str, Any]:
        """Build the message to be sent by the bot."""

        embeds: list[dict[str, Any]] = []

        for listing in listings:
            embeds.append(
                {
                    "title": f"{listing.title}",
                    "fields": [
                        {"name": "Web URL", "value": str(listing.web_url)},
                        {
                            "name": "Origin Time",
                            "value": f"{listing.item_origin_date.isoformat()}",
                        },
                        {
                            "name": "Total Price",
                            "value": f"£{listing.total_price or 'N/A'}",
                        },
                        {
                            "name": "Total Bid Price",
                            "value": f"£{listing.total_bid_price or 'N/A'}",
                        },
                        {
                            "name": "Shipping Price",
                            "value": f"£{listing.shipping_price or 0}",
                        },
                    ],
                }
            )

        message = {  # message to be sent by bot
            "username": "Alerter",
            "embeds": embeds,
        }

        return message

    def _send_message(self, message: dict[str, str | list]) -> int:
        """
        Send a message to webhook and return status code.
        Raises RuntimeError if response is not 2xx.
        """

        r = requests.post(self.webhook_url, json=message)

        logging.debug(
            f"response code: {r.status_code}\n response text: {r.text or 'N/A'}"
        )
        if str(r.status_code)[0] != "2":
            raise RuntimeError("Unexpected response from Discord.")

        return r.status_code
