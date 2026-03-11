"""Technical indicator repository for data access."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models import TechnicalIndicator
from app.repositories.base_repository import BaseRepository


class TechnicalIndicatorRepository(BaseRepository[TechnicalIndicator]):
    """Repository for TechnicalIndicator model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize technical indicator repository."""
        super().__init__(TechnicalIndicator, session)

    async def get_latest_indicator(
        self, stock_id: int, indicator_name: str, period: Optional[int] = None,
        timeframe: str = "1d"
    ) -> Optional[TechnicalIndicator]:
        """Get latest technical indicator value.

        Args:
            stock_id: Stock ID
            indicator_name: Indicator name (SMA, EMA, RSI, MACD, BB)
            period: Optional period
            timeframe: Timeframe

        Returns:
            Latest TechnicalIndicator instance or None
        """
        query = select(TechnicalIndicator).where(
            and_(
                TechnicalIndicator.stock_id == stock_id,
                TechnicalIndicator.indicator_name == indicator_name,
                TechnicalIndicator.timeframe == timeframe,
            )
        )
        if period:
            query = query.where(TechnicalIndicator.period == period)
        query = query.order_by(desc(TechnicalIndicator.timestamp)).limit(1)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_indicator_history(
        self,
        stock_id: int,
        indicator_name: str,
        period: Optional[int] = None,
        timeframe: str = "1d",
        limit: int = 100,
    ) -> List[TechnicalIndicator]:
        """Get technical indicator history.

        Args:
            stock_id: Stock ID
            indicator_name: Indicator name
            period: Optional period
            timeframe: Timeframe
            limit: Maximum number of records

        Returns:
            List of TechnicalIndicator instances
        """
        query = select(TechnicalIndicator).where(
            and_(
                TechnicalIndicator.stock_id == stock_id,
                TechnicalIndicator.indicator_name == indicator_name,
                TechnicalIndicator.timeframe == timeframe,
            )
        )
        if period:
            query = query.where(TechnicalIndicator.period == period)
        query = query.order_by(desc(TechnicalIndicator.timestamp)).limit(limit)
        result = await self.session.execute(query)
        data = result.scalars().all()
        return list(reversed(data))  # Return oldest first

    async def get_indicators_by_type(
        self,
        stock_id: int,
        indicator_name: str,
        timeframe: str = "1d",
        limit: int = 100,
    ) -> List[TechnicalIndicator]:
        """Get all indicators of specific type.

        Args:
            stock_id: Stock ID
            indicator_name: Indicator name
            timeframe: Timeframe
            limit: Maximum number of records

        Returns:
            List of TechnicalIndicator instances
        """
        query = (
            select(TechnicalIndicator)
            .where(
                and_(
                    TechnicalIndicator.stock_id == stock_id,
                    TechnicalIndicator.indicator_name == indicator_name,
                    TechnicalIndicator.timeframe == timeframe,
                )
            )
            .order_by(desc(TechnicalIndicator.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(query)
        data = result.scalars().all()
        return list(reversed(data))

    async def delete_old_indicators(
        self, stock_id: int, indicator_name: str, before_date: datetime
    ):
        """Delete old indicator data.

        Args:
            stock_id: Stock ID
            indicator_name: Indicator name
            before_date: Delete data before this date
        """
        from sqlalchemy import delete

        query = delete(TechnicalIndicator).where(
            and_(
                TechnicalIndicator.stock_id == stock_id,
                TechnicalIndicator.indicator_name == indicator_name,
                TechnicalIndicator.timestamp < before_date,
            )
        )
        await self.session.execute(query)
