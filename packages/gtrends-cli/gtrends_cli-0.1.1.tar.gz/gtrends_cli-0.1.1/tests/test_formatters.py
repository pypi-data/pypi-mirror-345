"""Tests for formatting functions."""

from unittest.mock import patch

import pandas as pd

from gtrends.formatters import (
    export_to_file,
    format_related_data,
    format_trending_searches,
    is_bat_available,
)


class TestFormatters:
    """Test formatting functions."""

    def test_is_bat_available(self):
        """Test bat availability check."""
        with patch("os.system", return_value=0):
            assert is_bat_available() is True

        with patch("os.system", return_value=1):
            assert is_bat_available() is False

    @patch("gtrends.formatters.console.print")
    def test_format_trending_searches(self, mock_print):
        """Test trending searches formatter."""
        # Create test data
        data = pd.DataFrame(
            {
                "rank": [1, 2, 3],
                "title": ["Topic A", "Topic B", "Topic C"],
                "traffic": ["1M+", "500K+", "200K+"],
            }
        )

        # Test function
        format_trending_searches(data, title="Test Trends", count=3)

        # Assert console.print was called
        assert mock_print.called

    @patch("gtrends.formatters.console.print")
    def test_format_trending_searches_empty(self, mock_print):
        """Test trending searches formatter with empty data."""
        # Create empty DataFrame
        data = pd.DataFrame()

        # Test function
        format_trending_searches(data, title="Empty Test")

        # Should still call console.print with a message
        assert mock_print.called

    @patch("gtrends.formatters.console.print")
    def test_format_related_data(self, mock_print):
        """Test related data formatter."""
        # Create test data
        data = {
            "top": pd.DataFrame({"topic_title": ["Topic A", "Topic B"], "value": [100, 90]}),
            "rising": pd.DataFrame({"topic_title": ["Topic C", "Topic D"], "value": [200, 180]}),
        }

        # Test function
        format_related_data(data, data_type="topics", count=2)

        # Assert console.print was called
        assert mock_print.called

    def test_export_to_file(self, temp_output_dir):
        """Test export to file function."""
        # Create test data
        data = pd.DataFrame(
            {
                "rank": [1, 2, 3],
                "title": ["Topic A", "Topic B", "Topic C"],
                "traffic": ["1M+", "500K+", "200K+"],
            }
        )

        # Test export to CSV
        csv_path = temp_output_dir / "test_export.csv"
        result = export_to_file(data, csv_path, format="csv")

        assert result is True
        assert csv_path.exists()

        # Test export to JSON
        json_path = temp_output_dir / "test_export.json"
        result = export_to_file(data, json_path, format="json")

        assert result is True
        assert json_path.exists()
