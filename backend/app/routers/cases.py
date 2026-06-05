"""Weapon case API routes."""
from fastapi import APIRouter, Query
from ..schemas.common import ApiResponse
from ..services.case_service import case_service

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])


@router.get("/overview")
async def get_cases_overview():
    """Get case opening stats summary."""
    data = await case_service.get_overview()
    return ApiResponse.ok(data)


@router.get("/list")
async def get_cases_list(sort: str = Query("roi", description="Sort: roi, volume")):
    """Get weapon case list."""
    data = await case_service.get_list(sort)
    return ApiResponse.ok(data)


@router.get("/{case_id}")
async def get_case_detail(case_id: str):
    """Get case detail with ROI chart, open history, contents."""
    data = await case_service.get_detail(case_id)
    return ApiResponse.ok(data)


@router.get("/{case_id}/expected-value")
async def get_case_expected_value(case_id: str):
    """Get expected value analysis for a case."""
    data = await case_service.get_expected_value(case_id)
    return ApiResponse.ok(data)
