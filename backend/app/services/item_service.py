"""Item service — search, detail, chart, compare."""
from __future__ import annotations
import logging
from .csqaq_client import csqaq_client
from .cache_service import cache
from ..config import settings

logger = logging.getLogger(__name__)


class ItemService:

    async def search(self, query: str, limit: int = 20) -> list:
        """Fuzzy search items."""
        cache_key = f"item:search:{query.lower()}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.search_items(query)
            items = result.get("data", []) if isinstance(result, dict) else []
            if isinstance(items, list):
                items = items[:limit]
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            items = []

        cache.set(cache_key, items, ttl_seconds=settings.cache_ttl_item_search)
        return items

    async def get_detail(self, good_id: str) -> dict:
        """Get full item detail."""
        cache_key = f"item:detail:{good_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.get_item_detail(good_id)
            detail = result.get("data", result) if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Detail failed for {good_id}: {e}")
            detail = {}

        if detail:
            cache.set(cache_key, detail, ttl_seconds=settings.cache_ttl_item_search)
        return detail

    async def get_chart(
        self,
        good_id: str,
        platform: str = "1",
        period: str = "30",
        key: str = "sell_price",
        style: str = "all_style",
    ) -> list:
        """Get item chart data."""
        cache_key = f"item:chart:{good_id}:{platform}:{period}:{key}:{style}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.get_item_chart(good_id, platform, period, key, style)
            data = result.get("data", []) if isinstance(result, dict) else []
            if not isinstance(data, list):
                data = []
        except Exception as e:
            logger.error(f"Chart failed for {good_id}: {e}")
            data = []

        cache.set(cache_key, data, ttl_seconds=settings.cache_ttl_charts)
        return data

    async def batch_prices(self, names: list[str]) -> list:
        """Get batch prices by market hash names."""
        try:
            result = await csqaq_client.batch_get_prices(names)
            return result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Batch price failed: {e}")
            return []

    async def compare(self, good_ids: list[str]) -> list:
        """Compare multiple items side by side."""
        results = []
        for gid in good_ids:
            detail = await self.get_detail(gid)
            if detail:
                results.append(detail)
        return results


item_service = ItemService()
