"""
Unit tests for authentication and authorization.
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from jose import jwt

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_creates_hash(self):
        """hash_password creates a bcrypt hash."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password_valid(self):
        """verify_password returns True for correct password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_invalid(self):
        """verify_password returns False for incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_same_password_different_hashes(self):
        """Hashing same password multiple times produces different hashes."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessTokenCreation:
    """Tests for access token creation and validation."""

    def test_create_access_token_default_expiration(self):
        """create_access_token creates token with default expiration."""
        user_id = 123
        token = create_access_token(data={"sub": user_id})

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_create_access_token_custom_expiration(self):
        """create_access_token respects custom expiration."""
        user_id = 123
        expires_delta = timedelta(hours=1)
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
        # Verify expiration is roughly 1 hour from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()
        assert 3500 < time_diff < 3700  # Allow 100 seconds variance

    def test_create_access_token_contains_data(self):
        """create_access_token encodes all provided data."""
        data = {"sub": 456, "username": "testuser", "email": "test@example.com"}
        token = create_access_token(data=data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == 456
        assert payload["username"] == "testuser"
        assert payload["email"] == "test@example.com"

    def test_access_token_expired(self):
        """Expired access tokens are rejected."""
        user_id = 789
        # Create token that expired 1 hour ago
        expires_delta = timedelta(hours=-1)
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

        # Token should be expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class TestRefreshTokenCreation:
    """Tests for refresh token creation and validation."""

    def test_create_refresh_token(self):
        """create_refresh_token creates a valid refresh token."""
        user_id = 123
        token = create_refresh_token(data={"sub": user_id})

        assert token is not None
        assert isinstance(token, str)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_refresh_token_longer_expiration(self):
        """Refresh tokens have longer expiration than access tokens."""
        user_id = 456
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})

        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Refresh token should expire much later
        refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
        access_exp = datetime.fromtimestamp(access_payload["exp"])

        assert refresh_exp > access_exp
        time_diff_days = (refresh_exp - access_exp).days
        assert time_diff_days >= 6  # At least 6 days difference


class TestTokenValidation:
    """Tests for token validation."""

    def test_invalid_token_signature(self):
        """Invalid token signature is rejected."""
        # Create token with different secret
        wrong_secret = "wrong_secret_key_12345"
        token = jwt.encode({"sub": 123}, wrong_secret, algorithm=ALGORITHM)

        # Should fail to decode with correct secret
        with pytest.raises(jwt.JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_malformed_token(self):
        """Malformed token is rejected."""
        malformed_token = "not.a.valid.jwt.token"

        with pytest.raises(jwt.JWTError):
            jwt.decode(malformed_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_token_missing_subject(self):
        """Token without 'sub' claim is still decoded but missing user_id."""
        token = jwt.encode({"username": "test"}, SECRET_KEY, algorithm=ALGORITHM)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload.get("sub") is None
        assert payload["username"] == "test"


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    async def test_get_current_user_valid_token(self):
        """get_current_user returns user_id from valid token."""
        user_id = 789
        token = create_access_token(data={"sub": user_id})

        # Mock HTTPAuthCredentials
        from fastapi.security import HTTPAuthCredentials
        credentials = HTTPAuthCredentials(scheme="bearer", credentials=token)

        result = await get_current_user(credentials)
        assert result["user_id"] == user_id

    async def test_get_current_user_expired_token(self):
        """get_current_user raises 401 for expired token."""
        from fastapi import HTTPException
        user_id = 123
        expires_delta = timedelta(hours=-1)
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

        from fastapi.security import HTTPAuthCredentials
        credentials = HTTPAuthCredentials(scheme="bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_invalid_token(self):
        """get_current_user raises 401 for invalid token."""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthCredentials
        credentials = HTTPAuthCredentials(scheme="bearer", credentials="invalid.token.here")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_missing_sub(self):
        """get_current_user raises 401 if token missing 'sub' claim."""
        from fastapi import HTTPException
        token = jwt.encode({"username": "test"}, SECRET_KEY, algorithm=ALGORITHM)

        from fastapi.security import HTTPAuthCredentials
        credentials = HTTPAuthCredentials(scheme="bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_refresh_token_rejected(self):
        """get_current_user rejects refresh tokens."""
        from fastapi import HTTPException
        user_id = 456
        refresh_token = create_refresh_token(data={"sub": user_id})

        from fastapi.security import HTTPAuthCredentials
        credentials = HTTPAuthCredentials(scheme="bearer", credentials=refresh_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "refresh token" in exc_info.value.detail.lower()
