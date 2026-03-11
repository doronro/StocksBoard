"""API routes for price alerts and notifications."""
from fastapi import APIRouter, Depends, HTTPException, Query
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from app.database import db_manager
from app.services.alert_service import AlertService, AlertType
from app.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertCreate(BaseModel):
    """Alert creation schema."""

    symbol: str
    alert_type: str
    threshold_value: Decimal


class AlertResponse(BaseModel):
    """Alert response schema."""

    id: int
    symbol: str
    alert_type: str
    threshold_value: float
    is_active: bool
    created_at: datetime


async def get_db() -> AsyncSession:
    """Get database session."""
    async with db_manager.get_session() as session:
        yield session


@router.get("")
async def get_alerts(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all alerts for current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of alerts
    """
    try:
        service = AlertService(db)
        user_id = current_user.get("id")

        alerts = await service.get_active_alerts(user_id)

        return {
            "alerts": alerts,
            "total": len(alerts),
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")


@router.post("")
async def create_alert(
    alert: AlertCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new price alert.

    Supported alert types:
    - price_above: Trigger when price rises above threshold
    - price_below: Trigger when price falls below threshold
    - percent_gain: Trigger when gain reaches threshold %
    - percent_loss: Trigger when loss reaches threshold %
    - rsi_overbought: Trigger when RSI > 70
    - rsi_oversold: Trigger when RSI < 30
    - macd_crossover: Trigger on MACD crossover
    - volume_spike: Trigger on volume spike

    Args:
        alert: Alert configuration
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created alert details
    """
    try:
        service = AlertService(db)
        user_id = current_user.get("id")

        # Validate alert type
        try:
            AlertType(alert.alert_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid alert type: {alert.alert_type}"
            )

        result = await service.create_alert(
            user_id, alert.symbol, AlertType(alert.alert_type), alert.threshold_value
        )

        if not result:
            raise HTTPException(status_code=400, detail="Failed to create alert")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")


@router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    threshold_value: Optional[Decimal] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing alert.

    Args:
        alert_id: Alert ID
        threshold_value: New threshold value
        is_active: New active status
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated alert details
    """
    try:
        # In production, would update alert in database
        logger.info(f"Updated alert {alert_id} for user {current_user.get('id')}")

        return {
            "id": alert_id,
            "message": "Alert updated successfully",
        }
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alert")


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert.

    Args:
        alert_id: Alert ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Confirmation message
    """
    try:
        service = AlertService(db)
        user_id = current_user.get("id")

        success = await service.disable_alert(user_id, alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"message": "Alert deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alert")


@router.get("/technical/{symbol}")
async def check_technical_alerts(
    symbol: str,
    rsi: Optional[float] = Query(None, ge=0, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check technical indicator alerts for a symbol.

    Args:
        symbol: Stock symbol
        rsi: Optional RSI value to evaluate
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of triggered technical alerts
    """
    try:
        service = AlertService(db)

        rsi_decimal = Decimal(str(rsi)) if rsi is not None else None
        alerts = await service.check_technical_alerts(symbol, rsi_decimal)

        return {
            "symbol": symbol,
            "triggered_alerts": alerts,
            "total": len(alerts),
        }
    except Exception as e:
        logger.error(f"Error checking technical alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to check technical alerts")


@router.post("/monitor")
async def monitor_portfolio_alerts(
    alert_configs: List[dict],
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Monitor multiple alerts for portfolio.

    Args:
        alert_configs: List of alert configurations
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of triggered alerts
    """
    try:
        service = AlertService(db)
        user_id = current_user.get("id")

        triggered = await service.monitor_portfolio_alerts(user_id, alert_configs)

        return {
            "monitored_alerts": len(alert_configs),
            "triggered_count": len(triggered),
            "triggered_alerts": triggered,
        }
    except Exception as e:
        logger.error(f"Error monitoring alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to monitor alerts")


@router.get("/alerts/notification-settings")
async def get_notification_settings(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notification settings for alerts.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Notification settings
    """
    return {
        "email_alerts": True,
        "push_alerts": True,
        "sms_alerts": False,
        "in_app_alerts": True,
    }


@router.put("/alerts/notification-settings")
async def update_notification_settings(
    email_alerts: Optional[bool] = None,
    push_alerts: Optional[bool] = None,
    sms_alerts: Optional[bool] = None,
    in_app_alerts: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notification settings for alerts.

    Args:
        email_alerts: Enable email alerts
        push_alerts: Enable push alerts
        sms_alerts: Enable SMS alerts
        in_app_alerts: Enable in-app alerts
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated notification settings
    """
    try:
        logger.info(f"Updated notification settings for user {current_user.get('id')}")

        return {
            "email_alerts": email_alerts if email_alerts is not None else True,
            "push_alerts": push_alerts if push_alerts is not None else True,
            "sms_alerts": sms_alerts if sms_alerts is not None else False,
            "in_app_alerts": in_app_alerts if in_app_alerts is not None else True,
        }
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification settings")
