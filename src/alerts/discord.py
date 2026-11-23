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
        """
        Build and send the messages containing all the listings.
        """

        messages = self._build_messages(listings)
        status_code = self._send_messages(messages)

        return status_code

    def _build_messages(self, listings: list[Listing]) -> list[dict[str, Any]]:
        """
        Build the messages to be sent by the bot.
        Splits into groups of 10 listings to not hit character limit.
        """

        embeds_list: list[list[dict[str, Any]]] = [[]]
        j = -1

        for i, listing in enumerate(listings):
            if i % 10 == 0:
                j += 1

            # Ensure embeds list always has an arr at j
            if len(embeds_list) < j + 1:
                embeds_list.append([])

            embeds_list[j].append(
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
                            "value": f"£{listing.total_price:.2f}"
                            if listing.total_price
                            else "N/A",
                        },
                        {
                            "name": "Total Bid Price",
                            "value": f"£{listing.total_bid_price:.2f}"
                            if listing.total_bid_price
                            else "N/A",
                        },
                        {
                            "name": "Shipping Price",
                            "value": f"£{listing.shipping_price:.2f}"
                            if listing.shipping_price
                            else str(0),
                        },
                    ],
                }
            )

        messages = [
            {
                "username": "Alerter",
                "embeds": embeds,
            }
            for embeds in embeds_list
        ]

        return messages

    def _send_messages(self, messages: list[dict[str, str | list]]) -> int:
        """
        Send messages to webhook and return status code of latest response.
        Raises RuntimeError if any singular response is not 2xx.
        """

        for message in messages:
            r = requests.post(self.webhook_url, json=message)

            if str(r.status_code)[0] != "2":
                raise RuntimeError("Unexpected response from Discord.")

            logging.debug(
                f"Sent {len(message.get('embeds'))} messages\n"
                f"response code: {r.status_code}\n"
                f"response text: {r.text or 'N/A'}"
            )

        return r.status_code
