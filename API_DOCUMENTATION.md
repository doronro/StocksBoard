# Stock Exchange Board API - Documentation

## Overview

The Stock Exchange Board API is a comprehensive backend service for a stock exchange board application. It provides real-time market data integration, portfolio management, order execution, technical analysis, and stock screening capabilities.

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy ORM
- **Caching**: Redis
- **API Documentation**: Swagger/OpenAPI (automatic)
- **Testing**: Pytest with async support
- **Deployment**: Docker and Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker and Docker Compose (optional)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd stock-exchange-board

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Update .env with your settings
nano .env
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Running Locally

```bash
# Start PostgreSQL and Redis manually, then:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py -v
```

## API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Documentation URLs
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Market Data APIs

### Get Stock Quote
```
GET /api/quotes/{symbol}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": "150.50",
  "bid": "150.45",
  "ask": "150.55",
  "change": "2.50",
  "change_percent": "1.69",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Multiple Quotes (Batch)
```
POST /api/quotes/batch
```

**Request:**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"]
}
```

**Response:**
```json
{
  "quotes": [
    { "symbol": "AAPL", "price": "150.50", ... },
    { "symbol": "GOOGL", "price": "140.20", ... },
    { "symbol": "MSFT", "price": "380.50", ... }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Market Indices
```
GET /api/indices
```

### Get Index Constituents
```
GET /api/indices/{index}/constituents?skip=0&limit=100
```

### Get Sector Performance
```
GET /api/sectors
```

### Get VIX (Volatility Index)
```
GET /api/vix
```

## Watchlist Management APIs

### Create Watchlist
```
POST /api/watchlists
```

**Request:**
```json
{
  "name": "Tech Stocks",
  "description": "My favorite tech companies",
  "is_default": false
}
```

### Get User's Watchlists
```
GET /api/watchlists?skip=0&limit=100
```

### Get Watchlist Details
```
GET /api/watchlists/{watchlist_id}
```

### Add Stock to Watchlist
```
POST /api/watchlists/{watchlist_id}/add
```

**Request:**
```json
{
  "symbol": "AAPL"
}
```

### Remove Stock from Watchlist
```
DELETE /api/watchlists/{watchlist_id}/remove/{stock_id}
```

### Update Watchlist
```
PUT /api/watchlists/{watchlist_id}
```

### Delete Watchlist
```
DELETE /api/watchlists/{watchlist_id}
```

## Portfolio Management APIs

### Get Portfolio Overview
```
GET /api/portfolio
```

**Response:**
```json
{
  "total_positions": 5,
  "total_cost": "50000.00",
  "current_value": "52500.00",
  "total_gain_loss": "2500.00",
  "total_gain_loss_percent": "5.00",
  "open_positions_count": 5,
  "closed_positions_count": 0,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Portfolio Positions
```
GET /api/portfolio/positions?skip=0&limit=100
```

### Get Portfolio Allocation
```
GET /api/portfolio/allocation
```

**Response:**
```json
{
  "total_value": "52500.00",
  "allocations": [
    {
      "sector": "Technology",
      "value": "26250.00",
      "percentage": "50.00",
      "stock_count": 2
    },
    {
      "sector": "Healthcare",
      "value": "26250.00",
      "percentage": "50.00",
      "stock_count": 1
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Portfolio Performance
```
GET /api/portfolio/performance
```

**Response:**
```json
{
  "daily_gain_loss": "125.50",
  "daily_gain_loss_percent": "0.25",
  "ytd_gain_loss": "2500.00",
  "ytd_gain_loss_percent": "5.00",
  "one_month_gain_loss_percent": "3.50",
  "three_month_gain_loss_percent": "8.50",
  "one_year_gain_loss_percent": "12.50"
}
```

### Create Position
```
POST /api/portfolio/positions
```

**Request:**
```json
{
  "symbol": "AAPL",
  "quantity": "10",
  "average_cost": "150.00"
}
```

### Update Position
```
PUT /api/portfolio/positions/{position_id}
```

### Delete Position
```
DELETE /api/portfolio/positions/{position_id}
```

## Order Management APIs

### Create Order
```
POST /api/orders
```

**Request:**
```json
{
  "symbol": "AAPL",
  "order_type": "limit",
  "side": "buy",
  "quantity": "10",
  "price": "150.00"
}
```

**Order Types:**
- `market`: Market order
- `limit`: Limit order (requires price)
- `stop`: Stop order (requires stop_price)
- `stop_limit`: Stop-limit order (requires price and stop_price)

### Get Order History
```
GET /api/orders?skip=0&limit=100
```

### Get Pending Orders
```
GET /api/orders/pending?skip=0&limit=100
```

### Get Order Details
```
GET /api/orders/{order_id}
```

### Check Order Status
```
GET /api/orders/{order_id}/status
```

### Update Order (Limit Orders Only)
```
PUT /api/orders/{order_id}
```

**Request:**
```json
{
  "price": "151.00"
}
```

### Cancel Order
```
DELETE /api/orders/{order_id}
```

## Technical Analysis & Charting APIs

### Get Candlestick Data
```
GET /api/charts/{symbol}/{timeframe}?limit=500
```

**Timeframes:** 1m, 5m, 15m, 30m, 1h, 1d

**Response:**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "timeframe": "1d",
      "open": "148.50",
      "high": "152.00",
      "low": "148.00",
      "close": "150.50",
      "volume": 52000000,
      "timestamp": "2024-01-15T00:00:00"
    }
  ],
  "symbol": "AAPL",
  "timeframe": "1d",
  "count": 100
}
```

### Get Technical Indicator
```
GET /api/indicators/{symbol}/{indicator}?period=20&timeframe=1d
```

**Indicators:** SMA, EMA, RSI, MACD, BB

**Response:**
```json
{
  "symbol": "AAPL",
  "indicator_name": "SMA",
  "period": 20,
  "timeframe": "1d",
  "value": "149.85",
  "timestamp": "2024-01-15T00:00:00"
}
```

### Get Indicator History
```
GET /api/indicators/{symbol}/{indicator}/history?period=20&timeframe=1d&limit=100
```

### Calculate Custom Indicator
```
POST /api/indicators/calculate
```

**Request:**
```json
{
  "symbol": "AAPL",
  "indicator": "RSI",
  "period": 14,
  "timeframe": "1d"
}
```

## Stock Screener APIs

### Get Pre-built Screeners
```
GET /api/screeners/prebuilt?skip=0&limit=100
```

### Create Custom Screener
```
POST /api/screeners
```

**Request:**
```json
{
  "name": "High Growth Tech",
  "description": "Tech stocks with high growth potential",
  "criteria": {
    "sectors": ["Technology"],
    "min_price": "100.00",
    "max_price": "500.00",
    "min_volume": 1000000
  },
  "is_public": false
}
```

### Get User's Screeners
```
GET /api/screeners?skip=0&limit=100
```

### Get Screener Details
```
GET /api/screeners/{screener_id}
```

### Execute Screener
```
POST /api/screeners/{screener_id}/run
```

**Response:**
```json
{
  "screener_id": 1,
  "results": [
    {
      "stock": { "symbol": "AAPL", "name": "Apple", ... },
      "matched_at": "2024-01-15T10:30:00"
    }
  ],
  "total_matches": 25,
  "executed_at": "2024-01-15T10:30:00"
}
```

### Get Screener Results
```
GET /api/screeners/{screener_id}/results?skip=0&limit=100
```

### Update Screener
```
PUT /api/screeners/{screener_id}
```

### Delete Screener
```
DELETE /api/screeners/{screener_id}
```

## User & Preferences APIs

### Register User
```
POST /api/users/register
```

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

### Get Current User
```
GET /api/users/me
```

### Get User Preferences
```
GET /api/user/preferences
```

**Response:**
```json
{
  "user_id": 1,
  "theme": "dark",
  "currency": "USD",
  "date_format": "YYYY-MM-DD",
  "time_zone": "America/New_York",
  "notifications_enabled": true,
  "price_alert_enabled": true,
  "email_notifications": false,
  "updated_at": "2024-01-15T10:30:00"
}
```

### Update User Preferences
```
PUT /api/user/preferences
```

**Request:**
```json
{
  "theme": "light",
  "currency": "EUR",
  "time_zone": "Europe/London",
  "notifications_enabled": true
}
```

### Get User Theme
```
GET /api/user/theme
```

### Set User Theme
```
POST /api/user/theme
```

**Request:**
```json
{
  "theme": "dark"
}
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Not Found",
  "message": "Stock not found: INVALID",
  "status_code": 404,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Server error

## Authentication

Currently, authentication is placeholder with `user_id=1` hardcoded. To implement proper JWT authentication:

1. Add `/api/auth/login` endpoint
2. Use `python-jose` for JWT token generation
3. Implement `get_current_user` dependency
4. Replace hardcoded `user_id` in route handlers

## Rate Limiting

The API supports rate limiting configuration via environment variables:

```
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

Endpoints return `429 Too Many Requests` when rate limit exceeded.

## Performance Considerations

### Database Optimization

- Async SQLAlchemy with connection pooling
- Indexed queries for common lookups
- Pagination on list endpoints (default 100, max 1000)

### Caching Strategy

- Redis caching for quote data (TTL: 5 minutes default)
- Historical data caching for technical indicators
- Portfolio metrics cached and revalidated on position changes

### WebSocket Support

The API is designed to support WebSocket connections for real-time quote updates:

- Quote subscription per user
- Heartbeat mechanism (30 second interval)
- Automatic reconnection handling on client side

## Development Guide

### Project Structure

```
stock-exchange-board/
├── app/
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic schemas
│   ├── config.py              # Configuration management
│   ├── database.py            # Database setup
│   ├── main.py                # FastAPI app initialization
│   ├── repositories/          # Data access layer
│   ├── services/              # Business logic layer
│   └── routes/                # API endpoint handlers
├── tests/                     # Unit and integration tests
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-container setup
└── README.md                  # Documentation
```

### Adding a New Endpoint

1. Define model in `models.py` if needed
2. Create Pydantic schema in `schemas.py`
3. Implement repository methods in `repositories/`
4. Create service class in `services/`
5. Add route handler in `routes/`
6. Write tests in `tests/`

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings to public methods
- Aim for 80%+ test coverage
- Use async/await for I/O operations

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t stock-exchange-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  --name stock-exchange-api \
  stock-exchange-api:latest
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## Monitoring & Logging

- Structured logging with Python logging module
- Log level configurable via `LOG_LEVEL` env var
- All requests and responses logged
- Error stack traces included in DEBUG mode

## Next Steps

### Phase 2 Features

- WebSocket real-time quote updates
- Authentication & authorization (JWT)
- News API integration
- Earnings calendar
- Sentiment analysis
- Advanced portfolio analytics
- Trade execution simulation
- Email notifications

### Integration with External APIs

- Market data: Alpha Vantage, Polygon.io, IEX Cloud
- News: NewsAPI, Finnhub
- Economic data: Federal Reserve API
- Currency rates: Open Exchange Rates

## Support & Contributing

For bug reports, feature requests, or contributions, please open an issue on the repository.

## License

MIT License - See LICENSE file for details.
