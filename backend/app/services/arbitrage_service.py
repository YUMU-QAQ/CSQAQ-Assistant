"""Arbitrage service."""
import logging
from .csqaq_client import csqaq_client
from .cache_service import cache
from ..config import settings

logger = logging.getLogger(__name__)


class ArbitrageService:

    async def get_overview(self) -> dict:
        """Get arbitrage/exchange overview."""
        cache_key = "arbitrage:overview"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.get_exchange_detail()
            overview = result.get("data", result) if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Arbitrage overview failed: {e}")
            overview = {}

        cache.set(cache_key, overview, ttl_seconds=settings.cache_ttl_rankings)
        return overview

    async def get_opportunities(self, min_profit: float = 0.05, sort: str = "profit_desc") -> list:
        """Get arbitrage opportunities."""
        cache_key = f"arbitrage:opportunities:{min_profit}:{sort}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # Use ranking endpoint with arbitrage filter
            result = await csqaq_client.get_rank_list(
                page_index=1,
                page_size=50,
                filter_params={"sort": "arbitrage_profit", "order": "desc"},
            )
            items = result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Arbitrage opportunities failed: {e}")
            items = []

        cache.set(cache_key, items, ttl_seconds=settings.cache_ttl_rankings)
        return items


arbitrage_service = ArbitrageService()
