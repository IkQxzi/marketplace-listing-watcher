'''API keys for bots, webhook URLs, etc.'''

import os
from dotenv import load_dotenv

from .dirs import ENV_PATH

load_dotenv(ENV_PATH)

DISCORD_WEBHOOK_URL = os.getenv('webhook_url')