"""Ranking service."""
import logging
from typing import Optional
from .csqaq_client import csqaq_client
from .cache_service import cache
from ..config import settings

logger = logging.getLogger(__name__)


class RankingService:

    async def get_rankings(
        self,
        page: int = 1,
        page_size: int = 50,
        filter_type: str = "gainers",
        category: Optional[str] = None,
        wear: Optional[str] = None,
    ) -> dict:
        """Get rankings list."""
        cache_key = f"rankings:{filter_type}:{page}:{page_size}:{category}:{wear}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Map our filter names to CSQAQ parameters
        filter_map = {
            "gainers": {"sort": "change_pct", "order": "desc"},
            "losers": {"sort": "change_pct", "order": "asc"},
            "volume": {"sort": "volume", "order": "desc"},
            "market_cap": {"sort": "market_cap", "order": "desc"},
            "hot": {"sort": "hot", "order": "desc"},
            "arbitrage": {"sort": "arbitrage_profit", "order": "desc"},
        }

        filter_params = filter_map.get(filter_type, filter_map["gainers"])
        if category:
            filter_params["category"] = category
        if wear:
            filter_params["wear"] = wear

        try:
            result = await csqaq_client.get_rank_list(page, page_size, filter_params)
            data = result.get("data", result) if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Rankings failed: {e}")
            data = {"items": [], "total": 0}

        cache.set(cache_key, data, ttl_seconds=settings.cache_ttl_rankings)
        return data


ranking_service = RankingService()
