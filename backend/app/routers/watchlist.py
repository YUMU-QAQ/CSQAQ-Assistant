"""Watchlist API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.common import ApiResponse
from ..schemas.watchlist import WatchlistItemCreate, WatchlistItemUpdate
from ..database import get_db
from ..services.watchlist_service import watchlist_service

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])


@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    """Get user's watchlist with current prices."""
    data = await watchlist_service.get_all(db)
    return ApiResponse.ok(data)


@router.post("")
async def add_to_watchlist(item: WatchlistItemCreate, db: AsyncSession = Depends(get_db)):
    """Add item to watchlist."""
    result = await watchlist_service.add(db, item.model_dump())
    return ApiResponse.ok({
        "id": result.id,
        "good_id": result.good_id,
    })


@router.patch("/{good_id}")
async def update_watchlist_item(good_id: str, data: WatchlistItemUpdate, db: AsyncSession = Depends(get_db)):
    """Update tags/notes."""
    result = await watchlist_service.update(db, good_id, data.model_dump())
    if not result:
        return ApiResponse.error(404, "Item not in watchlist")
    return ApiResponse.ok({"good_id": result.good_id})


@router.delete("/{good_id}")
async def remove_from_watchlist(good_id: str, db: AsyncSession = Depends(get_db)):
    """Remove item from watchlist."""
    ok = await watchlist_service.remove(db, good_id)
    if not ok:
        return ApiResponse.error(404, "Item not in watchlist")
    return ApiResponse.ok(None, "Removed")


@router.post("/refresh")
async def refresh_watchlist(db: AsyncSession = Depends(get_db)):
    """Force-refresh all watchlist prices."""
    data = await watchlist_service.refresh_prices(db)
    return ApiResponse.ok(data)
