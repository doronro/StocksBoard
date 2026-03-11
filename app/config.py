"""
Application configuration management using Pydantic Settings.
"""
import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Stock Exchange Board"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development")
    log_level: str = "INFO"

    # Database - CRITICAL: Must use environment variables
    database_url: str = Field(default="")
    database_echo: bool = False

    # Redis Cache
    redis_url: str = Field(default="redis://localhost:6379/0")
    cache_ttl_seconds: int = 300

    # API Keys for Market Data Providers - Should come from environment
    alpha_vantage_api_key: str = Field(default="")
    polygon_io_api_key: str = Field(default="")
    iex_cloud_api_key: str = Field(default="")
    yahoo_finance_api_key: str = Field(default="")

    # Authentication - CRITICAL: SECRET_KEY must come from environment
    secret_key: str = Field(default="")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS - Environment specific
    allowed_origins: List[str] = Field(default_factory=lambda: [
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ])
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["Content-Type", "Authorization"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # WebSocket
    websocket_heartbeat_interval: int = 30
    websocket_timeout: int = 60

    # External API Settings
    external_api_timeout: int = 10
    external_api_retries: int = 3

    # Background Jobs
    quote_update_interval_seconds: int = 5
    technical_indicator_update_interval_seconds: int = 300
    portfolio_revaluation_interval_seconds: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that SECRET_KEY is properly set and secure.

        Args:
            v: The secret_key value

        Returns:
            The validated secret_key value

        Raises:
            ValueError: If SECRET_KEY is not set or is a default placeholder in production
        """
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            if not v or v == "change-me-in-production":
                raise ValueError(
                    "SECRET_KEY environment variable must be set to a secure value in production. "
                    "It cannot be empty or the default placeholder 'change-me-in-production'. "
                    "Use a strong random string of at least 32 characters."
                )
            if len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long for secure JWT signing"
                )
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database configuration.

        Args:
            v: The database_url value

        Returns:
            The validated database_url value (may be empty, constructed from env vars)

        Raises:
            ValueError: If database configuration is invalid
        """
        # database_url can be empty - it's constructed from DB_* env vars
        # Only validate if explicitly provided
        if v and "user:password" in v:
            import logging
            logging.getLogger(__name__).warning(
                "DATABASE_URL appears to contain placeholder credentials. "
                "Consider using individual DB_USER, DB_PASSWORD env vars instead."
            )
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug_mode(cls, v: bool) -> bool:
        """Prevent debug mode in production environment."""
        if v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("Debug mode cannot be enabled in production")
        return v


class DatabaseConfig:
    """Database configuration with secure defaults."""

    @property
    def database_url(self) -> str:
        """Build database URL from environment variables with SSL support.

        Returns:
            PostgreSQL connection URL

        Raises:
            ValueError: If required environment variables are missing
        """
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "stock_exchange")

        if not password:
            raise ValueError(
                "DB_PASSWORD environment variable is required for secure database access"
            )

        # Use SSL in production
        environment = os.getenv("ENVIRONMENT", "development")
        ssl_mode = "?ssl=require" if environment == "production" else ""

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}{ssl_mode}"

    @property
    def pool_size(self) -> int:
        """Connection pool size based on environment.

        Returns:
            Pool size (higher for production)
        """
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            return 150  # For 1000+ concurrent users
        return 20  # Development default

    @property
    def pool_recycle(self) -> int:
        """Recycle connections after this time (seconds).

        Returns:
            Recycle time in seconds
        """
        return 3600  # 1 hour

    @property
    def max_overflow(self) -> int:
        """Maximum overflow connections.

        Returns:
            Max overflow connections
        """
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            return 50
        return 10


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
