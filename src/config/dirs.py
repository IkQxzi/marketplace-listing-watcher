"""Directories."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = ROOT_DIR / "configs"
DATA_DIR = ROOT_DIR / "data"
SOLD_DIR = DATA_DIR / "sold"
ACTIVE_DIR = DATA_DIR / "active"  # /search/catId_catName
ENV_PATH = ROOT_DIR / ".env"

# Temporary
TEMP_DATA_DIR = ROOT_DIR / "temp_data"
TEMP_SOLD_DIR = TEMP_DATA_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_DATA_DIR / "active"
TEMP_STATS_DIR = TEMP_DATA_DIR / "stats"
