"""Watchlist management API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import WatchlistService
from app.schemas import WatchlistResponse, WatchlistCreate, WatchlistUpdate, AddToWatchlistRequest
from app.auth import get_current_user_id
from app.exceptions import NotFoundError

router = APIRouter()


@router.post("/watchlists", response_model=WatchlistResponse)
async def create_watchlist(
    request: WatchlistCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Create a new watchlist.

    Args:
        request: Watchlist creation request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Created WatchlistResponse
    """
    service = WatchlistService(session)
    watchlist = await service.create_watchlist(
        user_id=user_id,
        name=request.name,
        description=request.description,
        is_default=request.is_default,
    )
    return watchlist


@router.get("/watchlists", response_model=List[WatchlistResponse])
async def get_user_watchlists(
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get all watchlists for the user.

    Args:
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of WatchlistResponse objects
    """
    service = WatchlistService(session)
    return await service.get_user_watchlists(user_id, skip, limit)


@router.get("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get watchlist details with stocks and performance.

    Args:
        watchlist_id: Watchlist ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        WatchlistResponse with details
    """
    service = WatchlistService(session)
    watchlist = await service.get_watchlist(user_id, watchlist_id)

    if not watchlist:
        raise NotFoundError("Watchlist")

    return watchlist


@router.post("/watchlists/{watchlist_id}/add", response_model=WatchlistResponse)
async def add_stock_to_watchlist(
    watchlist_id: int,
    request: AddToWatchlistRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Add stock to watchlist.

    Args:
        watchlist_id: Watchlist ID
        request: Request with stock symbol
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated WatchlistResponse
    """
    service = WatchlistService(session)
    watchlist = await service.add_stock_to_watchlist(
        user_id=user_id,
        watchlist_id=watchlist_id,
        symbol=request.symbol.upper(),
    )

    if not watchlist:
        raise NotFoundError("Watchlist or stock")

    return watchlist


@router.delete("/watchlists/{watchlist_id}/remove/{stock_id}", response_model=WatchlistResponse)
async def remove_stock_from_watchlist(
    watchlist_id: int,
    stock_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Remove stock from watchlist.

    Args:
        watchlist_id: Watchlist ID
        stock_id: Stock ID to remove
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated WatchlistResponse
    """
    service = WatchlistService(session)
    watchlist = await service.remove_stock_from_watchlist(user_id, watchlist_id, stock_id)

    if not watchlist:
        raise NotFoundError("Watchlist or stock")

    return watchlist


@router.put("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: int,
    request: WatchlistUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update watchlist details.

    Args:
        watchlist_id: Watchlist ID
        request: Update request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated WatchlistResponse
    """
    service = WatchlistService(session)
    watchlist = await service.update_watchlist(
        user_id=user_id,
        watchlist_id=watchlist_id,
        name=request.name,
        description=request.description,
        is_default=request.is_default,
    )

    if not watchlist:
        raise NotFoundError("Watchlist")

    return watchlist


@router.delete("/watchlists/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Delete a watchlist.

    Args:
        watchlist_id: Watchlist ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Success message
    """
    service = WatchlistService(session)
    success = await service.delete_watchlist(user_id, watchlist_id)

    if not success:
        raise NotFoundError("Watchlist")

    return {"message": "Watchlist deleted successfully"}
