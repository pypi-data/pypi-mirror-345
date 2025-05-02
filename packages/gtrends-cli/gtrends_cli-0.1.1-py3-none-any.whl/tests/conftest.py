"""Pytest configuration and shared fixtures."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from gtrends.content_suggestions import ContentSuggester
from gtrends.trends_api import TrendsClient


@pytest.fixture
def mock_trends_client():
    """Create a mock TrendsClient with predefined responses."""
    client = MagicMock(spec=TrendsClient)

    # Mock get_current_region
    client.get_current_region.return_value = "US"

    # Mock get_trending_searches
    trending_data = {
        "rank": [1, 2, 3, 4, 5],
        "title": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
        "traffic": ["1M+", "500K+", "200K+", "100K+", "50K+"],
    }
    client.get_trending_searches.return_value = pd.DataFrame(trending_data)

    # Mock get_trending_searches_with_articles
    news_articles = {
        "Topic 1": [
            {
                "title": "News about Topic 1",
                "source": "Example News",
                "url": "https://example.com/news1",
                "time_ago": "2 hours ago",
            }
        ]
    }
    client.get_trending_searches_with_articles.return_value = (
        pd.DataFrame(trending_data),
        news_articles,
    )

    # Mock get_related_topics
    top_topics_data = {"topic_title": ["Related Topic 1", "Related Topic 2"], "value": [100, 90]}
    rising_topics_data = {"topic_title": ["Rising Topic 1", "Rising Topic 2"], "value": [120, 150]}

    related_topics = {
        "top": pd.DataFrame(top_topics_data),
        "rising": pd.DataFrame(rising_topics_data),
    }
    client.get_related_topics.return_value = related_topics

    # Mock get_related_queries
    top_queries_data = {"query": ["Related Query 1", "Related Query 2"], "value": [100, 90]}
    rising_queries_data = {"query": ["Rising Query 1", "Rising Query 2"], "value": [120, 150]}

    related_queries = {
        "top": pd.DataFrame(top_queries_data),
        "rising": pd.DataFrame(rising_queries_data),
    }
    client.get_related_queries.return_value = related_queries

    # Mock get_interest_over_time
    dates = pd.date_range(start="1/1/2023", periods=10, freq="D")
    interest_data = {
        "date": dates,
        "query1": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "query2": [100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
    }
    client.get_interest_over_time.return_value = pd.DataFrame(interest_data)

    # Mock get_interest_by_region
    region_data = {"query1": [100, 90, 80, 70, 60], "query2": [50, 60, 70, 80, 90]}
    region_df = pd.DataFrame(region_data, index=["US", "GB", "CA", "AU", "IN"])
    client.get_interest_by_region.return_value = region_df

    return client


@pytest.fixture
def mock_content_suggester(mock_trends_client):
    """Create a mock ContentSuggester with predefined responses."""
    suggester = ContentSuggester(mock_trends_client)

    # Mock suggest_topics
    topics_data = {
        "topic": ["Suggested Topic 1", "Suggested Topic 2", "Suggested Topic 3"],
        "relevance_score": [95, 80, 70],
        "source": ["Trending searches", "Related to books", "Related to fiction"],
        "category": ["books", "books", "books"],
        "rising": [True, True, False],
    }

    with patch.object(ContentSuggester, "suggest_topics", return_value=pd.DataFrame(topics_data)):
        # Mock get_writing_opportunities
        opportunities_data = {
            "opportunity": ["Writing Idea 1", "Writing Idea 2", "Writing Idea 3"],
            "related_to": ["books", "fiction", "literature"],
            "growth_value": [200, 150, 120],
            "suggestion": [
                "Write an article exploring the relationship between Writing Idea 1 and books",
                "Create a listicle of 10 Ways Writing Idea 2 is Changing fiction",
                "Interview experts about the rise of Writing Idea 3 in the literature community",
            ],
            "type": ["Rising Topic", "Rising Query", "Rising Topic"],
        }

        with patch.object(
            ContentSuggester,
            "get_writing_opportunities",
            return_value=pd.DataFrame(opportunities_data),
        ):
            yield suggester


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "exports"
    output_dir.mkdir()
    return output_dir
