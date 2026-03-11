"""Stock screener API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import ScreenerService
from app.schemas import (
    ScreenerResponse,
    CreateScreenerRequest,
    ScreenerExecutionResponse,
)
from app.auth import get_current_user_id
from app.exceptions import NotFoundError

router = APIRouter()


@router.get("/screeners/prebuilt")
async def get_prebuilt_screeners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get pre-built screening templates.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of pre-built screeners
    """
    # TODO: Implement pre-built screeners
    return {
        "screeners": [],
        "total": 0,
    }


@router.post("/screeners", response_model=ScreenerResponse)
async def create_screener(
    request: CreateScreenerRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Create a custom screener.

    Args:
        request: Screener creation request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Created ScreenerResponse
    """
    service = ScreenerService(session)
    screener = await service.create_screener(
        user_id=user_id,
        name=request.name,
        description=request.description,
        criteria=request.criteria,
        is_public=request.is_public,
    )
    return screener


@router.get("/screeners", response_model=List[ScreenerResponse])
async def get_user_screeners(
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get user's screeners.

    Args:
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of ScreenerResponse objects
    """
    service = ScreenerService(session)
    return await service.get_user_screeners(user_id, skip, limit)


@router.get("/screeners/{screener_id}", response_model=ScreenerResponse)
async def get_screener(
    screener_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get screener details.

    Args:
        screener_id: Screener ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        ScreenerResponse with details
    """
    service = ScreenerService(session)
    screener = await service.get_screener(user_id, screener_id)

    if not screener:
        raise NotFoundError("Screener")

    return screener


@router.post("/screeners/{screener_id}/run", response_model=ScreenerExecutionResponse)
async def execute_screener(
    screener_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Execute screener and return matching stocks.

    Args:
        screener_id: Screener ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        ScreenerExecutionResponse with results
    """
    service = ScreenerService(session)
    result = await service.execute_screener(user_id, screener_id)

    if not result:
        raise NotFoundError("Screener")

    return result


@router.get("/screeners/{screener_id}/results")
async def get_screener_results(
    screener_id: int,
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get stocks matching screener criteria.

    Args:
        screener_id: Screener ID
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of matching stocks
    """
    # TODO: Implement get screener results
    return {
        "results": [],
        "total": 0,
    }


@router.put("/screeners/{screener_id}")
async def update_screener(
    screener_id: int,
    request: CreateScreenerRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update a screener.

    Args:
        screener_id: Screener ID
        request: Update request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated ScreenerResponse
    """
    service = ScreenerService(session)
    screener = await service.update_screener(
        user_id=user_id,
        screener_id=screener_id,
        name=request.name,
        description=request.description,
        criteria=request.criteria,
        is_public=request.is_public,
    )

    if not screener:
        raise NotFoundError("Screener")

    return screener


@router.delete("/screeners/{screener_id}")
async def delete_screener(
    screener_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Delete a screener.

    Args:
        screener_id: Screener ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Success message
    """
    service = ScreenerService(session)
    success = await service.delete_screener(user_id, screener_id)

    if not success:
        raise NotFoundError("Screener")

    return {"message": "Screener deleted successfully"}
