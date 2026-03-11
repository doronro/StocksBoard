# Backend API Integration Guide for Frontend

This guide explains how the frontend should integrate with the backend APIs.

---

## Quick Reference

### Base URL
```
Development: http://localhost:8000/api
Production: https://api.stockexchangeboard.com/api
```

### Documentation
```
Swagger UI: /api/docs
ReDoc:      /api/redoc
OpenAPI:    /api/openapi.json
```

---

## Authentication

### JWT Tokens

All protected endpoints require a Bearer token in the Authorization header:

```javascript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};
```

### User Registration

```http
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe"
}
```

### User Login

```http
POST /api/users/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token

```http
POST /api/users/refresh
Authorization: Bearer {refresh_token}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Market Data APIs

### Get Single Quote

```http
GET /api/quotes/{symbol}
Authorization: Bearer {token}
```

**Example**: `GET /api/quotes/AAPL`

**Response**: `200 OK`
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "bid": 150.20,
  "ask": 150.30,
  "bid_size": 1500,
  "ask_size": 2000,
  "volume": 50000000,
  "change": 2.50,
  "change_percent": 1.70,
  "previous_close": 147.75,
  "open": 148.00,
  "high": 151.50,
  "low": 147.80,
  "timestamp": "2026-03-11T10:30:00Z"
}
```

### Get Batch Quotes

```http
POST /api/quotes/batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbols": ["AAPL", "GOOGL", "MSFT"]
}
```

**Response**: `200 OK`
```json
{
  "quotes": [
    {
      "symbol": "AAPL",
      "price": 150.25,
      "bid": 150.20,
      "ask": 150.30,
      ...
    },
    {
      "symbol": "GOOGL",
      "price": 140.50,
      ...
    },
    {
      "symbol": "MSFT",
      "price": 380.25,
      ...
    }
  ],
  "timestamp": "2026-03-11T10:30:00Z"
}
```

### Get Market Indices

```http
GET /api/indices
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "indices": [
    {
      "symbol": "^GSPC",
      "name": "S&P 500",
      "price": 4500.25,
      "change": 25.50,
      "change_percent": 0.57,
      "timestamp": "2026-03-11T10:30:00Z"
    },
    {
      "symbol": "^IXIC",
      "name": "NASDAQ Composite",
      "price": 14200.50,
      "change": 150.30,
      "change_percent": 1.07,
      "timestamp": "2026-03-11T10:30:00Z"
    }
  ],
  "timestamp": "2026-03-11T10:30:00Z"
}
```

---

## Watchlist APIs

### List User Watchlists

```http
GET /api/watchlists
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "watchlists": [
    {
      "id": 1,
      "name": "Tech Stocks",
      "description": "Leading technology companies",
      "is_default": true,
      "created_at": "2026-03-01T08:00:00Z",
      "items_count": 5
    },
    {
      "id": 2,
      "name": "Dividend Stocks",
      "description": "High dividend yield stocks",
      "is_default": false,
      "created_at": "2026-03-05T10:00:00Z",
      "items_count": 3
    }
  ]
}
```

### Create Watchlist

```http
POST /api/watchlists
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Growth Stocks",
  "description": "Fast growing companies"
}
```

**Response**: `201 Created`
```json
{
  "id": 3,
  "name": "Growth Stocks",
  "description": "Fast growing companies",
  "is_default": false,
  "created_at": "2026-03-11T10:30:00Z"
}
```

### Get Watchlist Details

```http
GET /api/watchlists/{id}
Authorization: Bearer {token}
```

**Example**: `GET /api/watchlists/1`

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Tech Stocks",
  "description": "Leading technology companies",
  "is_default": true,
  "items": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "price": 150.25,
      "change": 2.50,
      "change_percent": 1.70,
      "added_at": "2026-03-01T08:00:00Z"
    },
    {
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "sector": "Technology",
      "price": 140.50,
      "change": -1.25,
      "change_percent": -0.88,
      "added_at": "2026-03-01T08:30:00Z"
    }
  ],
  "created_at": "2026-03-01T08:00:00Z"
}
```

### Add Stock to Watchlist

```http
POST /api/watchlists/{id}/symbols
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "MSFT"
}
```

**Response**: `200 OK`
```json
{
  "message": "Stock added to watchlist",
  "symbol": "MSFT"
}
```

### Remove Stock from Watchlist

```http
DELETE /api/watchlists/{id}/symbols/{symbol}
Authorization: Bearer {token}
```

**Example**: `DELETE /api/watchlists/1/symbols/MSFT`

**Response**: `200 OK`
```json
{
  "message": "Stock removed from watchlist",
  "symbol": "MSFT"
}
```

### Update Watchlist

```http
PUT /api/watchlists/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Updated Name",
  "description": "Updated description",
  "is_default": true,
  "updated_at": "2026-03-11T10:30:00Z"
}
```

### Delete Watchlist

```http
DELETE /api/watchlists/{id}
Authorization: Bearer {token}
```

**Response**: `204 No Content`

---

## Portfolio APIs

### Get Portfolio Summary

```http
GET /api/portfolio
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "total_value": 150000.00,
  "total_cost": 145000.00,
  "cash_balance": 50000.00,
  "total_gain_loss": 5000.00,
  "total_gain_loss_percent": 3.45,
  "positions_count": 5,
  "buying_power": 50000.00,
  "created_at": "2026-01-01T08:00:00Z"
}
```

### Get Portfolio Positions

```http
GET /api/portfolio/positions
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "positions": [
    {
      "id": 1,
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 100,
      "average_cost": 140.00,
      "current_price": 150.25,
      "total_cost": 14000.00,
      "current_value": 15025.00,
      "unrealized_gain_loss": 1025.00,
      "unrealized_gain_loss_percent": 7.32,
      "opened_at": "2026-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "quantity": 50,
      "average_cost": 135.00,
      "current_price": 140.50,
      "total_cost": 6750.00,
      "current_value": 7025.00,
      "unrealized_gain_loss": 275.00,
      "unrealized_gain_loss_percent": 4.07,
      "opened_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

### Get Portfolio Performance

```http
GET /api/portfolio/performance
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "total_invested": 145000.00,
  "total_current_value": 150000.00,
  "total_return": 5000.00,
  "total_return_percent": 3.45,
  "daily_return": 250.00,
  "daily_return_percent": 0.17,
  "realized_gain_loss": 2000.00,
  "unrealized_gain_loss": 3000.00,
  "performance_by_position": [
    {
      "symbol": "AAPL",
      "return_percent": 7.32
    },
    {
      "symbol": "GOOGL",
      "return_percent": 4.07
    }
  ]
}
```

### Get Asset Allocation

```http
GET /api/portfolio/allocation
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "allocations": [
    {
      "sector": "Technology",
      "value": 105000.00,
      "percentage": 70.0
    },
    {
      "sector": "Healthcare",
      "value": 30000.00,
      "percentage": 20.0
    },
    {
      "sector": "Finance",
      "value": 15000.00,
      "percentage": 10.0
    }
  ],
  "cash_percentage": 25.0,
  "total_value": 150000.00
}
```

---

## Order APIs

### Create Order

```http
POST /api/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "AAPL",
  "order_type": "market",
  "side": "buy",
  "quantity": 10
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "order_type": "market",
  "side": "buy",
  "quantity": 10,
  "price": null,
  "status": "pending",
  "created_at": "2026-03-11T10:30:00Z"
}
```

### Create Limit Order

```http
POST /api/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "AAPL",
  "order_type": "limit",
  "side": "buy",
  "quantity": 10,
  "price": 150.00
}
```

### List Orders

```http
GET /api/orders
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "orders": [
    {
      "id": 1,
      "symbol": "AAPL",
      "order_type": "market",
      "side": "buy",
      "quantity": 10,
      "status": "filled",
      "average_filled_price": 150.25,
      "created_at": "2026-03-10T10:00:00Z",
      "filled_at": "2026-03-10T10:05:00Z"
    },
    {
      "id": 2,
      "symbol": "GOOGL",
      "order_type": "limit",
      "side": "sell",
      "quantity": 5,
      "price": 145.00,
      "status": "pending",
      "created_at": "2026-03-11T10:00:00Z"
    }
  ]
}
```

### Get Order Details

```http
GET /api/orders/{id}
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "order_type": "market",
  "side": "buy",
  "quantity": 10,
  "filled_quantity": 10,
  "average_filled_price": 150.25,
  "status": "filled",
  "created_at": "2026-03-10T10:00:00Z",
  "filled_at": "2026-03-10T10:05:00Z"
}
```

### Cancel Order

```http
DELETE /api/orders/{id}
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "message": "Order cancelled",
  "id": 2,
  "status": "cancelled"
}
```

---

## Technical Analysis APIs

### Get OHLC Data

```http
GET /api/candles/{symbol}?interval=1d&limit=30
Authorization: Bearer {token}
```

**Query Parameters**:
- `interval`: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w (default: 1d)
- `limit`: Number of candles (default: 100, max: 1000)

**Response**: `200 OK`
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "candles": [
    {
      "timestamp": "2026-03-11T00:00:00Z",
      "open": 148.00,
      "high": 151.50,
      "low": 147.80,
      "close": 150.25,
      "volume": 50000000
    },
    {
      "timestamp": "2026-03-10T00:00:00Z",
      "open": 147.00,
      "high": 149.50,
      "low": 146.50,
      "close": 147.75,
      "volume": 45000000
    }
  ]
}
```

### Get Technical Indicators

```http
GET /api/indicators/{symbol}?type=sma,ema,rsi,macd
Authorization: Bearer {token}
```

**Query Parameters**:
- `type`: Comma-separated indicator types
  - sma (Simple Moving Average)
  - ema (Exponential Moving Average)
  - rsi (Relative Strength Index)
  - macd (MACD)
  - bollinger (Bollinger Bands)
  - atr (Average True Range)

**Response**: `200 OK`
```json
{
  "symbol": "AAPL",
  "indicators": {
    "sma": {
      "period_20": 149.50,
      "period_50": 148.75,
      "period_200": 147.25
    },
    "ema": {
      "period_12": 149.85,
      "period_26": 148.90
    },
    "rsi": {
      "value": 65.5,
      "signal": "overbought"
    },
    "macd": {
      "value": 0.95,
      "signal_line": 0.80,
      "histogram": 0.15
    },
    "bollinger": {
      "upper": 152.00,
      "middle": 149.50,
      "lower": 147.00,
      "signal": "near_upper"
    }
  },
  "timestamp": "2026-03-11T10:30:00Z"
}
```

---

## User Preferences APIs

### Get User Profile

```http
GET /api/users/me
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2026-01-01T08:00:00Z"
}
```

### Get User Preferences

```http
GET /api/users/preferences
Authorization: Bearer {token}
```

**Response**: `200 OK`
```json
{
  "theme": "dark",
  "currency": "USD",
  "date_format": "YYYY-MM-DD",
  "time_zone": "America/New_York",
  "notifications_enabled": true,
  "price_alert_enabled": true,
  "email_notifications": false
}
```

### Update User Preferences

```http
PUT /api/users/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "theme": "light",
  "currency": "EUR",
  "time_zone": "Europe/London",
  "notifications_enabled": true,
  "price_alert_enabled": true
}
```

**Response**: `200 OK`
```json
{
  "theme": "light",
  "currency": "EUR",
  "time_zone": "Europe/London",
  "notifications_enabled": true,
  "price_alert_enabled": true,
  "updated_at": "2026-03-11T10:30:00Z"
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid request data",
  "status": 400
}
```

### 401 Unauthorized

```json
{
  "error": "Not authenticated",
  "status": 401
}
```

### 403 Forbidden

```json
{
  "error": "Insufficient permissions",
  "status": 403
}
```

### 404 Not Found

```json
{
  "error": "Quote not found for INVALID",
  "status": 404
}
```

### 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded",
  "status": 429
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "status": 500
}
```

---

## Frontend Implementation Examples

### TypeScript/React

```typescript
// api.ts
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired, refresh or redirect to login
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API error');
  }

  return response.json();
}

// Usage
export async function getQuote(symbol: string) {
  return apiCall(`/quotes/${symbol}`);
}

export async function getWatchlists() {
  return apiCall('/watchlists');
}

export async function createOrder(symbol: string, quantity: number) {
  return apiCall('/orders', {
    method: 'POST',
    body: JSON.stringify({
      symbol,
      quantity,
      order_type: 'market',
      side: 'buy',
    }),
  });
}
```

### React Component Example

```typescript
import { useState, useEffect } from 'react';
import { getQuote, getWatchlists } from './api';

export function Dashboard() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [quoteData, watchlistData] = await Promise.all([
          getQuote('AAPL'),
          getWatchlists(),
        ]);
        setQuote(quoteData);
        setWatchlists(watchlistData.watchlists);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>{quote?.symbol} - ${quote?.price}</h1>
      <h2>My Watchlists</h2>
      {watchlists.map(wl => (
        <div key={wl.id}>
          <h3>{wl.name}</h3>
          <p>{wl.items_count} stocks</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Common Integration Patterns

### Real-Time Updates (Phase 2)

Once WebSocket support is implemented:

```typescript
const ws = new WebSocket('ws://localhost:8000/ws/quotes');

ws.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'quote_update') {
    updateQuoteDisplay(data.quote);
  }
});

// Subscribe to symbols
ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['AAPL', 'GOOGL', 'MSFT']
}));
```

### Error Handling Pattern

```typescript
async function safeApiCall(fn: () => Promise<any>) {
  try {
    return await fn();
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('401')) {
        // Handle auth error
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      } else if (error.message.includes('429')) {
        // Handle rate limit
        showNotification('Too many requests, please wait...');
      } else {
        // Handle other errors
        showNotification(`Error: ${error.message}`);
      }
    }
    throw error;
  }
}
```

---

## Summary

The backend provides a complete RESTful API for:

✅ User authentication and management
✅ Real-time market data and quotes
✅ Watchlist management
✅ Portfolio tracking and performance
✅ Order management (buy/sell)
✅ Technical analysis indicators
✅ Stock screening

All endpoints are documented in Swagger UI at `/api/docs` and return standardized JSON responses.

For additional support, refer to:
- API_DOCUMENTATION.md - Complete API reference
- PHASE1_BACKEND_COMPLETE.md - Technical architecture
- BACKEND_DEPLOYMENT_GUIDE.md - Deployment instructions
