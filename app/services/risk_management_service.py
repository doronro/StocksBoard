"""Risk management service for portfolio analysis and risk calculations."""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import statistics
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories import PositionRepository, QuoteRepository, StockRepository
from app.models import Position, Quote, Order, OrderStatus, PositionStatus
import logging

logger = logging.getLogger(__name__)


class RiskManagementService:
    """Service for managing portfolio risk metrics and calculations."""

    def __init__(self, session: AsyncSession):
        """Initialize risk management service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.position_repo = PositionRepository(session)
        self.quote_repo = QuoteRepository(session)
        self.stock_repo = StockRepository(session)

    async def calculate_portfolio_beta(self, user_id: int) -> Decimal:
        """Calculate portfolio beta relative to S&P 500.

        Beta measures systematic risk - how much the portfolio moves
        relative to market movements.

        Args:
            user_id: User ID

        Returns:
            Portfolio beta value
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return Decimal("0")

        total_value = Decimal("0")
        weighted_beta = Decimal("0")

        for position in positions:
            position_value = position.current_value
            total_value += position_value

        if total_value == 0:
            return Decimal("0")

        # For MVP, use simplified beta calculation
        # In production, would fetch from market data provider
        for position in positions:
            position_weight = position.current_value / total_value if total_value else Decimal("0")
            # Default beta of 1.0 for stocks, can be enhanced with real data
            stock_beta = Decimal("1.0")
            weighted_beta += position_weight * stock_beta

        return weighted_beta

    async def calculate_portfolio_variance(self, user_id: int, days: int = 30) -> Decimal:
        """Calculate portfolio variance based on historical returns.

        Args:
            user_id: User ID
            days: Number of historical days to analyze

        Returns:
            Portfolio variance
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return Decimal("0")

        # Collect daily returns
        daily_returns = []
        start_date = datetime.utcnow() - timedelta(days=days)

        # In production, would calculate from OHLC historical data
        # For MVP, use simplified calculation
        if positions:
            # Get latest position values over time
            for position in positions:
                # Calculate return for this position
                if position.total_cost > 0:
                    return_pct = (position.current_value - position.total_cost) / position.total_cost
                    daily_returns.append(float(return_pct))

        if len(daily_returns) < 2:
            return Decimal("0")

        variance = Decimal(str(statistics.variance(daily_returns)))
        return variance

    async def calculate_sharpe_ratio(
        self, user_id: int, risk_free_rate: Decimal = Decimal("0.045")
    ) -> Decimal:
        """Calculate portfolio Sharpe ratio.

        Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Standard Deviation
        Measures risk-adjusted returns.

        Args:
            user_id: User ID
            risk_free_rate: Annual risk-free rate (default 4.5% for US Treasury)

        Returns:
            Sharpe ratio value
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return Decimal("0")

        total_cost = sum(p.total_cost for p in positions)
        total_value = sum(p.current_value for p in positions)

        if total_cost == 0:
            return Decimal("0")

        # Portfolio return
        portfolio_return = (total_value - total_cost) / total_cost

        # Portfolio variance
        variance = await self.calculate_portfolio_variance(user_id)
        std_dev = Decimal(str(variance ** 0.5)) if variance > 0 else Decimal("0")

        if std_dev == 0:
            return Decimal("0")

        sharpe_ratio = (portfolio_return - risk_free_rate) / std_dev
        return sharpe_ratio

    async def calculate_max_drawdown(self, user_id: int, days: int = 90) -> Decimal:
        """Calculate maximum drawdown over specified period.

        Maximum drawdown is the largest peak-to-trough decline.

        Args:
            user_id: User ID
            days: Number of historical days to analyze

        Returns:
            Maximum drawdown as decimal (e.g., -0.25 for 25% drawdown)
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return Decimal("0")

        # Get total portfolio value at various points
        # In production, would use historical data from database
        peak_value = Decimal("0")
        min_value = Decimal("0")
        current_value = sum(p.current_value for p in positions)

        if current_value <= 0:
            return Decimal("0")

        peak_value = current_value
        max_drawdown = Decimal("0")

        # Simplified calculation - would use historical daily values
        for position in positions:
            if position.total_cost > 0:
                if position.current_value < position.total_cost:
                    drawdown = (position.current_value - position.total_cost) / position.total_cost
                    if drawdown < max_drawdown:
                        max_drawdown = drawdown

        return max_drawdown

    async def calculate_concentration_risk(self, user_id: int) -> Dict[str, any]:
        """Calculate portfolio concentration risk.

        Measures how concentrated the portfolio is in single holdings,
        sectors, etc.

        Args:
            user_id: User ID

        Returns:
            Dictionary with concentration metrics
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return {
                "total_positions": 0,
                "largest_position_pct": Decimal("0"),
                "herfindahl_index": Decimal("0"),  # 0 = diversified, 1 = concentrated
                "sector_concentration": {},
            }

        total_value = sum(p.current_value for p in positions)
        if total_value == 0:
            return {
                "total_positions": 0,
                "largest_position_pct": Decimal("0"),
                "herfindahl_index": Decimal("0"),
                "sector_concentration": {},
            }

        # Calculate position weights
        position_weights = []
        sector_values = {}

        for position in positions:
            weight = position.current_value / total_value if total_value else Decimal("0")
            position_weights.append(weight)

            # Aggregate by sector
            sector = position.stock.sector or "Unknown"
            if sector not in sector_values:
                sector_values[sector] = Decimal("0")
            sector_values[sector] += position.current_value

        # Find largest position
        largest_position_pct = max(position_weights) if position_weights else Decimal("0")

        # Calculate Herfindahl index (sum of squared weights)
        herfindahl = sum(w * w for w in position_weights)

        # Sector concentration
        sector_concentration = {
            sector: (value / total_value * 100) if total_value else Decimal("0")
            for sector, value in sector_values.items()
        }

        return {
            "total_positions": len(positions),
            "largest_position_pct": float(largest_position_pct * 100),
            "herfindahl_index": float(herfindahl),  # 1/n for equal weight, 1 for single stock
            "sector_concentration": sector_concentration,
        }

    async def calculate_value_at_risk(
        self, user_id: int, confidence_level: float = 0.95, holding_period_days: int = 1
    ) -> Dict[str, any]:
        """Calculate Value at Risk (VaR) for portfolio.

        VaR estimates the maximum loss at a given confidence level
        over a specific holding period.

        Args:
            user_id: User ID
            confidence_level: Confidence level (0.95 = 95%, 0.99 = 99%)
            holding_period_days: Holding period in days

        Returns:
            Dictionary with VaR estimates
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return {
                "var_absolute": Decimal("0"),
                "var_percent": Decimal("0"),
                "confidence_level": confidence_level,
                "holding_period_days": holding_period_days,
            }

        portfolio_value = sum(p.current_value for p in positions)
        if portfolio_value == 0:
            return {
                "var_absolute": Decimal("0"),
                "var_percent": Decimal("0"),
                "confidence_level": confidence_level,
                "holding_period_days": holding_period_days,
            }

        # Simplified VaR calculation using historical volatility
        # In production, would use more sophisticated methods
        variance = await self.calculate_portfolio_variance(user_id)
        std_dev = Decimal(str(variance ** 0.5)) if variance > 0 else Decimal("0.2")

        # Z-score for confidence level
        z_scores = {
            0.90: Decimal("1.28"),
            0.95: Decimal("1.645"),
            0.99: Decimal("2.326"),
        }
        z_score = z_scores.get(confidence_level, Decimal("1.645"))

        # Daily VaR
        daily_var = portfolio_value * std_dev * z_score

        # Adjust for holding period
        var_absolute = daily_var * Decimal(str(holding_period_days ** 0.5))
        var_percent = (var_absolute / portfolio_value * 100) if portfolio_value else Decimal("0")

        return {
            "var_absolute": float(var_absolute),
            "var_percent": float(var_percent),
            "confidence_level": confidence_level,
            "holding_period_days": holding_period_days,
        }

    async def calculate_position_sizing(
        self,
        account_size: Decimal,
        risk_percent: Decimal,
        entry_price: Decimal,
        stop_price: Decimal,
    ) -> Dict[str, any]:
        """Calculate position size based on risk parameters.

        Args:
            account_size: Total account size
            risk_percent: Percentage of account willing to risk (e.g., 2 for 2%)
            entry_price: Entry price for position
            stop_price: Stop loss price

        Returns:
            Dictionary with position sizing recommendations
        """
        if entry_price <= 0 or stop_price < 0 or account_size <= 0 or risk_percent <= 0:
            return {
                "recommended_shares": 0,
                "position_size_dollars": Decimal("0"),
                "max_loss": Decimal("0"),
                "risk_reward_ratio": Decimal("0"),
            }

        # Risk amount
        risk_amount = account_size * (risk_percent / Decimal("100"))

        # Price risk per share
        price_risk = abs(entry_price - stop_price)

        if price_risk == 0:
            return {
                "recommended_shares": 0,
                "position_size_dollars": Decimal("0"),
                "max_loss": Decimal("0"),
                "risk_reward_ratio": Decimal("0"),
            }

        # Number of shares
        shares = int(risk_amount / price_risk)
        position_size = shares * entry_price
        max_loss = shares * price_risk

        return {
            "recommended_shares": shares,
            "position_size_dollars": float(position_size),
            "max_loss": float(max_loss),
            "risk_reward_ratio": float(entry_price / stop_price) if stop_price > 0 else 0,
        }

    async def analyze_order_margin_impact(
        self, user_id: int, order_price: Decimal, order_quantity: Decimal
    ) -> Dict[str, any]:
        """Analyze margin impact of a potential order.

        Args:
            user_id: User ID
            order_price: Order price
            order_quantity: Order quantity

        Returns:
            Dictionary with margin impact analysis
        """
        positions = await self.position_repo.get_user_positions(user_id)

        current_portfolio_value = sum(p.current_value for p in positions)
        order_value = order_price * order_quantity

        # Simple margin calculation (50% for longs, 30% for shorts)
        required_margin = order_value * Decimal("0.5")
        cash_requirement = order_value * Decimal("0.5")

        return {
            "current_portfolio_value": float(current_portfolio_value),
            "order_value": float(order_value),
            "required_margin": float(required_margin),
            "buying_power_impact": float(cash_requirement),
            "estimated_new_portfolio_value": float(current_portfolio_value + order_value),
        }

    async def detect_concentrated_positions(self, user_id: int, threshold_pct: float = 20.0) -> List[Dict]:
        """Detect positions that exceed concentration threshold.

        Args:
            user_id: User ID
            threshold_pct: Concentration threshold percentage (default 20%)

        Returns:
            List of concentrated positions
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return []

        total_value = sum(p.current_value for p in positions)
        if total_value == 0:
            return []

        concentrated = []
        for position in positions:
            position_pct = (position.current_value / total_value) * 100
            if position_pct > threshold_pct:
                concentrated.append({
                    "symbol": position.stock.symbol,
                    "position_value": float(position.current_value),
                    "portfolio_percent": float(position_pct),
                    "shares": float(position.quantity),
                    "current_price": float(position.current_price),
                })

        return concentrated

    async def estimate_tax_loss_harvesting_opportunities(self, user_id: int) -> List[Dict]:
        """Identify positions with unrealized losses for tax loss harvesting.

        Args:
            user_id: User ID

        Returns:
            List of positions with losses
        """
        positions = await self.position_repo.get_user_positions(user_id)
        if not positions:
            return []

        loss_opportunities = []
        for position in positions:
            if position.unrealized_gain_loss and position.unrealized_gain_loss < 0:
                loss_opportunities.append({
                    "symbol": position.stock.symbol,
                    "unrealized_loss": float(position.unrealized_gain_loss),
                    "loss_percent": float(position.unrealized_gain_loss_percent),
                    "tax_benefit": float(position.unrealized_gain_loss) * Decimal("0.21"),  # 21% federal rate
                    "opened_at": position.opened_at,
                })

        # Sort by loss amount (largest first)
        loss_opportunities.sort(key=lambda x: x["unrealized_loss"])
        return loss_opportunities
