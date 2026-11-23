import pytest

from marketplace_listing_watcher.alerts.discord import DiscordBot
from marketplace_listing_watcher.api import Listing
from marketplace_listing_watcher.api.searching import ListingSearcher
from marketplace_listing_watcher.config.alerts import DISCORD_WEBHOOK_URL
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
    messages = bot._build_messages(listings)

    for i, message in enumerate(messages):
        for j, embed in enumerate(message["embeds"]):
            ind = 10 * i + j
            assert embed["title"] == listings[ind].title
            assert any(
                field["value"] == str(listings[ind].web_url)
                for field in embed["fields"]
            )
