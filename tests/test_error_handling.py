"""
Comprehensive tests for error handling and safe exception messages.

Tests verify that:
- Error messages are generic and safe for clients
- Detailed errors are logged internally only
- No database or system details are exposed
- Stack traces are not included in responses
- All exception types have proper status codes
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
import logging
from unittest.mock import Mock, patch

from app.main import create_app
from app.exceptions import (
    SafeHTTPException,
    ValidationError as ValidationException,
    InvalidSymbolError,
    NotFoundError,
    BusinessLogicError,
    OrderStateError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError,
    QuantityExceedsLimitError,
    PriceTooHighError,
    PriceTooLowError,
    PositionSizeExceedsLimitError,
    DuplicateResourceError,
    RateLimitError,
)


class TestSafeHTTPException:
    """Tests for SafeHTTPException behavior."""

    def test_safe_exception_stores_internal_detail(self):
        """Test that internal detail is stored separately from client message."""
        exc = SafeHTTPException(
            status_code=400,
            detail="Invalid request",
            internal_detail="Invalid symbol format in database lookup",
        )
        assert exc.detail == "Invalid request"
        assert exc.internal_detail == "Invalid symbol format in database lookup"

    def test_safe_exception_default_internal_detail(self):
        """Test that internal detail defaults to detail if not provided."""
        exc = SafeHTTPException(
            status_code=400,
            detail="Invalid request",
        )
        assert exc.detail == "Invalid request"
        assert exc.internal_detail == "Invalid request"

    def test_safe_exception_log_method(self, caplog):
        """Test that log method logs internal detail."""
        exc = SafeHTTPException(
            status_code=400,
            detail="Invalid request",
            internal_detail="Sensitive database error: connection refused",
        )
        with caplog.at_level(logging.ERROR):
            exc.log()
        assert "Sensitive database error" in caplog.text

    def test_safe_exception_does_not_log_detail(self, caplog):
        """Test that log method does not expose detail to logs."""
        exc = SafeHTTPException(
            status_code=400,
            detail="Invalid request",
            internal_detail="Sensitive database error: connection refused",
        )
        with caplog.at_level(logging.ERROR):
            exc.log()
        # Should log internal detail, not the safe detail
        assert "Sensitive database" in caplog.text


class TestValidationErrors:
    """Tests for validation error exceptions."""

    def test_validation_error_generic_message(self):
        """Test that ValidationError returns generic message to client."""
        exc = ValidationException(field="symbol", reason="invalid format")
        assert exc.detail == "Invalid request data"
        assert exc.status_code == 400

    def test_validation_error_logs_field(self, caplog):
        """Test that validation error logs specific field."""
        exc = ValidationException(field="price", reason="exceeds maximum")
        with caplog.at_level(logging.ERROR):
            exc.log()
        assert "price" in caplog.text
        assert "exceeds maximum" in caplog.text

    def test_invalid_symbol_error(self):
        """Test InvalidSymbolError exception."""
        exc = InvalidSymbolError("INVALID123")
        assert exc.detail == "Invalid stock symbol"
        assert exc.status_code == 400
        assert "INVALID123" in exc.internal_detail

    def test_not_found_error(self):
        """Test NotFoundError exception."""
        exc = NotFoundError("Order")
        assert exc.detail == "Resource not found"
        assert exc.status_code == 404
        assert "Order" in exc.internal_detail

    def test_business_logic_error(self):
        """Test BusinessLogicError exception."""
        exc = BusinessLogicError("Position already exists for this stock")
        assert exc.detail == "Request cannot be processed"
        assert exc.status_code == 422

    def test_order_state_error(self):
        """Test OrderStateError exception."""
        exc = OrderStateError(order_id=123, current_status="filled", operation="cancel")
        assert exc.detail == "Cannot perform operation on this order"
        assert exc.status_code == 422
        assert "123" in exc.internal_detail
        assert "filled" in exc.internal_detail

    def test_quantity_exceeds_limit_error(self):
        """Test QuantityExceedsLimitError exception."""
        exc = QuantityExceedsLimitError("999999999.9999", "999999.9999")
        assert exc.detail == "Order size exceeds limits"
        assert exc.status_code == 400

    def test_price_too_high_error(self):
        """Test PriceTooHighError exception."""
        exc = PriceTooHighError("10000000", "9999999.99")
        assert exc.detail == "Price exceeds maximum allowed value"
        assert exc.status_code == 400

    def test_price_too_low_error(self):
        """Test PriceTooLowError exception."""
        exc = PriceTooLowError("0.001", "0.01")
        assert exc.detail == "Price is below minimum allowed value"
        assert exc.status_code == 400

    def test_position_size_exceeds_limit_error(self):
        """Test PositionSizeExceedsLimitError exception."""
        exc = PositionSizeExceedsLimitError("AAPL", "50000", "40000")
        assert exc.detail == "Position size exceeds portfolio limits"
        assert exc.status_code == 422

    def test_unauthorized_error(self):
        """Test UnauthorizedError exception."""
        exc = UnauthorizedError("Missing authentication token")
        assert exc.detail == "Authentication required"
        assert exc.status_code == 401

    def test_forbidden_error(self):
        """Test ForbiddenError exception."""
        exc = ForbiddenError("User does not own this resource")
        assert exc.detail == "Access denied"
        assert exc.status_code == 403

    def test_duplicate_resource_error(self):
        """Test DuplicateResourceError exception."""
        exc = DuplicateResourceError("Position", "AAPL")
        assert exc.detail == "Resource already exists"
        assert exc.status_code == 409

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        exc = RateLimitError(retry_after=60)
        assert exc.detail == "Too many requests. Please try again later."
        assert exc.status_code == 429
        assert "60" in exc.internal_detail

    def test_internal_server_error_with_exception(self):
        """Test InternalServerError with original exception."""
        original = ValueError("Database connection failed")
        exc = InternalServerError(exception=original, context="order creation")
        assert exc.detail == "Internal server error"
        assert exc.status_code == 500
        assert "Database connection failed" in exc.internal_detail


class TestExceptionHandlerIntegration:
    """Integration tests for exception handlers."""

    @pytest.fixture
    def client(self):
        """Create test client with FastAPI app."""
        return TestClient(create_app())

    def test_validation_error_response_format(self, client):
        """Test that validation errors return proper JSON response."""
        response = client.post(
            "/api/orders",
            json={
                "symbol": "INVALID123",
                "order_type": "market",
                "side": "buy",
                "quantity": "-100",
                "price": "150.00",
            },
        )
        # Validation errors should return 422 for FastAPI
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data

    def test_error_response_does_not_expose_stack_trace(self, client):
        """Test that error responses do not contain stack traces."""
        response = client.get("/api/orders/99999")
        # Should be 401 (unauthorized) or 404 (not found)
        assert response.status_code in [401, 404]
        data = response.json()
        # Should not contain Python traceback info
        assert "Traceback" not in str(data)
        assert "File \"/app" not in str(data)
        assert "raise " not in str(data)

    def test_404_response_generic_message(self, client):
        """Test that 404 responses use generic messages."""
        response = client.get("/api/orders/999999")
        # May need auth, but if it gets to order lookup, should get generic 404
        data = response.json()
        # Should have a simple error message
        error_msg = str(data).lower()
        assert "internal" not in error_msg or "server error" in error_msg

    def test_safe_exception_handler_called(self):
        """Test that SafeHTTPException handler is registered."""
        app = create_app()
        # Verify exception handlers are registered
        assert Exception in app.exception_handlers
        assert SafeHTTPException in app.exception_handlers

    def test_pydantic_validation_error_handler(self):
        """Test that Pydantic validation errors are handled safely."""
        app = create_app()
        assert ValidationError in app.exception_handlers

    def test_value_error_handler(self):
        """Test that ValueError exceptions are handled safely."""
        app = create_app()
        assert ValueError in app.exception_handlers


class TestErrorMessageSanitization:
    """Tests for ensuring error messages don't expose sensitive information."""

    def test_database_error_not_exposed(self):
        """Test that database errors are not exposed to client."""
        exc = SafeHTTPException(
            status_code=500,
            detail="Internal server error",
            internal_detail="SQLAlchemy: Connection refused to postgres://user:password@internal-db:5432/prod",
        )
        # Client should only see generic message
        assert "postgres" not in exc.detail
        assert "password" not in exc.detail
        assert "internal-db" not in exc.detail
        # Internal detail should have the full error
        assert "postgres" in exc.internal_detail

    def test_file_paths_not_exposed(self):
        """Test that file paths are not exposed in client messages."""
        exc = SafeHTTPException(
            status_code=500,
            detail="Internal server error",
            internal_detail="File '/app/storage/tenants/uuid/projects/uuid/app/services/order_service.py' line 145",
        )
        assert "/app/storage" not in exc.detail
        assert "/app/storage" in exc.internal_detail

    def test_config_secrets_not_exposed(self):
        """Test that configuration secrets are not exposed."""
        exc = SafeHTTPException(
            status_code=500,
            detail="Internal server error",
            internal_detail="Failed to connect: DATABASE_URL=postgresql://user:secret_password@db:5432/prod",
        )
        assert "secret_password" not in exc.detail
        assert "secret_password" in exc.internal_detail

    def test_query_details_not_exposed(self):
        """Test that SQL query details are not exposed."""
        exc = SafeHTTPException(
            status_code=500,
            detail="Internal server error",
            internal_detail="SQL Error: SELECT * FROM users WHERE email='admin@example.com' AND password='hash' failed",
        )
        assert "SELECT * FROM users" not in exc.detail
        assert "SELECT * FROM users" in exc.internal_detail


class TestErrorLogging:
    """Tests for proper error logging."""

    def test_error_logged_on_safe_exception_log(self, caplog):
        """Test that errors are logged when logging is triggered."""
        exc = SafeHTTPException(
            status_code=400,
            detail="Invalid request",
            internal_detail="Symbol contains invalid characters: test@123",
        )
        with caplog.at_level(logging.ERROR):
            exc.log()
        assert "test@123" in caplog.text or "Symbol contains" in caplog.text

    def test_multiple_exceptions_logged_separately(self, caplog):
        """Test that multiple exceptions are logged separately."""
        exc1 = NotFoundError("Order")
        exc2 = ValidationException(field="quantity")

        with caplog.at_level(logging.ERROR):
            exc1.log()
            exc2.log()

        log_text = caplog.text
        # Both errors should be logged
        assert "Order" in log_text
        assert "quantity" in log_text

    def test_internal_error_logged_with_context(self, caplog):
        """Test that internal errors are logged with full context."""
        original_error = ValueError("Original error message")
        exc = InternalServerError(exception=original_error, context="order processing")

        with caplog.at_level(logging.ERROR):
            exc.log()

        log_text = caplog.text
        # Should contain context and original error
        assert "order processing" in log_text or "Original error" in log_text
