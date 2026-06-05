"""Alert schemas."""
from pydantic import BaseModel
from typing import Optional


class AlertCreate(BaseModel):
    """Create a price alert."""
    good_id: str
    market_hash_name: str
    alert_type: str  # price_above, price_below, pct_change_up, pct_change_down
    threshold_value: float
    platform: str = "BUFF"


class AlertUpdate(BaseModel):
    """Update an alert."""
    is_active: Optional[int] = None
    threshold_value: Optional[float] = None


class AlertResponse(BaseModel):
    """Alert with status."""
    id: int
    good_id: str
    market_hash_name: str
    alert_type: str
    threshold_value: float
    platform: str
    is_active: int
    triggered_at: Optional[str] = None
    last_notified_price: Optional[float] = None
    created_at: str
