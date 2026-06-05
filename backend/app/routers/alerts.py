"""Alerts API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.common import ApiResponse
from ..schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from ..database import get_db
from ..services.alert_service import alert_service

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.get("")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    """Get all alerts."""
    data = await alert_service.get_all(db)
    return ApiResponse.ok([
        {
            "id": a.id,
            "good_id": a.good_id,
            "market_hash_name": a.market_hash_name,
            "alert_type": a.alert_type,
            "threshold_value": a.threshold_value,
            "platform": a.platform,
            "is_active": a.is_active,
            "triggered_at": a.triggered_at,
            "last_notified_price": a.last_notified_price,
            "created_at": a.created_at,
        }
        for a in data
    ])


@router.post("")
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a price alert."""
    result = await alert_service.create(db, alert_data.model_dump())
    return ApiResponse.ok({"id": result.id})


@router.patch("/{alert_id}")
async def update_alert(alert_id: int, data: AlertUpdate, db: AsyncSession = Depends(get_db)):
    """Update/toggle an alert."""
    result = await alert_service.update(db, alert_id, data.model_dump(exclude_none=True))
    if not result:
        return ApiResponse.error(404, "Alert not found")
    return ApiResponse.ok({"id": result.id})


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an alert."""
    ok = await alert_service.remove(db, alert_id)
    if not ok:
        return ApiResponse.error(404, "Alert not found")
    return ApiResponse.ok(None, "Deleted")


@router.get("/triggered")
async def get_triggered(db: AsyncSession = Depends(get_db)):
    """Get triggered alerts."""
    data = await alert_service.get_triggered(db)
    return ApiResponse.ok([
        {
            "id": a.id,
            "good_id": a.good_id,
            "market_hash_name": a.market_hash_name,
            "alert_type": a.alert_type,
            "threshold_value": a.threshold_value,
            "triggered_at": a.triggered_at,
            "last_notified_price": a.last_notified_price,
        }
        for a in data
    ])
