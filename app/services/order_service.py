"""Order service for order management."""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories import OrderRepository, StockRepository
from app.models import Order, OrderStatus, OrderType, OrderSide, User
from app.schemas import OrderResponse
from app.audit import AuditLogger
from app.exceptions import InvalidSymbolError
import logging
import re

logger = logging.getLogger(__name__)


class OrderService:
    """Service for managing orders."""

    def __init__(self, session: AsyncSession, audit_logger: Optional[AuditLogger] = None):
        """Initialize order service.

        Args:
            session: AsyncSession instance
            audit_logger: AuditLogger instance for logging operations
        """
        self.session = session
        self.order_repo = OrderRepository(session)
        self.stock_repo = StockRepository(session)
        self.audit_logger = audit_logger

    async def validate_buying_power(
        self, user_id: int, quantity: Decimal, price: Decimal
    ) -> bool:
        """Validate user has sufficient buying power for order.

        Args:
            user_id: User ID
            quantity: Order quantity
            price: Price per share

        Returns:
            True if user has sufficient buying power

        Raises:
            ValueError: If insufficient buying power
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        required_cash = quantity * price
        if user.cash_balance < required_cash:
            raise ValueError(
                f"Insufficient buying power. Required: {required_cash}, Available: {user.cash_balance}"
            )
        return True

    async def create_order(
        self,
        user_id: int,
        symbol: str,
        order_type: str,
        side: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        expires_at: Optional[datetime] = None,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Optional[OrderResponse]:
        """Create a new order.

        Args:
            user_id: User ID
            symbol: Stock symbol
            order_type: Order type (market, limit, stop, stop_limit)
            side: Order side (buy, sell)
            quantity: Number of shares
            price: Limit price (for limit/stop_limit orders)
            stop_price: Stop price (for stop/stop_limit orders)
            expires_at: Order expiration time
            request_ip: IP address of the request
            user_agent: User-Agent header from request

        Returns:
            OrderResponse or None
        """
        # Check for idempotency key to prevent duplicate orders from rapid clicks
        if idempotency_key:
            existing_order = await self.order_repo.get_by_idempotency_key(idempotency_key)
            if existing_order:
                logger.info(
                    f"Order {existing_order.id} already exists with idempotency_key {idempotency_key}"
                )
                return self._convert_to_response(existing_order)

        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            error_msg = f"Stock not found: {symbol}"
            logger.warning(error_msg)
            if self.audit_logger:
                await self.audit_logger.log_action(
                    user_id=user_id,
                    action="create_order",
                    resource_type="order",
                    status="failure",
                    error_message=error_msg,
                    request_ip=request_ip,
                    user_agent=user_agent,
                )
            return None

        # Validate buying power for buy orders
        if side.lower() == OrderSide.BUY.value:
            effective_price = price if price else Decimal("0")
            if effective_price == Decimal("0"):
                error_msg = "Cannot determine price for buying power validation"
                logger.warning(error_msg)
                if self.audit_logger:
                    await self.audit_logger.log_action(
                        user_id=user_id,
                        action="create_order",
                        resource_type="order",
                        status="failure",
                        error_message=error_msg,
                        request_ip=request_ip,
                        user_agent=user_agent,
                    )
                return None

            try:
                await self.validate_buying_power(user_id, quantity, effective_price)
            except ValueError as e:
                error_msg = str(e)
                logger.warning(error_msg)
                if self.audit_logger:
                    await self.audit_logger.log_action(
                        user_id=user_id,
                        action="create_order",
                        resource_type="order",
                        status="failure",
                        error_message=error_msg,
                        request_ip=request_ip,
                        user_agent=user_agent,
                    )
                return None

        # Validate order parameters
        if order_type == OrderType.LIMIT.value and price is None:
            error_msg = "Limit order requires a price"
            logger.warning(error_msg)
            if self.audit_logger:
                await self.audit_logger.log_action(
                    user_id=user_id,
                    action="create_order",
                    resource_type="order",
                    status="failure",
                    error_message=error_msg,
                    request_ip=request_ip,
                    user_agent=user_agent,
                )
            return None

        if order_type in [OrderType.STOP.value, OrderType.STOP_LIMIT.value] and stop_price is None:
            error_msg = f"{order_type} order requires a stop price"
            logger.warning(error_msg)
            if self.audit_logger:
                await self.audit_logger.log_action(
                    user_id=user_id,
                    action="create_order",
                    resource_type="order",
                    status="failure",
                    error_message=error_msg,
                    request_ip=request_ip,
                    user_agent=user_agent,
                )
            return None

        try:
            order = Order(
                user_id=user_id,
                stock_id=stock.id,
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                expires_at=expires_at,
                status=OrderStatus.PENDING.value,
                idempotency_key=idempotency_key,
            )
            order = await self.order_repo.create(order)
            await self.session.commit()

            # Log successful order creation
            if self.audit_logger:
                await self.audit_logger.log_action(
                    user_id=user_id,
                    action="create_order",
                    resource_type="order",
                    resource_id=order.id,
                    after_state={
                        "symbol": symbol,
                        "quantity": str(quantity),
                        "price": str(price) if price else None,
                        "stop_price": str(stop_price) if stop_price else None,
                        "type": order_type,
                        "side": side,
                    },
                    status="success",
                    request_ip=request_ip,
                    user_agent=user_agent,
                )

            logger.info(f"Created order {order.id} for user {user_id}: {side} {quantity} {symbol}")
            return self._convert_to_response(order)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating order: {error_msg}", exc_info=True)
            if self.audit_logger:
                await self.audit_logger.log_action(
                    user_id=user_id,
                    action="create_order",
                    resource_type="order",
                    status="failure",
                    error_message=error_msg,
                    request_ip=request_ip,
                    user_agent=user_agent,
                )
            raise

    async def get_user_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[OrderResponse]:
        """Get all orders for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of OrderResponse objects
        """
        orders = await self.order_repo.get_user_orders(user_id, skip, limit)
        return [self._convert_to_response(o) for o in orders]

    async def get_pending_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[OrderResponse]:
        """Get pending orders for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending OrderResponse objects
        """
        orders = await self.order_repo.get_pending_orders(user_id, skip, limit)
        return [self._convert_to_response(o) for o in orders]

    async def get_order(self, user_id: int, order_id: int) -> Optional[OrderResponse]:
        """Get specific order for a user.

        Args:
            user_id: User ID
            order_id: Order ID

        Returns:
            OrderResponse or None
        """
        order = await self.order_repo.get_user_order(user_id, order_id)
        if not order:
            return None
        return self._convert_to_response(order)

    async def update_order(
        self,
        user_id: int,
        order_id: int,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        expires_at: Optional[datetime] = None,
    ) -> Optional[OrderResponse]:
        """Update an order (only for limit orders).

        Args:
            user_id: User ID
            order_id: Order ID
            price: New limit price
            stop_price: New stop price
            expires_at: New expiration time

        Returns:
            Updated OrderResponse or None
        """
        order = await self.order_repo.get_user_order(user_id, order_id)
        if not order:
            return None

        # Can only update pending orders
        if order.status not in [OrderStatus.PENDING.value, OrderStatus.PARTIALLY_FILLED.value]:
            logger.warning(f"Cannot update order with status {order.status}")
            return None

        update_data = {}
        if price is not None:
            update_data["price"] = price
        if stop_price is not None:
            update_data["stop_price"] = stop_price
        if expires_at is not None:
            update_data["expires_at"] = expires_at

        if update_data:
            order = await self.order_repo.update(order_id, **update_data)
            await self.session.commit()

        return self._convert_to_response(order)

    async def cancel_order(
        self,
        user_id: int,
        order_id: int,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Cancel an order.

        Args:
            user_id: User ID
            order_id: Order ID
            request_ip: IP address of the request
            user_agent: User-Agent header from request

        Returns:
            True if cancelled, False otherwise
        """
        order = await self.order_repo.get_user_order(user_id, order_id)
        if not order:
            return False

        # Can only cancel pending or partially filled orders
        if order.status not in [OrderStatus.PENDING.value, OrderStatus.PARTIALLY_FILLED.value]:
            logger.warning(f"Cannot cancel order with status {order.status}")
            return False

        before_state = {"status": order.status}
        order = await self.order_repo.update(order_id, status=OrderStatus.CANCELLED.value)
        await self.session.commit()

        # Log order cancellation
        if self.audit_logger:
            await self.audit_logger.log_action(
                user_id=user_id,
                action="cancel_order",
                resource_type="order",
                resource_id=order_id,
                before_state=before_state,
                after_state={"status": OrderStatus.CANCELLED.value},
                status="success",
                request_ip=request_ip,
                user_agent=user_agent,
            )

        logger.info(f"Cancelled order {order_id}")
        return True

    async def fill_order(
        self,
        order_id: int,
        filled_quantity: Decimal,
        average_filled_price: Decimal,
    ) -> Optional[OrderResponse]:
        """Fill an order (internal method for order execution).

        Args:
            order_id: Order ID
            filled_quantity: Quantity filled
            average_filled_price: Average price of filled portion

        Returns:
            Updated OrderResponse or None
        """
        order = await self.order_repo.get(order_id)
        if not order:
            return None

        remaining_quantity = order.quantity - filled_quantity
        new_status = (
            OrderStatus.FILLED.value
            if remaining_quantity <= 0
            else OrderStatus.PARTIALLY_FILLED.value
        )

        update_data = {
            "filled_quantity": filled_quantity,
            "average_filled_price": average_filled_price,
            "status": new_status,
        }

        if new_status == OrderStatus.FILLED.value:
            update_data["filled_at"] = datetime.utcnow()

        order = await self.order_repo.update(order_id, **update_data)
        await self.session.commit()
        logger.info(f"Filled order {order_id}: {filled_quantity} shares")
        return self._convert_to_response(order)

    async def expire_orders(self) -> int:
        """Expire all expired orders.

        Returns:
            Number of orders expired
        """
        expired_orders = await self.order_repo.get_expired_orders()
        count = 0
        for order in expired_orders:
            await self.order_repo.update(order.id, status=OrderStatus.EXPIRED.value)
            count += 1
        if count > 0:
            await self.session.commit()
            logger.info(f"Expired {count} orders")
        return count

    def _validate_symbol(self, symbol: str) -> bool:
        """
        Validate stock symbol format.

        Symbol must be 1-10 characters, contain only letters, hyphens, and periods.

        Args:
            symbol: Symbol to validate

        Returns:
            True if valid

        Raises:
            InvalidSymbolError: If symbol is invalid
        """
        if not symbol:
            raise InvalidSymbolError("")
        if len(symbol) > 10:
            raise InvalidSymbolError(symbol)
        if not re.match(r'^[A-Za-z\-\.]+$', symbol):
            raise InvalidSymbolError(symbol)
        return True

    def _convert_to_response(self, order: Order) -> OrderResponse:
        """Convert Order model to OrderResponse schema.

        Args:
            order: Order model instance

        Returns:
            OrderResponse object
        """
        from app.schemas import StockResponse

        return OrderResponse(
            id=order.id,
            stock=StockResponse(
                id=order.stock_id,
                symbol=order.stock.symbol,
                name=order.stock.name,
                sector=order.stock.sector,
                industry=order.stock.industry,
                exchange=order.stock.exchange,
                is_active=order.stock.is_active,
                created_at=order.stock.created_at,
                updated_at=order.stock.updated_at,
            ),
            order_type=order.order_type,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            stop_price=order.stop_price,
            filled_quantity=order.filled_quantity,
            average_filled_price=order.average_filled_price,
            status=order.status,
            expires_at=order.expires_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            filled_at=order.filled_at,
        )
