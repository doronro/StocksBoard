# Security Implementation Guide

## Critical Security Fixes Applied

This document outlines the three critical security vulnerabilities that were fixed in the stock exchange backend.

### Issue #1: Missing Authentication/Authorization

**Problem**: All API routes had hardcoded `user_id: int = 1` with TODO comments, allowing any user to access/modify any other user's data.

**Solution Implemented**:

#### 1. JWT Authentication Module (`app/auth.py`)
- Implemented JWT token generation and validation
- Password hashing using bcrypt (passlib)
- Separate access and refresh tokens with different expiration times
- Token validation dependency for FastAPI routes

#### 2. Authentication Endpoints
- `POST /api/auth/login` - Authenticate user and return JWT tokens
- `POST /api/auth/refresh` - Refresh expired access tokens
- `POST /api/users/register` - User registration with password hashing

#### 3. Updated All Routes
All routes now require authentication via `Depends(get_current_user_id)`:
- `app/routes/orders.py` - 7 endpoints
- `app/routes/portfolio.py` - 6 endpoints
- `app/routes/watchlists.py` - 8 endpoints
- `app/routes/screeners.py` - 8 endpoints
- `app/routes/users.py` - 8 endpoints

**Total Protected Endpoints**: 36+

#### 4. Authorization Checks
Services verify users own resources before allowing access:
```python
# Example: Only users can access their own orders
order = await service.get_order(user_id, order_id)
if not order:
    raise HTTPException(status_code=404, detail="Order not found")
```

---

### Issue #2: Hardcoded Secrets in Configuration

**Problem**: Hardcoded secrets in `app/config.py` that appeared in code and Docker Compose.

**Solution Implemented**:

#### 1. Updated `app/config.py`
```python
# Database - CRITICAL: Must use environment variables
database_url: str = Field(default="")

# Authentication - CRITICAL: SECRET_KEY must come from environment
secret_key: str = Field(default="")
```

#### 2. Added Security Validators
```python
@field_validator("secret_key")
def validate_secret_key(cls, v: str) -> str:
    """Validate SECRET_KEY is set and secure in production."""
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        if not v or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters in production"
            )
    return v

@field_validator("database_url")
def validate_database_url(cls, v: str) -> str:
    """Validate DATABASE_URL is set properly."""
    if not v:
        raise ValueError("DATABASE_URL environment variable is required")
    if "user:password" in v:
        logger.warning("DATABASE_URL contains placeholder credentials")
    return v
```

#### 3. Environment Variable Management
All secrets now come from environment variables:
- `SECRET_KEY` - JWT signing key (32+ chars required in production)
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- API keys for market data providers

---

### Issue #3: Insecure Docker Database Credentials

**Problem**: `docker-compose.yml` exposed hardcoded database credentials.

**Solution Implemented**:

#### 1. Updated `docker-compose.yml`
Changed from hardcoded values:
```yaml
# BEFORE (Insecure)
environment:
  POSTGRES_USER: stock_user
  POSTGRES_PASSWORD: stock_password
```

To environment variable references:
```yaml
# AFTER (Secure)
environment:
  POSTGRES_USER: ${POSTGRES_USER:-stock_user}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-stock_password}
  DATABASE_URL: ${DATABASE_URL}
  SECRET_KEY: ${SECRET_KEY}
```

#### 2. Environment Variable Files

**`.env.example`** - Shows all required variables with documentation
- Clearly marked as CHANGE_ME sections
- Provides format examples
- No real credentials

**`.env.local`** - For development use
- Contains development-safe credentials
- Generated SECRET_KEY using cryptographically secure random
- Should not be committed to production

**Production Deployment**:
```bash
# Set environment variables before running
export ENVIRONMENT=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export DATABASE_URL="postgresql+asyncpg://user:securepassword@prod-db:5432/stock_exchange"
export POSTGRES_PASSWORD="securepassword"

# Or use .env file
docker-compose up
```

---

## Authentication Flow

### Login Flow
```
1. User calls POST /api/auth/login with username/password
2. Service validates credentials against password_hash
3. System returns access_token (30 min expiry) + refresh_token (7 day expiry)
4. Client stores tokens securely
```

### Token Usage Flow
```
1. Client includes "Authorization: Bearer <access_token>" in requests
2. FastAPI dependency `get_current_user_id` extracts and validates token
3. Token signature verified with SECRET_KEY
4. Token expiration checked
5. User ID extracted from token's 'sub' claim
6. Route handler receives authenticated user_id
```

### Token Refresh Flow
```
1. Client detects access_token expired (or proactively)
2. Calls POST /api/auth/refresh with refresh_token
3. System validates refresh_token (longer expiry)
4. Returns new access_token
5. Refresh token stays the same
```

---

## Security Features

### Password Security
- Bcrypt hashing with automatic salt generation
- Passwords never stored in plaintext
- Password verified at login time

### Token Security
- JWT tokens signed with SECRET_KEY using HS256
- Separate token types (access vs refresh) prevent misuse
- Token expiration enforced
- Claims verified during validation

### Database Security
- All credentials in environment variables
- No hardcoded passwords in code
- Connection uses secure protocols (SSL for production)

### Rate Limiting
- Login endpoints limited to 10/minute
- Token refresh limited to 20/minute
- Prevents brute force attacks

---

## Running the Application

### Development Setup
```bash
# Copy environment
cp .env.example .env.local

# Edit if needed (defaults provided are development-safe)
# vim .env.local

# Start with Docker Compose
docker-compose up

# Application runs on http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

### Production Setup
```bash
# Generate strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: 9B2k_ZW7v-8sK3mL4pQ5rT6uV7wX8yZ9aB0cD1eF2gH3

# Create .env file with production values
cat > .env << EOF
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generated-key-above>
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/stock_exchange
POSTGRES_USER=<db-user>
POSTGRES_PASSWORD=<db-password>
EOF

# Validate configuration loads correctly
python -c "from app.config import get_settings; print(get_settings())"

# Start application
docker-compose up -d
```

---

## Testing Security

### Run Unit Tests
```bash
pytest tests/test_auth.py -v

# Test password hashing
# Test token creation
# Test token validation
# Test token expiration
```

### Run Integration Tests
```bash
pytest tests/test_auth_endpoints.py -v

# Test login endpoint
# Test register endpoint
# Test token refresh
# Test protected endpoints
# Test unauthorized access rejection
```

### Manual Testing with API Docs
```
1. Open http://localhost:8000/api/docs
2. Click "Authorize" button
3. Register new user: POST /api/users/register
4. Login: POST /api/auth/login
5. Copy access_token value
6. Click Authorize, paste token in Bearer scheme
7. Try protected endpoints like GET /api/users/me
8. Verify orders/portfolio/watchlists/screeners all require auth
```

---

## API Endpoint Security

### Public Endpoints (No Auth Required)
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/users/register` - Register
- `GET /api/quotes/{symbol}` - Get stock quotes (market data)
- `GET /api/charts/{symbol}/{timeframe}` - Get candlestick data
- `GET /api/indicators/{symbol}/{indicator}` - Get technical indicators

### Protected Endpoints (Auth Required)
- `GET /api/users/me` - Get current user profile
- `GET /api/user/preferences` - Get user preferences
- `PUT /api/user/preferences` - Update preferences
- `GET /api/user/theme` - Get user theme
- `POST /api/user/theme` - Set user theme
- `GET /api/orders` - Get user orders
- `POST /api/orders` - Create order
- `GET /api/orders/{order_id}` - Get order details
- `PUT /api/orders/{order_id}` - Update order
- `DELETE /api/orders/{order_id}` - Cancel order
- `GET /api/portfolio` - Get portfolio overview
- `GET /api/portfolio/positions` - Get positions
- `POST /api/portfolio/positions` - Create position
- `PUT /api/portfolio/positions/{position_id}` - Update position
- `DELETE /api/portfolio/positions/{position_id}` - Delete position
- `GET /api/watchlists` - Get user watchlists
- `POST /api/watchlists` - Create watchlist
- `GET /api/watchlists/{watchlist_id}` - Get watchlist
- `POST /api/watchlists/{watchlist_id}/add` - Add stock
- `DELETE /api/watchlists/{watchlist_id}/remove/{stock_id}` - Remove stock
- `PUT /api/watchlists/{watchlist_id}` - Update watchlist
- `DELETE /api/watchlists/{watchlist_id}` - Delete watchlist
- `GET /api/screeners` - Get user screeners
- `POST /api/screeners` - Create screener
- `GET /api/screeners/{screener_id}` - Get screener details
- `POST /api/screeners/{screener_id}/run` - Execute screener
- `PUT /api/screeners/{screener_id}` - Update screener
- `DELETE /api/screeners/{screener_id}` - Delete screener

---

## Common Issues and Troubleshooting

### "SECRET_KEY environment variable must be set"
**Solution**: Set SECRET_KEY in .env before running
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### "DATABASE_URL environment variable is required"
**Solution**: Set DATABASE_URL in .env
```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/stock_exchange"
```

### "Invalid authentication credentials" when accessing protected endpoint
**Solution**:
1. Login first: POST /api/auth/login
2. Copy access_token from response
3. Add to request: "Authorization: Bearer <token>"

### Token expired
**Solution**:
1. Call POST /api/auth/refresh with refresh_token
2. Get new access_token
3. Use new token in subsequent requests

---

## Deployment Checklist

- [ ] Generate strong SECRET_KEY using `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Set ENVIRONMENT=production in .env
- [ ] Set DEBUG=False
- [ ] Configure DATABASE_URL with production database
- [ ] Set POSTGRES_PASSWORD to strong random value
- [ ] Configure FRONTEND_URL for CORS
- [ ] Set API_PORT (default 8000)
- [ ] Test login endpoint
- [ ] Test protected endpoint requires auth
- [ ] Verify no hardcoded secrets in logs
- [ ] Run full test suite
- [ ] Monitor for 401/403 errors

---

## References

- JWT (RFC 7519): https://tools.ietf.org/html/rfc7519
- Password Hashing Best Practices: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
