"""API keys for LLMs."""

import os

from dotenv import load_dotenv

from .dirs import ENV_PATH

load_dotenv(ENV_PATH)
GEMINI_API_KEY = os.getenv("gemini_api_key")
OPENROUTER_API_KEY = os.getenv("openrouter_api_key")
