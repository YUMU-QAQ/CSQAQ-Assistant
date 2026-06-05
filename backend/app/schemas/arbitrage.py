"""Arbitrage and case schemas."""
from __future__ import annotations
from typing import Optional, List, Dict
from pydantic import BaseModel
from typing import Optional


class ArbitrageOverview(BaseModel):
    """Arbitrage market overview."""
    buff_steam_ratio: Optional[float] = None
    uuyp_steam_ratio: Optional[float] = None
    platforms: List[Dict] = []


class ArbitrageOpportunity(BaseModel):
    """An arbitrage opportunity."""
    good_id: str
    name: str
    market_hash_name: str
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    profit_margin: Optional[float] = None  # percentage
    platform_from: Optional[str] = None
    platform_to: Optional[str] = None


class CaseOverview(BaseModel):
    """Weapon case stats summary."""
    total_opened_today: Optional[int] = None
    total_opened_week: Optional[int] = None
    trend_direction: Optional[str] = None  # up, down, stable


class CaseListItem(BaseModel):
    """Weapon case in a list."""
    case_id: str
    name: str
    image_url: Optional[str] = None
    price: Optional[float] = None
    roi_pct: Optional[float] = None
    expected_value: Optional[float] = None
    open_count_24h: Optional[int] = None


class CaseDetail(BaseModel):
    """Full case detail."""
    case_id: str
    name: str
    image_url: Optional[str] = None
    price: Optional[float] = None
    roi_pct: Optional[float] = None
    expected_value: Optional[float] = None
    open_count_24h: Optional[int] = None
    roi_chart: list = []
    open_history: list = []
    contents: list = []  # items with drop rates and values
