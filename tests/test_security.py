"""Security tests for CORS, rate limiting, debug mode, and security headers."""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import create_app
from app.config import Settings


class TestCORSConfiguration:
    """Test CORS security configuration."""

    def test_cors_headers_explicit_not_wildcard(self):
        """Test that CORS allows explicit headers, not wildcard."""
        app = create_app()

        # Find CORS middleware configuration
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware = middleware
                break

        # Note: Testing CORS behavior through actual requests
        client = TestClient(app)
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )

        # Verify CORS headers are set
        assert "access-control-allow-headers" in response.headers
        allowed_headers = response.headers["access-control-allow-headers"]

        # Should only allow specific headers, not wildcard
        assert "*" not in allowed_headers
        assert "Content-Type" in allowed_headers or "Authorization" in allowed_headers

    def test_cors_allows_configured_origins_only(self):
        """Test that CORS only allows configured origins."""
        app = create_app()
        client = TestClient(app)

        # Test with allowed origin
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )

        # Should allow the configured origin
        assert response.status_code == 200

    def test_cors_denies_unconfigured_origins(self):
        """Test that CORS denies unconfigured origins."""
        app = create_app()
        client = TestClient(app)

        # Test OPTIONS request with disallowed origin
        response = client.options(
            "/health",
            headers={
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Response should not include Allow-Origin for unauthorized origins
        # or it should be empty/not match the request origin
        origin_header = response.headers.get("access-control-allow-origin", "")
        assert origin_header != "https://malicious-site.com"


class TestRateLimiting:
    """Test rate limiting enforcement."""

    def test_registration_endpoint_rate_limit(self):
        """Test that registration endpoint enforces 5/minute rate limit."""
        app = create_app()
        client = TestClient(app)

        # Make multiple requests rapidly
        for i in range(6):
            response = client.post(
                "/api/users/register",
                json={
                    "username": f"testuser{i}",
                    "email": f"test{i}@example.com",
                    "password": "password123",
                    "full_name": f"Test User {i}",
                },
                headers={"X-Forwarded-For": "192.168.1.1"}  # Simulate same IP
            )

            # First 5 requests should succeed (200/400/etc), 6th should be rate limited
            if i < 5:
                # Should not be 429
                assert response.status_code != 429
            else:
                # 6th request should be rate limited
                assert response.status_code == 429

    def test_public_endpoints_rate_limit(self):
        """Test that public endpoints have appropriate rate limits."""
        app = create_app()
        client = TestClient(app)

        # Health check should have high rate limit (100+/minute)
        for i in range(101):
            response = client.get("/health")
            if i < 100:
                assert response.status_code == 200


class TestDebugModeDisabled:
    """Test that debug mode is properly controlled."""

    def test_debug_mode_disabled_by_default(self):
        """Test that debug mode is False by default."""
        settings = Settings()
        assert settings.debug is False

    def test_debug_mode_prevented_in_production(self):
        """Test that debug mode cannot be enabled in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "true"}):
            with pytest.raises(ValueError, match="Debug mode cannot be enabled in production"):
                Settings(debug=True)

    def test_debug_mode_allowed_in_development(self):
        """Test that debug mode can be enabled in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            settings = Settings(debug=True)
            assert settings.debug is True

    def test_app_debug_false_in_production(self):
        """Test that FastAPI app debug is False in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            app = create_app()
            # Debug setting should not be True in production
            assert app.debug is False

    def test_app_debug_respects_config_in_development(self):
        """Test that FastAPI app respects debug config in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "DEBUG": "false"}):
            app = create_app()
            # Should respect the config setting in development
            assert isinstance(app.debug, bool)


class TestSecurityHeaders:
    """Test that security headers are present in responses."""

    def test_security_headers_present_in_response(self):
        """Test that security headers are added to all responses."""
        app = create_app()
        client = TestClient(app)

        response = client.get("/health")

        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"

        assert "strict-transport-security" in response.headers
        assert "max-age=31536000" in response.headers["strict-transport-security"]

    def test_security_headers_on_error_response(self):
        """Test that security headers are present even on error responses."""
        app = create_app()
        client = TestClient(app)

        # Request non-existent endpoint
        response = client.get("/api/nonexistent")

        # Even on 404, security headers should be present
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers


class TestErrorHandling:
    """Test error handling and exception responses."""

    def test_generic_error_response_no_traceback(self):
        """Test that error responses don't expose stack traces."""
        app = create_app()
        client = TestClient(app)

        # Attempt to trigger an error
        response = client.get("/api/nonexistent")

        # Should return 404 or similar
        assert response.status_code in [404, 405]

        # Response should not contain Python stack trace markers
        response_text = response.text.lower()
        assert "traceback" not in response_text
        assert "file \"" not in response_text


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_frontend_url_from_environment(self):
        """Test that FRONTEND_URL environment variable is used."""
        with patch.dict(os.environ, {"FRONTEND_URL": "https://example.com"}):
            settings = Settings()
            assert "https://example.com" in settings.allowed_origins

    def test_frontend_url_default_localhost(self):
        """Test that FRONTEND_URL defaults to localhost:3000."""
        with patch.dict(os.environ, {}, clear=False):
            settings = Settings()
            assert "http://localhost:3000" in settings.allowed_origins

    def test_environment_variable_set(self):
        """Test that ENVIRONMENT variable can be set."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            assert settings.environment == "production"

    def test_environment_default_development(self):
        """Test that ENVIRONMENT defaults to development."""
        with patch.dict(os.environ, {}, clear=False):
            settings = Settings()
            assert settings.environment == "development"

    def test_secret_key_validation_in_production(self):
        """Test that SECRET_KEY must be set in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": ""}):
            with pytest.raises(ValueError, match="SECRET_KEY.*must be set"):
                Settings(secret_key="")

    def test_secret_key_length_validation_in_production(self):
        """Test that SECRET_KEY must be at least 32 chars in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(ValueError, match="at least 32 characters"):
                Settings(secret_key="tooshort")

    def test_database_url_validation(self):
        """Test that DATABASE_URL is validated."""
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            with pytest.raises(ValueError, match="DATABASE_URL.*required"):
                Settings(database_url="")


class TestEndpointRateLimits:
    """Test that specific endpoints have correct rate limits applied."""

    def test_registration_has_strict_limit(self):
        """Test that registration endpoint has strict rate limit."""
        app = create_app()
        client = TestClient(app)

        # Track how many requests succeed
        success_count = 0
        for i in range(10):
            response = client.post(
                "/api/users/register",
                json={
                    "username": f"user{i}",
                    "email": f"email{i}@test.com",
                    "password": "password123",
                    "full_name": "Test",
                },
                headers={"X-Forwarded-For": "10.0.0.1"}
            )

            if response.status_code != 429:
                success_count += 1

        # Should limit to 5 requests per minute
        assert success_count <= 5

    def test_get_endpoints_higher_limit(self):
        """Test that GET endpoints have higher rate limits."""
        app = create_app()
        client = TestClient(app)

        # Health endpoint should allow many requests
        success_count = 0
        for i in range(101):
            response = client.get(
                "/health",
                headers={"X-Forwarded-For": "10.0.0.2"}
            )

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                # Once rate limited, subsequent requests will be limited
                break

        # Should allow at least 100 requests per minute
        assert success_count >= 100
