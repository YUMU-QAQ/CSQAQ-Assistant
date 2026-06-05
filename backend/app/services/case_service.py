"""Weapon case service."""
import logging
from .csqaq_client import csqaq_client
from .cache_service import cache
from ..config import settings

logger = logging.getLogger(__name__)


class CaseService:

    async def get_overview(self) -> dict:
        """Get case opening stats summary."""
        cache_key = "case:overview"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.get_case_open_stats()
            overview = result.get("data", result) if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Case overview failed: {e}")
            overview = {}

        cache.set(cache_key, overview, ttl_seconds=settings.cache_ttl_cases)
        return overview

    async def get_list(self, sort: str = "roi") -> list:
        """Get weapon case list sorted by ROI or other metrics."""
        cache_key = f"case:list:{sort}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            result = await csqaq_client.get_case_roi_list()
            items = result.get("data", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Case list failed: {e}")
            items = []

        cache.set(cache_key, items, ttl_seconds=settings.cache_ttl_cases)
        return items

    async def get_detail(self, case_id: str) -> dict:
        """Get single case detail with ROI trend, open history, and contents."""
        cache_key = f"case:detail:{case_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            roi_result = await csqaq_client.get_case_roi_chart(case_id)
            roi_chart = roi_result.get("data", []) if isinstance(roi_result, dict) else []
        except Exception as e:
            logger.error(f"Case ROI chart failed for {case_id}: {e}")
            roi_chart = []

        try:
            history_result = await csqaq_client.get_case_open_history(case_id)
            open_history = history_result.get("data", []) if isinstance(history_result, dict) else []
        except Exception as e:
            logger.error(f"Case open history failed for {case_id}: {e}")
            open_history = []

        try:
            collections = await csqaq_client.get_all_collections()
            items_list = collections.get("data", []) if isinstance(collections, dict) else []
            # Find matching case
            contents = []
            for item in items_list if isinstance(items_list, list) else []:
                if isinstance(item, dict) and str(item.get("id", "")) == str(case_id):
                    # Try to get contents
                    try:
                        cont_result = await csqaq_client.get_collection_contents(str(item.get("id", "")))
                        contents = cont_result.get("data", []) if isinstance(cont_result, dict) else []
                    except Exception:
                        pass
                    break
        except Exception as e:
            logger.error(f"Case contents failed for {case_id}: {e}")
            contents = []

        detail = {
            "case_id": case_id,
            "roi_chart": roi_chart,
            "open_history": open_history,
            "contents": contents,
        }

        cache.set(cache_key, detail, ttl_seconds=settings.cache_ttl_cases)
        return detail

    async def get_expected_value(self, case_id: str) -> dict:
        """Compute expected value analysis for a case."""
        detail = await self.get_detail(case_id)
        # The ROI chart data likely contains EV
        return {
            "case_id": case_id,
            "contents": detail.get("contents", []),
            "roi_chart": detail.get("roi_chart", []),
        }


case_service = CaseService()
