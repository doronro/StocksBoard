# Developer Quick Reference

A quick lookup guide for common development tasks.

---

## Starting Development

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Local Development

```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest tests/ -v
```

---

## API Endpoints Quick Reference

| Category | Method | Endpoint | Purpose |
|----------|--------|----------|---------|
| **Quotes** | GET | /api/quotes/{symbol} | Get single quote |
| | POST | /api/quotes/batch | Get multiple quotes |
| | GET | /api/indices | Get market indices |
| **Watchlist** | GET | /api/watchlists | List watchlists |
| | POST | /api/watchlists | Create watchlist |
| | POST | /api/watchlists/{id}/symbols | Add stock |
| | DELETE | /api/watchlists/{id}/symbols/{symbol} | Remove stock |
| **Portfolio** | GET | /api/portfolio | Get summary |
| | GET | /api/portfolio/positions | Get holdings |
| | GET | /api/portfolio/performance | Get P&L |
| **Orders** | GET | /api/orders | List orders |
| | POST | /api/orders | Create order |
| | DELETE | /api/orders/{id} | Cancel order |
| **Indicators** | GET | /api/candles/{symbol} | Get OHLC data |
| | GET | /api/indicators/{symbol} | Get indicators |
| **Users** | POST | /api/users | Register |
| | POST | /api/users/login | Login |
| | GET | /api/users/me | Get profile |

---

## Code Locations

### Core Files
```
app/main.py                 # FastAPI app
app/models.py              # Database models
app/database.py            # Database setup
app/config.py              # Configuration
app/auth.py                # Authentication
```

### API Routes
```
app/routes/quotes.py       # Market data endpoints
app/routes/watchlists.py   # Watchlist endpoints
app/routes/portfolio.py    # Portfolio endpoints
app/routes/orders.py       # Order endpoints
app/routes/indicators.py   # Technical analysis endpoints
app/routes/users.py        # User endpoints
app/routes/screeners.py    # Screener endpoints
```

### Services (Business Logic)
```
app/services/quote_service.py
app/services/watchlist_service.py
app/services/portfolio_service.py
app/services/order_service.py
app/services/indicator_service.py
app/services/user_service.py
app/services/screener_service.py
```

### Repositories (Data Access)
```
app/repositories/stock_repository.py
app/repositories/quote_repository.py
app/repositories/watchlist_repository.py
app/repositories/position_repository.py
app/repositories/order_repository.py
app/repositories/user_repository.py
app/repositories/ohlc_repository.py
app/repositories/indicator_repository.py
app/repositories/screener_repository.py
```

### Tests
```
tests/test_services.py
tests/test_repositories.py
tests/test_auth.py
tests/test_error_handling.py
tests/test_security.py
tests/test_validation.py
```

---

## Common Commands

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test
pytest tests/test_services.py::TestQuoteService -v

# With output
pytest tests/ -s -v
```

### Database Operations

```bash
# Connect to database
psql -U postgres -d stock_exchange

# List tables
\dt

# Describe table
\d stocks

# View data
SELECT * FROM stocks LIMIT 10;
```

### Redis Operations

```bash
# Test connection
redis-cli ping

# View keys
redis-cli KEYS "*"

# View cache value
redis-cli GET "quote:AAPL"

# Clear cache
redis-cli FLUSHALL
```

### Docker Operations

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Execute command
docker-compose exec api pytest tests/ -v

# Rebuild
docker-compose build

# Clean up
docker-compose down -v
```

---

## Environment Variables

### Critical (Must Change)
```
DB_PASSWORD=your_secure_password
SECRET_KEY=32_character_random_key
```

### Important (Configure for Environment)
```
ENVIRONMENT=development|production
DEBUG=True|False
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000
```

### Optional (Default Values Work)
```
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_exchange
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_ENABLED=True
```

---

## API Authentication

### Get Token
```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Use Token
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/quotes/AAPL
```

### Python Example
```python
import requests

# Login
response = requests.post(
  'http://localhost:8000/api/users/login',
  json={'username': 'user', 'password': 'pass'}
)
token = response.json()['access_token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
  'http://localhost:8000/api/quotes/AAPL',
  headers=headers
)
```

---

## Database Models Quick Lookup

| Model | Purpose | Key Fields |
|-------|---------|------------|
| User | User accounts | id, username, email, hashed_password |
| Stock | Stock metadata | id, symbol, name, sector |
| Quote | Real-time prices | id, stock_id, price, bid, ask |
| Watchlist | Stock lists | id, user_id, name |
| WatchlistItem | Stocks in list | watchlist_id, stock_id |
| Position | Portfolio holdings | id, user_id, stock_id, quantity |
| Order | Buy/sell orders | id, user_id, symbol, quantity, status |
| OHLCData | Candlestick data | stock_id, timeframe, open, high, low, close |
| TechnicalIndicator | Indicators | stock_id, indicator_name, value |
| Screener | Screening rules | id, user_id, criteria |
| ScreenerResult | Screen matches | screener_id, stock_id |
| MarketIndex | Index definitions | symbol, name |
| IndexQuote | Index prices | index_id, price |
| UserPreference | User settings | user_id, theme, currency |
| AuditLog | Operation logs | user_id, action, resource_type |

---

## Adding a New Feature

### Step 1: Create Model (app/models.py)
```python
class MyModel(Base):
    __tablename__ = "my_models"
    id = Column(Integer, primary_key=True)
    # Add fields
```

### Step 2: Create Schema (app/schemas.py)
```python
from pydantic import BaseModel

class MyModelResponse(BaseModel):
    id: int
    # Add fields
```

### Step 3: Create Repository (app/repositories/my_repository.py)
```python
from app.repositories import BaseRepository
from app.models import MyModel

class MyModelRepository(BaseRepository):
    async def get_my_models(self):
        # Implement query
```

### Step 4: Create Service (app/services/my_service.py)
```python
from app.repositories import MyModelRepository

class MyService:
    def __init__(self, session):
        self.repo = MyModelRepository(session)

    async def get_models(self):
        # Implement logic
```

### Step 5: Create Routes (app/routes/my_routes.py)
```python
from fastapi import APIRouter
from app.services import MyService

router = APIRouter()

@router.get("/my-models")
async def get_models(session = Depends(get_db)):
    service = MyService(session)
    return await service.get_models()
```

### Step 6: Register Route (app/main.py)
```python
from app.routes import my_routes
app.include_router(my_routes.router, prefix="/api")
```

### Step 7: Write Tests (tests/test_my_feature.py)
```python
import pytest
from app.services import MyService

@pytest.mark.asyncio
async def test_get_models():
    # Setup
    # Act
    # Assert
```

---

## Error Handling

### Common Error Codes
```
400 - Bad Request (validation error)
401 - Unauthorized (missing/invalid token)
403 - Forbidden (no permission)
404 - Not Found (resource not found)
429 - Too Many Requests (rate limited)
500 - Internal Server Error
```

### Custom Exception
```python
from app.exceptions import SafeHTTPException

raise SafeHTTPException(
    status_code=400,
    detail="Invalid input"
)
```

---

## Testing Patterns

### Test Service
```python
@pytest.mark.asyncio
async def test_quote_service():
    # Setup
    session = AsyncSession()
    service = QuoteService(session)

    # Act
    result = await service.get_quote("AAPL")

    # Assert
    assert result is not None
    assert result.symbol == "AAPL"
```

### Test Endpoint
```python
@pytest.mark.asyncio
async def test_quote_endpoint(client):
    response = client.get("/api/quotes/AAPL")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
```

---

## Debugging

### Enable Query Logging
```env
DATABASE_ECHO=True
```

### Print Statements
```bash
pytest tests/ -s
```

### Verbose Output
```bash
pytest tests/ -vv --tb=long
```

### Browser DevTools
1. Open http://localhost:8000/api/docs
2. Try requests in Swagger UI
3. Check Network tab in browser

---

## Performance Tips

### 1. Use Database Indexes
```python
__table_args__ = (
    Index("idx_user_email", "email"),
)
```

### 2. Use Relationships Efficiently
```python
# Bad: N+1 query
for user in users:
    watchlists = user.watchlists

# Good: Use selectinload
selectinload(User.watchlists)
```

### 3. Use Redis Caching
```python
# Cache key
cache_key = f"quote:{symbol}"
cached = await redis.get(cache_key)
```

### 4. Use Batch Operations
```python
# Add symbols one by one = slow
# Use batch = fast
await session.execute(insert(Quote).values(quotes))
```

---

## Security Checklist

- [ ] All routes require authentication (except login/register)
- [ ] All inputs validated with Pydantic
- [ ] All passwords hashed with bcrypt
- [ ] CORS configured with specific origins
- [ ] Rate limiting enabled
- [ ] SQL injection prevented (ORM usage)
- [ ] CSRF protection in place
- [ ] Security headers set
- [ ] Audit logging enabled
- [ ] Sensitive data not logged

---

## Documentation Access

| Topic | File |
|-------|------|
| Complete Technical Guide | PHASE1_BACKEND_COMPLETE.md |
| Deployment & Testing | BACKEND_DEPLOYMENT_GUIDE.md |
| Frontend Integration | BACKEND_API_INTEGRATION_GUIDE.md |
| API Reference | API_DOCUMENTATION.md |
| Executive Summary | BACKEND_PHASE1_SUMMARY.md |
| Quick Start | README_BACKEND.md |
| This Quick Reference | DEVELOPER_QUICK_REFERENCE.md |

---

## Getting Help

1. **Check Documentation** - Start with the guides above
2. **Search Code** - Look for similar implementations
3. **Read Tests** - Tests show expected behavior
4. **Check Logs** - Enable query logging and verbose output
5. **Ask Team** - Contact backend development team

---

**Happy Coding! 🚀**
