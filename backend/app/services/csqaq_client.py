"""CSQAQ API HTTP client with rate limiting, caching, and retry logic."""
from __future__ import annotations
import asyncio
import logging
from typing import Optional, Any
import httpx
from ..config import settings
from ..utils.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


class CSQAQClient:
    """Async HTTP client for CSQAQ API."""

    BASE_URL = settings.csqaq_base_url

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = get_rate_limiter(rate=settings.csqaq_rate_limit)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "ApiToken": settings.csqaq_api_token,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        """Make a rate-limited request with retry logic."""
        client = await self._get_client()

        for attempt in range(retries):
            try:
                await self._rate_limiter.acquire()

                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                )

                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", "2"))
                    logger.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1}/{retries})")
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code} (attempt {attempt + 1}/{retries})")
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                data = response.json()
                return data

            except httpx.TimeoutException:
                logger.warning(f"Timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text[:200]}")
                raise
            except Exception as e:
                logger.error(f"Request error: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise RuntimeError(f"Request failed after {retries} retries: {method} {path}")

    # ==================================================================
    # Market / Index endpoints
    # ==================================================================

    async def get_homepage_index(self) -> dict:
        """Get homepage index data (指数数据、涨跌分布、在线人数、今日走势)."""
        return await self._request("GET", "/api/v1/info/market/index")

    async def get_index_detail(self) -> dict:
        """Get index detail (今天涨跌数据、图表数据)."""
        return await self._request("GET", "/api/v1/info/market/index_detail")

    async def get_index_kline(self, period: str = "7d") -> dict:
        """Get index K-line chart data."""
        return await self._request("POST", "/api/v1/info/market/index_kline", json_data={"period": period})

    # ==================================================================
    # Item endpoints
    # ==================================================================

    async def search_items(self, query: str) -> dict:
        """Fuzzy search items by name."""
        return await self._request("GET", "/api/v1/info/good/associate", params={"name": query})

    async def get_item_by_id(self, good_id: str) -> dict:
        """Get item ID info by good_id."""
        return await self._request("GET", "/api/v1/info/good/id", params={"good_id": good_id})

    async def get_item_detail(self, good_id: str) -> dict:
        """Get single item full detail."""
        return await self._request("GET", "/api/v1/info/good/detail", params={"good_id": good_id})

    async def get_item_chart(
        self,
        good_id: str,
        platform: str = "1",
        period: str = "30",
        key: str = "sell_price",
        style: str = "all_style",
    ) -> dict:
        """Get item chart data (POST)."""
        return await self._request("POST", "/api/v1/info/good/chart", json_data={
            "good_id": good_id,
            "platform": platform,
            "period": period,
            "key": key,
            "style": style,
        })

    async def get_item_existence(self, good_id: str) -> dict:
        """Get item circulation/existence trend (180 days)."""
        return await self._request("GET", "/api/v1/info/good/existence", params={"good_id": good_id})

    async def batch_get_prices(self, names: list[str]) -> dict:
        """Batch get prices by marketHashName."""
        return await self._request("POST", "/api/v1/info/good/batch_price", json_data={"names": names})

    async def get_item_kline(self, good_id: str, platform: str = "1", period: str = "30") -> dict:
        """Get single item multi-platform K-line data."""
        return await self._request("POST", "/api/v1/info/good/kline", json_data={
            "good_id": good_id,
            "platform": platform,
            "period": period,
        })

    # ==================================================================
    # Ranking endpoints
    # ==================================================================

    async def get_rank_list(self, page_index: int = 1, page_size: int = 50, filter_params: Optional[dict] = None, show_recently_price: bool = True) -> dict:
        """Get ranking list."""
        body = {
            "page_index": page_index,
            "page_size": page_size,
            "filter": filter_params or {},
            "show_recently_price": show_recently_price,
        }
        return await self._request("POST", "/api/v1/info/good/rank_list", json_data=body)

    async def get_item_list(self, page_index: int = 1, page_size: int = 50, filter_params: Optional[dict] = None) -> dict:
        """Get all items list (饰品列表)."""
        body = {
            "page_index": page_index,
            "page_size": page_size,
            "filter": filter_params or {},
        }
        return await self._request("POST", "/api/v1/info/good/list", json_data=body)

    async def get_hot_items(self) -> dict:
        """Get hot items list (大家都在看)."""
        return await self._request("GET", "/api/v1/info/good/hot")

    async def get_hot_series_list(self) -> dict:
        """Get hot series list."""
        return await self._request("GET", "/api/v1/info/good/series")

    async def get_series_detail(self, series_id: str) -> dict:
        """Get single series detail."""
        return await self._request("GET", "/api/v1/info/good/series_detail", params={"series_id": series_id})

    # ==================================================================
    # Arbitrage / Exchange endpoints
    # ==================================================================

    async def get_exchange_detail(self) -> dict:
        """Get exchange/arbitrage detail (挂刀行情)."""
        return await self._request("GET", "/api/v1/info/exchange/detail")

    # ==================================================================
    # Inventory monitoring endpoints
    # ==================================================================

    async def get_monitor_updates(self) -> dict:
        """Get latest inventory monitoring updates."""
        return await self._request("GET", "/api/v1/info/monitor")

    async def get_monitor_task_list(self, query: str = "") -> dict:
        """Get inventory monitoring task list."""
        return await self._request("GET", "/api/v1/info/monitor/list", params={"query": query})

    async def get_monitor_holdings_rank(self, good_id: str) -> dict:
        """Get holdings ranking for a specific item."""
        return await self._request("GET", "/api/v1/info/monitor/holdings_rank", params={"good_id": good_id})

    async def get_monitor_user_info(self, task_id: str) -> dict:
        """Get monitored user info."""
        return await self._request("GET", "/api/v1/info/monitor/user", params={"task_id": task_id})

    async def get_monitor_user_inventory(self, task_id: str) -> dict:
        """Get monitored user full inventory."""
        return await self._request("GET", "/api/v1/info/monitor/user_inventory", params={"task_id": task_id})

    # ==================================================================
    # Weapon case endpoints
    # ==================================================================

    async def get_case_open_stats(self) -> dict:
        """Get weapon case open count stats."""
        return await self._request("GET", "/api/v1/info/case/stats")

    async def get_case_roi_list(self) -> dict:
        """Get weapon case ROI list."""
        return await self._request("GET", "/api/v1/info/case/roi_list")

    async def get_case_roi_chart(self, case_id: str) -> dict:
        """Get single case ROI trend."""
        return await self._request("GET", "/api/v1/info/case/roi_chart", params={"case_id": case_id})

    async def get_case_open_history(self, case_id: str) -> dict:
        """Get single case daily open count history."""
        return await self._request("GET", "/api/v1/info/case/open_history", params={"case_id": case_id})

    async def get_all_collections(self) -> dict:
        """Get all weapon cases and collections overview."""
        return await self._request("GET", "/api/v1/info/case/collections")

    async def get_collection_contents(self, collection_id: str) -> dict:
        """Get items contained in a collection/case."""
        return await self._request("GET", "/api/v1/info/case/collection_contents", params={"collection_id": collection_id})

    # ==================================================================
    # Utility
    # ==================================================================

    async def bind_ip(self) -> dict:
        """Bind current IP to API token (for non-fixed IP)."""
        return await self._request("POST", "/api/v1/info/bind_ip")


# Singleton
csqaq_client = CSQAQClient()
