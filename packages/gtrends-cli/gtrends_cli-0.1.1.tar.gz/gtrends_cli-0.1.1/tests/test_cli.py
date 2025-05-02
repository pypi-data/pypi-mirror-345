"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gtrends.cli import cli, compare, related, suggest_topics, trending, writing_opportunities


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_cli_help(self, cli_runner):
        """Test --help option works correctly."""
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Google Trends CLI" in result.output
        assert "trending" in result.output
        assert "related" in result.output
        assert "suggest-topics" in result.output

    @patch("gtrends.cli.TrendsClient")
    def test_trending_command(self, mock_client_class, cli_runner, mock_trends_client):
        """Test trending command."""
        # Setup the mock
        mock_client_class.return_value = mock_trends_client

        # Test basic command
        result = cli_runner.invoke(trending, [])
        assert result.exit_code == 0
        assert "Trending Searches" in result.output
        assert "Topic 1" in result.output

        # Test with news option
        result = cli_runner.invoke(trending, ["--with-news"])
        assert result.exit_code == 0
        assert "Trending Searches" in result.output
        assert "Related News Articles" in result.output

    @patch("gtrends.cli.TrendsClient")
    def test_related_command(self, mock_client_class, cli_runner, mock_trends_client):
        """Test related command."""
        # Setup the mock
        mock_client_class.return_value = mock_trends_client

        # Test command
        result = cli_runner.invoke(related, ["books"])
        assert result.exit_code == 0
        assert "Related data for" in result.output
        assert "Related Topic" in result.output
        assert "Related Query" in result.output

    @patch("gtrends.cli.TrendsClient")
    @patch("gtrends.cli.ContentSuggester")
    def test_suggest_topics_command(
        self, mock_suggester_class, mock_client_class, cli_runner, mock_content_suggester
    ):
        """Test suggest-topics command."""
        # Setup the mocks
        mock_client_class.return_value = MagicMock()
        mock_suggester_class.return_value = mock_content_suggester

        # Test command
        result = cli_runner.invoke(suggest_topics, [])
        assert result.exit_code == 0
        assert "Content Suggestions" in result.output
        assert "Suggested Topic" in result.output

    @patch("gtrends.cli.TrendsClient")
    def test_compare_command(self, mock_client_class, cli_runner, mock_trends_client):
        """Test compare command."""
        # Setup the mock
        mock_client_class.return_value = mock_trends_client

        # Test command
        result = cli_runner.invoke(compare, ["topic1", "topic2"])
        assert result.exit_code == 0
        assert "Interest Comparison" in result.output

    @patch("gtrends.cli.TrendsClient")
    @patch("gtrends.cli.ContentSuggester")
    def test_writing_opportunities_command(
        self, mock_suggester_class, mock_client_class, cli_runner, mock_content_suggester
    ):
        """Test writing-opportunities command."""
        # Setup the mocks
        mock_client_class.return_value = MagicMock()
        mock_suggester_class.return_value = mock_content_suggester

        # Test command
        result = cli_runner.invoke(writing_opportunities, ["books"])
        assert result.exit_code == 0
        assert "Writing Opportunities" in result.output
        assert "Writing Idea" in result.output


class TestCLIErrors:
    """Test CLI error handling."""

    @patch("gtrends.cli.TrendsClient")
    def test_trending_error_handling(self, mock_client_class, cli_runner):
        """Test error handling in trending command."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.get_trending_searches.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        # Test command with error
        result = cli_runner.invoke(trending, [])
        assert result.exit_code == 0  # We catch exceptions
        assert "Error" in result.output
