'''Directories.'''

from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent

CONFIG_DIR = ROOT_DIR / "configs"
LOG_DIR = ROOT_DIR / "logs"
SOLD_DIR = LOG_DIR / "sold"
ACTIVE_DIR = LOG_DIR / "active" # /search/catId_catName
ENV_PATH = ROOT_DIR / "used.env"

# Temporary
TEMP_LOG_DIR = ROOT_DIR / "temp_logs"
TEMP_SOLD_DIR = TEMP_LOG_DIR / "sold"
TEMP_ACTIVE_DIR = TEMP_LOG_DIR / "active"