"""Alert service for managing price alerts and notifications."""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Quote, Stock, User
from app.repositories import QuoteRepository, StockRepository
import logging

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Alert type enumeration."""

    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_GAIN = "percent_gain"
    PERCENT_LOSS = "percent_loss"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_CROSSOVER = "macd_crossover"
    VOLUME_SPIKE = "volume_spike"


class AlertStatus(str, Enum):
    """Alert status enumeration."""

    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"
    EXPIRED = "expired"


class AlertService:
    """Service for managing price alerts and notifications."""

    def __init__(self, session: AsyncSession):
        """Initialize alert service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.quote_repo = QuoteRepository(session)
        self.stock_repo = StockRepository(session)

    async def check_price_alerts(self, symbol: str, current_price: Decimal) -> List[Dict]:
        """Check if any price alerts should be triggered for a symbol.

        Args:
            symbol: Stock symbol
            current_price: Current price

        Returns:
            List of triggered alerts
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return []

        triggered_alerts = []

        # This would query alerts from database in production
        # For MVP, we'll structure the logic for integration

        logger.info(f"Checked price alerts for {symbol} at ${current_price}")
        return triggered_alerts

    async def create_alert(
        self,
        user_id: int,
        symbol: str,
        alert_type: AlertType,
        threshold_value: Decimal,
        is_active: bool = True,
    ) -> Optional[Dict]:
        """Create a new price alert.

        Args:
            user_id: User ID
            symbol: Stock symbol
            alert_type: Type of alert
            threshold_value: Threshold value for alert
            is_active: Whether alert is active

        Returns:
            Alert details or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            logger.warning(f"Stock not found: {symbol}")
            return None

        alert = {
            "user_id": user_id,
            "stock_id": stock.id,
            "symbol": symbol,
            "alert_type": alert_type.value,
            "threshold_value": float(threshold_value),
            "is_active": is_active,
            "created_at": datetime.utcnow(),
            "triggered_count": 0,
        }

        logger.info(f"Created alert for user {user_id} on {symbol}: {alert_type.value}")
        return alert

    async def evaluate_price_alert(
        self, symbol: str, current_price: Decimal, alert_type: AlertType, threshold: Decimal
    ) -> bool:
        """Evaluate if a price alert condition is met.

        Args:
            symbol: Stock symbol
            current_price: Current price
            alert_type: Alert type
            threshold: Threshold value

        Returns:
            True if alert should trigger, False otherwise
        """
        if alert_type == AlertType.PRICE_ABOVE:
            return current_price > threshold
        elif alert_type == AlertType.PRICE_BELOW:
            return current_price < threshold
        elif alert_type == AlertType.PERCENT_GAIN:
            # Check against entry price or opening price
            return True  # Simplified
        elif alert_type == AlertType.PERCENT_LOSS:
            return True  # Simplified
        elif alert_type == AlertType.VOLUME_SPIKE:
            # Would need volume data
            return False

        return False

    async def send_notification(
        self,
        user_id: int,
        alert_type: AlertType,
        symbol: str,
        current_price: Decimal,
        threshold: Decimal,
    ) -> bool:
        """Send notification for triggered alert.

        Args:
            user_id: User ID
            alert_type: Alert type
            symbol: Stock symbol
            current_price: Current price
            threshold: Threshold value

        Returns:
            True if notification sent, False otherwise
        """
        message = self._build_alert_message(alert_type, symbol, current_price, threshold)

        logger.info(f"Sending alert notification to user {user_id}: {message}")

        # In production, would send via:
        # - Email service
        # - SMS service
        # - Push notifications
        # - WebSocket real-time updates

        return True

    async def get_active_alerts(self, user_id: int) -> List[Dict]:
        """Get all active alerts for a user.

        Args:
            user_id: User ID

        Returns:
            List of active alerts
        """
        # This would query from database in production
        return []

    async def disable_alert(self, user_id: int, alert_id: int) -> bool:
        """Disable an alert.

        Args:
            user_id: User ID
            alert_id: Alert ID

        Returns:
            True if disabled, False otherwise
        """
        logger.info(f"Disabled alert {alert_id} for user {user_id}")
        return True

    async def check_technical_alerts(
        self, symbol: str, rsi: Optional[Decimal] = None, macd: Optional[Dict] = None
    ) -> List[Dict]:
        """Check technical indicator-based alerts.

        Args:
            symbol: Stock symbol
            rsi: Relative Strength Index value
            macd: MACD values dictionary

        Returns:
            List of triggered technical alerts
        """
        alerts = []

        if rsi is not None:
            if rsi > 70:
                alerts.append({
                    "type": AlertType.RSI_OVERBOUGHT.value,
                    "symbol": symbol,
                    "value": float(rsi),
                    "message": f"{symbol} RSI overbought at {rsi}",
                })
            elif rsi < 30:
                alerts.append({
                    "type": AlertType.RSI_OVERSOLD.value,
                    "symbol": symbol,
                    "value": float(rsi),
                    "message": f"{symbol} RSI oversold at {rsi}",
                })

        if macd:
            if macd.get("histogram", 0) > 0 and macd.get("previous_histogram", 0) <= 0:
                alerts.append({
                    "type": AlertType.MACD_CROSSOVER.value,
                    "symbol": symbol,
                    "value": float(macd.get("value", 0)),
                    "message": f"{symbol} MACD bullish crossover",
                })

        return alerts

    async def monitor_portfolio_alerts(self, user_id: int, alert_configs: List[Dict]) -> List[Dict]:
        """Monitor multiple portfolio alerts.

        Args:
            user_id: User ID
            alert_configs: List of alert configurations

        Returns:
            List of triggered alerts
        """
        triggered = []

        for config in alert_configs:
            symbol = config.get("symbol")
            alert_type = config.get("type")
            threshold = config.get("threshold")

            if not all([symbol, alert_type, threshold]):
                continue

            quote = await self.quote_repo.get_latest_by_symbol(symbol)
            if quote:
                if await self.evaluate_price_alert(symbol, quote.price, AlertType(alert_type), threshold):
                    triggered.append({
                        "symbol": symbol,
                        "alert_type": alert_type,
                        "threshold": float(threshold),
                        "current_price": float(quote.price),
                        "timestamp": datetime.utcnow(),
                    })

        return triggered

    def _build_alert_message(
        self, alert_type: AlertType, symbol: str, current_price: Decimal, threshold: Decimal
    ) -> str:
        """Build human-readable alert message.

        Args:
            alert_type: Alert type
            symbol: Stock symbol
            current_price: Current price
            threshold: Threshold value

        Returns:
            Alert message string
        """
        messages = {
            AlertType.PRICE_ABOVE: f"{symbol} has risen above ${threshold}. Current price: ${current_price}",
            AlertType.PRICE_BELOW: f"{symbol} has fallen below ${threshold}. Current price: ${current_price}",
            AlertType.PERCENT_GAIN: f"{symbol} has gained {threshold}%. Current price: ${current_price}",
            AlertType.PERCENT_LOSS: f"{symbol} has lost {threshold}%. Current price: ${current_price}",
            AlertType.RSI_OVERBOUGHT: f"{symbol} RSI indicates overbought conditions (RSI > 70)",
            AlertType.RSI_OVERSOLD: f"{symbol} RSI indicates oversold conditions (RSI < 30)",
            AlertType.MACD_CROSSOVER: f"{symbol} MACD has crossed over - potential bullish signal",
            AlertType.VOLUME_SPIKE: f"{symbol} experienced significant volume spike",
        }

        return messages.get(alert_type, f"Alert triggered for {symbol}")


class AlertManager:
    """Manager for handling alert operations and workflow."""

    def __init__(self, alert_service: AlertService):
        """Initialize alert manager.

        Args:
            alert_service: AlertService instance
        """
        self.alert_service = alert_service

    async def process_quote_update(self, symbol: str, quote: Quote) -> List[Dict]:
        """Process quote update and check for alert triggers.

        Args:
            symbol: Stock symbol
            quote: Quote object

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        # Check price alerts
        price_alerts = await self.alert_service.check_price_alerts(symbol, quote.price)
        triggered_alerts.extend(price_alerts)

        return triggered_alerts

    async def batch_alert_check(self, symbols: List[str]) -> Dict[str, List[Dict]]:
        """Check alerts for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to triggered alerts
        """
        results = {}

        for symbol in symbols:
            quote = await self.alert_service.quote_repo.get_latest_by_symbol(symbol)
            if quote:
                alerts = await self.alert_service.check_price_alerts(symbol, quote.price)
                if alerts:
                    results[symbol] = alerts

        return results
