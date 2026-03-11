"""CSRF protection utilities for FastAPI application.

This module implements CSRF token generation, validation, and middleware
using the double-submit cookie pattern for maximum security.
"""
import secrets
import time
from typing import Optional
from datetime import datetime, timedelta
import hmac
import hashlib
from fastapi import HTTPException, status


class CSRFManager:
    """Manages CSRF token generation and validation."""

    def __init__(self, secret_key: str, token_expiration_hours: int = 24):
        """Initialize CSRF manager.

        Args:
            secret_key: Secret key for signing tokens
            token_expiration_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.token_expiration_hours = token_expiration_hours
        self.token_header_name = "X-CSRF-Token"
        self.token_cookie_name = "csrf_token"

    def generate_token(self) -> str:
        """Generate a new CSRF token.

        Returns:
            A secure random token string
        """
        # Generate random token (256 bits = 32 bytes)
        random_token = secrets.token_urlsafe(32)

        # Create timestamp for expiration validation
        timestamp = str(int(time.time()))

        # Create signature: HMAC-SHA256(secret_key, token + timestamp)
        message = f"{random_token}:{timestamp}".encode()
        signature = hmac.new(
            self.secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()

        # Combine: token:timestamp:signature
        return f"{random_token}:{timestamp}:{signature}"

    def validate_token(self, token: str) -> bool:
        """Validate CSRF token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid, False otherwise

        Raises:
            ValueError: If token format is invalid
        """
        try:
            # Parse token components
            parts = token.split(":")
            if len(parts) != 3:
                return False

            random_token, timestamp_str, provided_signature = parts

            # Validate timestamp
            try:
                timestamp = int(timestamp_str)
            except ValueError:
                return False

            # Check expiration
            current_time = int(time.time())
            expiration_seconds = self.token_expiration_hours * 3600
            if current_time - timestamp > expiration_seconds:
                return False

            # Verify signature
            message = f"{random_token}:{timestamp_str}".encode()
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message,
                hashlib.sha256
            ).hexdigest()

            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(provided_signature, expected_signature)

        except Exception:
            return False

    def validate_token_pair(self, token_from_header: str, token_from_cookie: str) -> bool:
        """Validate token pair (header token should match cookie token).

        In double-submit cookie pattern, the token value in header should
        match the value in cookie (same random component).

        Args:
            token_from_header: Token from request header
            token_from_cookie: Token from request cookie

        Returns:
            True if both tokens are valid and match
        """
        # Both tokens must be valid
        if not self.validate_token(token_from_header):
            return False

        if not self.validate_token(token_from_cookie):
            return False

        # Extract random components and compare
        try:
            header_random = token_from_header.split(":")[0]
            cookie_random = token_from_cookie.split(":")[0]

            return hmac.compare_digest(header_random, cookie_random)
        except Exception:
            return False


class CSRFException(HTTPException):
    """CSRF validation exception."""

    def __init__(self, detail: str = "CSRF token validation failed"):
        """Initialize CSRF exception.

        Args:
            detail: Error message to return to client
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
