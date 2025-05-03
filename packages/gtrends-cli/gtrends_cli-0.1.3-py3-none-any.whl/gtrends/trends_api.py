"""Core module for fetching Google Trends data using TrendsPy."""

import time
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
from trendspy import BatchPeriod, Trends

from gtrends.config import DEFAULT_CATEGORY, DEFAULT_REGION, DEFAULT_TIMEFRAME


class TrendsClient:
    """Client for interacting with Google Trends API using TrendsPy."""

    def __init__(self, hl: str = "en-US", tz: int = 360, proxy: Optional[Union[str, Dict]] = None):
        """Initialize the TrendsClient with language, timezone, and proxy settings.

        Args:
            hl: Language parameter
            tz: Timezone offset (360 corresponds to US CST)
            proxy: Optional proxy configuration
        """
        self.trends = Trends(hl=hl, tz=tz, proxy=proxy, request_delay=3.0)
        self._session = requests.Session()
        self._last_request_time = 0

        # Cache for categories and geo data
        self._categories_cache = None
        self._geo_cache = {}

    def _throttle_requests(self, min_interval: float = 1.0):
        """Prevent sending too many requests in a short time.

        Args:
            min_interval: Minimum time between requests in seconds
        """
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)

        self._last_request_time = time.time()

    def get_current_region(self) -> str:
        """Determine the user's current region based on IP.

        Returns:
            Two-letter country code
        """
        try:
            self._throttle_requests()
            response = self._session.get("https://ipinfo.io/json", timeout=5)
            data = response.json()
            return data.get("country", DEFAULT_REGION)
        except Exception:
            # Fallback to default region on any error
            return DEFAULT_REGION

    def get_categories(self, find: Optional[str] = None) -> List[Dict[str, str]]:
        """Get available Google Trends categories, optionally filtered by search term.

        Args:
            find: Optional search term to filter categories

        Returns:
            List of dictionaries with category information
        """
        if self._categories_cache is None:
            self._throttle_requests()
            self._categories_cache = self.trends.categories()

        if find:
            find = find.lower()
            return [cat for cat in self._categories_cache if find in cat["name"].lower()]

        return self._categories_cache

    def get_geo_codes(self, find: str) -> List[Dict[str, str]]:
        """Find location codes based on search term.

        Args:
            find: Search term for location

        Returns:
            List of dictionaries with location information
        """
        if find in self._geo_cache:
            return self._geo_cache[find]

        self._throttle_requests()
        results = self.trends.geo(find=find)
        self._geo_cache[find] = results

        return results

    def get_trending_searches(self, region: Optional[str] = None, limit: int = 20) -> pd.DataFrame:
        """Get real-time trending searches.

        Args:
            region: Two-letter country code (or None to auto-detect)
            limit: Maximum number of results to return

        Returns:
            DataFrame of trending searches
        """
        if region is None:
            region = self.get_current_region()

        self._throttle_requests()

        # Get trending searches
        trending = self.trends.trending_now(geo=region)

        # Convert TrendKeyword objects to DataFrame for consistent interface
        data = []
        for i, trend in enumerate(trending[:limit]):
            data.append(
                {
                    "rank": i + 1,
                    "title": trend.keyword,  # Changed from trend.title to trend.keyword
                    "traffic": trend.volume if hasattr(trend, "volume") else "",
                    "news_tokens": trend.news_tokens if hasattr(trend, "news_tokens") else None,
                    "raw_data": trend,  # Store the raw object for later access
                }
            )

        return pd.DataFrame(data)

    def get_trending_searches_with_articles(
        self, region: Optional[str] = None, limit: int = 20
    ) -> Tuple[pd.DataFrame, Dict]:
        """Get trending searches with associated news articles.

        Args:
            region: Two-letter country code (or None to auto-detect)
            limit: Maximum number of results to return

        Returns:
            Tuple of (DataFrame of trending searches, Dictionary of news articles)
        """
        if region is None:
            region = self.get_current_region()

        self._throttle_requests()

        # Get trending searches with news
        trending = self.trends.trending_now_by_rss(geo=region)

        # Convert to DataFrame for consistent interface
        data = []
        news_articles = {}

        for i, trend in enumerate(trending[:limit]):
            data.append(
                {
                    "rank": i + 1,
                    "title": trend.keyword,  # Changed from trend.title to trend.keyword
                    "traffic": (
                        trend.volume if hasattr(trend, "volume") else ""
                    ),  # Changed to volume
                    "raw_data": trend,  # Store the raw object for later access
                }
            )

            # Store any news articles
            if hasattr(trend, "news") and trend.news:
                articles = []
                for article in trend.news:
                    articles.append(
                        {
                            "title": article.title,
                            "source": article.source,
                            "url": article.url,
                            "time_ago": article.time_ago if hasattr(article, "time_ago") else "",
                        }
                    )
                news_articles[trend.keyword] = articles  # Changed from trend.title to trend.keyword

        return pd.DataFrame(data), news_articles

    def get_related_topics(
        self,
        query: str,
        region: Optional[str] = None,
        timeframe: str = DEFAULT_TIMEFRAME,
        category: str = DEFAULT_CATEGORY,
    ) -> Dict[str, pd.DataFrame]:
        """Get topics related to a query.

        Args:
            query: Search term
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            category: Category ID to filter results

        Returns:
            Dictionary with 'top' and 'rising' DataFrames
        """
        if region is None:
            region = self.get_current_region()

        self._throttle_requests()

        # Get related topics
        related = self.trends.related_topics(query, timeframe=timeframe, geo=region, cat=category)

        result = {}

        # Process top topics
        if "top" in related and related["top"] is not None:
            result["top"] = related["top"]

        # Process rising topics
        if "rising" in related and related["rising"] is not None:
            result["rising"] = related["rising"]

        return result

    def get_related_queries(
        self,
        query: str,
        region: Optional[str] = None,
        timeframe: str = DEFAULT_TIMEFRAME,
        category: str = DEFAULT_CATEGORY,
    ) -> Dict[str, pd.DataFrame]:
        """Get search queries related to a term.

        Args:
            query: Search term
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            category: Category ID to filter results

        Returns:
            Dictionary with 'top' and 'rising' DataFrames
        """
        if region is None:
            region = self.get_current_region()

        self._throttle_requests()

        # Get related queries
        related = self.trends.related_queries(query, timeframe=timeframe, geo=region, cat=category)

        result = {}

        # Process top queries
        if "top" in related and related["top"] is not None:
            result["top"] = related["top"]

        # Process rising queries
        if "rising" in related and related["rising"] is not None:
            result["rising"] = related["rising"]

        return result

    def get_interest_over_time(
        self,
        queries: Union[str, List[str]],
        region: Optional[str] = None,
        timeframe: Union[str, List[str]] = DEFAULT_TIMEFRAME,
        category: str = DEFAULT_CATEGORY,
    ) -> pd.DataFrame:
        """Get interest over time for up to 5 terms.

        Args:
            queries: Single search term or list of search terms (max 5)
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            category: Category ID to filter results

        Returns:
            DataFrame with interest over time
        """
        if region is None:
            region = self.get_current_region()

        # Ensure queries is a list
        if isinstance(queries, str):
            queries = [queries]

        # Limit to 5 queries (Google Trends limitation)
        if len(queries) > 5:
            queries = queries[:5]

        self._throttle_requests()

        # Get interest over time
        interest_df = self.trends.interest_over_time(
            queries, timeframe=timeframe, geo=region, cat=category
        )

        return interest_df

    def get_interest_by_region(
        self,
        queries: Union[str, List[str]],
        region: Optional[str] = None,
        timeframe: str = DEFAULT_TIMEFRAME,
        category: str = DEFAULT_CATEGORY,
        resolution: str = "COUNTRY",
    ) -> pd.DataFrame:
        """Get interest by geographic region.

        Args:
            queries: Single search term or list of search terms (max 5)
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            category: Category ID to filter results
            resolution: Geographic resolution (COUNTRY, REGION, CITY, etc.)

        Returns:
            DataFrame with interest by region
        """
        if region is None:
            region = self.get_current_region()

        # Ensure queries is a list
        if isinstance(queries, str):
            queries = [queries]

        # Limit to 5 queries (Google Trends limitation)
        if len(queries) > 5:
            queries = queries[:5]

        self._throttle_requests()

        # Get interest by region
        interest_df = self.trends.interest_by_region(
            queries, timeframe=timeframe, geo=region, cat=category, resolution=resolution
        )

        return interest_df

    def get_showcase_timeline(
        self, keywords: List[str], time_period: BatchPeriod = BatchPeriod.Past24H
    ) -> pd.DataFrame:
        """Get historical timeline data for many keywords with independent normalization.

        Args:
            keywords: List of keywords (up to 500+)
            time_period: Time period to analyze

        Returns:
            DataFrame with timeline data
        """
        self._throttle_requests()

        # Get showcase timeline
        timeline_df = self.trends.trending_now_showcase_timeline(keywords, timeframe=time_period)

        return timeline_df
