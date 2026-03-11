"""Watchlist repository for data access."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Watchlist, WatchlistItem, Stock
from app.repositories.base_repository import BaseRepository


class WatchlistRepository(BaseRepository[Watchlist]):
    """Repository for Watchlist model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize watchlist repository."""
        super().__init__(Watchlist, session)

    async def get_user_watchlists(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Watchlist]:
        """Get all watchlists for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Watchlist instances
        """
        query = (
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_default_watchlist(self, user_id: int) -> Optional[Watchlist]:
        """Get default watchlist for a user.

        Args:
            user_id: User ID

        Returns:
            Watchlist instance or None
        """
        query = select(Watchlist).where(
            and_(Watchlist.user_id == user_id, Watchlist.is_default == True)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def add_stock(self, watchlist_id: int, stock_id: int) -> WatchlistItem:
        """Add stock to watchlist.

        Args:
            watchlist_id: Watchlist ID
            stock_id: Stock ID

        Returns:
            Created WatchlistItem instance
        """
        item = WatchlistItem(watchlist_id=watchlist_id, stock_id=stock_id)
        self.session.add(item)
        await self.session.flush()
        return item

    async def remove_stock(self, watchlist_id: int, stock_id: int) -> bool:
        """Remove stock from watchlist.

        Args:
            watchlist_id: Watchlist ID
            stock_id: Stock ID

        Returns:
            True if removed, False if not found
        """
        query = select(WatchlistItem).where(
            and_(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.stock_id == stock_id,
            )
        )
        result = await self.session.execute(query)
        item = result.scalars().first()
        if item:
            await self.session.delete(item)
            return True
        return False

    async def is_stock_in_watchlist(
        self, watchlist_id: int, stock_id: int
    ) -> bool:
        """Check if stock is in watchlist.

        Args:
            watchlist_id: Watchlist ID
            stock_id: Stock ID

        Returns:
            True if in watchlist, False otherwise
        """
        query = select(WatchlistItem).where(
            and_(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.stock_id == stock_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None

    async def get_watchlist_stocks(self, watchlist_id: int) -> List[Stock]:
        """Get all stocks in a watchlist.

        Args:
            watchlist_id: Watchlist ID

        Returns:
            List of Stock instances
        """
        query = (
            select(Stock)
            .join(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_watchlist_item_count(self, watchlist_id: int) -> int:
        """Get number of stocks in watchlist.

        Args:
            watchlist_id: Watchlist ID

        Returns:
            Number of stocks
        """
        query = select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id
        )
        result = await self.session.execute(query)
        return len(result.scalars().all())
