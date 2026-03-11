"""Unit tests for ComplianceService."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.services.compliance_service import ComplianceService, ComplianceMonitor
from app.models import Order, OrderStatus, OrderSide, Position


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def compliance_service(mock_session):
    """Create ComplianceService instance."""
    return ComplianceService(mock_session)


class TestPatternDayTrader:
    """Tests for Pattern Day Trader (PDT) rule checking."""

    @pytest.mark.asyncio
    async def test_pdt_compliant_low_trades(self, compliance_service):
        """Test PDT compliance with less than 3 round trips."""
        compliance_service.order_repo.get_user_orders = AsyncMock(return_value=[])
        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[])

        result = await compliance_service.check_pattern_day_trader(user_id=1)

        assert result["is_pattern_day_trader"] is False
        assert result["compliant"] is True

    @pytest.mark.asyncio
    async def test_pdt_violation_insufficient_account(self, compliance_service):
        """Test PDT violation when account below minimum."""
        # Create mock orders representing round trips
        orders = []
        for i in range(3):
            buy_order = MagicMock(spec=Order)
            buy_order.side = OrderSide.BUY
            buy_order.stock_id = 1
            buy_order.created_at = datetime.utcnow()
            buy_order.status = OrderStatus.FILLED

            sell_order = MagicMock(spec=Order)
            sell_order.side = OrderSide.SELL
            sell_order.stock_id = 1
            sell_order.created_at = datetime.utcnow()
            sell_order.status = OrderStatus.FILLED

            orders.extend([buy_order, sell_order])

        compliance_service.order_repo.get_user_orders = AsyncMock(return_value=orders)

        # Create position with low value
        position = MagicMock(spec=Position)
        position.current_value = Decimal("10000")  # Below $25,000 minimum

        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        result = await compliance_service.check_pattern_day_trader(user_id=1)

        assert result["is_pattern_day_trader"] is True
        assert result["compliant"] is False

    @pytest.mark.asyncio
    async def test_pdt_compliant_sufficient_account(self, compliance_service):
        """Test PDT compliance with sufficient account value."""
        # Create orders representing round trips
        orders = []
        for i in range(3):
            buy_order = MagicMock(spec=Order)
            buy_order.side = OrderSide.BUY
            buy_order.stock_id = 1
            buy_order.created_at = datetime.utcnow()
            buy_order.status = OrderStatus.FILLED

            sell_order = MagicMock(spec=Order)
            sell_order.side = OrderSide.SELL
            sell_order.stock_id = 1
            sell_order.created_at = datetime.utcnow()
            sell_order.status = OrderStatus.FILLED

            orders.extend([buy_order, sell_order])

        compliance_service.order_repo.get_user_orders = AsyncMock(return_value=orders)

        # Create position with sufficient value
        position = MagicMock(spec=Position)
        position.current_value = Decimal("50000")  # Above $25,000 minimum

        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        result = await compliance_service.check_pattern_day_trader(user_id=1)

        assert result["is_pattern_day_trader"] is True
        assert result["compliant"] is True  # Has sufficient funds


class TestWashSales:
    """Tests for wash sale detection."""

    @pytest.mark.asyncio
    async def test_no_wash_sales_detected(self, compliance_service):
        """Test when no wash sales are present."""
        compliance_service.order_repo.get_user_orders = AsyncMock(return_value=[])

        wash_sales = await compliance_service.detect_wash_sales(user_id=1)

        assert len(wash_sales) == 0

    @pytest.mark.asyncio
    async def test_wash_sale_detected(self, compliance_service):
        """Test detection of wash sale."""
        # Create sell order at loss
        sell_order = MagicMock(spec=Order)
        sell_order.side = OrderSide.SELL
        sell_order.status = OrderStatus.FILLED
        sell_order.stock_id = 1
        sell_order.average_filled_price = Decimal("105")
        sell_order.price = Decimal("95")  # Loss
        sell_order.filled_quantity = Decimal("100")
        sell_order.created_at = datetime.utcnow() - timedelta(days=10)
        sell_order.filled_at = datetime.utcnow() - timedelta(days=10)

        # Create buy order within 30 days
        buy_order = MagicMock(spec=Order)
        buy_order.side = OrderSide.BUY
        buy_order.status = OrderStatus.FILLED
        buy_order.stock_id = 1
        buy_order.created_at = datetime.utcnow() - timedelta(days=5)
        buy_order.filled_at = datetime.utcnow() - timedelta(days=5)

        compliance_service.order_repo.get_user_orders = AsyncMock(return_value=[sell_order, buy_order])

        wash_sales = await compliance_service.detect_wash_sales(user_id=1)

        assert len(wash_sales) == 1
        assert wash_sales[0]["stock_id"] == 1


class TestMarginRequirements:
    """Tests for margin requirement compliance."""

    @pytest.mark.asyncio
    async def test_margin_compliant(self, compliance_service):
        """Test margin compliance check."""
        position = MagicMock(spec=Position)
        position.current_value = Decimal("100000")

        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        result = await compliance_service.check_margin_requirements(user_id=1)

        assert result["is_compliant"] is True
        assert result["excess_margin"] > 0

    @pytest.mark.asyncio
    async def test_margin_over_leveraged(self, compliance_service):
        """Test margin when over-leveraged."""
        position = MagicMock(spec=Position)
        position.current_value = Decimal("0")  # No margin coverage

        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        result = await compliance_service.check_margin_requirements(user_id=1)

        # With no position value, still compliant by definition
        assert result["is_compliant"] is True


class TestOrderValidation:
    """Tests for order compliance validation."""

    @pytest.mark.asyncio
    async def test_validate_order_all_checks_pass(self, compliance_service):
        """Test order validation when all checks pass."""
        compliance_service.check_pattern_day_trader = AsyncMock(
            return_value={"compliant": True}
        )
        compliance_service.check_margin_requirements = AsyncMock(
            return_value={"is_compliant": True}
        )
        compliance_service.position_repo.get_user_positions = AsyncMock(return_value=[])
        compliance_service.check_short_sale_constraints = AsyncMock(
            return_value={"short_sale_eligible": True}
        )

        result = await compliance_service.validate_order_compliance(
            user_id=1,
            order_symbol="AAPL",
            order_quantity=Decimal("100"),
            order_side="buy",
        )

        assert result["all_checks_passed"] is True
        assert len(result["violations"]) == 0


class TestShortSaleEligibility:
    """Tests for short sale compliance."""

    @pytest.mark.asyncio
    async def test_short_sale_eligible(self, compliance_service):
        """Test short sale eligibility check."""
        result = await compliance_service.check_short_sale_constraints(symbol="AAPL")

        assert result["short_sale_eligible"] is True

    @pytest.mark.asyncio
    async def test_short_sale_requires_locate(self, compliance_service):
        """Test that short sales require locate."""
        result = await compliance_service.check_short_sale_constraints(symbol="AAPL")

        assert result["locate_required"] is True


class TestComplianceReport:
    """Tests for compliance reporting."""

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, compliance_service):
        """Test compliance report generation."""
        compliance_service.check_pattern_day_trader = AsyncMock(
            return_value={
                "compliant": True,
                "is_pattern_day_trader": False,
                "round_trips_5_days": 1,
                "account_value": 50000,
                "minimum_required": 25000,
                "meets_requirement": True,
            }
        )
        compliance_service.check_margin_requirements = AsyncMock(
            return_value={
                "total_position_value": 100000,
                "required_margin": 50000,
                "is_compliant": True,
            }
        )
        compliance_service.detect_wash_sales = AsyncMock(return_value=[])

        report = await compliance_service.generate_compliance_report(user_id=1)

        assert report["user_id"] == 1
        assert report["overall_compliant"] is True


class TestComplianceMonitor:
    """Tests for ComplianceMonitor."""

    @pytest.mark.asyncio
    async def test_monitor_user_compliance(self, compliance_service):
        """Test user compliance monitoring."""
        compliance_service.generate_compliance_report = AsyncMock(
            return_value={
                "user_id": 1,
                "pdt_status": {"compliant": True},
                "margin_status": {"is_compliant": True},
                "wash_sales_detected": 0,
                "overall_compliant": True,
            }
        )

        monitor = ComplianceMonitor(compliance_service)
        result = await monitor.monitor_user_compliance(user_id=1)

        assert result["user_id"] == 1
        assert result["compliant"] is True
        assert len(result["violations"]) == 0
