"""Configuration settings for the Google Trends CLI tool."""

import os
from enum import Enum
from pathlib import Path

# Default configurations
DEFAULT_REGION = "US"  # Will be overridden by IP-based location when possible
DEFAULT_TIMEFRAME = "today 1-d"  # Last 24 hours
DEFAULT_CATEGORY = "0"  # All categories
DEFAULT_OUTPUT_FORMAT = "text"
DEFAULT_SUGGESTIONS_COUNT = 10
DEFAULT_EXPORT_PATH = Path.home() / "gtrends-exports"

# Ensure export directory exists
os.makedirs(DEFAULT_EXPORT_PATH, exist_ok=True)

# Category mappings for content creators
CONTENT_CATEGORIES = {
    "books": "22",  # Books & Literature
    "news": "16",  # News
    "arts": "5",  # Arts & Entertainment
    "fiction": "22",  # Books & Literature (we'll filter further in code)
    "culture": "3",  # Arts & Entertainment - Performing Arts
    "all": "0",  # All categories
}

# Region code mappings (partial list, will be expanded)
REGION_CODES = {
    "yemen": "YE",
    "us": "US",
    "uk": "GB",
    "uae": "AE",
    "saudi": "SA",
    "egypt": "EG",
    "global": "",  # Empty string for global
}

# Time periods for showcases


class BatchPeriod(str, Enum):
    Past4H = "custom_4h"
    Past24H = "custom_1d"
    Past48H = "custom_2d"
    Past7D = "custom_7d"
