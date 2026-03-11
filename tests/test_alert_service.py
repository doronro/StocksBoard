"""Unit tests for AlertService."""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.services.alert_service import AlertService, AlertType


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def alert_service(mock_session):
    """Create AlertService instance."""
    return AlertService(mock_session)


class TestAlertCreation:
    """Tests for alert creation."""

    @pytest.mark.asyncio
    async def test_create_alert_valid(self, alert_service):
        """Test creating a valid alert."""
        mock_stock = MagicMock()
        mock_stock.id = 1
        mock_stock.symbol = "AAPL"

        alert_service.stock_repo.get_by_symbol = AsyncMock(return_value=mock_stock)

        result = await alert_service.create_alert(
            user_id=1,
            symbol="AAPL",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("150"),
        )

        assert result is not None
        assert result["symbol"] == "AAPL"
        assert result["alert_type"] == AlertType.PRICE_ABOVE.value
        assert result["threshold_value"] == 150.0

    @pytest.mark.asyncio
    async def test_create_alert_stock_not_found(self, alert_service):
        """Test creating alert for non-existent stock."""
        alert_service.stock_repo.get_by_symbol = AsyncMock(return_value=None)

        result = await alert_service.create_alert(
            user_id=1,
            symbol="INVALID",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("150"),
        )

        assert result is None


class TestAlertEvaluation:
    """Tests for alert condition evaluation."""

    @pytest.mark.asyncio
    async def test_evaluate_price_above_alert_triggered(self, alert_service):
        """Test price above alert when condition is met."""
        triggered = await alert_service.evaluate_price_alert(
            symbol="AAPL",
            current_price=Decimal("155"),
            alert_type=AlertType.PRICE_ABOVE,
            threshold=Decimal("150"),
        )

        assert triggered is True

    @pytest.mark.asyncio
    async def test_evaluate_price_above_alert_not_triggered(self, alert_service):
        """Test price above alert when condition not met."""
        triggered = await alert_service.evaluate_price_alert(
            symbol="AAPL",
            current_price=Decimal("145"),
            alert_type=AlertType.PRICE_ABOVE,
            threshold=Decimal("150"),
        )

        assert triggered is False

    @pytest.mark.asyncio
    async def test_evaluate_price_below_alert_triggered(self, alert_service):
        """Test price below alert when condition is met."""
        triggered = await alert_service.evaluate_price_alert(
            symbol="AAPL",
            current_price=Decimal("145"),
            alert_type=AlertType.PRICE_BELOW,
            threshold=Decimal("150"),
        )

        assert triggered is True

    @pytest.mark.asyncio
    async def test_evaluate_price_below_alert_not_triggered(self, alert_service):
        """Test price below alert when condition not met."""
        triggered = await alert_service.evaluate_price_alert(
            symbol="AAPL",
            current_price=Decimal("155"),
            alert_type=AlertType.PRICE_BELOW,
            threshold=Decimal("150"),
        )

        assert triggered is False


class TestTechnicalAlerts:
    """Tests for technical indicator alerts."""

    @pytest.mark.asyncio
    async def test_rsi_overbought_alert(self, alert_service):
        """Test RSI overbought alert (RSI > 70)."""
        alerts = await alert_service.check_technical_alerts(
            symbol="AAPL",
            rsi=Decimal("75"),  # Overbought
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == AlertType.RSI_OVERBOUGHT.value

    @pytest.mark.asyncio
    async def test_rsi_oversold_alert(self, alert_service):
        """Test RSI oversold alert (RSI < 30)."""
        alerts = await alert_service.check_technical_alerts(
            symbol="AAPL",
            rsi=Decimal("25"),  # Oversold
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == AlertType.RSI_OVERSOLD.value

    @pytest.mark.asyncio
    async def test_no_rsi_alert_neutral(self, alert_service):
        """Test no alert when RSI in neutral zone."""
        alerts = await alert_service.check_technical_alerts(
            symbol="AAPL",
            rsi=Decimal("50"),  # Neutral
        )

        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_macd_bullish_crossover(self, alert_service):
        """Test MACD bullish crossover alert."""
        macd_data = {
            "value": Decimal("0.5"),
            "histogram": Decimal("0.1"),  # Positive
            "previous_histogram": Decimal("-0.1"),  # Was negative
        }

        alerts = await alert_service.check_technical_alerts(
            symbol="AAPL",
            macd=macd_data,
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == AlertType.MACD_CROSSOVER.value


class TestNotifications:
    """Tests for alert notifications."""

    @pytest.mark.asyncio
    async def test_send_notification_price_above(self, alert_service):
        """Test notification message for price above alert."""
        result = await alert_service.send_notification(
            user_id=1,
            alert_type=AlertType.PRICE_ABOVE,
            symbol="AAPL",
            current_price=Decimal("155"),
            threshold=Decimal("150"),
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_notification_price_below(self, alert_service):
        """Test notification message for price below alert."""
        result = await alert_service.send_notification(
            user_id=1,
            alert_type=AlertType.PRICE_BELOW,
            symbol="AAPL",
            current_price=Decimal("145"),
            threshold=Decimal("150"),
        )

        assert result is True


class TestAlertMessages:
    """Tests for alert message generation."""

    def test_build_price_above_message(self, alert_service):
        """Test message for price above alert."""
        message = alert_service._build_alert_message(
            alert_type=AlertType.PRICE_ABOVE,
            symbol="AAPL",
            current_price=Decimal("155"),
            threshold=Decimal("150"),
        )

        assert "AAPL" in message
        assert "155" in message or "150" in message

    def test_build_price_below_message(self, alert_service):
        """Test message for price below alert."""
        message = alert_service._build_alert_message(
            alert_type=AlertType.PRICE_BELOW,
            symbol="AAPL",
            current_price=Decimal("145"),
            threshold=Decimal("150"),
        )

        assert "AAPL" in message
        assert "fallen" in message.lower() or "below" in message.lower()

    def test_build_rsi_overbought_message(self, alert_service):
        """Test message for RSI overbought alert."""
        message = alert_service._build_alert_message(
            alert_type=AlertType.RSI_OVERBOUGHT,
            symbol="AAPL",
            current_price=Decimal("150"),
            threshold=Decimal("70"),
        )

        assert "AAPL" in message
        assert "overbought" in message.lower()

    def test_build_rsi_oversold_message(self, alert_service):
        """Test message for RSI oversold alert."""
        message = alert_service._build_alert_message(
            alert_type=AlertType.RSI_OVERSOLD,
            symbol="AAPL",
            current_price=Decimal("150"),
            threshold=Decimal("30"),
        )

        assert "AAPL" in message
        assert "oversold" in message.lower()


class TestAlertDisabling:
    """Tests for disabling alerts."""

    @pytest.mark.asyncio
    async def test_disable_alert_success(self, alert_service):
        """Test successfully disabling an alert."""
        result = await alert_service.disable_alert(user_id=1, alert_id=123)

        assert result is True
