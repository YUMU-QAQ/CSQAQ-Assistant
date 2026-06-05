"""Market schemas."""
from pydantic import BaseModel
from typing import Optional


class IndexData(BaseModel):
    """Market index data."""
    index_value: Optional[float] = None
    index_change_pct: Optional[float] = None
    online_players: Optional[int] = None


class MarketOverview(BaseModel):
    """Aggregated dashboard overview."""
    index: Optional[IndexData] = None
    total_market_cap: Optional[float] = None
    volume_24h: Optional[int] = None
    top_gainers: list = []
    top_losers: list = []
    hot_items: list = []
