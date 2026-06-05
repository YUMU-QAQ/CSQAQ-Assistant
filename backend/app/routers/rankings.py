"""Rankings API routes."""
from typing import Optional
from fastapi import APIRouter, Query
from ..schemas.common import ApiResponse
from ..services.ranking_service import ranking_service

router = APIRouter(prefix="/api/v1/rankings", tags=["Rankings"])


@router.get("/list")
async def get_rankings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    filter: str = Query("gainers", description="gainers|losers|volume|market_cap|hot|arbitrage"),
    category: Optional[str] = Query(None, description="Category filter"),
    wear: Optional[str] = Query(None, description="Wear filter"),
):
    """Get ranking list."""
    data = await ranking_service.get_rankings(page, page_size, filter, category, wear)
    return ApiResponse.ok(data)
