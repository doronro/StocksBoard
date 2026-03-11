"""
Unit tests for critical security and QA fixes.

Tests for:
- SEC-001: JWT Secret Key Fallback Vulnerability
- SEC-011: Password Validation
- SEC-002: Token Refresh User Validation
- SEC-018: Buying Power Validation
- QA-008: Concurrent Order Race Condition (Idempotency)
- QA-002: Closed Positions Count
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.services.order_service import OrderService
from app.services.portfolio_service import PortfolioService
from app.models import User, Order, Stock, Position, PositionStatus, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.position_repository import PositionRepository
from app.schemas import CreateOrderRequest, PositionResponse


class TestPasswordValidation:
    """SEC-011: Tests for password strength validation."""

    def test_validate_password_valid(self):
        """validate_password accepts strong password."""
        password = "StrongPass123!@#"
        assert UserService.validate_password(password) is True

    def test_validate_password_too_short(self):
        """validate_password rejects password shorter than 12 characters."""
        with pytest.raises(ValueError, match="at least 12 characters"):
            UserService.validate_password("Short1!")

    def test_validate_password_no_uppercase(self):
        """validate_password rejects password without uppercase letter."""
        with pytest.raises(ValueError, match="uppercase letter"):
            UserService.validate_password("lowercase123!@#")

    def test_validate_password_no_lowercase(self):
        """validate_password rejects password without lowercase letter."""
        with pytest.raises(ValueError, match="lowercase letter"):
            UserService.validate_password("UPPERCASE123!@#")

    def test_validate_password_no_digit(self):
        """validate_password rejects password without digit."""
        with pytest.raises(ValueError, match="digit"):
            UserService.validate_password("NoDigits!@#AbC")

    def test_validate_password_no_special_character(self):
        """validate_password rejects password without special character."""
        with pytest.raises(ValueError, match="special character"):
            UserService.validate_password("NoSpecialChar123")

    @pytest.mark.asyncio
    async def test_create_user_validates_password(self, async_session: AsyncSession):
        """create_user calls validate_password."""
        service = UserService(async_session)

        with pytest.raises(ValueError, match="at least 12 characters"):
            await service.create_user(
                username="testuser",
                email="test@example.com",
                password="weak",
                full_name="Test User",
            )


class TestBuyingPowerValidation:
    """SEC-018: Tests for buying power validation before orders."""

    @pytest.mark.asyncio
    async def test_validate_buying_power_sufficient(self, async_session: AsyncSession):
        """validate_buying_power returns True when user has sufficient funds."""
        service = OrderService(async_session)

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            cash_balance=Decimal("10000.00"),
        )
        async_session.add(user)
        await async_session.commit()

        result = await service.validate_buying_power(
            user_id=1, quantity=Decimal("10"), price=Decimal("100.00")
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_buying_power_insufficient(self, async_session: AsyncSession):
        """validate_buying_power raises ValueError when insufficient funds."""
        service = OrderService(async_session)

        user = User(
            id=2,
            username="testuser2",
            email="test2@example.com",
            hashed_password="hashed",
            cash_balance=Decimal("100.00"),
        )
        async_session.add(user)
        await async_session.commit()

        with pytest.raises(ValueError, match="Insufficient buying power"):
            await service.validate_buying_power(
                user_id=2, quantity=Decimal("100"), price=Decimal("100.00")
            )

    @pytest.mark.asyncio
    async def test_validate_buying_power_exact_amount(self, async_session: AsyncSession):
        """validate_buying_power succeeds with exact amount available."""
        service = OrderService(async_session)

        user = User(
            id=3,
            username="testuser3",
            email="test3@example.com",
            hashed_password="hashed",
            cash_balance=Decimal("1000.00"),
        )
        async_session.add(user)
        await async_session.commit()

        result = await service.validate_buying_power(
            user_id=3, quantity=Decimal("10"), price=Decimal("100.00")
        )
        assert result is True


class TestOrderIdempotency:
    """QA-008: Tests for idempotency key handling to prevent duplicate orders."""

    def test_order_model_has_idempotency_key(self):
        """Order model includes idempotency_key field."""
        order = Order(
            user_id=1,
            stock_id=1,
            order_type="market",
            side="buy",
            quantity=Decimal("10"),
            idempotency_key="unique-key-123",
        )
        assert order.idempotency_key == "unique-key-123"

    @pytest.mark.asyncio
    async def test_get_by_idempotency_key_found(self, async_session: AsyncSession):
        """get_by_idempotency_key returns existing order."""
        repo = OrderRepository(async_session)

        order = Order(
            id=1,
            user_id=1,
            stock_id=1,
            order_type="market",
            side="buy",
            quantity=Decimal("10"),
            idempotency_key="key-123",
            status=OrderStatus.PENDING.value,
        )
        async_session.add(order)
        await async_session.commit()

        found = await repo.get_by_idempotency_key("key-123")
        assert found is not None
        assert found.id == 1
        assert found.idempotency_key == "key-123"

    @pytest.mark.asyncio
    async def test_get_by_idempotency_key_not_found(self, async_session: AsyncSession):
        """get_by_idempotency_key returns None for non-existent key."""
        repo = OrderRepository(async_session)

        found = await repo.get_by_idempotency_key("nonexistent-key")
        assert found is None


class TestClosedPositionsCount:
    """QA-002: Tests for properly counting closed positions."""

    @pytest.mark.asyncio
    async def test_count_by_user_and_status_open(self, async_session: AsyncSession):
        """count_by_user_and_status counts open positions correctly."""
        repo = PositionRepository(async_session)

        position = Position(
            user_id=1,
            stock_id=1,
            quantity=Decimal("10"),
            average_cost=Decimal("100.00"),
            current_price=Decimal("100.00"),
            total_cost=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            status=PositionStatus.OPEN,
        )
        async_session.add(position)
        await async_session.commit()

        count = await repo.count_by_user_and_status(1, PositionStatus.OPEN)
        assert count == 1

    @pytest.mark.asyncio
    async def test_count_by_user_and_status_closed(self, async_session: AsyncSession):
        """count_by_user_and_status counts closed positions correctly."""
        repo = PositionRepository(async_session)

        position = Position(
            user_id=1,
            stock_id=1,
            quantity=Decimal("0"),
            average_cost=Decimal("100.00"),
            current_price=Decimal("100.00"),
            total_cost=Decimal("0"),
            current_value=Decimal("0"),
            status=PositionStatus.CLOSED,
            closed_at=datetime.utcnow(),
        )
        async_session.add(position)
        await async_session.commit()

        count = await repo.count_by_user_and_status(1, PositionStatus.CLOSED)
        assert count == 1

    @pytest.mark.asyncio
    async def test_count_by_user_and_status_zero(self, async_session: AsyncSession):
        """count_by_user_and_status returns 0 when no matching positions."""
        repo = PositionRepository(async_session)

        count = await repo.count_by_user_and_status(1, PositionStatus.OPEN)
        assert count == 0

    @pytest.mark.asyncio
    async def test_update_position_marks_closed_when_quantity_zero(
        self, async_session: AsyncSession
    ):
        """update_position marks position as CLOSED when quantity becomes 0."""
        service = PortfolioService(async_session)

        stock = Stock(
            id=1,
            symbol="AAPL",
            name="Apple",
            exchange="NASDAQ",
            is_active=True,
        )
        position = Position(
            user_id=1,
            stock_id=1,
            quantity=Decimal("10"),
            average_cost=Decimal("100.00"),
            current_price=Decimal("100.00"),
            total_cost=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            status=PositionStatus.OPEN,
        )

        async_session.add(stock)
        async_session.add(position)
        await async_session.commit()

        updated = await service.update_position(
            user_id=1, position_id=position.id, quantity=Decimal("0")
        )

        assert updated.status == PositionStatus.CLOSED.value
        assert updated.quantity == Decimal("0")
        assert updated.closed_at is not None

    @pytest.mark.asyncio
    async def test_get_portfolio_overview_counts_closed_positions(
        self, async_session: AsyncSession
    ):
        """get_portfolio_overview correctly counts closed positions."""
        service = PortfolioService(async_session)

        stock = Stock(
            id=1,
            symbol="AAPL",
            name="Apple",
            exchange="NASDAQ",
            is_active=True,
        )
        open_position = Position(
            user_id=1,
            stock_id=1,
            quantity=Decimal("10"),
            average_cost=Decimal("100.00"),
            current_price=Decimal("100.00"),
            total_cost=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            status=PositionStatus.OPEN,
        )
        closed_position = Position(
            user_id=1,
            stock_id=1,
            quantity=Decimal("0"),
            average_cost=Decimal("100.00"),
            current_price=Decimal("100.00"),
            total_cost=Decimal("0"),
            current_value=Decimal("0"),
            status=PositionStatus.CLOSED,
            closed_at=datetime.utcnow(),
        )

        async_session.add(stock)
        async_session.add(open_position)
        async_session.add(closed_position)
        await async_session.commit()

        overview = await service.get_portfolio_overview(user_id=1)

        assert overview.open_positions_count == 1
        assert overview.closed_positions_count == 1


class TestTokenRefreshValidation:
    """SEC-002: Tests for token refresh user existence and status check."""

    @pytest.mark.asyncio
    async def test_user_service_get_user_returns_active_user(
        self, async_session: AsyncSession
    ):
        """UserService.get_user returns user response when user is active."""
        service = UserService(async_session)

        user = User(
            id=1,
            username="activeuser",
            email="active@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        async_session.add(user)
        await async_session.commit()

        result = await service.get_user(1)
        assert result is not None
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_user_service_get_user_returns_inactive_user(
        self, async_session: AsyncSession
    ):
        """UserService.get_user returns user response for inactive user."""
        service = UserService(async_session)

        user = User(
            id=1,
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password="hashed",
            is_active=False,
        )
        async_session.add(user)
        await async_session.commit()

        result = await service.get_user(1)
        assert result is not None
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_user_service_get_nonexistent_user(self, async_session: AsyncSession):
        """UserService.get_user returns None for nonexistent user."""
        service = UserService(async_session)

        result = await service.get_user(999)
        assert result is None
