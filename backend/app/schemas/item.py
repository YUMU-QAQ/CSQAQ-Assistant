"""Item-related schemas."""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel
from typing import Optional


class ItemSearchResult(BaseModel):
    """Search result item."""
    good_id: str
    name: str
    market_hash_name: str
    image_url: Optional[str] = None


class ItemDetail(BaseModel):
    """Full item detail."""
    good_id: str
    name: str
    market_hash_name: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    prices: dict = {}         # platform -> {sell_price, buy_price, ...}
    volume: Optional[dict] = None
    circulation: Optional[int] = None
    market_cap: Optional[float] = None
    change_pct_24h: Optional[float] = None
    change_pct_7d: Optional[float] = None


class ChartDataPoint(BaseModel):
    """A single chart data point."""
    date: str
    value: float


class ItemChartResponse(BaseModel):
    """Chart data for an item."""
    good_id: str
    platform: str
    period: str
    key: str
    data: List[ChartDataPoint] = []


class BatchPriceRequest(BaseModel):
    """Request for batch price lookup."""
    names: List[str]


class BatchPriceItem(BaseModel):
    """Single item in batch price response."""
    market_hash_name: str
    price: Optional[float] = None
    change_pct_24h: Optional[float] = None


class CompareRequest(BaseModel):
    """Request to compare multiple items."""
    good_ids: List[str]
