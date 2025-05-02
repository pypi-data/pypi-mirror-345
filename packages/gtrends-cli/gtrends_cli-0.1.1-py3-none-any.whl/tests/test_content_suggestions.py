"""Tests for ContentSuggester."""

from unittest.mock import MagicMock

import pandas as pd

from gtrends.content_suggestions import ContentSuggester


class TestContentSuggester:
    """Test ContentSugg functionality."""

    def test_init(self, mock_trends_client):
        """Test suggester initialization."""
        suggester = ContentSuggester(mock_trends_client)
        assert suggester.client == mock_trends_client

    def test_suggest_topics(self, mock_content_suggester):
        """Test suggest_topics method."""
        # Test method
        result = mock_content_suggester.suggest_topics(category="books", region="US")

        assert isinstance(result, pd.DataFrame)
        assert "topic" in result.columns
        assert "relevance_score" in result.columns
        assert "rising" in result.columns
        assert len(result) > 0

    def test_get_writing_opportunities(self, mock_content_suggester):
        """Test get_writing_opportunities method."""
        # Test method
        result = mock_content_suggester.get_writing_opportunities(
            seed_topics=["books", "fiction"], region="US"
        )

        assert isinstance(result, pd.DataFrame)
        assert "opportunity" in result.columns
        assert "suggestion" in result.columns
        assert "growth_value" in result.columns
        assert len(result) > 0

    def test_generate_writing_suggestion(self):
        """Test _generate_writing_suggestion method."""
        # Create a real instance for this test
        mock_client = MagicMock()
        suggester = ContentSuggester(mock_client)

        # Test method directly
        suggestion = suggester._generate_writing_suggestion(topic="AI fiction", seed="books")

        assert isinstance(suggestion, str)
        assert "AI fiction" in suggestion
        assert "books" in suggestion
        assert len(suggestion) > 20  # Should be a substantial suggestion
