"""Item API routes."""
from fastapi import APIRouter, Query
from ..schemas.common import ApiResponse
from ..schemas.item import BatchPriceRequest, CompareRequest
from ..services.item_service import item_service

router = APIRouter(prefix="/api/v1/items", tags=["Items"])


@router.get("/search")
async def search_items(q: str = Query(..., description="Search query"), limit: int = Query(20, ge=1, le=100)):
    """Fuzzy search items by name."""
    data = await item_service.search(q, limit)
    return ApiResponse.ok(data)


@router.get("/{good_id}")
async def get_item_detail(good_id: str):
    """Get single item full detail."""
    data = await item_service.get_detail(good_id)
    if not data:
        return ApiResponse.error(404, "Item not found")
    return ApiResponse.ok(data)


@router.get("/{good_id}/chart")
async def get_item_chart(
    good_id: str,
    platform: str = Query("1", description="Platform: 1=BUFF, etc."),
    period: str = Query("30", description="Period in days"),
    key: str = Query("sell_price", description="Data key"),
    style: str = Query("all_style", description="Style filter"),
):
    """Get item chart data."""
    data = await item_service.get_chart(good_id, platform, period, key, style)
    return ApiResponse.ok(data)


@router.post("/batch-price")
async def batch_get_prices(req: BatchPriceRequest):
    """Batch get prices by market hash names."""
    data = await item_service.batch_prices(req.names)
    return ApiResponse.ok(data)


@router.post("/compare")
async def compare_items(req: CompareRequest):
    """Compare multiple items side by side."""
    data = await item_service.compare(req.good_ids)
    return ApiResponse.ok(data)
