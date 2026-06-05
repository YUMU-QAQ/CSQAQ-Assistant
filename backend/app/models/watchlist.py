"""Watchlist model — items the user is tracking."""
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    good_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    market_hash_name: Mapped[str] = mapped_column(String(256), nullable=False)
    item_name: Mapped[str] = mapped_column(String(256), nullable=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=True)
    tags: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    added_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())
    last_price: Mapped[float] = mapped_column(Float, nullable=True)
    last_updated_at: Mapped[str] = mapped_column(String(32), nullable=True)
