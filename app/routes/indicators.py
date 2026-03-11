"""Technical analysis and charting API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import IndicatorService
from app.repositories import OHLCRepository, StockRepository
from app.schemas import (
    TechnicalIndicatorResponse,
    CalculateIndicatorRequest,
    CandlestickResponse,
    OHLCDataResponse,
)

router = APIRouter()


@router.get("/charts/{symbol}/{timeframe}", response_model=CandlestickResponse)
async def get_candlesticks(
    symbol: str,
    timeframe: str,
    limit: int = Query(500, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get OHLC candlestick data for charting.

    Args:
        symbol: Stock symbol
        timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 1d)
        limit: Maximum number of candles (default 500)
        session: Database session

    Returns:
        CandlestickResponse with OHLC data
    """
    stock_repo = StockRepository(session)
    ohlc_repo = OHLCRepository(session)

    stock = await stock_repo.get_by_symbol(symbol.upper())
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock not found: {symbol}")

    candlesticks = await ohlc_repo.get_candlesticks(stock.id, timeframe, limit)

    data = [
        OHLCDataResponse(
            symbol=symbol.upper(),
            timeframe=timeframe,
            open=c.open_price,
            high=c.high,
            low=c.low,
            close=c.close,
            volume=c.volume,
            timestamp=c.timestamp,
        )
        for c in candlesticks
    ]

    from datetime import datetime

    return CandlestickResponse(
        data=data,
        symbol=symbol.upper(),
        timeframe=timeframe,
        count=len(data),
        timestamp=datetime.utcnow(),
    )


@router.get("/indicators/{symbol}/{indicator}", response_model=TechnicalIndicatorResponse)
async def get_indicator(
    symbol: str,
    indicator: str,
    period: int = Query(20, ge=1, le=500),
    timeframe: str = Query("1d", regex="^(1m|5m|15m|30m|1h|1d)$"),
    session: AsyncSession = Depends(get_db),
):
    """Get technical indicator value.

    Args:
        symbol: Stock symbol
        indicator: Indicator name (SMA, EMA, RSI, MACD, BB)
        period: Period for the indicator
        timeframe: Timeframe (1d, 1h, etc.)
        session: Database session

    Returns:
        TechnicalIndicatorResponse with indicator value
    """
    service = IndicatorService(session)
    indicator_resp = await service.get_latest_indicator(
        symbol=symbol.upper(),
        indicator_name=indicator.upper(),
        period=period,
        timeframe=timeframe,
    )

    if not indicator_resp:
        raise HTTPException(status_code=404, detail=f"Indicator not found: {indicator}")

    return indicator_resp


@router.get("/indicators/{symbol}/{indicator}/history", response_model=List[TechnicalIndicatorResponse])
async def get_indicator_history(
    symbol: str,
    indicator: str,
    period: int = Query(20, ge=1, le=500),
    timeframe: str = Query("1d", regex="^(1m|5m|15m|30m|1h|1d)$"),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get technical indicator history.

    Args:
        symbol: Stock symbol
        indicator: Indicator name
        period: Period for the indicator
        timeframe: Timeframe
        limit: Maximum number of records
        session: Database session

    Returns:
        List of TechnicalIndicatorResponse objects
    """
    service = IndicatorService(session)
    indicators = await service.get_indicator_history(
        symbol=symbol.upper(),
        indicator_name=indicator.upper(),
        period=period,
        timeframe=timeframe,
        limit=limit,
    )

    return indicators


@router.post("/indicators/calculate", response_model=TechnicalIndicatorResponse)
async def calculate_indicator(
    request: CalculateIndicatorRequest,
    session: AsyncSession = Depends(get_db),
):
    """Calculate technical indicator and save result.

    Args:
        request: Indicator calculation request
        session: Database session

    Returns:
        TechnicalIndicatorResponse with calculated value
    """
    service = IndicatorService(session)
    indicator = request.indicator.upper()
    symbol = request.symbol.upper()

    if indicator == "SMA":
        result = await service.calculate_sma(symbol, request.period, request.timeframe)
    elif indicator == "EMA":
        result = await service.calculate_ema(symbol, request.period, request.timeframe)
    elif indicator == "RSI":
        result = await service.calculate_rsi(symbol, request.period, request.timeframe)
    elif indicator == "MACD":
        result = await service.calculate_macd(symbol, timeframe=request.timeframe)
    elif indicator == "BB":
        result = await service.calculate_bollinger_bands(symbol, request.period, timeframe=request.timeframe)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown indicator: {indicator}")

    if not result:
        raise HTTPException(status_code=400, detail="Failed to calculate indicator")

    return result


@router.post("/charts/calculations")
async def calculate_custom_indicators(
    requests: List[CalculateIndicatorRequest],
    session: AsyncSession = Depends(get_db),
):
    """Calculate multiple custom indicators.

    Args:
        requests: List of indicator calculation requests
        session: Database session

    Returns:
        Dictionary with calculated indicators
    """
    # TODO: Implement batch indicator calculation
    from datetime import datetime

    return {
        "results": [],
        "count": 0,
        "timestamp": datetime.utcnow(),
    }
