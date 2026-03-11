"""OHLC data repository for data access."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models import OHLCData
from app.repositories.base_repository import BaseRepository


class OHLCRepository(BaseRepository[OHLCData]):
    """Repository for OHLCData model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize OHLC repository."""
        super().__init__(OHLCData, session)

    async def get_candlesticks(
        self, stock_id: int, timeframe: str, limit: int = 500
    ) -> List[OHLCData]:
        """Get candlestick data for a stock.

        Args:
            stock_id: Stock ID
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 1d)
            limit: Maximum number of candles to return

        Returns:
            List of OHLCData instances
        """
        query = (
            select(OHLCData)
            .where(
                and_(
                    OHLCData.stock_id == stock_id,
                    OHLCData.timeframe == timeframe,
                )
            )
            .order_by(desc(OHLCData.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(query)
        data = result.scalars().all()
        return list(reversed(data))  # Return oldest first

    async def get_candlestick_by_time(
        self, stock_id: int, timeframe: str, timestamp: datetime
    ) -> Optional[OHLCData]:
        """Get candlestick data for specific time.

        Args:
            stock_id: Stock ID
            timeframe: Timeframe
            timestamp: Timestamp

        Returns:
            OHLCData instance or None
        """
        query = select(OHLCData).where(
            and_(
                OHLCData.stock_id == stock_id,
                OHLCData.timeframe == timeframe,
                OHLCData.timestamp == timestamp,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_latest_candlestick(
        self, stock_id: int, timeframe: str
    ) -> Optional[OHLCData]:
        """Get latest candlestick for a stock.

        Args:
            stock_id: Stock ID
            timeframe: Timeframe

        Returns:
            Latest OHLCData instance or None
        """
        query = (
            select(OHLCData)
            .where(
                and_(
                    OHLCData.stock_id == stock_id,
                    OHLCData.timeframe == timeframe,
                )
            )
            .order_by(desc(OHLCData.timestamp))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_candlesticks_by_time_range(
        self,
        stock_id: int,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[OHLCData]:
        """Get candlesticks within time range.

        Args:
            stock_id: Stock ID
            timeframe: Timeframe
            start_time: Start datetime
            end_time: End datetime

        Returns:
            List of OHLCData instances
        """
        query = (
            select(OHLCData)
            .where(
                and_(
                    OHLCData.stock_id == stock_id,
                    OHLCData.timeframe == timeframe,
                    OHLCData.timestamp >= start_time,
                    OHLCData.timestamp <= end_time,
                )
            )
            .order_by(OHLCData.timestamp)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_old_data(self, stock_id: int, timeframe: str, before_date: datetime):
        """Delete old OHLC data.

        Args:
            stock_id: Stock ID
            timeframe: Timeframe
            before_date: Delete data before this date
        """
        from sqlalchemy import delete

        query = delete(OHLCData).where(
            and_(
                OHLCData.stock_id == stock_id,
                OHLCData.timeframe == timeframe,
                OHLCData.timestamp < before_date,
            )
        )
        await self.session.execute(query)
