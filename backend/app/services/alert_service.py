"""Price alert service."""
from __future__ import annotations
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.alert import PriceAlert
from .item_service import item_service

logger = logging.getLogger(__name__)


class AlertService:

    async def get_all(self, db: AsyncSession) -> list[PriceAlert]:
        """Get all alerts."""
        result = await db.execute(select(PriceAlert).order_by(PriceAlert.created_at.desc()))
        return result.scalars().all()

    async def create(self, db: AsyncSession, data: dict) -> PriceAlert:
        """Create a price alert."""
        alert = PriceAlert(
            good_id=data["good_id"],
            market_hash_name=data.get("market_hash_name", ""),
            alert_type=data["alert_type"],
            threshold_value=data["threshold_value"],
            platform=data.get("platform", "BUFF"),
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def update(self, db: AsyncSession, alert_id: int, data: dict) -> Optional[PriceAlert]:
        """Update an alert."""
        result = await db.execute(select(PriceAlert).where(PriceAlert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            return None

        if data.get("is_active") is not None:
            alert.is_active = data["is_active"]
        if data.get("threshold_value") is not None:
            alert.threshold_value = data["threshold_value"]

        await db.commit()
        await db.refresh(alert)
        return alert

    async def remove(self, db: AsyncSession, alert_id: int) -> bool:
        """Remove an alert."""
        result = await db.execute(delete(PriceAlert).where(PriceAlert.id == alert_id))
        await db.commit()
        return result.rowcount > 0

    async def get_triggered(self, db: AsyncSession) -> list[PriceAlert]:
        """Get recently triggered alerts."""
        result = await db.execute(
            select(PriceAlert)
            .where(PriceAlert.triggered_at.isnot(None))
            .order_by(PriceAlert.triggered_at.desc())
            .limit(20)
        )
        return result.scalars().all()

    async def check_alerts(self, db: AsyncSession) -> list[dict]:
        """Check all active alerts against current prices. Returns triggered alerts."""
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.is_active == 1)
        )
        active_alerts = result.scalars().all()

        if not active_alerts:
            return []

        # Get unique item names
        names = list(set(a.market_hash_name for a in active_alerts if a.market_hash_name))
        if not names:
            return []

        try:
            batch = await item_service.batch_prices(names)
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []

        price_map = {}
        for p in batch:
            if isinstance(p, dict):
                price_map[p.get("market_hash_name", "")] = p.get("price")

        triggered = []
        for alert in active_alerts:
            current_price = price_map.get(alert.market_hash_name)
            if current_price is None:
                continue

            should_trigger = False
            if alert.alert_type == "price_above" and current_price >= alert.threshold_value:
                should_trigger = True
            elif alert.alert_type == "price_below" and current_price <= alert.threshold_value:
                should_trigger = True
            # For pct change alerts, we need previous price comparison
            # Simplified: just check if price moved significantly

            if should_trigger:
                from datetime import datetime
                alert.triggered_at = datetime.now().isoformat()
                alert.last_notified_price = current_price
                triggered.append({
                    "id": alert.id,
                    "good_id": alert.good_id,
                    "market_hash_name": alert.market_hash_name,
                    "alert_type": alert.alert_type,
                    "threshold_value": alert.threshold_value,
                    "current_price": current_price,
                })

        if triggered:
            await db.commit()

        return triggered


alert_service = AlertService()
