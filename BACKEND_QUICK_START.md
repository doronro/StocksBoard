# Backend Quick Start Guide

Quick reference for developers working on the Stock Exchange Board backend.

---

## Setup (5 minutes)

### 1. Install Dependencies
```bash
cd /path/to/project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Create .env file with database URL
echo "DATABASE_URL=postgresql://user:password@localhost:5432/stock_exchange" > .env

# Run migrations
alembic upgrade head

# Verify database connection
psql -U user -d stock_exchange -c "SELECT version();"
```

### 3. Run Application
```bash
# Development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. View API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

---

## Common Tasks

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_portfolio_service.py

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_portfolio_service.py::TestPortfolioService::test_create_position_valid

# Watch mode (auto-rerun on changes)
pytest-watch tests/
```

### Database Migrations

```bash
# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

### Code Quality

```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/

# All checks
black app/ tests/ && flake8 app/ tests/ && mypy app/
```

---

## API Endpoints Quick Reference

### Risk Management
```bash
# Get portfolio metrics (Sharpe, Beta, Max Drawdown)
curl -X GET http://localhost:8000/api/risk/portfolio/metrics \
  -H "Authorization: Bearer $TOKEN"

# Calculate position size
curl -X POST http://localhost:8000/api/risk/position-sizing \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_size": 50000,
    "risk_percent": 2,
    "entry_price": 100,
    "stop_price": 95
  }'

# Get tax loss harvesting opportunities
curl -X GET http://localhost:8000/api/risk/tax-loss-harvesting \
  -H "Authorization: Bearer $TOKEN"
```

### Alerts
```bash
# Create price alert
curl -X POST http://localhost:8000/api/alerts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "alert_type": "price_above",
    "threshold_value": 150
  }'

# Get all alerts
curl -X GET http://localhost:8000/api/alerts \
  -H "Authorization: Bearer $TOKEN"

# Check technical alerts
curl -X GET "http://localhost:8000/api/alerts/technical/AAPL?rsi=75" \
  -H "Authorization: Bearer $TOKEN"
```

### Compliance
```bash
# Check overall compliance status
curl -X GET http://localhost:8000/api/compliance/status \
  -H "Authorization: Bearer $TOKEN"

# Check PDT status
curl -X GET http://localhost:8000/api/compliance/pdt-status \
  -H "Authorization: Bearer $TOKEN"

# Validate order before submission
curl -X POST http://localhost:8000/api/compliance/validate-order \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 100,
    "side": "buy"
  }'

# Detect wash sales
curl -X GET http://localhost:8000/api/compliance/wash-sales \
  -H "Authorization: Bearer $TOKEN"
```

### Portfolio
```bash
# Get portfolio overview
curl -X GET http://localhost:8000/api/portfolio \
  -H "Authorization: Bearer $TOKEN"

# Get all positions
curl -X GET http://localhost:8000/api/portfolio/positions \
  -H "Authorization: Bearer $TOKEN"

# Get sector allocation
curl -X GET http://localhost:8000/api/portfolio/allocation \
  -H "Authorization: Bearer $TOKEN"
```

### Orders
```bash
# Submit market order
curl -X POST http://localhost:8000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 100,
    "order_type": "market",
    "side": "buy"
  }'

# Get order history
curl -X GET http://localhost:8000/api/orders \
  -H "Authorization: Bearer $TOKEN"

# Cancel order
curl -X PUT http://localhost:8000/api/orders/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

---

## Service Reference

### RiskManagementService

**File**: `app/services/risk_management_service.py`

```python
from app.services.risk_management_service import RiskManagementService

service = RiskManagementService(session)

# Portfolio metrics
sharpe = await service.calculate_sharpe_ratio(user_id)
beta = await service.calculate_portfolio_beta(user_id)
drawdown = await service.calculate_max_drawdown(user_id)

# Position sizing
sizing = await service.calculate_position_sizing(
    account_size=50000,
    risk_percent=2,
    entry_price=100,
    stop_price=95
)

# Risk analysis
var = await service.calculate_value_at_risk(user_id, confidence_level=0.95)
concentration = await service.calculate_concentration_risk(user_id)
```

### AlertService

**File**: `app/services/alert_service.py`

```python
from app.services.alert_service import AlertService, AlertType

service = AlertService(session)

# Create alert
alert = await service.create_alert(
    user_id=1,
    symbol="AAPL",
    alert_type=AlertType.PRICE_ABOVE,
    threshold_value=150
)

# Evaluate alert
triggered = await service.evaluate_price_alert(
    symbol="AAPL",
    current_price=155,
    alert_type=AlertType.PRICE_ABOVE,
    threshold=150
)

# Technical alerts
tech_alerts = await service.check_technical_alerts(
    symbol="AAPL",
    rsi=75
)
```

### ComplianceService

**File**: `app/services/compliance_service.py`

```python
from app.services.compliance_service import ComplianceService

service = ComplianceService(session)

# PDT compliance
pdt = await service.check_pattern_day_trader(user_id)

# Wash sales
wash_sales = await service.detect_wash_sales(user_id)

# Margin check
margin = await service.check_margin_requirements(user_id)

# Order validation
validation = await service.validate_order_compliance(
    user_id=1,
    order_symbol="AAPL",
    order_quantity=100,
    order_side="buy"
)

# Compliance report
report = await service.generate_compliance_report(user_id)
```

---

## Database Schemas

### User
```python
User(
    id: int,
    username: str,
    email: str,
    hashed_password: str,
    is_active: bool = True,
    created_at: datetime,
    updated_at: datetime
)
```

### Stock
```python
Stock(
    id: int,
    symbol: str,  # Unique
    name: str,
    sector: str,
    industry: str,
    exchange: str = "NASDAQ"
)
```

### Position
```python
Position(
    id: int,
    user_id: int,  # FK
    stock_id: int,  # FK
    quantity: Decimal,
    average_cost: Decimal,
    current_price: Decimal,
    current_value: Decimal,
    unrealized_gain_loss: Decimal,
    status: PositionStatus,
    opened_at: datetime,
    closed_at: datetime
)
```

### Order
```python
Order(
    id: int,
    user_id: int,  # FK
    stock_id: int,  # FK
    order_type: OrderType,  # market/limit/stop
    side: OrderSide,  # buy/sell
    quantity: Decimal,
    price: Decimal,  # For limit/stop
    status: OrderStatus,
    created_at: datetime,
    filled_at: datetime
)
```

---

## Environment Variables

### Required
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/stock_exchange
SECRET_KEY=your-secret-key-here
```

### Optional (with defaults)
```bash
DEBUG=False
ENVIRONMENT=production
APP_NAME="Stock Exchange Board"
APP_VERSION="2.0.0"
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Query Logging
```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

### Test a Service Directly
```bash
python
>>> import asyncio
>>> from app.services.risk_management_service import RiskManagementService
>>> from app.database import db_manager
>>> session = db_manager.get_session()
>>> service = RiskManagementService(session)
>>> asyncio.run(service.calculate_sharpe_ratio(1))
```

### Check Database State
```bash
psql -U user -d stock_exchange

# List tables
\dt

# Query positions
SELECT id, symbol, quantity, current_value FROM positions WHERE user_id = 1;

# Check orders
SELECT id, symbol, order_type, status FROM orders WHERE user_id = 1;
```

---

## Common Errors & Fixes

### "Database connection refused"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Or with Docker
docker ps | grep postgres

# Verify connection string
echo $DATABASE_URL
```

### "No such table: positions"
```bash
# Run migrations
alembic upgrade head

# Check migration status
alembic current
```

### "Import error: No module named 'app'"
```bash
# Make sure you're in project root
cd /path/to/project

# And venv is activated
source venv/bin/activate
```

### "JWT token invalid"
```bash
# Get fresh token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in requests
export TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" ...
```

---

## File Structure

```
app/
├── main.py                 # FastAPI app entry point
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic validation schemas
├── config.py              # Settings/configuration
├── database.py            # Database connection/session
├── auth.py               # Authentication logic
├── exceptions.py         # Custom exceptions
├── routes/               # API route handlers
│   ├── portfolio.py
│   ├── orders.py
│   ├── quotes.py
│   ├── risk.py          # NEW: Risk management endpoints
│   ├── alerts.py        # NEW: Alert endpoints
│   └── compliance.py    # NEW: Compliance endpoints
├── services/            # Business logic
│   ├── portfolio_service.py
│   ├── order_service.py
│   ├── quote_service.py
│   ├── risk_management_service.py  # NEW
│   ├── alert_service.py             # NEW
│   └── compliance_service.py         # NEW
└── repositories/        # Data access layer
    ├── position_repository.py
    ├── order_repository.py
    └── ...

tests/
├── test_portfolio_service.py
├── test_order_service.py
├── test_risk_management_service.py   # NEW
├── test_alert_service.py             # NEW
├── test_compliance_service.py        # NEW
└── conftest.py          # Shared fixtures
```

---

## Performance Tips

### Optimize Database Queries
```python
# Use select() with specific columns
from sqlalchemy import select
query = select(Position.id, Position.quantity, Position.current_value)

# Lazy load relationships only when needed
position = session.query(Position).options(joinedload(Position.stock))

# Batch queries
positions = await position_repo.get_user_positions(user_id, limit=100)
```

### Use Caching
```python
# Cache portfolio overview (5 sec TTL)
redis.set(f"portfolio:{user_id}", json.dumps(overview), ex=5)

# Cache quotes (30 sec TTL)
redis.set(f"quote:{symbol}", json.dumps(quote), ex=30)
```

### Async Operations
```python
# Don't block I/O
positions = await position_service.get_user_positions(user_id)

# Parallel requests
tasks = [
    service.calculate_sharpe_ratio(user_id),
    service.calculate_portfolio_beta(user_id),
    service.calculate_max_drawdown(user_id)
]
results = await asyncio.gather(*tasks)
```

---

## Useful Commands

```bash
# Start dev server with auto-reload
uvicorn app.main:app --reload

# Run tests with coverage
pytest --cov=app --cov-report=html tests/

# Format code
black app/ tests/

# Check types
mypy app/

# Generate DB migration
alembic revision --autogenerate -m "Description"

# Create superuser (if implemented)
python -m app.create_user --admin

# Database backup
pg_dump stock_exchange > backup.sql

# Database restore
psql stock_exchange < backup.sql

# Check API status
curl http://localhost:8000/health
```

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic](https://docs.pydantic.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Pytest](https://docs.pytest.org/)

---

## Getting Help

1. Check logs: `grep -i error app.log`
2. Review tests: Look at `tests/test_*.py` for usage examples
3. Check docstrings: `python -c "from app.services import RiskManagementService; help(RiskManagementService)"`
4. API docs: Visit `/api/docs` in browser
5. Ask in Slack: #backend-dev channel

---

**Last Updated**: March 11, 2026
**Version**: 2.0
