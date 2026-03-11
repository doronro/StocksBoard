"""API routes for risk management and analysis."""
from fastapi import APIRouter, Depends, HTTPException, Query
from decimal import Decimal
from app.database import db_manager
from app.services.risk_management_service import RiskManagementService
from app.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["Risk Management"])


async def get_db() -> AsyncSession:
    """Get database session."""
    async with db_manager.get_session() as session:
        yield session


@router.get("/portfolio/metrics")
async def get_portfolio_metrics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portfolio risk metrics.

    Returns:
    - Sharpe ratio
    - Beta
    - Maximum drawdown
    - Volatility
    - Concentration metrics

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with portfolio metrics
    """
    try:
        service = RiskManagementService(db)
        user_id = current_user.get("id")

        sharpe_ratio = await service.calculate_sharpe_ratio(user_id)
        beta = await service.calculate_portfolio_beta(user_id)
        max_drawdown = await service.calculate_max_drawdown(user_id)
        concentration = await service.calculate_concentration_risk(user_id)

        return {
            "user_id": user_id,
            "sharpe_ratio": float(sharpe_ratio),
            "beta": float(beta),
            "max_drawdown": float(max_drawdown),
            "concentration": concentration,
        }
    except Exception as e:
        logger.error(f"Error getting portfolio metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate metrics")


@router.get("/portfolio/var")
async def calculate_value_at_risk(
    confidence_level: float = Query(0.95, ge=0.90, le=0.99),
    holding_period_days: int = Query(1, ge=1, le=30),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate Value at Risk (VaR) for portfolio.

    VaR estimates the maximum loss at a given confidence level
    over a specific holding period.

    Args:
        confidence_level: Confidence level (0.90 to 0.99)
        holding_period_days: Number of days (1 to 30)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with VaR estimates
    """
    try:
        service = RiskManagementService(db)
        user_id = current_user.get("id")

        var = await service.calculate_value_at_risk(
            user_id, confidence_level, holding_period_days
        )

        return var
    except Exception as e:
        logger.error(f"Error calculating VaR: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate VaR")


@router.get("/concentration")
async def get_concentration_analysis(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed concentration analysis.

    Identifies:
    - Largest positions
    - Sector concentration
    - Geographic concentration
    - Industry concentration

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with concentration analysis
    """
    try:
        service = RiskManagementService(db)
        user_id = current_user.get("id")

        concentration = await service.calculate_concentration_risk(user_id)
        concentrated_positions = await service.detect_concentrated_positions(user_id)

        return {
            "summary": concentration,
            "concentrated_positions": concentrated_positions,
        }
    except Exception as e:
        logger.error(f"Error getting concentration analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze concentration")


@router.post("/position-sizing")
async def calculate_position_sizing(
    account_size: Decimal,
    risk_percent: Decimal,
    entry_price: Decimal,
    stop_price: Decimal,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate recommended position size based on risk parameters.

    Args:
        account_size: Total account size
        risk_percent: Percentage of account to risk
        entry_price: Entry price for position
        stop_price: Stop loss price
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with position sizing recommendation
    """
    try:
        service = RiskManagementService(db)

        result = await service.calculate_position_sizing(
            account_size, risk_percent, entry_price, stop_price
        )

        return result
    except Exception as e:
        logger.error(f"Error calculating position sizing: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate position sizing")


@router.post("/order-margin-impact")
async def analyze_order_margin_impact(
    symbol: str,
    quantity: Decimal,
    price: Decimal,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze margin impact of a potential order.

    Args:
        symbol: Stock symbol
        quantity: Order quantity
        price: Order price
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dictionary with margin impact analysis
    """
    try:
        service = RiskManagementService(db)
        user_id = current_user.get("id")

        result = await service.analyze_order_margin_impact(user_id, price, quantity)

        return result
    except Exception as e:
        logger.error(f"Error analyzing margin impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze margin impact")


@router.get("/tax-loss-harvesting")
async def get_tax_loss_harvesting_opportunities(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get positions with unrealized losses for tax loss harvesting.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of positions with unrealized losses
    """
    try:
        service = RiskManagementService(db)
        user_id = current_user.get("id")

        opportunities = await service.estimate_tax_loss_harvesting_opportunities(user_id)

        return {
            "total_opportunities": len(opportunities),
            "estimated_tax_benefit": sum(o["tax_benefit"] for o in opportunities),
            "positions": opportunities,
        }
    except Exception as e:
        logger.error(f"Error getting tax loss harvesting opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze tax opportunities")
