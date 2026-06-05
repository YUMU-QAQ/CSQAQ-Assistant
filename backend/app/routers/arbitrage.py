"""Arbitrage API routes."""
from fastapi import APIRouter, Query
from ..schemas.common import ApiResponse
from ..services.arbitrage_service import arbitrage_service

router = APIRouter(prefix="/api/v1/arbitrage", tags=["Arbitrage"])


@router.get("/overview")
async def get_arbitrage_overview():
    """Get arbitrage/exchange overview."""
    data = await arbitrage_service.get_overview()
    return ApiResponse.ok(data)


@router.get("/opportunities")
async def get_opportunities(
    min_profit: float = Query(0.05, description="Minimum profit margin"),
    sort: str = Query("profit_desc", description="Sort order"),
):
    """Get arbitrage opportunities."""
    data = await arbitrage_service.get_opportunities(min_profit, sort)
    return ApiResponse.ok(data)
