"""Helper utilities and functions."""

import locale
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from gtrends.config import DEFAULT_EXPORT_PATH, DEFAULT_TIMEFRAME


def determine_locale() -> str:
    """Determine the user's locale for region detection.

    Returns:
        Two-letter locale code
    """
    try:
        # Try to get from environment
        env_lang = os.environ.get("LANG", "")
        if env_lang and "_" in env_lang:
            return env_lang.split("_")[1].split(".")[0].upper()

        # Try to get from locale module
        loc = locale.getlocale()[0]
        if loc and "_" in loc:
            return loc.split("_")[1].upper()
    except Exception:
        pass

    # Default fallback
    return "US"


def validate_region_code(region_code: str) -> str:
    """Validate and normalize a region code.

    Args:
        region_code: Two-letter country code

    Returns:
        Normalized region code
    """
    if not region_code:
        return determine_locale()

    # Normalize to uppercase
    region_code = region_code.upper()

    return region_code


def validate_export_path(path: Optional[str] = None) -> Path:
    """Validate and create export path if needed.

    Args:
        path: Path string or None for default

    Returns:
        Path object for the export directory
    """
    if not path:
        export_path = DEFAULT_EXPORT_PATH
    else:
        export_path = Path(path).expanduser().resolve()

    # Create directory if it doesn't exist
    os.makedirs(export_path, exist_ok=True)

    return export_path


def parse_timeframe(timeframe: str) -> str:
    """Parse and validate a timeframe string for TrendsPy.

    Args:
        timeframe: Time range for data

    Returns:
        Valid timeframe string
    """

    # Check for valid time formats

    # 1. Standard format: 'now X-Y' or 'today X-Y'
    if timeframe.startswith(("now ", "today ")):
        parts = timeframe.split(" ")
        if len(parts) == 2:
            # Validate time specification (e.g., "1-H", "3-m", etc.)
            time_spec = parts[1]
            if "-" in time_spec:
                number, unit = time_spec.split("-")
                if number.isdigit() and unit in ["H", "h", "d", "m", "y"]:
                    return timeframe

    # 2. Date range format: 'YYYY-MM-DD YYYY-MM-DD'
    if " " in timeframe and timeframe.count("-") >= 2:
        parts = timeframe.split(" ")
        if len(parts) == 2:
            try:
                # Try to parse the dates
                start_date = datetime.strptime(parts[0], "%Y-%m-%d")
                end_date = datetime.strptime(parts[1], "%Y-%m-%d")

                # Valid if start is before end and within reasonable range
                if start_date < end_date and (end_date - start_date) < timedelta(days=3650):
                    return timeframe
            except ValueError:
                pass

    # 3. Hourly precision: 'YYYY-MM-DDThh YYYY-MM-DDThh'
    if " " in timeframe and "T" in timeframe:
        parts = timeframe.split(" ")
        if len(parts) == 2 and "T" in parts[0] and "T" in parts[1]:
            try:
                # Try to parse the timestamps
                start_time = datetime.strptime(parts[0], "%Y-%m-%dT%H")
                end_time = datetime.strptime(parts[1], "%Y-%m-%dT%H")

                # Valid if start is before end and within reasonable range
                if start_time < end_time and (end_time - start_time) < timedelta(days=8):
                    return timeframe
            except ValueError:
                pass

    # 4. Date with offset: 'YYYY-MM-DD X-Y'
    if " " in timeframe and "-" in timeframe:
        parts = timeframe.split(" ")
        if len(parts) == 2:
            try:
                # Try to parse the date
                start_date = datetime.strptime(parts[0], "%Y-%m-%d")

                # Validate offset
                offset = parts[1]
                if "-" in offset:
                    number, unit = offset.split("-")
                    if number.isdigit() and unit in ["d", "m", "y"]:
                        return timeframe
            except ValueError:
                pass

    # 5. Special case: 'all'
    if timeframe.lower() == "all":
        return "all"

    # If no valid format detected, return default
    return DEFAULT_TIMEFRAME


def format_region_name(region_code: str) -> str:
    """Format region code as a readable name.

    Args:
        region_code: Two-letter country code

    Returns:
        Human-readable region name
    """
    # Map of common region codes to names
    region_names = {
        "US": "United States",
        "GB": "United Kingdom",
        "AE": "United Arab Emirates",
        "SA": "Saudi Arabia",
        "EG": "Egypt",
        "CA": "Canada",
        "AU": "Australia",
        "IN": "India",
        "FR": "France",
        "DE": "Germany",
        "YE": "Republic of Yemen",
        "": "Global",
    }

    return region_names.get(region_code, region_code)
