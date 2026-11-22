from api.searching import ListingSearcher
import pytest

from alerts.discord import DiscordBot
from api import Listing
from config.alerts import DISCORD_WEBHOOK_URL
from config.alerts import DISCORD_WEBHOOK_URL
from tests.data.api.listings import EXAMPLE_LISTING_ARGS


@pytest.mark.alert
def test_discord_alert_returns_2xx():
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("Webhook URL required this test")

    bot = DiscordBot(DISCORD_WEBHOOK_URL)

    listings = [
        Listing(
            **{**EXAMPLE_LISTING_ARGS, "web_url": f"https://example/com/listing{i}"}
        )
        for i in range(3)
    ]

    status_code = bot.alert(listings)
    assert str(status_code)[0] == "2"


@pytest.mark.api
def test_discord_message_constructed_correctly_by_searcher(
    load_access_token, form_payload, tmp_path
):
    payload = form_payload()

    if not DISCORD_WEBHOOK_URL:
        raise ValueError("Discord webhook URL missing from env.")

    bot = DiscordBot(DISCORD_WEBHOOK_URL)
    searcher = ListingSearcher(payload=payload, active_listing_dir=tmp_path)
    access_token = load_access_token()

    listings = searcher.get_latest_listings_and_alert(access_token)
    message = bot._build_message(listings)
    for embed, listing in zip(message["embeds"], listings):
        assert embed["title"] == listing.title
        assert any(field["value"] == str(listing.web_url) for field in embed["fields"])
