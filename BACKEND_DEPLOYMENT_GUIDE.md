# Backend Deployment & Testing Guide

## Quick Start Commands

### Docker Compose (Recommended)

```bash
# Start all services (database, redis, api)
docker-compose up -d

# View logs
docker-compose logs -f api

# Check service status
docker-compose ps

# Stop services
docker-compose down

# Reset database and volumes
docker-compose down -v
```

### Local Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local configuration

# Ensure PostgreSQL and Redis are running locally

# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Testing Strategy

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py -v

# Run specific test function
pytest tests/test_services.py::TestQuoteService::test_get_quote -v

# Run tests matching pattern
pytest tests/ -k "quote" -v

# Run with output capture disabled (see print statements)
pytest tests/ -s

# Run with detailed failure output
pytest tests/ -vv --tb=long
```

### Test Files Overview

| File | Purpose | Coverage |
|------|---------|----------|
| test_services.py | Service layer tests | Quote, Watchlist, Portfolio, Order services |
| test_repositories.py | Repository layer tests | Data access operations |
| test_auth.py | Authentication tests | Token generation, validation |
| test_auth_endpoints.py | Auth endpoint tests | Login, register, refresh endpoints |
| test_error_handling.py | Error handling tests | Exception handling, validation |
| test_security.py | Security tests | CORS, rate limiting, SQL injection prevention |
| test_validation.py | Input validation tests | Pydantic schema validation |
| test_audit_logging.py | Audit trail tests | Financial operation logging |

---

## API Endpoint Testing

### Using Swagger UI

1. Start backend: `docker-compose up -d` or `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Open browser: `http://localhost:8000/api/docs`
3. Authenticate:
   - Click "Authorize" button
   - Enter test credentials (if configured)
4. Test endpoints directly in UI

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get quote
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/quotes/AAPL

# Create watchlist
curl -X POST http://localhost:8000/api/watchlists \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tech Stocks", "description": "My tech watchlist"}'

# List watchlists
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/watchlists
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get quote
response = requests.get(f"{BASE_URL}/quotes/AAPL")
print(response.json())

# Get batch quotes
response = requests.post(
    f"{BASE_URL}/quotes/batch",
    json={"symbols": ["AAPL", "GOOGL", "MSFT"]}
)
print(response.json())
```

---

## Database Setup

### PostgreSQL

```bash
# Using Docker (recommended)
docker-compose up -d db

# Using local PostgreSQL
# Ensure PostgreSQL 13+ is installed and running

# Create database
createdb stock_exchange

# Create user
createuser stock_user
psql -c "ALTER USER stock_user WITH PASSWORD 'stock_password';"

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE stock_exchange TO stock_user;"
```

### Database Migrations

The application automatically creates all tables on startup:

```python
# In app/main.py
await db_manager.create_all_tables()
```

### Manual Database Inspection

```bash
# Connect to database
psql -U postgres -d stock_exchange

# List tables
\dt

# Describe table
\d stocks

# View table data
SELECT * FROM stocks LIMIT 10;
```

---

## Redis Setup

### Using Docker

```bash
# Start Redis
docker-compose up -d redis

# Test connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Using Local Redis

```bash
# Install Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu

# Start Redis
redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

---

## Environment Configuration

### .env File Template

```env
# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_NAME=Stock Exchange Board
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=development
LOG_LEVEL=INFO

# ============================================================================
# DATABASE CONFIGURATION (REQUIRED)
# ============================================================================
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_exchange
DATABASE_ECHO=False

# ============================================================================
# SECURITY (REQUIRED)
# ============================================================================
SECRET_KEY=your_32_character_random_key_here_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_PORT=6379
CACHE_TTL_SECONDS=300

# ============================================================================
# API CONFIGURATION
# ============================================================================
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization
API_PORT=8000

# ============================================================================
# RATE LIMITING
# ============================================================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# ============================================================================
# MARKET DATA PROVIDERS (OPTIONAL)
# ============================================================================
ALPHA_VANTAGE_API_KEY=
POLYGON_IO_API_KEY=
IEX_CLOUD_API_KEY=
YAHOO_FINANCE_API_KEY=

# ============================================================================
# WEBSOCKET SETTINGS (Future Phase)
# ============================================================================
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_TIMEOUT=60

# ============================================================================
# DATA UPDATE INTERVALS
# ============================================================================
QUOTE_UPDATE_INTERVAL_SECONDS=5
TECHNICAL_INDICATOR_UPDATE_INTERVAL_SECONDS=300
PORTFOLIO_REVALUATION_INTERVAL_SECONDS=60
```

---

## Performance Testing

### Load Testing with Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class StockExchangeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_quote(self):
        self.client.get("/api/quotes/AAPL")

    @task
    def list_watchlists(self):
        self.client.get(
            "/api/watchlists",
            headers={"Authorization": "Bearer <token>"}
        )

# Run: locust -f locustfile.py -u 100 -r 10 -t 5m
```

### Database Query Performance

```bash
# Enable query logging
# In .env: DATABASE_ECHO=True

# Check slow queries
psql stock_exchange -c "SELECT * FROM pg_stat_statements
  WHERE mean_time > 100
  ORDER BY mean_time DESC LIMIT 10;"
```

---

## Monitoring & Logging

### Application Logs

```bash
# View logs in Docker
docker-compose logs -f api

# View specific number of lines
docker-compose logs -f --tail=100 api

# View logs from specific time
docker-compose logs --since 10m api
```

### Structured Logging

The application logs all important events:

```
2026-03-11 10:30:45 - app.main - INFO - Starting Stock Exchange Board API
2026-03-11 10:30:46 - app.database - INFO - Database connection established
2026-03-11 10:30:47 - app.routes.quotes - INFO - GET /api/quotes/AAPL
2026-03-11 10:30:48 - app.audit - INFO - User user123 created order for MSFT
```

### Health Check

```bash
# Check API health
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "Stock Exchange Board"}

# Check with verbose output
curl -v http://localhost:8000/health
```

---

## Security Testing

### SQL Injection Prevention

```bash
# Test SQLi protection (should not work)
curl "http://localhost:8000/api/quotes/AAPL' OR '1'='1"
# Expected: 404 or validation error

# ORM prevents SQL injection automatically
# All queries use parameterized statements
```

### Authentication Testing

```bash
# Request without token (should fail)
curl http://localhost:8000/api/watchlists
# Response: {"detail": "Not authenticated"}

# Request with invalid token (should fail)
curl -H "Authorization: Bearer invalid.token.here" \
  http://localhost:8000/api/watchlists
# Response: {"detail": "Invalid token"}
```

### CORS Testing

```bash
# Test CORS headers
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:8000/api/quotes/AAPL -v
```

### Rate Limiting Testing

```bash
# Send 100+ requests rapidly
for i in {1..120}; do
  curl http://localhost:8000/health
done

# Should eventually return 429 (Too Many Requests)
```

---

## Integration Testing

### Frontend Integration

```javascript
// Example: Fetch quotes from backend
async function getStockQuote(symbol) {
  const token = localStorage.getItem('access_token');

  const response = await fetch(
    `http://localhost:8000/api/quotes/${symbol}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  return response.json();
}

// Usage
const quote = await getStockQuote('AAPL');
console.log(quote);
```

### End-to-End Workflow

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "secure_password"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "secure_password"
  }'
# Response: {"access_token": "...", "token_type": "bearer"}

# 3. Create watchlist
curl -X POST http://localhost:8000/api/watchlists \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Watchlist"}'

# 4. Add stock to watchlist
curl -X POST http://localhost:8000/api/watchlists/1/symbols \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# 5. Get watchlist with quotes
curl http://localhost:8000/api/watchlists/1 \
  -H "Authorization: Bearer <token>"
```

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Refused

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart db

# Check connection
psql -U postgres -h localhost -c "SELECT 1;"
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose ps

# Test Redis connection
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Test Failures

```bash
# Run tests with verbose output
pytest tests/ -vv

# Run with print statements
pytest tests/ -s

# Run specific test with full traceback
pytest tests/test_services.py::TestQuoteService -vv --tb=long

# Check conftest.py for test fixtures
cat tests/conftest.py
```

---

## Performance Optimization

### Database Query Optimization

```python
# Use relationships to avoid N+1 queries
watchlist = await session.get(Watchlist, 1,
    selectinload(Watchlist.items).selectinload(WatchlistItem.stock)
)

# Use indexes for frequent queries
# Already configured in models (see models.py)

# Cache frequently accessed data
# Redis cache layer configured in services
```

### API Response Optimization

```bash
# Enable GZIP compression
# Already configured in main.py

# Check response size
curl -H "Accept-Encoding: gzip" -w "%{size_download}" \
  http://localhost:8000/api/watchlists

# Monitor response times
curl -w "@curl-format.txt" http://localhost:8000/api/quotes/AAPL
```

### Database Indexing

Current indexes (see models.py):
- Stock symbol (unique)
- User email (unique)
- Quote timestamp per stock
- Order user + status
- Position user + stock
- Watchlist stock
- Audit logs (multi-field)

---

## Backup & Recovery

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U postgres stock_exchange > backup.sql

# Restore from backup
docker-compose exec -T db psql -U postgres stock_exchange < backup.sql
```

### Redis Backup

```bash
# Redis automatically saves to disk
# Backup Redis dump
docker cp stock-exchange-redis:/data/dump.rdb ./redis-backup.rdb

# Restore Redis dump
docker cp ./redis-backup.rdb stock-exchange-redis:/data/dump.rdb
docker-compose restart redis
```

---

## Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Configure all required environment variables
- [ ] Generate strong SECRET_KEY
- [ ] Generate strong database password
- [ ] Configure ALLOWED_ORIGINS for production domain
- [ ] Set DEBUG=False for production
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Check test coverage: `pytest tests/ --cov=app`
- [ ] Run security checks (CORS, authentication, SQL injection)
- [ ] Test all API endpoints
- [ ] Test database connectivity
- [ ] Test Redis connectivity
- [ ] Review logs for errors
- [ ] Set up monitoring and alerts
- [ ] Configure backups
- [ ] Document any custom configurations
- [ ] Create runbooks for common issues

---

## Summary

The Phase 1 backend is fully functional and ready for deployment with:

✅ Docker Compose setup for easy deployment
✅ Comprehensive test suite
✅ API endpoint testing via Swagger UI
✅ Database and cache configuration
✅ Security and performance optimizations
✅ Monitoring and logging infrastructure
✅ Troubleshooting guides
✅ Deployment checklist

**Status: Ready for Production** 🚀

For more information, see:
- README_BACKEND.md - Backend overview
- PHASE1_BACKEND_COMPLETE.md - Comprehensive technical guide
- API_DOCUMENTATION.md - API reference
