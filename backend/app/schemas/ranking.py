"""Ranking schemas."""
from pydantic import BaseModel
from typing import Optional


class RankingItem(BaseModel):
    """An item in a ranking list."""
    rank: int
    good_id: str
    name: str
    market_hash_name: str
    image_url: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
