"""
Integration tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import create_app
from app.models import Base, User
from app.auth import hash_password
from app.database import get_db


@pytest.fixture
async def test_db():
    """Create an in-memory SQLite database for testing."""
    # Use SQLite for testing - faster and no external dependencies
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    return engine, AsyncSessionLocal, override_get_db


@pytest.fixture
async def client(test_db):
    """Create test client with in-memory database."""
    engine, AsyncSessionLocal, override_get_db = test_db

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    await engine.dispose()


@pytest.fixture
async def test_user(test_db):
    """Create a test user in the database."""
    engine, AsyncSessionLocal, override_get_db = test_db

    async with AsyncSessionLocal() as session:
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("test_password_123"),
            full_name="Test User",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.mark.asyncio
class TestAuthenticationEndpoints:
    """Tests for user authentication endpoints."""

    async def test_register_new_user(self, client):
        """POST /auth/register creates a new user."""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "secure_password_123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["is_active"] is True
        # Password should not be returned
        assert "password" not in data

    async def test_register_duplicate_username(self, client, test_user):
        """POST /auth/register rejects duplicate username."""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "password": "another_password",
                "full_name": "Another User",
            },
        )

        assert response.status_code == 400

    async def test_login_success(self, client, test_user):
        """POST /auth/login returns tokens for valid credentials."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    async def test_login_invalid_username(self, client):
        """POST /auth/login rejects invalid username."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "any_password",
            },
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    async def test_login_invalid_password(self, client, test_user):
        """POST /auth/login rejects invalid password."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    async def test_login_inactive_user(self, test_db):
        """POST /auth/login rejects inactive users."""
        engine, AsyncSessionLocal, override_get_db = test_db

        async with AsyncSessionLocal() as session:
            inactive_user = User(
                username="inactive",
                email="inactive@example.com",
                password_hash=hash_password("password123"),
                full_name="Inactive User",
                is_active=False,
            )
            session.add(inactive_user)
            await session.commit()

        app = create_app()
        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "inactive",
                    "password": "password123",
                },
            )

        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    async def test_refresh_token_success(self, client, test_user):
        """POST /auth/refresh returns new access token."""
        # First login to get refresh token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, client):
        """POST /auth/refresh rejects invalid refresh token."""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        assert "Invalid or expired" in response.json()["detail"]


@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication."""

    async def test_get_user_profile_authenticated(self, client, test_user):
        """GET /users/me returns user profile when authenticated."""
        # Login first
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Get user profile
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_get_user_profile_unauthenticated(self, client):
        """GET /users/me returns 401 when not authenticated."""
        response = await client.get("/api/users/me")

        assert response.status_code == 403  # No credentials provided

    async def test_get_user_profile_invalid_token(self, client):
        """GET /users/me returns 401 with invalid token."""
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    async def test_orders_requires_authentication(self, client):
        """GET /orders returns 401 when not authenticated."""
        response = await client.get("/api/orders")

        assert response.status_code == 403

    async def test_orders_authenticated(self, client, test_user):
        """GET /orders returns orders when authenticated."""
        # Login first
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Get orders
        response = await client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Should succeed (may be empty list, but not 401)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
class TestTokenExpiration:
    """Tests for token expiration and refresh."""

    async def test_expired_token_rejected(self, client):
        """Expired tokens are rejected."""
        from app.auth import create_access_token
        from datetime import timedelta

        # Create an already-expired token
        expired_token = create_access_token(
            data={"sub": 999},
            expires_delta=timedelta(hours=-1),
        )

        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    async def test_access_token_valid_for_duration(self, client, test_user):
        """Access token remains valid during its expiration window."""
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Token should be valid immediately
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Tests for security-related headers."""

    async def test_auth_header_required(self, client):
        """Protected endpoints require Authorization header."""
        response = await client.get("/api/users/me")

        # Should reject without proper auth
        assert response.status_code in (401, 403)

    async def test_bearer_token_format(self, client, test_user):
        """Bearer token format is required."""
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "test_password_123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Test with wrong format
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Basic {access_token}"},
        )

        # Should reject non-Bearer tokens
        assert response.status_code == 403
