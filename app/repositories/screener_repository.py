"""Screener repository for data access."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models import Screener, ScreenerResult
from app.repositories.base_repository import BaseRepository


class ScreenerRepository(BaseRepository[Screener]):
    """Repository for Screener model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize screener repository."""
        super().__init__(Screener, session)

    async def get_user_screeners(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Screener]:
        """Get all screeners for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Screener instances
        """
        query = (
            select(Screener)
            .where(Screener.user_id == user_id)
            .order_by(desc(Screener.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_public_screeners(self, skip: int = 0, limit: int = 100) -> List[Screener]:
        """Get all public screeners.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Screener instances
        """
        query = (
            select(Screener)
            .where(Screener.is_public == True)
            .order_by(desc(Screener.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_screener(self, user_id: int, screener_id: int) -> Optional[Screener]:
        """Get specific screener for a user.

        Args:
            user_id: User ID
            screener_id: Screener ID

        Returns:
            Screener instance or None
        """
        query = select(Screener).where(
            and_(Screener.user_id == user_id, Screener.id == screener_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_screener_results(
        self, screener_id: int, skip: int = 0, limit: int = 100
    ) -> List[ScreenerResult]:
        """Get results for a screener.

        Args:
            screener_id: Screener ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ScreenerResult instances
        """
        query = (
            select(ScreenerResult)
            .where(ScreenerResult.screener_id == screener_id)
            .order_by(desc(ScreenerResult.matched_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_screener_result_count(self, screener_id: int) -> int:
        """Get number of results for a screener.

        Args:
            screener_id: Screener ID

        Returns:
            Number of results
        """
        query = select(ScreenerResult).where(ScreenerResult.screener_id == screener_id)
        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def add_result(self, screener_id: int, stock_id: int) -> ScreenerResult:
        """Add result to screener.

        Args:
            screener_id: Screener ID
            stock_id: Stock ID

        Returns:
            Created ScreenerResult instance
        """
        result = ScreenerResult(screener_id=screener_id, stock_id=stock_id)
        self.session.add(result)
        await self.session.flush()
        return result

    async def clear_results(self, screener_id: int):
        """Clear all results for a screener.

        Args:
            screener_id: Screener ID
        """
        from sqlalchemy import delete

        query = delete(ScreenerResult).where(ScreenerResult.screener_id == screener_id)
        await self.session.execute(query)
