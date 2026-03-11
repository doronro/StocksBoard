"""Position repository for data access."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from decimal import Decimal
from app.models import Position, PositionStatus
from app.repositories.base_repository import BaseRepository


class PositionRepository(BaseRepository[Position]):
    """Repository for Position model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize position repository."""
        super().__init__(Position, session)

    async def get_user_positions(
        self, user_id: int, status: Optional[PositionStatus] = None, skip: int = 0, limit: int = 100
    ) -> List[Position]:
        """Get all positions for a user.

        Args:
            user_id: User ID
            status: Optional position status filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Position instances
        """
        query = select(Position).where(Position.user_id == user_id)
        if status:
            query = query.where(Position.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_position_by_stock(
        self, user_id: int, stock_id: int
    ) -> Optional[Position]:
        """Get user position for a specific stock.

        Args:
            user_id: User ID
            stock_id: Stock ID

        Returns:
            Position instance or None
        """
        query = select(Position).where(
            and_(Position.user_id == user_id, Position.stock_id == stock_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_open_positions(self, user_id: int) -> List[Position]:
        """Get all open positions for a user.

        Args:
            user_id: User ID

        Returns:
            List of open Position instances
        """
        query = select(Position).where(
            and_(
                Position.user_id == user_id,
                Position.status.in_([PositionStatus.OPEN, PositionStatus.PARTIALLY_CLOSED]),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_closed_positions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Position]:
        """Get all closed positions for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of closed Position instances
        """
        query = (
            select(Position)
            .where(
                and_(
                    Position.user_id == user_id,
                    Position.status == PositionStatus.CLOSED,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_portfolio_metrics(self, user_id: int) -> Optional[dict]:
        """Get portfolio metrics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with portfolio metrics
        """
        query = select(
            func.count(Position.id).label("total_positions"),
            func.sum(Position.total_cost).label("total_cost"),
            func.sum(Position.current_value).label("current_value"),
            func.sum(Position.unrealized_gain_loss).label("total_gain_loss"),
        ).where(
            and_(
                Position.user_id == user_id,
                Position.status.in_([PositionStatus.OPEN, PositionStatus.PARTIALLY_CLOSED]),
            )
        )
        result = await self.session.execute(query)
        row = result.first()
        if row and row.total_cost:
            return {
                "total_positions": row.total_positions or 0,
                "total_cost": row.total_cost or Decimal("0"),
                "current_value": row.current_value or Decimal("0"),
                "total_gain_loss": row.total_gain_loss or Decimal("0"),
                "total_gain_loss_percent": (
                    (row.total_gain_loss / row.total_cost * 100)
                    if row.total_cost and row.total_gain_loss
                    else Decimal("0")
                ),
            }
        return None

    async def get_sector_allocation(self, user_id: int) -> List[dict]:
        """Get portfolio allocation by sector.

        Args:
            user_id: User ID

        Returns:
            List of sector allocation data
        """
        from app.models import Stock

        query = (
            select(
                Stock.sector,
                func.sum(Position.current_value).label("sector_value"),
                func.count(Position.id).label("stock_count"),
            )
            .join(Stock)
            .where(
                and_(
                    Position.user_id == user_id,
                    Position.status.in_([PositionStatus.OPEN, PositionStatus.PARTIALLY_CLOSED]),
                )
            )
            .group_by(Stock.sector)
        )
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {"sector": row.sector, "value": row.sector_value, "stock_count": row.stock_count}
            for row in rows
        ]

    async def count_by_user_and_status(
        self, user_id: int, status: PositionStatus
    ) -> int:
        """Count positions for user with specific status.

        Args:
            user_id: User ID
            status: Position status to count

        Returns:
            Count of positions with given status
        """
        query = select(func.count(Position.id)).where(
            and_(Position.user_id == user_id, Position.status == status)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
