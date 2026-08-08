'''Discord bot implementations.'''

import requests
from typing import Any

from utils.misc import get_text_timestamp
from .core import Alerter, ActiveListingInfo


class DiscordBot(Alerter):

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url


    def alert(self, list_info: ActiveListingInfo) -> int:

        message = self._build_message(list_info)
        status_code = self._send_message(message)

        return status_code
    

    def _build_message(self, list_info: ActiveListingInfo) -> dict[str, Any]:

        message = { #message to be sent by bot
                    "username": "Alerter",
                    "embeds": [
                        {
                            "title": f"{list_info.title}",
                            "url": list_info.url, 
                            "fields": [
                                {"name": "Time", "value": f"{list_info.timestamp}"},
                                {"name": "Price", "value": f"£{list_info.price:.2f}"},
                                {"name": "Percentile", "value": f"£{list_info.percentile:.1f}"}
                            ],
                        }
                    ]
                }         

        return message


    def _send_message(self, message: dict[str, Any]) -> int:

        response = requests.post(self.webhook_url, json=message)
        return response.status_code
    
