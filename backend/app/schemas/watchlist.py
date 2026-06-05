"""Watchlist schemas."""
from typing import Optional, List
from pydantic import BaseModel


class WatchlistItemCreate(BaseModel):
    """Add item to watchlist."""
    good_id: str
    market_hash_name: Optional[str] = None
    item_name: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WatchlistItemUpdate(BaseModel):
    """Update watchlist item."""
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    """Watchlist item with live price."""
    id: int
    good_id: str
    market_hash_name: str
    item_name: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    tags: list = []
    notes: Optional[str] = None
    added_at: str
    last_price: Optional[float] = None
    change_pct_24h: Optional[float] = None
    last_updated_at: Optional[str] = None
