"""Quote repository for data access."""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.models import Quote
from app.repositories.base_repository import BaseRepository


class QuoteRepository(BaseRepository[Quote]):
    """Repository for Quote model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize quote repository."""
        super().__init__(Quote, session)

    async def get_latest_by_stock_id(self, stock_id: int) -> Optional[Quote]:
        """Get latest quote for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            Latest Quote instance or None
        """
        query = (
            select(Quote)
            .where(Quote.stock_id == stock_id)
            .order_by(desc(Quote.timestamp))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_latest_by_stock_ids(self, stock_ids: List[int]) -> List[Quote]:
        """Get latest quotes for multiple stocks.

        Args:
            stock_ids: List of stock IDs

        Returns:
            List of Quote instances
        """
        subquery = (
            select(Quote.stock_id, func.max(Quote.timestamp).label("max_timestamp"))
            .where(Quote.stock_id.in_(stock_ids))
            .group_by(Quote.stock_id)
            .subquery()
        )
        query = select(Quote).join(
            subquery,
            and_(
                Quote.stock_id == subquery.c.stock_id,
                Quote.timestamp == subquery.c.max_timestamp,
            ),
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_historical(
        self, stock_id: int, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[Quote]:
        """Get historical quotes for a stock.

        Args:
            stock_id: Stock ID
            hours: Number of hours to look back
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Quote instances
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = (
            select(Quote)
            .where(
                and_(
                    Quote.stock_id == stock_id,
                    Quote.timestamp >= cutoff_time,
                )
            )
            .order_by(desc(Quote.timestamp))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_time_range(
        self, stock_id: int, start_time: datetime, end_time: datetime
    ) -> List[Quote]:
        """Get quotes within time range.

        Args:
            stock_id: Stock ID
            start_time: Start datetime
            end_time: End datetime

        Returns:
            List of Quote instances
        """
        query = (
            select(Quote)
            .where(
                and_(
                    Quote.stock_id == stock_id,
                    Quote.timestamp >= start_time,
                    Quote.timestamp <= end_time,
                )
            )
            .order_by(desc(Quote.timestamp))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_daily_change(self, stock_id: int) -> Optional[dict]:
        """Get daily change metrics for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            Dictionary with daily metrics or None
        """
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        query = (
            select(
                func.max(Quote.price).label("high"),
                func.min(Quote.price).label("low"),
                func.first_value(Quote.price).over(order_by=Quote.timestamp).label("open"),
                func.last_value(Quote.price).over(order_by=Quote.timestamp).label("close"),
                func.sum(Quote.volume).label("volume"),
            )
            .where(
                and_(
                    Quote.stock_id == stock_id,
                    Quote.timestamp >= start_of_day,
                )
            )
        )
        result = await self.session.execute(query)
        row = result.first()
        if row and row.close:
            return {
                "high": row.high,
                "low": row.low,
                "open": row.open,
                "close": row.close,
                "volume": row.volume,
            }
        return None
