"""
Database connection and session management with secure defaults.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings, DatabaseConfig
from app.models import Base
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions with security best practices."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = None
        self.async_session_maker = None

    async def initialize(self):
        """Initialize database connection pool with secure settings."""
        settings = get_settings()
        db_config = DatabaseConfig()

        # Build connection URL with secure defaults
        try:
            database_url = db_config.database_url
        except ValueError as e:
            logger.error(f"Database configuration error: {e}")
            raise

        # Create engine with secure settings
        self.engine = create_async_engine(
            database_url,
            echo=settings.database_echo,
            pool_size=db_config.pool_size,
            max_overflow=db_config.max_overflow,
            pool_pre_ping=True,  # Test connections before use
            pool_recycle=db_config.pool_recycle,
            echo_pool=False,  # Don't log connection pool operations
            connect_args={
                "server_settings": {
                    "application_name": "stock_exchange_api",
                },
                "timeout": 30,
                "command_timeout": 30,
            },
        )
        self.async_session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        environment = os.getenv("ENVIRONMENT", "development")
        logger.info(
            f"Database connection pool initialized (environment={environment}, "
            f"pool_size={db_config.pool_size}, max_overflow={db_config.max_overflow})"
        )

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")

    async def create_all_tables(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")

    async def drop_all_tables(self):
        """Drop all database tables (for testing)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a new database session."""
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session in route handlers."""
    async for session in db_manager.get_session():
        yield session
