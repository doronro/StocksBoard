# Security Implementation Verification Guide

## Quick Verification Checklist

Run these checks to verify all security fixes are properly implemented.

### 1. Authentication Module Exists
```bash
ls -la app/auth.py
```
Expected: File exists with ~200+ lines of code

### 2. No Hardcoded User IDs in Routes
```bash
grep -r "user_id: int = 1" app/routes/
```
Expected: No matches (0 results)

### 3. All Auth Imports Present
```bash
grep -r "get_current_user_id" app/routes/*.py | wc -l
```
Expected: 38+ occurrences (all protected endpoints)

### 4. Login Endpoint Exists
```bash
grep -n "@router.post.*login" app/routes/users.py
```
Expected: Should show login endpoint defined

### 5. Refresh Token Endpoint Exists
```bash
grep -n "@router.post.*refresh" app/routes/users.py
```
Expected: Should show refresh endpoint defined

### 6. Config Has Security Validators
```bash
grep -n "def validate_secret_key\|def validate_database_url" app/config.py
```
Expected: Both validators defined

### 7. No Hardcoded Secrets in Config
```bash
grep "secret_key.*default=" app/config.py
```
Expected: Should show `secret_key: str = Field(default="")` (empty)

### 8. Docker Compose Uses Environment Variables
```bash
grep -E "DATABASE_URL|SECRET_KEY" docker-compose.yml | grep -v "^\s*#"
```
Expected: Should show `${DATABASE_URL}` and `${SECRET_KEY}` (not hardcoded values)

### 9. Environment Files Exist
```bash
ls -la .env.example .env.local
```
Expected: Both files exist

### 10. Tests Exist
```bash
ls -la tests/test_auth.py tests/test_auth_endpoints.py
```
Expected: Both test files exist with 30+ tests

### 11. Documentation Exists
```bash
ls -la SECURITY.md SECURITY_FIXES_SUMMARY.md
```
Expected: Both documentation files exist

---

## Automated Verification Script

Create a file `verify_security.sh`:

```bash
#!/bin/bash

echo "================================"
echo "Security Implementation Check"
echo "================================"
echo ""

ERRORS=0

echo "1. Checking auth.py exists..."
if [ -f "app/auth.py" ]; then
    echo "   ✓ app/auth.py exists"
else
    echo "   ✗ app/auth.py NOT found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "2. Checking for hardcoded user_id defaults..."
HARDCODED=$(grep -r "user_id: int = 1" app/routes/ 2>/dev/null | wc -l)
if [ "$HARDCODED" -eq 0 ]; then
    echo "   ✓ No hardcoded user_id defaults found"
else
    echo "   ✗ Found $HARDCODED hardcoded user_id defaults"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "3. Checking for get_current_user_id usage..."
USAGES=$(grep -r "get_current_user_id" app/routes/ 2>/dev/null | wc -l)
if [ "$USAGES" -gt 30 ]; then
    echo "   ✓ Found $USAGES get_current_user_id usages (expected 30+)"
else
    echo "   ✗ Only found $USAGES get_current_user_id usages (expected 30+)"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "4. Checking for validators in config.py..."
VALIDATORS=$(grep -c "def validate_" app/config.py)
if [ "$VALIDATORS" -ge 3 ]; then
    echo "   ✓ Found $VALIDATORS validators in config.py"
else
    echo "   ✗ Found only $VALIDATORS validators (expected 3+)"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "5. Checking docker-compose.yml uses env vars..."
ENV_VARS=$(grep -c '${' docker-compose.yml)
if [ "$ENV_VARS" -gt 5 ]; then
    echo "   ✓ Found $ENV_VARS environment variable references"
else
    echo "   ✗ Found only $ENV_VARS environment variable references"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "6. Checking .env.example exists..."
if [ -f ".env.example" ]; then
    echo "   ✓ .env.example exists"
else
    echo "   ✗ .env.example NOT found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "7. Checking test files..."
if [ -f "tests/test_auth.py" ] && [ -f "tests/test_auth_endpoints.py" ]; then
    echo "   ✓ Both test files exist"
else
    echo "   ✗ Test files missing"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "8. Checking documentation..."
if [ -f "SECURITY.md" ] && [ -f "SECURITY_FIXES_SUMMARY.md" ]; then
    echo "   ✓ Security documentation exists"
else
    echo "   ✗ Security documentation missing"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "================================"
if [ "$ERRORS" -eq 0 ]; then
    echo "✓ All security checks passed!"
    exit 0
else
    echo "✗ Found $ERRORS issues"
    exit 1
fi
```

Run it:
```bash
chmod +x verify_security.sh
./verify_security.sh
```

---

## Manual Testing

### 1. Test Registration
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "secure_password_123",
    "full_name": "Test User"
  }'
```

Expected Response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2024-03-10T...",
  "updated_at": "2024-03-10T..."
}
```

### 2. Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "secure_password_123"
  }'
```

Expected Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` for next tests.

### 3. Test Protected Endpoint Without Token
```bash
curl -X GET http://localhost:8000/api/users/me
```

Expected Response: 403 Forbidden

### 4. Test Protected Endpoint With Token
```bash
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <access_token>"
```

Expected Response: 200 OK with user data

### 5. Test Token Refresh
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

Expected Response: 200 OK with new access_token

### 6. Test Invalid Token
```bash
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer invalid.token.here"
```

Expected Response: 401 Unauthorized

### 7. Test Other Protected Endpoints
```bash
# Get orders (should be empty list, not 401)
curl -X GET http://localhost:8000/api/orders \
  -H "Authorization: Bearer <access_token>"

# Get portfolio
curl -X GET http://localhost:8000/api/portfolio \
  -H "Authorization: Bearer <access_token>"

# Get watchlists
curl -X GET http://localhost:8000/api/watchlists \
  -H "Authorization: Bearer <access_token>"

# Get screeners
curl -X GET http://localhost:8000/api/screeners \
  -H "Authorization: Bearer <access_token>"
```

All should return 200 OK (may be empty, but authenticated).

---

## API Documentation Testing

1. Open http://localhost:8000/api/docs
2. Look for "Authorize" button in top right
3. Click Authorize button
4. Select "Bearer" from scheme dropdown
5. Enter access_token from login response
6. Try protected endpoints - they should work
7. Try without token - should get 401

---

## Running Tests

### Run Unit Tests
```bash
pytest tests/test_auth.py -v
```

Expected: 17 tests pass

### Run Integration Tests
```bash
pytest tests/test_auth_endpoints.py -v
```

Expected: 19 tests pass

### Run All Auth Tests
```bash
pytest tests/test_auth.py tests/test_auth_endpoints.py -v
```

Expected: 36 tests pass

### Run With Coverage
```bash
pytest tests/test_auth.py tests/test_auth_endpoints.py \
  --cov=app.auth \
  --cov=app.routes \
  -v
```

Expected: High coverage on auth.py and routes

---

## Configuration Testing

### Test Environment Variable Validation

```python
# Should pass (development)
ENVIRONMENT=development SECRET_KEY=short python -c "from app.config import get_settings; print(get_settings())"

# Should fail (production with short key)
ENVIRONMENT=production SECRET_KEY=short python -c "from app.config import get_settings; print(get_settings())"
# Expected: ValueError about SECRET_KEY length

# Should fail (missing DATABASE_URL)
DATABASE_URL= python -c "from app.config import get_settings; print(get_settings())"
# Expected: ValueError about DATABASE_URL

# Should pass (valid production)
ENVIRONMENT=production \
SECRET_KEY=9B2k_ZW7v-8sK3mL4pQ5rT6uV7wX8yZ9aB0cD1eF2gH3 \
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db \
python -c "from app.config import get_settings; print('Success')"
# Expected: Success
```

---

## Security Issues Fixed Summary

| Issue | Status | Tests | Documentation |
|-------|--------|-------|----------------|
| Hardcoded user_id | ✓ Fixed | 36 tests | SECURITY.md |
| Missing auth on routes | ✓ Fixed | 36 tests | SECURITY.md |
| Hardcoded secrets | ✓ Fixed | validators | SECURITY.md |
| No env vars in config | ✓ Fixed | validators | SECURITY.md |
| Hardcoded Docker creds | ✓ Fixed | manual | SECURITY.md |

---

## Sign-Off Checklist

- [ ] Verification script passes (./verify_security.sh)
- [ ] Manual API tests pass (registration, login, protected endpoints)
- [ ] Unit tests pass (pytest tests/test_auth.py)
- [ ] Integration tests pass (pytest tests/test_auth_endpoints.py)
- [ ] Configuration validation working (test environment variables)
- [ ] Docker Compose starts without errors
- [ ] API docs accessible at /api/docs
- [ ] No hardcoded secrets in code/config/docker-compose
- [ ] All 36+ endpoints require authentication
- [ ] Documentation complete and accurate

**All checks passing = Implementation Ready for Production**
