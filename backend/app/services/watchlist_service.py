"""Watchlist service."""
from __future__ import annotations
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.watchlist import WatchlistItem
from .item_service import item_service
from .cache_service import cache

logger = logging.getLogger(__name__)


class WatchlistService:

    async def get_all(self, db: AsyncSession) -> list[dict]:
        """Get full watchlist with live prices."""
        result = await db.execute(select(WatchlistItem).order_by(WatchlistItem.added_at.desc()))
        items = result.scalars().all()

        if not items:
            return []

        # Try to refresh prices
        names = [i.market_hash_name for i in items if i.market_hash_name]
        prices = {}
        if names:
            try:
                batch = await item_service.batch_prices(names)
                for p in batch:
                    if isinstance(p, dict):
                        prices[p.get("market_hash_name", "")] = p
            except Exception as e:
                logger.error(f"Batch price refresh failed: {e}")

        result_list = []
        for item in items:
            price_info = prices.get(item.market_hash_name, {})
            try:
                tags = json.loads(item.tags) if item.tags else []
            except (json.JSONDecodeError, TypeError):
                tags = []

            result_list.append({
                "id": item.id,
                "good_id": item.good_id,
                "market_hash_name": item.market_hash_name,
                "item_name": item.item_name,
                "image_url": item.image_url,
                "category": item.category,
                "tags": tags,
                "notes": item.notes,
                "added_at": item.added_at,
                "last_price": price_info.get("price") or item.last_price,
                "change_pct_24h": price_info.get("change_pct_24h"),
                "last_updated_at": item.last_updated_at,
            })

        return result_list

    async def add(self, db: AsyncSession, data: dict) -> WatchlistItem:
        """Add item to watchlist."""
        item = WatchlistItem(
            good_id=data["good_id"],
            market_hash_name=data.get("market_hash_name", ""),
            item_name=data.get("item_name"),
            image_url=data.get("image_url"),
            category=data.get("category"),
            tags=json.dumps(data.get("tags", [])),
            notes=data.get("notes"),
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def update(self, db: AsyncSession, good_id: str, data: dict) -> Optional[WatchlistItem]:
        """Update watchlist item tags/notes."""
        result = await db.execute(select(WatchlistItem).where(WatchlistItem.good_id == good_id))
        item = result.scalar_one_or_none()
        if not item:
            return None

        if data.get("tags") is not None:
            item.tags = json.dumps(data["tags"])
        if data.get("notes") is not None:
            item.notes = data["notes"]

        await db.commit()
        await db.refresh(item)
        return item

    async def remove(self, db: AsyncSession, good_id: str) -> bool:
        """Remove item from watchlist."""
        result = await db.execute(delete(WatchlistItem).where(WatchlistItem.good_id == good_id))
        await db.commit()
        return result.rowcount > 0

    async def refresh_prices(self, db: AsyncSession) -> list[dict]:
        """Force-refresh all watchlist prices."""
        result = await db.execute(select(WatchlistItem))
        items = result.scalars().all()

        names = [i.market_hash_name for i in items if i.market_hash_name]
        batch = await item_service.batch_prices(names)

        price_map = {}
        for p in batch:
            if isinstance(p, dict):
                price_map[p.get("market_hash_name", "")] = p.get("price")

        # Update cached prices in DB
        for item in items:
            if item.market_hash_name in price_map:
                item.last_price = price_map[item.market_hash_name]

        await db.commit()

        # Clear cache
        cache.delete("watchlist:all")
        return await self.get_all(db)


watchlist_service = WatchlistService()
