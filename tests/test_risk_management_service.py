"""Unit tests for RiskManagementService."""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.risk_management_service import RiskManagementService
from app.models import Position, Stock, PositionStatus


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def risk_service(mock_session):
    """Create RiskManagementService instance."""
    return RiskManagementService(mock_session)


class TestPortfolioBeta:
    """Tests for portfolio beta calculation."""

    @pytest.mark.asyncio
    async def test_calculate_portfolio_beta_empty_portfolio(self, risk_service, mock_session):
        """Test beta calculation with empty portfolio."""
        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[])

        beta = await risk_service.calculate_portfolio_beta(user_id=1)

        assert beta == Decimal("0")

    @pytest.mark.asyncio
    async def test_calculate_portfolio_beta_single_position(self, risk_service, mock_session):
        """Test beta calculation with single position."""
        stock = MagicMock(spec=Stock)
        stock.symbol = "AAPL"

        position = MagicMock(spec=Position)
        position.stock = stock
        position.current_value = Decimal("10000")

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        beta = await risk_service.calculate_portfolio_beta(user_id=1)

        assert beta == Decimal("1.0")  # Default beta for stocks


class TestSharpeRatio:
    """Tests for Sharpe ratio calculation."""

    @pytest.mark.asyncio
    async def test_calculate_sharpe_ratio_empty_portfolio(self, risk_service):
        """Test Sharpe ratio with empty portfolio."""
        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[])

        sharpe = await risk_service.calculate_sharpe_ratio(user_id=1)

        assert sharpe == Decimal("0")

    @pytest.mark.asyncio
    async def test_calculate_sharpe_ratio_positive_return(self, risk_service):
        """Test Sharpe ratio with positive returns."""
        stock = MagicMock(spec=Stock)
        position = MagicMock(spec=Position)
        position.stock = stock
        position.total_cost = Decimal("10000")
        position.current_value = Decimal("12000")  # 20% gain

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])
        risk_service.calculate_portfolio_variance = AsyncMock(return_value=Decimal("0.04"))

        sharpe = await risk_service.calculate_sharpe_ratio(user_id=1)

        # Should be positive (return > risk-free rate)
        assert sharpe > Decimal("0")


class TestMaxDrawdown:
    """Tests for maximum drawdown calculation."""

    @pytest.mark.asyncio
    async def test_calculate_max_drawdown_no_loss(self, risk_service):
        """Test max drawdown when no losses."""
        stock = MagicMock(spec=Stock)
        position = MagicMock(spec=Position)
        position.stock = stock
        position.current_value = Decimal("12000")
        position.total_cost = Decimal("10000")  # 20% gain

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        drawdown = await risk_service.calculate_max_drawdown(user_id=1)

        assert drawdown == Decimal("0")

    @pytest.mark.asyncio
    async def test_calculate_max_drawdown_with_loss(self, risk_service):
        """Test max drawdown when position has loss."""
        stock = MagicMock(spec=Stock)
        position = MagicMock(spec=Position)
        position.stock = stock
        position.current_value = Decimal("8000")
        position.total_cost = Decimal("10000")  # 20% loss

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        drawdown = await risk_service.calculate_max_drawdown(user_id=1)

        assert drawdown < Decimal("0")  # Negative drawdown


class TestConcentrationRisk:
    """Tests for concentration risk analysis."""

    @pytest.mark.asyncio
    async def test_concentration_risk_empty_portfolio(self, risk_service):
        """Test concentration analysis with empty portfolio."""
        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[])

        concentration = await risk_service.calculate_concentration_risk(user_id=1)

        assert concentration["total_positions"] == 0
        assert concentration["largest_position_pct"] == Decimal("0")

    @pytest.mark.asyncio
    async def test_concentration_risk_single_position(self, risk_service):
        """Test concentration with single position (100% concentrated)."""
        stock = MagicMock(spec=Stock)
        stock.sector = "Technology"

        position = MagicMock(spec=Position)
        position.stock = stock
        position.current_value = Decimal("10000")

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        concentration = await risk_service.calculate_concentration_risk(user_id=1)

        assert concentration["total_positions"] == 1
        assert concentration["largest_position_pct"] == 100.0  # 100% in single position

    @pytest.mark.asyncio
    async def test_concentration_risk_diversified(self, risk_service):
        """Test concentration with diversified portfolio."""
        stocks = [MagicMock(spec=Stock) for _ in range(5)]
        for i, stock in enumerate(stocks):
            stock.sector = f"Sector{i}"

        positions = []
        for stock in stocks:
            position = MagicMock(spec=Position)
            position.stock = stock
            position.current_value = Decimal("10000")  # Equal weight
            positions.append(position)

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=positions)

        concentration = await risk_service.calculate_concentration_risk(user_id=1)

        assert concentration["total_positions"] == 5
        assert concentration["largest_position_pct"] == 20.0  # 20% each


class TestValueAtRisk:
    """Tests for Value at Risk calculation."""

    @pytest.mark.asyncio
    async def test_calculate_var_empty_portfolio(self, risk_service):
        """Test VaR calculation with empty portfolio."""
        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[])

        var = await risk_service.calculate_value_at_risk(user_id=1)

        assert var["var_absolute"] == Decimal("0")
        assert var["var_percent"] == Decimal("0")

    @pytest.mark.asyncio
    async def test_calculate_var_with_positions(self, risk_service):
        """Test VaR calculation with positions."""
        stock = MagicMock(spec=Stock)
        position = MagicMock(spec=Position)
        position.stock = stock
        position.current_value = Decimal("100000")

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])
        risk_service.calculate_portfolio_variance = AsyncMock(return_value=Decimal("0.04"))

        var = await risk_service.calculate_value_at_risk(
            user_id=1, confidence_level=0.95
        )

        assert var["var_absolute"] > 0
        assert var["confidence_level"] == 0.95


class TestPositionSizing:
    """Tests for position sizing calculations."""

    @pytest.mark.asyncio
    async def test_position_sizing_valid(self, risk_service):
        """Test position sizing with valid parameters."""
        result = await risk_service.calculate_position_sizing(
            account_size=Decimal("50000"),
            risk_percent=Decimal("2"),  # Risk 2% on trade
            entry_price=Decimal("100"),
            stop_price=Decimal("95"),  # 5 point stop
        )

        assert result["recommended_shares"] > 0
        assert result["position_size_dollars"] > 0
        assert result["max_loss"] > 0

    @pytest.mark.asyncio
    async def test_position_sizing_risk_equals_stop(self, risk_service):
        """Test position sizing when entry equals stop."""
        result = await risk_service.calculate_position_sizing(
            account_size=Decimal("50000"),
            risk_percent=Decimal("2"),
            entry_price=Decimal("100"),
            stop_price=Decimal("100"),  # Same as entry
        )

        # Should return zero shares when no valid risk
        assert result["recommended_shares"] == 0

    @pytest.mark.asyncio
    async def test_position_sizing_invalid_account(self, risk_service):
        """Test position sizing with invalid account size."""
        result = await risk_service.calculate_position_sizing(
            account_size=Decimal("0"),  # Invalid
            risk_percent=Decimal("2"),
            entry_price=Decimal("100"),
            stop_price=Decimal("95"),
        )

        assert result["recommended_shares"] == 0


class TestTaxLossHarvesting:
    """Tests for tax loss harvesting opportunities."""

    @pytest.mark.asyncio
    async def test_no_tax_loss_opportunities(self, risk_service):
        """Test when no positions have losses."""
        stock = MagicMock(spec=Stock)
        stock.symbol = "AAPL"

        position = MagicMock(spec=Position)
        position.stock = stock
        position.unrealized_gain_loss = Decimal("5000")  # Positive gain
        position.unrealized_gain_loss_percent = Decimal("50")

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        opportunities = await risk_service.estimate_tax_loss_harvesting_opportunities(
            user_id=1
        )

        assert len(opportunities) == 0

    @pytest.mark.asyncio
    async def test_identify_tax_losses(self, risk_service):
        """Test identifying positions with losses."""
        stock = MagicMock(spec=Stock)
        stock.symbol = "AAPL"

        position = MagicMock(spec=Position)
        position.stock = stock
        position.unrealized_gain_loss = Decimal("-2000")  # Loss
        position.unrealized_gain_loss_percent = Decimal("-20")
        position.opened_at = datetime.utcnow()

        risk_service.position_repo.get_user_positions = AsyncMock(return_value=[position])

        opportunities = await risk_service.estimate_tax_loss_harvesting_opportunities(
            user_id=1
        )

        assert len(opportunities) == 1
        assert opportunities[0]["symbol"] == "AAPL"
        assert opportunities[0]["unrealized_loss"] < 0
