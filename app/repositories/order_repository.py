"""Order repository for data access."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models import Order, OrderStatus
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize order repository."""
        super().__init__(Order, session)

    async def get_user_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get all orders for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Order instances
        """
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_pending_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get all pending orders for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending Order instances
        """
        query = (
            select(Order)
            .where(
                and_(
                    Order.user_id == user_id,
                    Order.status.in_([OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]),
                )
            )
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_order(self, user_id: int, order_id: int) -> Optional[Order]:
        """Get specific order for a user.

        Args:
            user_id: User ID
            order_id: Order ID

        Returns:
            Order instance or None
        """
        query = select(Order).where(
            and_(Order.user_id == user_id, Order.id == order_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_expired_orders(self) -> List[Order]:
        """Get all expired orders.

        Returns:
            List of expired Order instances
        """
        now = datetime.utcnow()
        query = select(Order).where(
            and_(
                Order.expires_at <= now,
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_filled_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get all filled orders for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of filled Order instances
        """
        query = (
            select(Order)
            .where(
                and_(
                    Order.user_id == user_id,
                    Order.status.in_([OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]),
                )
            )
            .order_by(desc(Order.filled_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_buy_orders(
        self, user_id: int, status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get all buy orders for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of buy Order instances
        """
        query = select(Order).where(
            and_(Order.user_id == user_id, Order.side == "buy")
        )
        if status:
            query = query.where(Order.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_sell_orders(
        self, user_id: int, status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get all sell orders for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of sell Order instances
        """
        query = select(Order).where(
            and_(Order.user_id == user_id, Order.side == "sell")
        )
        if status:
            query = query.where(Order.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Order]:
        """Get order by idempotency key (for deduplication).

        Args:
            idempotency_key: Idempotency key

        Returns:
            Order instance or None
        """
        query = select(Order).where(Order.idempotency_key == idempotency_key)
        result = await self.session.execute(query)
        return result.scalars().first()
