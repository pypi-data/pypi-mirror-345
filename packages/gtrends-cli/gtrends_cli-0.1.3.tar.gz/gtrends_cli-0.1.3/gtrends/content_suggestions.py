"""Content creator suggestion features."""

from typing import List, Optional

import pandas as pd
from trendspy import BatchPeriod

from gtrends.config import CONTENT_CATEGORIES
from gtrends.trends_api import TrendsClient


class ContentSuggester:
    """Generate content suggestions based on Google Trends data."""

    def __init__(self, trends_client: TrendsClient):
        """Initialize with a TrendsClient instance.

        Args:
            trends_client: Initialized TrendsClient instance
        """
        self.client = trends_client

    def suggest_topics(
        self,
        category: str = "books",
        region: Optional[str] = None,
        timeframe: str = "today 7-d",
        count: int = 10,
    ) -> pd.DataFrame:
        """Get topic suggestions for content creators.

        Args:
            category: Content category (books, news, arts, fiction, culture)
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            count: Number of results to return

        Returns:
            DataFrame with topic suggestions and relevance scores
        """
        if region is None:
            region = self.client.get_current_region()

        # Get category ID
        category_id = CONTENT_CATEGORIES.get(category.lower(), "0")

        # First, get trending searches
        trending_df = self.client.get_trending_searches(region=region)

        # Second, get some category-specific seed keywords
        seed_keywords = self._get_seed_keywords(category)

        # Get related topics for each seed keyword
        topic_data = []

        for keyword in seed_keywords:
            print(f"Getting related topics for '{keyword}'")
            related_topics = self.client.get_related_topics(
                query=keyword, region=region, timeframe=timeframe, category=category_id
            )

            # Process rising topics
            if "rising" in related_topics and not related_topics["rising"].empty:
                rising_df = related_topics["rising"]

                if "topic_title" in rising_df.columns:
                    for _, row in rising_df.iterrows():
                        title = row["topic_title"]
                        value = row["value"]

                        # Skip if this topic is already in our list
                        if any(t["topic"] == title for t in topic_data):
                            continue

                        topic_data.append(
                            {
                                "topic": title,
                                "relevance_score": value,
                                "source": f"Related to '{keyword}'",
                                "category": category,
                                "rising": True,
                            }
                        )

            # Process top topics
            if "top" in related_topics and not related_topics["top"].empty:
                top_df = related_topics["top"]

                if "topic_title" in top_df.columns:
                    for _, row in top_df.iterrows():
                        title = row["topic_title"]
                        value = row["value"]

                        # Skip if this topic is already in our list
                        if any(t["topic"] == title for t in topic_data):
                            continue

                        topic_data.append(
                            {
                                "topic": title,
                                "relevance_score": value,
                                "source": f"Related to '{keyword}'",
                                "category": category,
                                "rising": False,
                            }
                        )

        # Add trending searches that might be relevant
        if not trending_df.empty:
            for _, row in trending_df.iterrows():
                title = row["title"]

                # Skip if this topic is already in our list
                if any(t["topic"] == title for t in topic_data):
                    continue

                # Check relevance to category
                relevance = self._check_topic_relevance(title, category)

                if relevance > 30:  # Only include if somewhat relevant
                    topic_data.append(
                        {
                            "topic": title,
                            "relevance_score": relevance,
                            "source": "Trending searches",
                            "category": category,
                            "rising": True,
                        }
                    )

        # Create DataFrame and sort by relevance
        if topic_data:
            suggestions_df = pd.DataFrame(topic_data)
            suggestions_df = suggestions_df.sort_values(
                by=["rising", "relevance_score"], ascending=[False, False]
            ).reset_index(drop=True)

            return suggestions_df.head(count)

        # Return empty DataFrame if no results
        return pd.DataFrame(columns=["topic", "relevance_score", "source", "category", "rising"])

    def _get_seed_keywords(self, category: str) -> List[str]:
        """Get category-specific seed keywords for content suggestion.

        Args:
            category: Content category

        Returns:
            List of seed keywords
        """
        seed_map = {
            "books": ["books", "reading", "literature", "novel", "author"],
            "news": ["news", "current events", "headlines", "journalism"],
            "arts": ["art", "gallery", "exhibition", "artist", "creativity"],
            "fiction": ["fiction", "novel", "story", "fantasy", "science fiction"],
            "culture": ["culture", "tradition", "heritage", "identity", "customs"],
        }

        return seed_map.get(category.lower(), ["trending", "popular"])

    def _check_topic_relevance(self, topic: str, category: str) -> float:
        """Check the relevance of a topic to a specific category.

        Args:
            topic: Topic to check
            category: Category to check against

        Returns:
            Relevance score (0-100)
        """
        # Simple keyword matching for relevance
        category_keywords = {
            "books": [
                "book",
                "read",
                "author",
                "novel",
                "literature",
                "story",
                "publish",
                "fiction",
                "nonfiction",
                "writer",
                "chapter",
                "page",
                "library",
            ],
            "news": [
                "news",
                "report",
                "journalist",
                "headline",
                "article",
                "media",
                "press",
                "coverage",
                "event",
                "announcement",
                "breaking",
            ],
            "arts": [
                "art",
                "artist",
                "creative",
                "gallery",
                "exhibition",
                "museum",
                "design",
                "painting",
                "sculpture",
                "drawing",
                "display",
                "craft",
            ],
            "fiction": [
                "fiction",
                "story",
                "novel",
                "character",
                "plot",
                "fantasy",
                "sci-fi",
                "mystery",
                "thriller",
                "adventure",
                "romance",
                "genre",
            ],
            "culture": [
                "culture",
                "tradition",
                "heritage",
                "identity",
                "custom",
                "ritual",
                "celebration",
                "festival",
                "history",
                "community",
            ],
        }

        # Get keywords for the specified category
        keywords = category_keywords.get(category.lower(), [])

        # Check how many keywords match
        topic_lower = topic.lower()
        matches = sum(1 for keyword in keywords if keyword in topic_lower)

        # Calculate score
        if not keywords:
            return 50  # Default middle value if category not found

        # More sophisticated scoring:
        # - Exact category name match is worth a lot (e.g., "new books")
        # - Individual keyword matches add points
        score = (matches / len(keywords)) * 70  # Base score from keyword matches

        # Bonus for category name in topic
        if category.lower() in topic_lower:
            score += 30

        return min(score, 100)  # Cap at 100

    def compare_topic_interest(
        self, topics: List[str], region: Optional[str] = None, timeframe: str = "today 3-m"
    ) -> pd.DataFrame:
        """Compare interest over time for multiple topics.

        Args:
            topics: List of topics to compare (max 5)
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data

        Returns:
            DataFrame with interest over time data
        """
        if region is None:
            region = self.client.get_current_region()

        # Get interest over time data
        interest_df = self.client.get_interest_over_time(
            queries=topics, region=region, timeframe=timeframe
        )

        return interest_df

    def get_writing_opportunities(
        self,
        seed_topics: List[str] = None,
        region: Optional[str] = None,
        timeframe: str = "today 1-m",
        count: int = 5,
    ) -> pd.DataFrame:
        """Identify specific writing opportunities based on trends.

        Args:
            seed_topics: List of seed topics to expand on, or None for auto-discovery
            region: Two-letter country code (or None to auto-detect)
            timeframe: Time range for data
            count: Number of opportunities to return

        Returns:
            DataFrame with writing opportunities
        """
        if region is None:
            region = self.client.get_current_region()

        # If no seed topics provided, use default books/writing related topics
        if not seed_topics:
            seed_topics = ["books", "writing", "literature", "stories", "authors"]

        # Get related topics and queries for all seeds
        opportunities = []

        for seed in seed_topics:
            print(f"Getting related topics for '{seed}'")
            # Get related topics
            related_topics = self.client.get_related_topics(
                query=seed,
                region=region,
                timeframe=timeframe,
                category=CONTENT_CATEGORIES.get("books", "0"),
            )

            # Get related queries
            related_queries = self.client.get_related_queries(
                query=seed,
                region=region,
                timeframe=timeframe,
                category=CONTENT_CATEGORIES.get("books", "0"),
            )

            # Process rising topics
            if "rising" in related_topics and not related_topics["rising"].empty:
                rising_df = related_topics["rising"]

                if "topic_title" in rising_df.columns:
                    for _, row in rising_df.iterrows():
                        title = row["topic_title"]
                        value = min(row["value"], 5000)  # Cap extreme values

                        # Skip if already in opportunities
                        if any(o["opportunity"] == title for o in opportunities):
                            continue

                        # Generate writing suggestion
                        suggestion = self._generate_writing_suggestion(title, seed)

                        opportunities.append(
                            {
                                "opportunity": title,
                                "related_to": seed,
                                "growth_value": value,
                                "suggestion": suggestion,
                                "type": "Rising Topic",
                            }
                        )

            # Process rising queries
            if "rising" in related_queries and not related_queries["rising"].empty:
                rising_df = related_queries["rising"]

                if "query" in rising_df.columns:
                    for _, row in rising_df.iterrows():
                        query = row["query"]
                        value = min(row["value"], 5000)  # Cap extreme values

                        # Skip if already in opportunities
                        if any(o["opportunity"] == query for o in opportunities):
                            continue

                        # Generate writing suggestion
                        suggestion = self._generate_writing_suggestion(query, seed)

                        opportunities.append(
                            {
                                "opportunity": query,
                                "related_to": seed,
                                "growth_value": value,
                                "suggestion": suggestion,
                                "type": "Rising Query",
                            }
                        )

        # Create DataFrame and sort by relevance
        if opportunities:
            opportunities_df = pd.DataFrame(opportunities)
            opportunities_df = opportunities_df.sort_values(
                by="growth_value", ascending=False
            ).reset_index(drop=True)

            return opportunities_df.head(count)

        # Return empty DataFrame if no results
        return pd.DataFrame(
            columns=["opportunity", "related_to", "growth_value", "suggestion", "type"]
        )

    def _generate_writing_suggestion(self, topic: str, seed: str) -> str:
        """Generate a writing suggestion based on the topic and seed.

        Args:
            topic: The trending topic
            seed: The seed keyword that led to this topic

        Returns:
            A writing suggestion
        """
        suggestions = [
            f"Write an article exploring the relationship between {topic} and {seed}",
            f"Create a listicle of '10 Ways {topic} is Changing {seed}'",
            f"Publish an opinion piece on how {topic} is influencing the world of {seed}",
            f"Interview experts about the rise of {topic} in the {seed} community",
            f"Develop a beginner's guide to understanding {topic} for {seed} enthusiasts",
            f"Analyze the historical development of {topic} within {seed}",
            f"Write a comparative analysis between {topic} and other trends in {seed}",
            f"Create a Q&A addressing common questions about {topic} in relation to {seed}",
            f"Publish a review of recent works that combine {topic} and {seed}",
            f"Develop a forecast of how {topic} might evolve in the {seed} space",
        ]

        # Use topic to deterministically select a suggestion
        # (but will be different for different topics)
        import hashlib

        hash_value = int(hashlib.md5(topic.encode()).hexdigest(), 16)
        index = hash_value % len(suggestions)

        return suggestions[index]

    def get_topic_growth_data(
        self, topics: List[str], time_period: BatchPeriod = BatchPeriod.Past24H
    ) -> pd.DataFrame:
        """Get detailed growth data for multiple topics with independent normalization.

        Args:
            topics: List of topics to analyze (up to 500)
            time_period: Time period to analyze

        Returns:
            DataFrame with growth data over time
        """
        # Get showcase timeline for the topics
        timeline_df = self.client.get_showcase_timeline(keywords=topics, time_period=time_period)

        return timeline_df
