"""Portfolio management API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import PortfolioService
from app.schemas import (
    PositionResponse,
    CreatePositionRequest,
    UpdatePositionRequest,
    PortfolioOverviewResponse,
    PortfolioPerformanceResponse,
    PortfolioAllocationResponse,
)
from app.auth import get_current_user_id
from app.exceptions import NotFoundError, BusinessLogicError

router = APIRouter()


@router.get("/portfolio", response_model=PortfolioOverviewResponse)
async def get_portfolio_overview(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get portfolio overview with key metrics.

    Args:
        user_id: User ID (from auth)
        session: Database session

    Returns:
        PortfolioOverviewResponse with metrics
    """
    service = PortfolioService(session)
    return await service.get_portfolio_overview(user_id)


@router.get("/portfolio/positions", response_model=List[PositionResponse])
async def get_portfolio_positions(
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get current portfolio holdings.

    Args:
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of PositionResponse objects
    """
    service = PortfolioService(session)
    return await service.get_user_positions(user_id, skip, limit)


@router.get("/portfolio/allocation", response_model=PortfolioAllocationResponse)
async def get_portfolio_allocation(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get asset allocation breakdown by sector.

    Args:
        user_id: User ID (from auth)
        session: Database session

    Returns:
        PortfolioAllocationResponse with sector breakdown
    """
    service = PortfolioService(session)
    return await service.get_portfolio_allocation(user_id)


@router.get("/portfolio/performance", response_model=PortfolioPerformanceResponse)
async def get_portfolio_performance(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get daily and YTD portfolio performance.

    Args:
        user_id: User ID (from auth)
        session: Database session

    Returns:
        PortfolioPerformanceResponse with P&L metrics
    """
    # TODO: Implement performance calculation
    from datetime import datetime
    from decimal import Decimal

    return PortfolioPerformanceResponse(
        daily_gain_loss=Decimal("0"),
        daily_gain_loss_percent=Decimal("0"),
        ytd_gain_loss=Decimal("0"),
        ytd_gain_loss_percent=Decimal("0"),
        timestamp=datetime.utcnow(),
    )


@router.post("/portfolio/positions", response_model=PositionResponse)
async def create_position(
    request: CreatePositionRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Add a new position to portfolio.

    Args:
        request: Position creation request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Created PositionResponse
    """
    service = PortfolioService(session)
    position = await service.create_position(
        user_id=user_id,
        symbol=request.symbol.upper(),
        quantity=request.quantity,
        average_cost=request.average_cost,
    )

    if not position:
        raise BusinessLogicError("Position creation failed - stock may not exist")

    return position


@router.put("/portfolio/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    request: UpdatePositionRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update an existing position.

    Args:
        position_id: Position ID
        request: Update request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated PositionResponse
    """
    service = PortfolioService(session)
    position = await service.update_position(
        user_id=user_id,
        position_id=position_id,
        quantity=request.quantity,
        average_cost=request.average_cost,
    )

    if not position:
        raise NotFoundError("Position")

    return position


@router.delete("/portfolio/positions/{position_id}")
async def delete_position(
    position_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Remove a position from portfolio.

    Args:
        position_id: Position ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Success message
    """
    service = PortfolioService(session)
    success = await service.delete_position(user_id, position_id)

    if not success:
        raise NotFoundError("Position")

    return {"message": "Position deleted successfully"}
