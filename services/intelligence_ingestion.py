"""
Intelligence Ingestion Layer — Sentinel AI V2.0
Provides adapters for live intelligence APIs (GDELT, NewsAPI).
Automatically falls back to historical data if APIs are unavailable.
Architecture supports future real-time sources without modification.
"""
import os
import requests
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, List
from utils.config import settings


class GDELTAdapter:
    """
    GDELT Project API adapter.
    Uses the GDELT DOC API to fetch recent global conflict-related articles.
    Falls back gracefully if API is unavailable.
    """
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def is_enabled(self) -> bool:
        return settings.GDELT_ENABLED

    def fetch_recent(self, query: str = "terrorism attack conflict", max_records: int = 25) -> List[dict]:
        """Fetch recent events from GDELT."""
        if not self.is_enabled():
            logger.info("GDELT adapter disabled. Returning empty feed.")
            return []

        try:
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": max_records,
                "format": "json",
                "sortby": "DateDesc",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])

            normalized = []
            for a in articles:
                normalized.append({
                    "date": a.get("seendate", datetime.now().strftime("%Y%m%d%H%M%S"))[:8],
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "source": a.get("domain", "GDELT"),
                    "country": a.get("sourcecountry", "Unknown"),
                    "summary": a.get("title", "No summary available."),
                    "source_dataset": "GDELT_LIVE",
                })
            logger.info(f"GDELT: Fetched {len(normalized)} live articles")
            return normalized

        except Exception as e:
            logger.warning(f"GDELT fetch failed: {e}. Falling back to historical data.")
            return []


class NewsAPIAdapter:
    """
    NewsAPI adapter for current intelligence headlines.
    Falls back gracefully if API key unavailable.
    """
    BASE_URL = "https://newsapi.org/v2/everything"

    def is_enabled(self) -> bool:
        return settings.NEWSAPI_ENABLED and bool(settings.NEWSAPI_KEY)

    def fetch_recent(self, query: str = "terrorism attack conflict", days_back: int = 7) -> List[dict]:
        """Fetch recent news from NewsAPI."""
        if not self.is_enabled():
            logger.info("NewsAPI adapter disabled. Returning empty feed.")
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 25,
                "apiKey": settings.NEWSAPI_KEY,
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])

            normalized = []
            for a in articles:
                normalized.append({
                    "date": a.get("publishedAt", "")[:10],
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", {}).get("name", "NewsAPI"),
                    "country": "Unknown",
                    "summary": a.get("description") or a.get("title", "No summary available."),
                    "source_dataset": "NEWSAPI_LIVE",
                })
            logger.info(f"NewsAPI: Fetched {len(normalized)} live articles")
            return normalized

        except Exception as e:
            logger.warning(f"NewsAPI fetch failed: {e}. Falling back to historical data.")
            return []


class IntelligenceIngestionLayer:
    """
    Unified intelligence ingestion coordinator.
    Queries all enabled live APIs and merges results.
    If no live APIs are available, returns metadata indicating historical mode.
    """

    def __init__(self):
        self.gdelt = GDELTAdapter()
        self.newsapi = NewsAPIAdapter()

    def is_live_mode(self) -> bool:
        """Returns True if any live API is enabled and available."""
        return self.gdelt.is_enabled() or self.newsapi.is_enabled()

    def get_live_context(self, query: str, max_items: int = 10) -> dict:
        """
        Retrieve live intelligence context for a given query.
        Returns dict with:
          - items: list of normalized articles
          - source: 'LIVE' or 'HISTORICAL'
          - disclaimer: message for the UI
        """
        items = []

        if self.gdelt.is_enabled():
            items.extend(self.gdelt.fetch_recent(query, max_records=max_items))

        if self.newsapi.is_enabled():
            items.extend(self.newsapi.fetch_recent(query))

        if items:
            return {
                "items": items[:max_items],
                "source": "LIVE",
                "disclaimer": (
                    f"Live intelligence from {len(items)} real-time sources "
                    f"(GDELT={'enabled' if self.gdelt.is_enabled() else 'disabled'}, "
                    f"NewsAPI={'enabled' if self.newsapi.is_enabled() else 'disabled'})."
                ),
            }
        else:
            return {
                "items": [],
                "source": "HISTORICAL",
                "disclaimer": (
                    "⚠️ Live intelligence APIs are not configured. "
                    "This response is based on historical dataset intelligence (GTD + ACLED). "
                    "To enable live intelligence, configure GDELT_ENABLED=true or set NEWSAPI_KEY in .env."
                ),
            }
