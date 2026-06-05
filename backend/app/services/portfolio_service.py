"""Portfolio service."""
from __future__ import annotations
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.portfolio import PortfolioHolding
from .item_service import item_service

logger = logging.getLogger(__name__)


class PortfolioService:

    async def get_all(self, db: AsyncSession) -> list[dict]:
        """Get all holdings with current valuation."""
        result = await db.execute(select(PortfolioHolding).order_by(PortfolioHolding.created_at.desc()))
        holdings = result.scalars().all()

        if not holdings:
            return []

        # Get current prices
        names = [h.market_hash_name for h in holdings if h.market_hash_name]
        price_map = {}
        if names:
            try:
                batch = await item_service.batch_prices(names)
                for p in batch:
                    if isinstance(p, dict):
                        price_map[p.get("market_hash_name", "")] = p.get("price")
            except Exception as e:
                logger.error(f"Failed to get batch prices for portfolio: {e}")

        results = []
        for h in holdings:
            current_price = price_map.get(h.market_hash_name)
            cost_basis = h.quantity * h.purchase_price
            current_value = h.quantity * current_price if current_price is not None else None
            pnl = current_value - cost_basis if current_value is not None else None
            pnl_pct = (pnl / cost_basis * 100) if pnl is not None and cost_basis != 0 else None

            results.append({
                "id": h.id,
                "good_id": h.good_id,
                "market_hash_name": h.market_hash_name,
                "item_name": h.item_name,
                "image_url": h.image_url,
                "quantity": h.quantity,
                "purchase_price": h.purchase_price,
                "current_price": current_price,
                "cost_basis": cost_basis,
                "current_value": current_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "purchase_date": h.purchase_date,
                "purchase_platform": h.purchase_platform,
                "wear": h.wear,
                "notes": h.notes,
            })

        return results

    async def get_summary(self, db: AsyncSession) -> dict:
        """Get portfolio summary: total cost, value, P&L, diversification."""
        holdings = await self.get_all(db)

        if not holdings:
            return {
                "total_cost": 0,
                "total_value": 0,
                "total_pnl": 0,
                "total_pnl_pct": 0,
                "holding_count": 0,
                "diversification": {},
            }

        total_cost = sum(h["cost_basis"] for h in holdings)
        total_value = sum(h["current_value"] for h in holdings if h["current_value"] is not None)
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost != 0 else 0

        # Diversification — group by category from item details (simplified)
        categories = {}
        for h in holdings:
            cat = "Other"
            name = h.get("market_hash_name", "")
            if "★" in name or "Knife" in name or "刀" in name:
                cat = "Knife"
            elif "手套" in name or "Gloves" in name:
                cat = "Gloves"
            elif any(w in name for w in ["AK-47", "M4", "AWP", "USP", "Glock", "Desert Eagle"]):
                cat = "Rifle"
            elif "箱" in name or "Case" in name:
                cat = "Case"
            elif "印花" in name or "Sticker" in name:
                cat = "Sticker"
            val = h.get("current_value") or h.get("cost_basis", 0)
            categories[cat] = categories.get(cat, 0) + val

        total_for_pct = total_value or total_cost
        diversification = {k: round(v / total_for_pct * 100, 1) for k, v in categories.items()} if total_for_pct > 0 else {}

        return {
            "total_cost": total_cost,
            "total_value": total_value or None,
            "total_pnl": total_pnl or None,
            "total_pnl_pct": round(total_pnl_pct, 2) if total_pnl_pct != 0 else 0,
            "holding_count": len(holdings),
            "diversification": diversification,
        }

    async def add(self, db: AsyncSession, data: dict) -> PortfolioHolding:
        """Add a holding."""
        holding = PortfolioHolding(
            good_id=data["good_id"],
            market_hash_name=data.get("market_hash_name", ""),
            item_name=data.get("item_name"),
            image_url=data.get("image_url"),
            quantity=data.get("quantity", 1),
            purchase_price=data["purchase_price"],
            purchase_date=data["purchase_date"],
            purchase_platform=data.get("purchase_platform", "BUFF"),
            wear=data.get("wear"),
            notes=data.get("notes"),
        )
        db.add(holding)
        await db.commit()
        await db.refresh(holding)
        return holding

    async def update(self, db: AsyncSession, holding_id: int, data: dict) -> Optional[PortfolioHolding]:
        """Update a holding."""
        result = await db.execute(select(PortfolioHolding).where(PortfolioHolding.id == holding_id))
        holding = result.scalar_one_or_none()
        if not holding:
            return None

        for key in ["quantity", "purchase_price", "purchase_date", "purchase_platform", "wear", "notes"]:
            if key in data and data[key] is not None:
                setattr(holding, key, data[key])

        await db.commit()
        await db.refresh(holding)
        return holding

    async def remove(self, db: AsyncSession, holding_id: int) -> bool:
        """Remove a holding."""
        result = await db.execute(delete(PortfolioHolding).where(PortfolioHolding.id == holding_id))
        await db.commit()
        return result.rowcount > 0


portfolio_service = PortfolioService()
