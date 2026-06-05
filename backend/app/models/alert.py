"""Price alert model."""
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    good_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    market_hash_name: Mapped[str] = mapped_column(String(256), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False)  # price_above, price_below, pct_change_up, pct_change_down
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    platform: Mapped[str] = mapped_column(String(32), default="BUFF")
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    triggered_at: Mapped[str] = mapped_column(String(32), nullable=True)
    last_notified_price: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())
