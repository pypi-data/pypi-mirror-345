"""Tests for TrendsClient."""

from unittest.mock import MagicMock, patch

import pandas as pd

from gtrends.trends_api import TrendsClient


class TestTrendsClient:
    """Test TrendsClient functionality."""

    @patch("gtrends.trends_api.Trends")
    @patch("gtrends.trends_api.requests.Session")
    def test_init(self, mock_session, mock_trends):
        """Test client initialization."""
        client = TrendsClient()
        print(client)
        assert mock_trends.called
        assert mock_session.called

    @patch("gtrends.trends_api.Trends")
    @patch("gtrends.trends_api.requests.Session")
    def test_get_current_region(self, mock_session, mock_trends):
        """Test get_current_region method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"country": "US"}

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Test method
        client = TrendsClient()
        region = client.get_current_region()

        assert region == "US"
        assert mock_session_instance.get.called

    @patch("gtrends.trends_api.Trends")
    def test_get_trending_searches(self, mock_trends):
        """Test get_trending_searches method."""
        # Setup mock
        mock_trends_instance = MagicMock()
        mock_trends_instance.trending_now.return_value = [
            MagicMock(title="Topic 1", traffic_text="1M+"),
            MagicMock(title="Topic 2", traffic_text="500K+"),
        ]
        mock_trends.return_value = mock_trends_instance

        # Test method
        client = TrendsClient()
        client.get_current_region = MagicMock(return_value="US")  # Override to avoid real calls

        result = client.get_trending_searches()

        assert isinstance(result, pd.DataFrame)
        assert mock_trends_instance.trending_now.called
        assert len(result) == 2

    @patch("gtrends.trends_api.Trends")
    def test_get_related_topics(self, mock_trends):
        """Test get_related_topics method."""
        # Setup mock
        mock_trends_instance = MagicMock()
        mock_trends_instance.related_topics.return_value = {
            "top": pd.DataFrame({"topic_title": ["Topic A"], "value": [100]}),
            "rising": pd.DataFrame({"topic_title": ["Topic B"], "value": [150]}),
        }
        mock_trends.return_value = mock_trends_instance

        # Test method
        client = TrendsClient()
        client.get_current_region = MagicMock(return_value="US")  # Override to avoid real calls

        result = client.get_related_topics("test query")

        assert isinstance(result, dict)
        assert "top" in result and "rising" in result
        assert mock_trends_instance.related_topics.called

    @patch("gtrends.trends_api.Trends")
    def test_get_interest_over_time(self, mock_trends):
        """Test get_interest_over_time method."""
        # Setup mock
        mock_trends_instance = MagicMock()
        mock_data = pd.DataFrame(
            {
                "date": pd.date_range(start="1/1/2023", periods=5, freq="D"),
                "query1": [10, 20, 30, 40, 50],
            }
        )
        mock_trends_instance.interest_over_time.return_value = mock_data
        mock_trends.return_value = mock_trends_instance

        # Test method
        client = TrendsClient()
        client.get_current_region = MagicMock(return_value="US")  # Override to avoid real calls

        result = client.get_interest_over_time("query1")

        assert isinstance(result, pd.DataFrame)
        assert "query1" in result.columns
        assert mock_trends_instance.interest_over_time.called
