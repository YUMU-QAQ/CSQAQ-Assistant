"""Portfolio API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.common import ApiResponse
from ..schemas.portfolio import PortfolioHoldingCreate, PortfolioHoldingUpdate
from ..database import get_db
from ..services.portfolio_service import portfolio_service

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])


@router.get("")
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    """Get all holdings with valuations."""
    data = await portfolio_service.get_all(db)
    return ApiResponse.ok(data)


@router.get("/summary")
async def get_portfolio_summary(db: AsyncSession = Depends(get_db)):
    """Get portfolio summary: cost, value, P&L, diversification."""
    data = await portfolio_service.get_summary(db)
    return ApiResponse.ok(data)


@router.post("")
async def add_holding(holding: PortfolioHoldingCreate, db: AsyncSession = Depends(get_db)):
    """Add a holding."""
    result = await portfolio_service.add(db, holding.model_dump())
    return ApiResponse.ok({"id": result.id})


@router.patch("/{holding_id}")
async def update_holding(holding_id: int, data: PortfolioHoldingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a holding."""
    result = await portfolio_service.update(db, holding_id, data.model_dump(exclude_none=True))
    if not result:
        return ApiResponse.error(404, "Holding not found")
    return ApiResponse.ok({"id": result.id})


@router.delete("/{holding_id}")
async def remove_holding(holding_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a holding."""
    ok = await portfolio_service.remove(db, holding_id)
    if not ok:
        return ApiResponse.error(404, "Holding not found")
    return ApiResponse.ok(None, "Removed")
