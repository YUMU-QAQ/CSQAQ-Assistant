"""Market service — aggregates data for dashboard."""
import logging
from .csqaq_client import csqaq_client
from .cache_service import cache
from ..config import settings

logger = logging.getLogger(__name__)


class MarketService:

    async def get_overview(self) -> dict:
        """Get aggregated market overview for dashboard."""
        cache_key = "market:overview"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # Fetch index and rankings in parallel where possible
            index_data = await csqaq_client.get_homepage_index()
        except Exception as e:
            logger.error(f"Failed to fetch market index: {e}")
            # Return cached stale data if available, or empty
            return cache.get(cache_key) or {
                "index": None,
                "total_market_cap": None,
                "volume_24h": None,
                "top_gainers": [],
                "top_losers": [],
                "hot_items": [],
            }

        # Try to get top gainers/losers
        top_gainers = []
        top_losers = []
        try:
            # Gainers
            gainers = await csqaq_client.get_rank_list(
                page_index=1, page_size=10,
                filter_params={"sort": "change_pct", "order": "desc"},
            )
            top_gainers = gainers.get("data", []) if isinstance(gainers, dict) else []
        except Exception as e:
            logger.error(f"Failed to fetch gainers: {e}")

        try:
            # Losers
            losers = await csqaq_client.get_rank_list(
                page_index=1, page_size=10,
                filter_params={"sort": "change_pct", "order": "asc"},
            )
            top_losers = losers.get("data", []) if isinstance(losers, dict) else []
        except Exception as e:
            logger.error(f"Failed to fetch losers: {e}")

        # Try to get hot items
        hot_items = []
        try:
            hot = await csqaq_client.get_hot_items()
            hot_items = hot.get("data", []) if isinstance(hot, dict) else []
        except Exception as e:
            logger.error(f"Failed to fetch hot items: {e}")

        # Build overview from index response
        idx = index_data.get("data", index_data) if isinstance(index_data, dict) else {}

        result = {
            "index": {
                "index_value": idx.get("index"),
                "index_change_pct": idx.get("change_pct"),
                "online_players": idx.get("online_players"),
            },
            "total_market_cap": idx.get("total_market_cap"),
            "volume_24h": idx.get("volume_24h"),
            "top_gainers": top_gainers[:10],
            "top_losers": top_losers[:10],
            "hot_items": hot_items[:8],
        }

        cache.set(cache_key, result, ttl_seconds=settings.cache_ttl_market_index)
        return result


market_service = MarketService()
