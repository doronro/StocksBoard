"""
Custom exception classes with safe error messaging.

This module provides exception classes that log detailed internal error messages
while returning generic messages to clients to prevent information disclosure.
"""
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class SafeHTTPException(HTTPException):
    """
    Base exception that returns safe messages to client while logging details internally.

    This exception prevents information disclosure by keeping internal error
    details separate from the client-facing message.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        internal_detail: str = None,
    ):
        """
        Initialize SafeHTTPException.

        Args:
            status_code: HTTP status code
            detail: Safe message to return to client
            internal_detail: Detailed message for internal logging
        """
        super().__init__(status_code=status_code, detail=detail)
        self.internal_detail = internal_detail or detail

    def log(self):
        """Log the internal detail message."""
        logger.error(f"API Error: {self.internal_detail}")


class ValidationError(SafeHTTPException):
    """Raised when input validation fails."""

    def __init__(self, field: str = None, reason: str = None):
        """
        Initialize ValidationError.

        Args:
            field: Field that failed validation
            reason: Reason for validation failure
        """
        internal_msg = f"Validation failed"
        if field:
            internal_msg += f" on field: {field}"
        if reason:
            internal_msg += f" ({reason})"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data",
            internal_detail=internal_msg,
        )


class InvalidSymbolError(SafeHTTPException):
    """Raised when stock symbol is invalid."""

    def __init__(self, symbol: str):
        """
        Initialize InvalidSymbolError.

        Args:
            symbol: Invalid symbol provided
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stock symbol",
            internal_detail=f"Invalid symbol format: {symbol}",
        )


class QuantityExceedsLimitError(SafeHTTPException):
    """Raised when quantity exceeds allowed limits."""

    def __init__(self, quantity: str, limit: str):
        """
        Initialize QuantityExceedsLimitError.

        Args:
            quantity: Requested quantity
            limit: Maximum allowed quantity
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order size exceeds limits",
            internal_detail=f"Quantity {quantity} exceeds maximum {limit}",
        )


class PriceTooHighError(SafeHTTPException):
    """Raised when price exceeds allowed limits."""

    def __init__(self, price: str, max_price: str):
        """
        Initialize PriceTooHighError.

        Args:
            price: Requested price
            max_price: Maximum allowed price
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price exceeds maximum allowed value",
            internal_detail=f"Price {price} exceeds maximum {max_price}",
        )


class PriceTooLowError(SafeHTTPException):
    """Raised when price is below minimum."""

    def __init__(self, price: str, min_price: str):
        """
        Initialize PriceTooLowError.

        Args:
            price: Requested price
            min_price: Minimum allowed price
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price is below minimum allowed value",
            internal_detail=f"Price {price} is below minimum {min_price}",
        )


class PositionSizeExceedsLimitError(SafeHTTPException):
    """Raised when position concentration exceeds limits."""

    def __init__(self, symbol: str, current_value: str, limit: str):
        """
        Initialize PositionSizeExceedsLimitError.

        Args:
            symbol: Stock symbol
            current_value: Current position value
            limit: Maximum allowed position value
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Position size exceeds portfolio limits",
            internal_detail=f"Position {symbol}: {current_value} exceeds limit {limit}",
        )


class UnauthorizedError(SafeHTTPException):
    """Raised when user is not authenticated or authorized."""

    def __init__(self, reason: str = ""):
        """
        Initialize UnauthorizedError.

        Args:
            reason: Reason for unauthorized access
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            internal_detail=f"Unauthorized: {reason}" if reason else "Unauthorized access attempt",
        )


class ForbiddenError(SafeHTTPException):
    """Raised when user does not have permission to access resource."""

    def __init__(self, reason: str = ""):
        """
        Initialize ForbiddenError.

        Args:
            reason: Reason for forbidden access
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            internal_detail=f"Forbidden: {reason}" if reason else "Access denied",
        )


class NotFoundError(SafeHTTPException):
    """Raised when resource is not found."""

    def __init__(self, resource: str):
        """
        Initialize NotFoundError.

        Args:
            resource: Type of resource not found (e.g., 'Order', 'Position')
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
            internal_detail=f"{resource} not found in database",
        )


class BusinessLogicError(SafeHTTPException):
    """Raised when business logic validation fails."""

    def __init__(self, reason: str):
        """
        Initialize BusinessLogicError.

        Args:
            reason: Reason for business logic violation
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request cannot be processed",
            internal_detail=f"Business logic violation: {reason}",
        )


class OrderStateError(SafeHTTPException):
    """Raised when operation is invalid for current order state."""

    def __init__(self, order_id: int, current_status: str, operation: str):
        """
        Initialize OrderStateError.

        Args:
            order_id: Order ID
            current_status: Current order status
            operation: Operation attempted
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot perform operation on this order",
            internal_detail=f"Cannot {operation} order {order_id} with status {current_status}",
        )


class DuplicateResourceError(SafeHTTPException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str, identifier: str):
        """
        Initialize DuplicateResourceError.

        Args:
            resource: Type of resource
            identifier: Unique identifier that already exists
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource already exists",
            internal_detail=f"{resource} with identifier {identifier} already exists",
        )


class RateLimitError(SafeHTTPException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = None):
        """
        Initialize RateLimitError.

        Args:
            retry_after: Seconds to wait before retrying
        """
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            internal_detail=f"Rate limit exceeded (retry after {retry_after}s)" if retry_after else "Rate limit exceeded",
        )


class InternalServerError(SafeHTTPException):
    """Raised when an unexpected server error occurs."""

    def __init__(self, exception: Exception = None, context: str = ""):
        """
        Initialize InternalServerError.

        Args:
            exception: Original exception that occurred
            context: Context where the error occurred
        """
        internal_msg = "Unhandled server error"
        if context:
            internal_msg += f" in {context}"
        if exception:
            internal_msg += f": {type(exception).__name__}: {str(exception)}"

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            internal_detail=internal_msg,
        )
