"""Stock repository for data access."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Stock
from app.repositories.base_repository import BaseRepository


class StockRepository(BaseRepository[Stock]):
    """Repository for Stock model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize stock repository."""
        super().__init__(Stock, session)

    async def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get stock by symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Stock instance or None
        """
        query = select(Stock).where(Stock.symbol == symbol)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_symbols(self, symbols: List[str]) -> List[Stock]:
        """Get multiple stocks by symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            List of Stock instances
        """
        query = select(Stock).where(Stock.symbol.in_(symbols))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_stocks(self, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Get active stocks with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Stock instances
        """
        query = select(Stock).where(Stock.is_active == True).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_sector(self, sector: str, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Get stocks by sector.

        Args:
            sector: Sector name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Stock instances
        """
        query = (
            select(Stock)
            .where((Stock.sector == sector) & (Stock.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_exchange(self, exchange: str, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Get stocks by exchange.

        Args:
            exchange: Exchange name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Stock instances
        """
        query = (
            select(Stock)
            .where((Stock.exchange == exchange) & (Stock.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_by_name(self, query_str: str, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Search stocks by name or symbol.

        Args:
            query_str: Search string
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Stock instances
        """
        query = (
            select(Stock)
            .where(
                ((Stock.name.ilike(f"%{query_str}%")) | (Stock.symbol.ilike(f"%{query_str}%")))
                & (Stock.is_active == True)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_count(self) -> int:
        """Get count of active stocks.

        Returns:
            Number of active stocks
        """
        query = select(func.count(Stock.id)).where(Stock.is_active == True)
        result = await self.session.execute(query)
        return result.scalar() or 0
