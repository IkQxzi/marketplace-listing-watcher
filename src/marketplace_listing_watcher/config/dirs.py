"""Directories."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

CONFIG_DIR = ROOT_DIR / "configs"
FILTER_DIR = ROOT_DIR / "filters"
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
ENV_PATH = ROOT_DIR / ".env"

SOLD_DIR = DATA_DIR / "sold"
ACTIVE_DIR = DATA_DIR / "active"

# Temporary
TEMP_DATA_DIR = ROOT_DIR / "temp_data"
TEMP_SOLD_DIR = TEMP_DATA_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_DATA_DIR / "active"
TEMP_STATS_DIR = TEMP_DATA_DIR / "stats"
