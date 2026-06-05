"""Market/Index API routes."""
from fastapi import APIRouter
from ..schemas.common import ApiResponse
from ..services.market_service import market_service

router = APIRouter(prefix="/api/v1/market", tags=["Market"])


@router.get("/overview")
async def get_market_overview():
    """Get dashboard overview: index, top gainers/losers, hot items."""
    data = await market_service.get_overview()
    return ApiResponse.ok(data)
