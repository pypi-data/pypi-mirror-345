"""Tests for utility functions."""

from unittest.mock import patch

from gtrends.utils import (
    determine_locale,
    format_region_name,
    parse_timeframe,
    validate_export_path,
    validate_region_code,
)


class TestUtils:
    """Test utility functions."""

    @patch("gtrends.utils.locale.getlocale")
    @patch("os.environ.get")
    def test_determine_locale(self, mock_env_get, mock_getlocale):
        """Test locale determination."""
        # Test with environment variable
        mock_env_get.return_value = "en_US.UTF-8"
        mock_getlocale.return_value = (None, None)

        result = determine_locale()
        assert result == "US"

        # Test with locale module
        mock_env_get.return_value = None
        mock_getlocale.return_value = ("en_GB", "UTF-8")

        result = determine_locale()
        assert result == "GB"

        # Test fallback
        mock_env_get.return_value = None
        mock_getlocale.return_value = (None, None)

        result = determine_locale()
        assert result == "US"

    def test_validate_region_code(self):
        """Test region code validation."""
        # Test with valid code
        assert validate_region_code("us") == "US"
        assert validate_region_code("GB") == "GB"

        # Test with empty code (should use determine_locale)
        with patch("gtrends.utils.determine_locale", return_value="XX"):
            assert validate_region_code("") == "XX"

    def test_validate_export_path(self, tmp_path):
        """Test export path validation."""
        # Test with specific path
        test_path = tmp_path / "exports"
        result = validate_export_path(str(test_path))

        assert result == test_path
        assert test_path.exists()

        # Test with None (should use default path)
        with patch("gtrends.utils.DEFAULT_EXPORT_PATH", tmp_path / "default"):
            result = validate_export_path(None)
            assert result == tmp_path / "default"
            assert (tmp_path / "default").exists()

    def test_parse_timeframe(self):
        """Test timeframe parsing."""
        # Test standard formats
        assert parse_timeframe("now 1-H") == "now 1-H"
        assert parse_timeframe("today 3-m") == "today 3-m"

        # Test date range
        assert parse_timeframe("2023-01-01 2023-12-31") == "2023-01-01 2023-12-31"

        # Test invalid format (should return default)
        with patch("gtrends.utils.DEFAULT_TIMEFRAME", "default_timeframe"):
            assert parse_timeframe("invalid format") == "default_timeframe"

    def test_format_region_name(self):
        """Test region name formatting."""
        assert format_region_name("US") == "United States"
        assert format_region_name("GB") == "United Kingdom"
        assert format_region_name("XYZ") == "XYZ"  # Unknown code returns itself
        assert format_region_name("") == "Global"
