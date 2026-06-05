"""Portfolio model — items the user owns."""
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    good_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    market_hash_name: Mapped[str] = mapped_column(String(256), nullable=False)
    item_name: Mapped[str] = mapped_column(String(256), nullable=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_date: Mapped[str] = mapped_column(String(32), nullable=False)
    purchase_platform: Mapped[str] = mapped_column(String(32), default="BUFF")
    wear: Mapped[str] = mapped_column(String(32), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())
    updated_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())
