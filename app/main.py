"""Main FastAPI application."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from pydantic import ValidationError
import logging

from app.config import get_settings
from app.database import db_manager
from app.rate_limit import limiter
from app.exceptions import SafeHTTPException
from app.routes import (
    quotes,
    watchlists,
    portfolio,
    orders,
    indicators,
    screeners,
    users,
    risk,
    alerts,
    compliance,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log financial operations and API requests."""

    async def dispatch(self, request: Request, call_next):
        """Log request details for audit trail and debugging.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            The response
        """
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log financial operations (POST, PUT, DELETE on /api/ endpoints)
        if request.method in ["POST", "PUT", "DELETE"] and "/api/" in request.url.path:
            logger.info(
                f"API Request: {request.method} {request.url.path} from {client_ip} "
                f"user_agent={user_agent[:100]}"
            )

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting Stock Exchange Board API")
    await db_manager.initialize()
    await db_manager.create_all_tables()
    yield
    # Shutdown
    logger.info("Shutting down Stock Exchange Board API")
    await db_manager.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    # Never enable debug in production
    is_production = os.getenv("ENVIRONMENT") == "production"
    debug_mode = False if is_production else settings.debug

    app = FastAPI(
        title=settings.app_name,
        description="Stock Exchange Board API with comprehensive market data integration",
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        debug=debug_mode,
    )

    # Request Logging Middleware (for audit trail)
    app.add_middleware(RequestLoggingMiddleware)

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS Middleware with explicit headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    # Rate Limiting Middleware
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter

    # GZIP Compression
    app.add_middleware(GZIPMiddleware, minimum_size=1000)

    # Include routers
    app.include_router(quotes.router, prefix="/api", tags=["Market Data"])
    app.include_router(watchlists.router, prefix="/api", tags=["Watchlist"])
    app.include_router(portfolio.router, prefix="/api", tags=["Portfolio"])
    app.include_router(orders.router, prefix="/api", tags=["Orders"])
    app.include_router(indicators.router, prefix="/api", tags=["Technical Analysis"])
    app.include_router(screeners.router, prefix="/api", tags=["Stock Screener"])
    app.include_router(users.router, prefix="/api", tags=["Users"])
    app.include_router(risk.router, prefix="/api", tags=["Risk Management"])
    app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
    app.include_router(compliance.router, prefix="/api", tags=["Compliance"])

    # Root endpoint
    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/api/docs",
        }

    # Health check endpoint
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name,
        }

    # Exception handler for safe HTTP exceptions
    @app.exception_handler(SafeHTTPException)
    async def safe_http_exception_handler(request: Request, exc: SafeHTTPException):
        """Handle SafeHTTPException with safe error messages.

        Args:
            request: The incoming request
            exc: The SafeHTTPException

        Returns:
            JSON response with safe error details
        """
        exc.log()
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status": exc.status_code}
        )

    # Exception handler for Pydantic validation errors
    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors with safe messages.

        Args:
            request: The incoming request
            exc: The ValidationError

        Returns:
            JSON response with safe validation error message
        """
        # Log detailed error internally
        logger.error(f"Validation error: {exc.json()}", exc_info=False)

        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request data", "status": 400}
        )

    # Exception handler for value errors
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError with safe messages.

        Args:
            request: The incoming request
            exc: The ValueError

        Returns:
            JSON response with safe error message
        """
        logger.error(f"Value error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request", "status": 400}
        )

    # Global exception handler for unhandled exceptions
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unhandled exceptions with generic response in production.

        Logs the full exception internally while returning only a generic
        message to the client to prevent information disclosure.

        Args:
            request: The incoming request
            exc: The Exception

        Returns:
            JSON response with generic error message
        """
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "status": 500}
        )

    return app


# Create app instance
app = create_app()
