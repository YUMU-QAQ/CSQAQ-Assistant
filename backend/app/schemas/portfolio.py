"""Portfolio schemas."""
from pydantic import BaseModel
from typing import Optional


class PortfolioHoldingCreate(BaseModel):
    """Add a holding."""
    good_id: str
    market_hash_name: str
    item_name: Optional[str] = None
    image_url: Optional[str] = None
    quantity: int = 1
    purchase_price: float
    purchase_date: str
    purchase_platform: str = "BUFF"
    wear: Optional[str] = None
    notes: Optional[str] = None


class PortfolioHoldingUpdate(BaseModel):
    """Update a holding."""
    quantity: Optional[int] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[str] = None
    purchase_platform: Optional[str] = None
    wear: Optional[str] = None
    notes: Optional[str] = None


class PortfolioHoldingResponse(BaseModel):
    """Holding with live valuation."""
    id: int
    good_id: str
    market_hash_name: str
    item_name: Optional[str] = None
    image_url: Optional[str] = None
    quantity: int
    purchase_price: float
    current_price: Optional[float] = None
    cost_basis: float         # quantity * purchase_price
    current_value: Optional[float] = None  # quantity * current_price
    pnl: Optional[float] = None            # current_value - cost_basis
    pnl_pct: Optional[float] = None        # pnl / cost_basis * 100
    purchase_date: str
    purchase_platform: str
    wear: Optional[str] = None
    notes: Optional[str] = None


class PortfolioSummary(BaseModel):
    """Portfolio summary."""
    total_cost: float
    total_value: Optional[float] = None
    total_pnl: Optional[float] = None
    total_pnl_pct: Optional[float] = None
    holding_count: int
    diversification: dict = {}  # category -> percentage


class ValueHistoryPoint(BaseModel):
    """Portfolio value at a point in time."""
    date: str
    value: float
