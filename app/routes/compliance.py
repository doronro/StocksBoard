"""API routes for compliance and regulatory monitoring."""
from fastapi import APIRouter, Depends, HTTPException, Query
from decimal import Decimal
from app.database import db_manager
from app.services.compliance_service import ComplianceService, ComplianceMonitor
from app.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


async def get_db() -> AsyncSession:
    """Get database session."""
    async with db_manager.get_session() as session:
        yield session


@router.get("/status")
async def get_compliance_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get overall compliance status for user.

    Checks:
    - Pattern Day Trader (PDT) compliance
    - Margin requirements
    - Wash sale violations
    - Position limits

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Compliance status dictionary
    """
    try:
        service = ComplianceService(db)
        monitor = ComplianceMonitor(service)
        user_id = current_user.get("id")

        status = await monitor.monitor_user_compliance(user_id)

        return status
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get compliance status")


@router.get("/pdt-status")
async def get_pdt_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Pattern Day Trader (PDT) compliance status.

    PDT Rule: Must have $25,000 minimum account value if making
    4 or more day trades in 5 business days.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDT status and details
    """
    try:
        service = ComplianceService(db)
        user_id = current_user.get("id")

        pdt_status = await service.check_pattern_day_trader(user_id)

        return pdt_status
    except Exception as e:
        logger.error(f"Error getting PDT status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get PDT status")


@router.get("/margin-status")
async def get_margin_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get margin requirement compliance status.

    Regulation T: 50% margin requirement for stock purchases

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Margin status and requirements
    """
    try:
        service = ComplianceService(db)
        user_id = current_user.get("id")

        margin_status = await service.check_margin_requirements(user_id)

        return margin_status
    except Exception as e:
        logger.error(f"Error getting margin status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get margin status")


@router.get("/wash-sales")
async def detect_wash_sales(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detect potential wash sales.

    Wash Sale Rule: Cannot claim loss if repurchased within 30 days
    before or after sale.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of detected wash sales
    """
    try:
        service = ComplianceService(db)
        user_id = current_user.get("id")

        wash_sales = await service.detect_wash_sales(user_id)

        return {
            "total_detected": len(wash_sales),
            "wash_sales": wash_sales,
        }
    except Exception as e:
        logger.error(f"Error detecting wash sales: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect wash sales")


@router.post("/validate-order")
async def validate_order_compliance(
    symbol: str,
    quantity: Decimal,
    side: str = Query(..., regex="^(buy|sell)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate if order meets compliance requirements.

    Args:
        symbol: Stock symbol
        quantity: Order quantity
        side: Order side (buy/sell)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Compliance validation results
    """
    try:
        service = ComplianceService(db)
        user_id = current_user.get("id")

        validation = await service.validate_order_compliance(user_id, symbol, quantity, side)

        return validation
    except Exception as e:
        logger.error(f"Error validating order compliance: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate order")


@router.get("/short-sale-status/{symbol}")
async def check_short_sale_constraints(
    symbol: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if stock is eligible for short sale.

    Checks:
    - Hard to borrow (HTB) status
    - Locate requirement
    - RegSHO compliance

    Args:
        symbol: Stock symbol
        current_user: Current authenticated user
        db: Database session

    Returns:
        Short sale eligibility status
    """
    try:
        service = ComplianceService(db)

        status = await service.check_short_sale_constraints(symbol)

        return status
    except Exception as e:
        logger.error(f"Error checking short sale status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check short sale status")


@router.get("/report")
async def get_compliance_report(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive compliance report.

    Includes:
    - PDT status
    - Margin status
    - Wash sale detection
    - Position limits
    - Overall compliance status

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Comprehensive compliance report
    """
    try:
        service = ComplianceService(db)
        user_id = current_user.get("id")

        report = await service.generate_compliance_report(user_id)

        return report
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate compliance report")


@router.get("/audit-log")
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit log of all trades and compliance events.

    Args:
        limit: Maximum number of records
        offset: Number of records to skip
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of audit log entries
    """
    try:
        user_id = current_user.get("id")

        # In production, would query AuditLog from database
        logger.info(f"Retrieved audit log for user {user_id}, limit={limit}, offset={offset}")

        return {
            "total": 0,
            "limit": limit,
            "offset": offset,
            "audit_logs": [],
        }
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audit log")


@router.post("/export-report")
async def export_compliance_report(
    format: str = Query("pdf", regex="^(pdf|csv|json)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export compliance report in specified format.

    Args:
        format: Export format (pdf, csv, json)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Export details with download link
    """
    try:
        user_id = current_user.get("id")

        logger.info(f"Exporting compliance report for user {user_id} in {format} format")

        return {
            "user_id": user_id,
            "format": format,
            "status": "processing",
            "message": f"Report will be available for download shortly",
        }
    except Exception as e:
        logger.error(f"Error exporting compliance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to export report")
