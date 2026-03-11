"""
Audit logging service for tracking financial operations and security events.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """Service for logging audit events to database."""

    def __init__(self, db_session: AsyncSession):
        """Initialize audit logger.

        Args:
            db_session: AsyncSession instance for database operations
        """
        self.db = db_session

    async def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> "AuditLog":
        """Log a financial operation for audit trail.

        Args:
            user_id: ID of the user performing the action
            action: Action type (e.g., create_order, cancel_order, execute_order)
            resource_type: Type of resource (order, position, watchlist)
            resource_id: ID of the affected resource
            before_state: State before the action
            after_state: State after the action
            request_ip: IP address of the request
            user_agent: User-Agent header from request
            status: Status of the action (success, failure)
            error_message: Error message if action failed

        Returns:
            Created AuditLog instance
        """
        from app.models import AuditLog

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=request_ip,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )

        self.db.add(audit_entry)
        await self.db.commit()

        # Log to application logs
        log_level = logging.WARNING if status == "failure" else logging.INFO
        logger.log(
            log_level,
            f"AUDIT: user={user_id} action={action} resource={resource_type}/{resource_id} status={status} ip={request_ip}",
        )

        return audit_entry

    async def get_user_audit_logs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list:
        """Get audit logs for a specific user.

        Args:
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances
        """
        from app.models import AuditLog
        from sqlalchemy import select

        query = select(AuditLog).where(AuditLog.user_id == user_id).order_by(
            AuditLog.created_at.desc()
        )
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_action_audit_logs(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list:
        """Get audit logs for a specific action type.

        Args:
            action: Action to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances
        """
        from app.models import AuditLog
        from sqlalchemy import select

        query = select(AuditLog).where(AuditLog.action == action).order_by(
            AuditLog.created_at.desc()
        )
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list:
        """Get audit logs for a specific resource.

        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances
        """
        from app.models import AuditLog
        from sqlalchemy import select

        query = select(AuditLog).where(
            (AuditLog.resource_type == resource_type)
            & (AuditLog.resource_id == resource_id)
        ).order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()


async def get_audit_logger(db_session: AsyncSession) -> AuditLogger:
    """Get an AuditLogger instance.

    Args:
        db_session: AsyncSession instance

    Returns:
        AuditLogger instance
    """
    return AuditLogger(db_session)
