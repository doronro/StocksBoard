"""Compliance service for regulatory compliance and risk monitoring."""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import Order, OrderStatus, OrderSide, Position, User, AuditLog
from app.repositories import OrderRepository, PositionRepository, UserRepository
import logging

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for managing compliance checks and regulatory requirements."""

    # Pattern Day Trader (PDT) rule: 3 round trips in 5 trading days
    PDT_ROUND_TRIPS_THRESHOLD = 3
    PDT_LOOKBACK_DAYS = 5
    PDT_MINIMUM_ACCOUNT_VALUE = Decimal("25000")

    # Wash sale rule: buy back within 30 days
    WASH_SALE_LOOKBACK_DAYS = 30

    # Position limits (simplified for MVP)
    SINGLE_STOCK_MAX_PCT = Decimal("40")  # Max 40% in single stock
    SECTOR_MAX_PCT = Decimal("50")  # Max 50% in single sector

    def __init__(self, session: AsyncSession):
        """Initialize compliance service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.order_repo = OrderRepository(session)
        self.position_repo = PositionRepository(session)
        self.user_repo = UserRepository(session)

    async def check_pattern_day_trader(self, user_id: int) -> Dict[str, any]:
        """Check if user meets Pattern Day Trader (PDT) criteria.

        PDT Rule: 4+ day trades in 5 business days requires $25,000 minimum account value.

        Args:
            user_id: User ID

        Returns:
            Dictionary with PDT status and details
        """
        # Get orders from past 5 days
        lookback_date = datetime.utcnow() - timedelta(days=self.PDT_LOOKBACK_DAYS)
        orders = await self.order_repo.get_user_orders(user_id)

        # Count round trips (buy + sell same stock within period)
        round_trips = self._count_round_trips(orders, lookback_date)

        # Get account value
        positions = await self.position_repo.get_user_positions(user_id)
        account_value = sum(p.current_value for p in positions)

        is_pdt = round_trips >= self.PDT_ROUND_TRIPS_THRESHOLD
        meets_requirement = account_value >= self.PDT_MINIMUM_ACCOUNT_VALUE

        return {
            "is_pattern_day_trader": is_pdt,
            "round_trips_5_days": round_trips,
            "account_value": float(account_value),
            "minimum_required": float(self.PDT_MINIMUM_ACCOUNT_VALUE),
            "meets_requirement": meets_requirement,
            "compliant": not is_pdt or meets_requirement,
        }

    async def detect_wash_sales(self, user_id: int) -> List[Dict]:
        """Detect potential wash sales (buying back within 30 days of loss).

        Wash Sale Rule: Cannot claim loss if repurchased within 30 days before/after sale.

        Args:
            user_id: User ID

        Returns:
            List of potential wash sales
        """
        wash_sales = []

        # Get all completed orders
        orders = await self.order_repo.get_user_orders(user_id)
        lookback_date = datetime.utcnow() - timedelta(days=self.WASH_SALE_LOOKBACK_DAYS)

        # Filter sells with losses and recent buys
        sells = [o for o in orders if o.side == OrderSide.SELL and o.status == OrderStatus.FILLED]
        buys = [o for o in orders if o.side == OrderSide.BUY and o.status == OrderStatus.FILLED]

        for sell_order in sells:
            # Check if sold at loss
            if sell_order.average_filled_price and sell_order.price:
                if sell_order.average_filled_price > sell_order.price:
                    # Look for buy of same stock within 30 days
                    for buy_order in buys:
                        if (buy_order.stock_id == sell_order.stock_id and
                            buy_order.created_at >= sell_order.created_at - timedelta(days=30) and
                            buy_order.created_at <= sell_order.created_at + timedelta(days=30)):

                            wash_sales.append({
                                "sell_order_id": sell_order.id,
                                "buy_order_id": buy_order.id,
                                "stock_id": sell_order.stock_id,
                                "loss_amount": float(
                                    (sell_order.price - sell_order.average_filled_price) * sell_order.filled_quantity
                                ),
                                "sell_date": sell_order.filled_at,
                                "buy_date": buy_order.filled_at,
                                "days_between": (buy_order.filled_at - sell_order.filled_at).days,
                            })

        return wash_sales

    async def check_margin_requirements(self, user_id: int) -> Dict[str, any]:
        """Check if user meets margin requirements.

        Args:
            user_id: User ID

        Returns:
            Dictionary with margin status
        """
        positions = await self.position_repo.get_user_positions(user_id)

        total_value = sum(p.current_value for p in positions)
        total_cost = sum(p.total_cost for p in positions)

        # Simplified margin calculation
        # Regulation T: 50% margin requirement for stocks
        required_margin = total_value * Decimal("0.5")
        excess_margin = Decimal(str(total_value)) - required_margin

        return {
            "total_position_value": float(total_value),
            "required_margin": float(required_margin),
            "excess_margin": float(excess_margin),
            "margin_level_pct": float((required_margin / total_value * 100) if total_value else 0),
            "is_compliant": excess_margin > 0,
        }

    async def check_short_sale_constraints(self, symbol: str) -> Dict[str, any]:
        """Check if stock is eligible for short sale (RegSHO Rule).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with short sale eligibility
        """
        # RegSHO Rule: Uptick rule for short sales on declining stocks
        # For MVP, simplified implementation

        return {
            "symbol": symbol,
            "is_hard_to_borrow": False,  # Would check actual borrow list
            "locate_required": True,
            "short_sale_eligible": True,
        }

    async def validate_order_compliance(
        self, user_id: int, order_symbol: str, order_quantity: Decimal, order_side: str
    ) -> Dict[str, any]:
        """Validate if order meets all compliance requirements.

        Args:
            user_id: User ID
            order_symbol: Stock symbol
            order_quantity: Order quantity
            order_side: Order side (buy/sell)

        Returns:
            Dictionary with compliance validation results
        """
        checks = {
            "pdt_compliant": True,
            "margin_compliant": True,
            "position_limit_compliant": True,
            "short_sale_compliant": True,
            "all_checks_passed": True,
            "violations": [],
        }

        # Check PDT
        pdt_status = await self.check_pattern_day_trader(user_id)
        checks["pdt_compliant"] = pdt_status["compliant"]
        if not pdt_status["compliant"]:
            checks["violations"].append("Pattern Day Trader rule violation")

        # Check margin
        margin_status = await self.check_margin_requirements(user_id)
        checks["margin_compliant"] = margin_status["is_compliant"]
        if not margin_status["is_compliant"]:
            checks["violations"].append("Insufficient margin")

        # Check position limits
        positions = await self.position_repo.get_user_positions(user_id)
        total_value = sum(p.current_value for p in positions)

        if total_value > 0 and order_side == "buy":
            # Check single stock limit
            order_value = Decimal(str(order_quantity))  # Simplified
            new_portfolio_pct = (order_value / total_value) * 100
            if new_portfolio_pct > float(self.SINGLE_STOCK_MAX_PCT):
                checks["position_limit_compliant"] = False
                checks["violations"].append(
                    f"Single stock position would exceed {self.SINGLE_STOCK_MAX_PCT}% limit"
                )

        # Check short sale
        if order_side == "sell":
            short_status = await self.check_short_sale_constraints(order_symbol)
            checks["short_sale_compliant"] = short_status["short_sale_eligible"]
            if not short_status["short_sale_eligible"]:
                checks["violations"].append("Stock not eligible for short sale")

        checks["all_checks_passed"] = len(checks["violations"]) == 0

        return checks

    async def log_trade_for_compliance(
        self,
        user_id: int,
        order_id: int,
        action: str,
        details: Dict,
    ) -> bool:
        """Log trade for compliance audit trail.

        Args:
            user_id: User ID
            order_id: Order ID
            action: Action description
            details: Additional details

        Returns:
            True if logged successfully
        """
        # In production, would create AuditLog entry
        logger.info(
            f"Compliance log - User {user_id}, Order {order_id}, Action: {action}, Details: {details}"
        )
        return True

    async def generate_compliance_report(self, user_id: int) -> Dict[str, any]:
        """Generate comprehensive compliance report for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with compliance report
        """
        pdt_status = await self.check_pattern_day_trader(user_id)
        margin_status = await self.check_margin_requirements(user_id)
        wash_sales = await self.detect_wash_sales(user_id)

        return {
            "user_id": user_id,
            "report_date": datetime.utcnow(),
            "pdt_status": pdt_status,
            "margin_status": margin_status,
            "wash_sales_detected": len(wash_sales),
            "wash_sales": wash_sales[:10],  # Top 10
            "overall_compliant": (
                pdt_status["compliant"] and margin_status["is_compliant"] and len(wash_sales) == 0
            ),
        }

    def _count_round_trips(self, orders: List[Order], lookback_date: datetime) -> int:
        """Count round trip trades (buy + sell same stock).

        Args:
            orders: List of orders
            lookback_date: Start date for lookback

        Returns:
            Number of round trips
        """
        round_trips = 0
        relevant_orders = [o for o in orders if o.created_at >= lookback_date]

        # Group by stock
        trades_by_stock = {}
        for order in relevant_orders:
            if order.stock_id not in trades_by_stock:
                trades_by_stock[order.stock_id] = {"buys": [], "sells": []}

            if order.side == OrderSide.BUY:
                trades_by_stock[order.stock_id]["buys"].append(order)
            else:
                trades_by_stock[order.stock_id]["sells"].append(order)

        # Count round trips (buy + sell)
        for stock_id, trades in trades_by_stock.items():
            round_trips += min(len(trades["buys"]), len(trades["sells"]))

        return round_trips


class ComplianceMonitor:
    """Monitor for continuous compliance checking."""

    def __init__(self, compliance_service: ComplianceService):
        """Initialize compliance monitor.

        Args:
            compliance_service: ComplianceService instance
        """
        self.compliance_service = compliance_service

    async def monitor_user_compliance(self, user_id: int) -> Dict[str, any]:
        """Continuously monitor user for compliance violations.

        Args:
            user_id: User ID

        Returns:
            Compliance monitoring results
        """
        report = await self.compliance_service.generate_compliance_report(user_id)

        violations = []
        if not report["pdt_status"]["compliant"]:
            violations.append("PDT Rule Violation")
        if not report["margin_status"]["is_compliant"]:
            violations.append("Margin Requirement Violation")
        if report["wash_sales_detected"] > 0:
            violations.append("Wash Sale Detected")

        return {
            "user_id": user_id,
            "compliant": len(violations) == 0,
            "violations": violations,
            "report": report,
        }

    async def batch_compliance_check(self, user_ids: List[int]) -> Dict[int, Dict]:
        """Check compliance for multiple users.

        Args:
            user_ids: List of user IDs

        Returns:
            Dictionary mapping user IDs to compliance status
        """
        results = {}

        for user_id in user_ids:
            results[user_id] = await self.monitor_user_compliance(user_id)

        return results
