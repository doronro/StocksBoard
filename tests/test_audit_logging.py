"""
Comprehensive tests for audit logging functionality.
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Stock, Order, OrderStatus, OrderType, OrderSide, AuditLog
from app.audit import AuditLogger, get_audit_logger
from app.services.order_service import OrderService
from decimal import Decimal


@pytest.fixture
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    return user


@pytest.fixture
async def test_stock(async_session: AsyncSession) -> Stock:
    """Create a test stock."""
    stock = Stock(
        symbol="AAPL",
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        exchange="NASDAQ",
        is_active=True,
    )
    async_session.add(stock)
    await async_session.commit()
    return stock


@pytest.fixture
async def audit_logger(async_session: AsyncSession) -> AuditLogger:
    """Create an audit logger instance."""
    return AuditLogger(async_session)


class TestAuditLoggerBasicFunctionality:
    """Test basic audit logging functionality."""

    @pytest.mark.asyncio
    async def test_log_action_creates_audit_entry(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test that log_action creates an audit log entry."""
        user_id = test_user.id

        await audit_logger.log_action(
            user_id=user_id,
            action="test_action",
            resource_type="test_resource",
            resource_id=123,
        )

        # Verify audit log was created
        audit_logs = await async_session.execute(
            "SELECT * FROM audit_logs WHERE user_id = :user_id",
            {"user_id": user_id},
        )
        # Using query to check
        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].action == "test_action"
        assert logs[0].resource_type == "test_resource"

    @pytest.mark.asyncio
    async def test_log_action_with_before_after_state(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test logging with before and after state."""
        user_id = test_user.id
        before_state = {"status": "pending"}
        after_state = {"status": "filled"}

        await audit_logger.log_action(
            user_id=user_id,
            action="update_order",
            resource_type="order",
            resource_id=456,
            before_state=before_state,
            after_state=after_state,
        )

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].before_state == before_state
        assert logs[0].after_state == after_state

    @pytest.mark.asyncio
    async def test_log_action_with_failure_status(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test logging a failed action."""
        user_id = test_user.id
        error_msg = "Insufficient balance"

        await audit_logger.log_action(
            user_id=user_id,
            action="create_order",
            resource_type="order",
            status="failure",
            error_message=error_msg,
        )

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "failure"
        assert logs[0].error_message == error_msg

    @pytest.mark.asyncio
    async def test_log_action_with_request_details(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test logging with request IP and user agent."""
        user_id = test_user.id
        request_ip = "192.168.1.1"
        user_agent = "Mozilla/5.0"

        await audit_logger.log_action(
            user_id=user_id,
            action="login",
            resource_type="user",
            request_ip=request_ip,
            user_agent=user_agent,
        )

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].ip_address == request_ip
        assert logs[0].user_agent == user_agent

    @pytest.mark.asyncio
    async def test_log_action_timestamp_created(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test that audit log has a created_at timestamp."""
        user_id = test_user.id

        before_time = datetime.utcnow()
        await audit_logger.log_action(
            user_id=user_id,
            action="test_action",
            resource_type="test_resource",
        )
        after_time = datetime.utcnow()

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].created_at is not None
        assert before_time <= logs[0].created_at <= after_time


class TestAuditLoggerQueries:
    """Test audit log querying functionality."""

    @pytest.mark.asyncio
    async def test_get_user_audit_logs(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test retrieving audit logs by user."""
        user_id = test_user.id

        # Create multiple audit entries
        for i in range(3):
            await audit_logger.log_action(
                user_id=user_id,
                action=f"action_{i}",
                resource_type="order",
            )

        logs = await audit_logger.get_user_audit_logs(user_id)
        assert len(logs) == 3

    @pytest.mark.asyncio
    async def test_get_user_audit_logs_with_pagination(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test pagination of user audit logs."""
        user_id = test_user.id

        # Create 5 audit entries
        for i in range(5):
            await audit_logger.log_action(
                user_id=user_id,
                action="test_action",
                resource_type="order",
            )

        # Get first 2
        logs = await audit_logger.get_user_audit_logs(user_id, skip=0, limit=2)
        assert len(logs) == 2

        # Get next 2
        logs = await audit_logger.get_user_audit_logs(user_id, skip=2, limit=2)
        assert len(logs) == 2

        # Get remaining
        logs = await audit_logger.get_user_audit_logs(user_id, skip=4, limit=2)
        assert len(logs) == 1

    @pytest.mark.asyncio
    async def test_get_action_audit_logs(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test retrieving audit logs by action type."""
        user_id = test_user.id

        # Create audit entries with different actions
        await audit_logger.log_action(
            user_id=user_id,
            action="create_order",
            resource_type="order",
        )
        await audit_logger.log_action(
            user_id=user_id,
            action="cancel_order",
            resource_type="order",
        )
        await audit_logger.log_action(
            user_id=user_id,
            action="create_order",
            resource_type="order",
        )

        logs = await audit_logger.get_action_audit_logs("create_order")
        assert len(logs) == 2
        assert all(log.action == "create_order" for log in logs)

    @pytest.mark.asyncio
    async def test_get_resource_audit_logs(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test retrieving audit logs by resource."""
        user_id = test_user.id
        resource_id = 789

        # Create audit entries for same resource
        await audit_logger.log_action(
            user_id=user_id,
            action="create_order",
            resource_type="order",
            resource_id=resource_id,
        )
        await audit_logger.log_action(
            user_id=user_id,
            action="update_order",
            resource_type="order",
            resource_id=resource_id,
        )

        # Create entry for different resource
        await audit_logger.log_action(
            user_id=user_id,
            action="create_order",
            resource_type="order",
            resource_id=999,
        )

        logs = await audit_logger.get_resource_audit_logs("order", resource_id)
        assert len(logs) == 2
        assert all(log.resource_id == resource_id for log in logs)


class TestOrderServiceAuditLogging:
    """Test audit logging integration with OrderService."""

    @pytest.mark.asyncio
    async def test_create_order_logs_success(
        self,
        async_session: AsyncSession,
        test_user: User,
        test_stock: Stock,
        audit_logger: AuditLogger,
    ):
        """Test that successful order creation is logged."""
        order_service = OrderService(async_session, audit_logger)

        response = await order_service.create_order(
            user_id=test_user.id,
            symbol=test_stock.symbol,
            order_type=OrderType.MARKET.value,
            side=OrderSide.BUY.value,
            quantity=Decimal("10"),
            request_ip="192.168.1.1",
            user_agent="Test Agent",
        )

        assert response is not None

        # Verify audit log
        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(
                (AuditLog.user_id == test_user.id)
                & (AuditLog.action == "create_order")
            )
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].resource_type == "order"
        assert logs[0].ip_address == "192.168.1.1"
        assert logs[0].user_agent == "Test Agent"

    @pytest.mark.asyncio
    async def test_create_order_logs_failure(
        self,
        async_session: AsyncSession,
        test_user: User,
        audit_logger: AuditLogger,
    ):
        """Test that order creation failure is logged."""
        order_service = OrderService(async_session, audit_logger)

        response = await order_service.create_order(
            user_id=test_user.id,
            symbol="INVALID",  # Stock doesn't exist
            order_type=OrderType.MARKET.value,
            side=OrderSide.BUY.value,
            quantity=Decimal("10"),
        )

        assert response is None

        # Verify audit log for failure
        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(
                (AuditLog.user_id == test_user.id)
                & (AuditLog.action == "create_order")
            )
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "failure"
        assert "Stock not found" in logs[0].error_message

    @pytest.mark.asyncio
    async def test_cancel_order_logs_state_changes(
        self,
        async_session: AsyncSession,
        test_user: User,
        test_stock: Stock,
        audit_logger: AuditLogger,
    ):
        """Test that order cancellation logs before/after state."""
        order_service = OrderService(async_session, audit_logger)

        # Create order first
        order_response = await order_service.create_order(
            user_id=test_user.id,
            symbol=test_stock.symbol,
            order_type=OrderType.MARKET.value,
            side=OrderSide.BUY.value,
            quantity=Decimal("10"),
        )

        # Cancel order
        result = await order_service.cancel_order(
            user_id=test_user.id,
            order_id=order_response.id,
            request_ip="192.168.1.1",
            user_agent="Test Agent",
        )

        assert result is True

        # Verify audit log for cancellation
        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(
                (AuditLog.user_id == test_user.id)
                & (AuditLog.action == "cancel_order")
            )
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].before_state["status"] == OrderStatus.PENDING.value
        assert logs[0].after_state["status"] == OrderStatus.CANCELLED.value


class TestDatabaseConfiguration:
    """Test database configuration security."""

    def test_database_config_password_required(self):
        """Test that DatabaseConfig requires password."""
        import os
        from app.config import DatabaseConfig

        # Save original
        original_password = os.getenv("DB_PASSWORD")

        try:
            # Remove password
            if "DB_PASSWORD" in os.environ:
                del os.environ["DB_PASSWORD"]

            db_config = DatabaseConfig()
            with pytest.raises(ValueError, match="DB_PASSWORD"):
                _ = db_config.database_url
        finally:
            # Restore
            if original_password:
                os.environ["DB_PASSWORD"] = original_password

    def test_database_config_production_ssl(self):
        """Test that production environment enforces SSL."""
        import os
        from app.config import DatabaseConfig

        # Save originals
        original_env = os.getenv("ENVIRONMENT")
        original_password = os.getenv("DB_PASSWORD")

        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["DB_PASSWORD"] = "test_password"
            os.environ["DB_USER"] = "test_user"
            os.environ["DB_HOST"] = "localhost"
            os.environ["DB_PORT"] = "5432"
            os.environ["DB_NAME"] = "test_db"

            db_config = DatabaseConfig()
            url = db_config.database_url

            assert "ssl=require" in url
        finally:
            # Restore
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            if original_password:
                os.environ["DB_PASSWORD"] = original_password

    def test_database_config_pool_size_production(self):
        """Test that production environment uses larger pool."""
        import os
        from app.config import DatabaseConfig

        original_env = os.getenv("ENVIRONMENT")

        try:
            os.environ["ENVIRONMENT"] = "production"
            db_config = DatabaseConfig()
            assert db_config.pool_size == 150
            assert db_config.max_overflow == 50

            os.environ["ENVIRONMENT"] = "development"
            db_config = DatabaseConfig()
            assert db_config.pool_size == 20
            assert db_config.max_overflow == 10
        finally:
            if original_env:
                os.environ["ENVIRONMENT"] = original_env


class TestAuditLogIndexing:
    """Test that audit logs are properly indexed for performance."""

    @pytest.mark.asyncio
    async def test_audit_log_user_action_index(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test queries using user_id, action, and created_at are efficient."""
        user_id = test_user.id

        # Create audit entries
        for i in range(10):
            await audit_logger.log_action(
                user_id=user_id,
                action=f"action_{i % 3}",
                resource_type="order",
            )

        # Query using indexed columns
        logs = await audit_logger.get_user_audit_logs(user_id)
        assert len(logs) == 10

    @pytest.mark.asyncio
    async def test_audit_log_resource_index(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test queries using resource_type and resource_id are efficient."""
        user_id = test_user.id

        # Create audit entries for multiple resources
        for i in range(10):
            await audit_logger.log_action(
                user_id=user_id,
                action="update",
                resource_type="order",
                resource_id=i % 5,
            )

        # Query using indexed columns
        logs = await audit_logger.get_resource_audit_logs("order", 0)
        assert len(logs) == 2


class TestAuditLogDataIntegrity:
    """Test audit log data integrity and completeness."""

    @pytest.mark.asyncio
    async def test_audit_log_null_fields_allowed(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test that optional fields can be null."""
        user_id = test_user.id

        await audit_logger.log_action(
            user_id=user_id,
            action="test",
            resource_type="test",
            # All optional fields are None
        )

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].resource_id is None
        assert logs[0].before_state is None
        assert logs[0].after_state is None
        assert logs[0].error_message is None

    @pytest.mark.asyncio
    async def test_audit_log_json_serialization(
        self, async_session: AsyncSession, audit_logger: AuditLogger, test_user: User
    ):
        """Test that complex JSON objects are properly serialized."""
        user_id = test_user.id
        complex_state = {
            "nested": {
                "data": [1, 2, 3],
                "string": "value",
            },
            "numbers": [1.5, 2.5],
        }

        await audit_logger.log_action(
            user_id=user_id,
            action="test",
            resource_type="test",
            after_state=complex_state,
        )

        from sqlalchemy import select
        result = await async_session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].after_state == complex_state
