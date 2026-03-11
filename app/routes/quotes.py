"""Market data API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import QuoteService
from app.schemas import QuoteResponse, BatchQuoteResponse, BatchQuoteRequest
from datetime import datetime

router = APIRouter()


@router.get("/quotes/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str, session: AsyncSession = Depends(get_db)):
    """Get real-time stock quote.

    Args:
        symbol: Stock symbol (e.g., AAPL)
        session: Database session

    Returns:
        QuoteResponse with current price and market data
    """
    service = QuoteService(session)
    quote = await service.get_quote(symbol.upper())

    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")

    return quote


@router.post("/quotes/batch", response_model=BatchQuoteResponse)
async def get_batch_quotes(
    request: BatchQuoteRequest,
    session: AsyncSession = Depends(get_db),
):
    """Get multiple stock quotes in one request.

    Args:
        request: BatchQuoteRequest with list of symbols
        session: Database session

    Returns:
        BatchQuoteResponse with multiple quotes
    """
    service = QuoteService(session)
    symbols = [s.upper() for s in request.symbols]
    quotes = await service.get_quotes(symbols)

    return BatchQuoteResponse(
        quotes=quotes,
        timestamp=datetime.utcnow(),
    )


@router.get("/indices")
async def get_indices(session: AsyncSession = Depends(get_db)):
    """Get market indices (S&P 500, NASDAQ-100, etc.).

    Args:
        session: Database session

    Returns:
        List of index data
    """
    # TODO: Implement market indices endpoint
    return {
        "message": "Market indices endpoint",
        "timestamp": datetime.utcnow(),
    }


@router.get("/indices/{index}/constituents")
async def get_index_constituents(
    index: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get stocks in a market index.

    Args:
        index: Index symbol (e.g., SPX, NDX)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of stocks in the index
    """
    # TODO: Implement index constituents endpoint
    return {
        "index": index,
        "constituents": [],
        "total": 0,
        "timestamp": datetime.utcnow(),
    }


@router.get("/sectors")
async def get_sector_performance(session: AsyncSession = Depends(get_db)):
    """Get sector performance data.

    Args:
        session: Database session

    Returns:
        Sector performance metrics
    """
    # TODO: Implement sector performance endpoint
    return {
        "sectors": [],
        "timestamp": datetime.utcnow(),
    }


@router.get("/vix")
async def get_vix(session: AsyncSession = Depends(get_db)):
    """Get VIX (volatility index) data.

    Args:
        session: Database session

    Returns:
        VIX data with volatility metrics
    """
    # TODO: Implement VIX endpoint
    return {
        "symbol": "VIX",
        "price": None,
        "timestamp": datetime.utcnow(),
    }
