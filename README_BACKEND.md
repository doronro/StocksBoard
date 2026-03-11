# Stock Exchange Board Backend

A comprehensive backend API for a stock exchange board application providing real-time market data, portfolio management, order execution, technical analysis, and stock screening capabilities.

## Features

### Phase 1 MVP Implementation

- **Market Data APIs**: Real-time quotes, batch requests, indices, sectors, VIX
- **Watchlist Management**: Create, manage, and track stocks of interest
- **Portfolio Management**: Track positions, calculate P&L, allocations
- **Order Management**: Create, update, cancel various order types
- **Technical Analysis**: OHLC data, technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Stock Screeners**: Pre-built and custom stock screening with rule-based filtering
- **User Preferences**: Theme, language, notification settings
- **Performance Metrics**: Portfolio performance tracking

### Architecture Highlights

- **Async/Await**: Full async support with SQLAlchemy
- **Repository Pattern**: Data access layer abstraction
- **Service Layer**: Centralized business logic
- **RESTful APIs**: Clean, intuitive API design
- **Type Safety**: Full Python type hints
- **Comprehensive Testing**: Unit and integration tests
- **Docker Ready**: Containerized deployment

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (async)
- **Caching**: Redis
- **Testing**: Pytest
- **API Docs**: Swagger/OpenAPI
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Docker and Docker Compose (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd stock-exchange-board

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Running with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access API
# Swagger UI: http://localhost:8000/api/docs
# API: http://localhost:8000

# Stop services
docker-compose down
```

### Running Locally

```bash
# Ensure PostgreSQL and Redis are running

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/stock_exchange"
export REDIS_URL="redis://localhost:6379/0"

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py -v
```

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for comprehensive API documentation.

## Key Directories

- **app/**: Main application code
- **app/models.py**: SQLAlchemy ORM models (13 models for full stock exchange functionality)
- **app/schemas.py**: Pydantic validation schemas
- **app/repositories/**: Data access layer with 9 specialized repositories
- **app/services/**: Business logic layer with 7 service classes
- **app/routes/**: FastAPI route handlers (7 route modules)
- **app/database.py**: Database connection and session management
- **app/config.py**: Configuration management
- **tests/**: Unit and integration tests with fixtures

## Project Structure

```
app/
├── models.py              # 13 ORM Models: User, Stock, Quote, Watchlist, Position, Order, etc.
├── schemas.py             # Pydantic schemas for validation
├── config.py              # Configuration from environment
├── database.py            # Async SQLAlchemy setup
├── main.py                # FastAPI app initialization
├── repositories/          # Data access layer (9 repos)
│   ├── base_repository.py
│   ├── stock_repository.py
│   ├── quote_repository.py
│   ├── watchlist_repository.py
│   ├── position_repository.py
│   ├── order_repository.py
│   ├── user_repository.py
│   ├── ohlc_repository.py
│   ├── indicator_repository.py
│   └── screener_repository.py
├── services/              # Business logic (7 services)
│   ├── quote_service.py
│   ├── watchlist_service.py
│   ├── portfolio_service.py
│   ├── order_service.py
│   ├── indicator_service.py
│   ├── screener_service.py
│   └── user_service.py
└── routes/                # API endpoints (7 routers)
    ├── quotes.py
    ├── watchlists.py
    ├── portfolio.py
    ├── orders.py
    ├── indicators.py
    ├── screeners.py
    └── users.py
```

## File Locations

All backend code is located at:
`/app/storage/tenants/ffed0886-4301-4aa9-b06a-85b553941fcf/projects/20c33ca0-7acd-47ca-a3bf-d0b7846ee12c/`

Key files:
- **app/main.py**: FastAPI application
- **app/models.py**: Database models
- **app/schemas.py**: Request/response schemas
- **requirements.txt**: Python dependencies
- **docker-compose.yml**: Multi-container setup
- **pytest.ini**: Test configuration
- **.env.example**: Configuration template

## Next Steps

1. **Set up environment**: Copy `.env.example` to `.env` and configure
2. **Run tests**: `pytest tests/ -v` to verify setup
3. **Start development**: `docker-compose up -d` or run locally
4. **Access API**: Open http://localhost:8000/api/docs for Swagger UI
5. **Integrate frontend**: Connect frontend to backend APIs

## Implementation Summary

Implemented 8 core API categories:

1. **Market Data** (6 endpoints) - Real-time quotes and market indices
2. **Watchlist Management** (7 endpoints) - Create and manage watchlists
3. **Portfolio Management** (7 endpoints) - Track positions and performance
4. **Order Management** (7 endpoints) - Create and execute orders
5. **Technical Analysis** (4 endpoints) - OHLC data and indicators
6. **Stock Screeners** (7 endpoints) - Custom and pre-built screeners
7. **User Management** (6 endpoints) - User accounts and preferences
8. **Additional** - Health checks, API docs, error handling

Total: 44+ API endpoints with full CRUD operations, proper error handling, and comprehensive testing.

## Database Models

13 SQLAlchemy ORM models with relationships:

1. **User** - User accounts with preferences
2. **Stock** - Stock metadata and symbols
3. **Quote** - Real-time price data
4. **Watchlist** - User watchlist collections
5. **WatchlistItem** - Stocks in watchlist
6. **Position** - Portfolio holdings
7. **Order** - Buy/sell orders with status tracking
8. **OHLCData** - Candlestick data
9. **TechnicalIndicator** - Calculated indicators
10. **Screener** - Stock screening rules
11. **ScreenerResult** - Screening results
12. **MarketIndex** - Index definitions
13. **IndexQuote** - Index prices
14. **UserPreference** - User settings

## Ready for Production

The backend implementation includes:

- Full async/await support
- Comprehensive error handling
- Input validation and sanitization
- Type hints throughout
- Unit tests with fixtures
- Docker containerization
- API documentation (Swagger)
- Rate limiting configuration
- CORS support
- Database connection pooling

## For Deployment

See deployment section in API_DOCUMENTATION.md for production deployment instructions.
