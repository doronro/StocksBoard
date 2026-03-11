# Data Models & API Contracts
## Stock Exchange Board Application

**Version**: 1.0
**Date**: March 11, 2026
**Audience**: Backend & Frontend Developers

---

## Table of Contents

1. Core Data Models
2. API Endpoints & Contracts
3. WebSocket Messages
4. Error Handling
5. Rate Limiting & Pagination
6. Data Validation Rules

---

## Part 1: Core Data Models

### 1.1 Quote Model

Represents a single stock price quote at a point in time.

```typescript
interface Quote {
  // Identification
  symbol: string              // "AAPL" - stock ticker
  name: string               // "Apple Inc." - company name
  exchange: string           // "NASDAQ" - exchange listing

  // Price Information
  price: number              // Current price ($)
  bid: number                // Best bid price
  ask: number                // Best ask price
  bidSize: number            // Number of shares at bid
  askSize: number            // Number of shares at ask

  // Daily Price Movement
  open: number               // Day opening price
  high: number               // Day high price
  low: number                // Day low price
  previousClose: number      // Previous day closing price

  // Change Information
  change: number             // Change in dollars
  changePercent: number      // Change in percentage

  // Volume
  volume: number             // Today's total volume
  avgVolume: number          // 30-day average volume

  // Market Information
  marketCap?: number         // Market capitalization ($)
  pe?: number                // Price-to-earnings ratio
  eps?: number               // Earnings per share ($)
  yield?: number             // Dividend yield (%)

  // Status
  trend: 'up' | 'down' | 'neutral'  // Price trend direction
  marketStatus: 'open' | 'closed' | 'pre-market' | 'after-hours'

  // Metadata
  timestamp: number          // Unix timestamp of quote
  source: 'real-time' | 'delayed' | 'mock'
}
```

**Validation Rules**:
- `symbol`: 1-5 uppercase characters, no spaces
- `price`: Must be positive
- `bid < ask`: Bid must be less than ask
- `high >= low`: High must be >= low
- `bid < price < ask`: Price between bid and ask
- `volume >= 0`: Cannot be negative
- `changePercent = (change / previousClose) * 100`

---

### 1.2 Candle Model (OHLC)

Represents price data for a specific time period.

```typescript
interface Candle {
  // Time period
  timestamp: number          // Unix timestamp (start of period)
  interval: string           // "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"

  // OHLC prices
  open: number               // Opening price
  high: number               // Highest price in period
  low: number                // Lowest price in period
  close: number              // Closing price

  // Volume and activity
  volume: number             // Total volume in period
  trades?: number            // Number of trades (optional)

  // Derived
  change?: number            // close - open
  changePercent?: number     // ((close - open) / open) * 100
}
```

**Validation Rules**:
- `high >= max(open, close, low)`
- `low <= min(open, close, high)`
- `open, high, low, close > 0`
- All prices in cents or dollars (consistent decimals)
- `volume >= 0`

---

### 1.3 Technical Indicator Model

Represents calculated technical analysis indicators.

```typescript
interface Indicators {
  symbol: string
  timestamp: number          // Calculation timestamp
  interval: string           // Timeframe of indicators

  // Simple Moving Averages
  sma?: {
    period_20: number
    period_50: number
    period_200: number
  }

  // Exponential Moving Averages
  ema?: {
    period_12: number
    period_26: number
  }

  // MACD
  macd?: {
    value: number            // MACD line
    signalLine: number       // Signal line
    histogram: number        // MACD - Signal line
    signal: 'bullish' | 'bearish' | 'neutral'
  }

  // RSI (Relative Strength Index)
  rsi?: {
    value: number            // 0-100
    signal: 'overbought' | 'neutral' | 'oversold'
  }

  // Bollinger Bands
  bollinger?: {
    upper: number            // Upper band
    middle: number           // SMA 20 (middle band)
    lower: number            // Lower band
    bandwidth: number        // (upper - lower) / middle
    signal: 'near_upper' | 'near_middle' | 'near_lower'
  }

  // ATR (Average True Range)
  atr?: {
    value: number
    percentOfPrice: number   // (ATR / price) * 100
  }

  // Volume
  volume?: {
    current: number
    average: number
    trend: 'up' | 'down' | 'neutral'
  }

  // Stochastic Oscillator (optional)
  stochastic?: {
    k: number                // 0-100
    d: number                // 0-100
    signal: 'overbought' | 'neutral' | 'oversold'
  }

  // Consolidated Signal
  signal?: {
    consensus: 'strong_bullish' | 'bullish' | 'neutral' | 'bearish' | 'strong_bearish'
    confidence: number       // 0-100 (agreement percentage)
    components: {
      [indicatorName: string]: 'bullish' | 'bearish' | 'neutral'
    }
  }
}
```

---

### 1.4 Portfolio Model

Represents a user's portfolio/account.

```typescript
interface Portfolio {
  id: string                 // Portfolio ID
  userId: string             // Associated user

  // Valuation
  totalValue: number         // Current portfolio value ($)
  totalCost: number          // Total amount invested ($)
  cash: number               // Available cash
  buyingPower: number        // Cash + margin available

  // Performance
  unrealizedGain: number     // Total unrealized P&L ($)
  unrealizedGainPercent: number  // Unrealized P&L (%)
  dayPnL: number             // Today's P&L ($)
  dayPnLPercent: number      // Today's P&L (%)
  realizedGain: number       // Realized gains from closed positions ($)

  // Positions
  holdings: Holding[]        // Array of holdings
  positionCount: number      // Number of open positions

  // Risk Metrics (calculated)
  beta?: number              // Portfolio beta
  sharpeRatio?: number       // Risk-adjusted return
  maxDrawdown?: number       // Max peak-to-trough decline

  // Metadata
  createdAt: number          // Portfolio creation timestamp
  updatedAt: number          // Last update timestamp
  currency: string           // "USD"
}

interface Holding {
  id: string                 // Holding ID
  symbol: string             // Stock symbol
  name: string              // Company name
  quantity: number           // Number of shares
  averagePrice: number       // Average cost per share
  currentPrice: number       // Current price per share
  totalCost: number          // quantity * averagePrice
  currentValue: number       // quantity * currentPrice

  // Performance
  unrealizedGain: number     // currentValue - totalCost
  unrealizedGainPercent: number  // (unrealizedGain / totalCost) * 100
  dailyChange: number        // Change today
  dailyChangePercent: number

  // Metadata
  entryDate: number          // When position was opened
  sectorAllocation: number   // % of portfolio this holds
  weight: number             // Position weight in portfolio
}
```

**Validation Rules**:
- `totalValue = sum(holding.currentValue) + cash`
- `totalCost = sum(holding.totalCost)`
- `unrealizedGain = totalValue - totalCost`
- `quantity > 0` for active holdings
- `averagePrice > 0`
- `buyingPower >= cash`

---

### 1.5 Order Model

Represents a buy/sell order.

```typescript
interface Order {
  id: string                 // Order ID
  userId: string             // User who placed order
  portfolioId: string        // Portfolio associated

  // Order Details
  symbol: string             // Stock symbol
  side: 'buy' | 'sell'      // Order direction
  type: 'market' | 'limit' | 'stop_loss' | 'trailing_stop'

  // Quantity
  quantity: number           // Shares to buy/sell
  filledQuantity: number     // Already filled shares

  // Price
  price?: number             // Limit price (for limit orders)
  stopPrice?: number         // Stop price (for stop orders)
  trailingPercent?: number   // Trail % (for trailing stops)

  // Execution
  status: 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected'
  averageFilledPrice?: number // Avg price of filled shares

  // Metadata
  createdAt: number
  submittedAt?: number
  filledAt?: number
  cancelledAt?: number

  // Estimated Cost
  estimatedCost?: number     // Estimated $ value

  // Error/Reason
  rejectionReason?: string   // Why order was rejected
}
```

**Validation Rules**:
- `quantity > 0`
- `price > 0` for limit orders
- `stopPrice > 0` for stop orders
- `trailingPercent > 0` for trailing stops
- Status transitions: pending → partial/filled/cancelled/rejected
- `filledQuantity <= quantity`
- `filledQuantity = 0` when status = 'pending'

---

### 1.6 Alert Model

Represents a price or technical alert.

```typescript
interface Alert {
  id: string
  userId: string

  // Trigger Setup
  symbol: string
  alertType: 'price_above' | 'price_below' | 'volume_spike' | 'technical_signal'

  // Conditions
  triggerPrice?: number      // For price alerts
  triggerVolume?: number     // For volume alerts
  signalType?: string        // For technical alerts

  // Status
  isActive: boolean          // Alert enabled?
  isTriggered: boolean       // Has triggered?

  // Notification
  notificationMethods: Array<'push' | 'email' | 'sms'>
  notificationSent?: number  // Timestamp when triggered

  // Metadata
  createdAt: number
  expiresAt?: number         // Auto-delete after date
  triggeredAt?: number
}
```

---

### 1.7 Watchlist Model

Represents a collection of symbols.

```typescript
interface Watchlist {
  id: string
  userId: string

  // Metadata
  name: string               // "Tech Stocks"
  description?: string
  isDefault: boolean         // Default watchlist?

  // Symbols
  symbols: string[]          // Array of stock symbols
  items?: WatchlistItem[]    // Rich item data

  // Statistics
  itemCount: number          // Number of stocks

  // Timestamps
  createdAt: number
  updatedAt: number
}

interface WatchlistItem {
  symbol: string
  name: string
  sector: string
  addedAt: number            // When added to list
  price: number              // Current price
  change: number
  changePercent: number
  trend: 'up' | 'down' | 'neutral'
}
```

---

### 1.8 Market Index Model

Represents major market indices.

```typescript
interface MarketIndex {
  symbol: string             // "^GSPC", "^IXIC", "^DJI"
  name: string              // "S&P 500", "NASDAQ", "Dow Jones"

  // Values
  value: number             // Current index value
  change: number            // Change in points
  changePercent: number     // Change in percent

  // Daily Range
  open: number
  high: number
  low: number
  previousClose: number

  // Volume/Components
  numberOfAdvances?: number // Stocks that went up
  numberOfDeclines?: number // Stocks that went down

  // Metadata
  timestamp: number
  marketStatus: 'open' | 'closed' | 'pre-market' | 'after-hours'
}
```

---

## Part 2: API Endpoints & Contracts

### 2.1 Quote Endpoints

#### GET /api/quotes/{symbol}
**Purpose**: Get current quote for a single symbol

**Request**:
```http
GET /api/quotes/AAPL
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "exchange": "NASDAQ",
  "price": 150.25,
  "bid": 150.20,
  "ask": 150.30,
  "bidSize": 1500,
  "askSize": 2000,
  "open": 148.00,
  "high": 151.50,
  "low": 147.80,
  "previousClose": 147.75,
  "change": 2.50,
  "changePercent": 1.70,
  "volume": 50000000,
  "avgVolume": 45000000,
  "marketCap": 2500000000000,
  "pe": 28.50,
  "eps": 5.28,
  "yield": 0.42,
  "trend": "up",
  "marketStatus": "open",
  "timestamp": 1710155400000,
  "source": "real-time"
}
```

**Error Responses**:
- `404 Not Found`: Symbol not found
- `401 Unauthorized`: Invalid token
- `429 Too Many Requests`: Rate limit exceeded

---

#### POST /api/quotes/batch
**Purpose**: Get quotes for multiple symbols

**Request**:
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "includeIndicators": false
}
```

**Response** (200 OK):
```json
{
  "quotes": [
    { "symbol": "AAPL", ... },
    { "symbol": "GOOGL", ... },
    { "symbol": "MSFT", ... }
  ],
  "timestamp": 1710155400000,
  "count": 3
}
```

---

### 2.2 Chart Data Endpoints

#### GET /api/candles/{symbol}?interval=1d&limit=100
**Purpose**: Get OHLC data for charting

**Query Parameters**:
- `interval`: Time period (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
- `limit`: Number of candles (default: 100, max: 1000)
- `startTime`: Unix timestamp (optional)
- `endTime`: Unix timestamp (optional)

**Response** (200 OK):
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "candles": [
    {
      "timestamp": 1710240000000,
      "open": 148.00,
      "high": 151.50,
      "low": 147.80,
      "close": 150.25,
      "volume": 50000000,
      "change": 2.25,
      "changePercent": 1.52
    },
    {
      "timestamp": 1710153600000,
      "open": 147.00,
      "high": 149.50,
      "low": 146.50,
      "close": 147.75,
      "volume": 45000000,
      "change": 0.75,
      "changePercent": 0.51
    }
  ],
  "count": 2
}
```

---

### 2.3 Technical Indicators Endpoints

#### GET /api/indicators/{symbol}?type=sma,rsi,macd
**Purpose**: Get technical indicators

**Query Parameters**:
- `type`: Comma-separated indicator types (sma, ema, rsi, macd, bollinger, atr)
- `interval`: Time period (default: 1d)

**Response** (200 OK):
```json
{
  "symbol": "AAPL",
  "timestamp": 1710155400000,
  "interval": "1d",
  "indicators": {
    "sma": {
      "period_20": 149.50,
      "period_50": 148.75,
      "period_200": 147.25
    },
    "rsi": {
      "value": 65.5,
      "signal": "overbought"
    },
    "macd": {
      "value": 0.95,
      "signalLine": 0.80,
      "histogram": 0.15,
      "signal": "bullish"
    }
  },
  "signal": {
    "consensus": "bullish",
    "confidence": 75,
    "components": {
      "sma": "bullish",
      "rsi": "bearish",
      "macd": "bullish"
    }
  }
}
```

---

### 2.4 Portfolio Endpoints

#### GET /api/portfolio
**Purpose**: Get portfolio summary

**Response** (200 OK):
```json
{
  "id": "portfolio_123",
  "totalValue": 250000.00,
  "totalCost": 245000.00,
  "cash": 50000.00,
  "buyingPower": 50000.00,
  "unrealizedGain": 5000.00,
  "unrealizedGainPercent": 2.04,
  "dayPnL": 1250.00,
  "dayPnLPercent": 0.50,
  "positionCount": 5,
  "beta": 1.05,
  "sharpeRatio": 1.85,
  "timestamp": 1710155400000
}
```

---

#### GET /api/portfolio/positions
**Purpose**: Get all holdings

**Query Parameters**:
- `sortBy`: "symbol", "value", "gain_percent" (default: "value")
- `order`: "asc", "desc"

**Response** (200 OK):
```json
{
  "positions": [
    {
      "id": "pos_1",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 100,
      "averagePrice": 140.00,
      "currentPrice": 150.25,
      "totalCost": 14000.00,
      "currentValue": 15025.00,
      "unrealizedGain": 1025.00,
      "unrealizedGainPercent": 7.32,
      "weight": 6.01,
      "entryDate": 1709894400000
    }
  ],
  "count": 5
}
```

---

### 2.5 Order Endpoints

#### POST /api/orders
**Purpose**: Create a new order

**Request**:
```json
{
  "symbol": "AAPL",
  "side": "buy",
  "type": "market",
  "quantity": 10,
  "price": null,
  "estimatedCost": 1502.50
}
```

**Response** (201 Created):
```json
{
  "id": "order_123",
  "symbol": "AAPL",
  "side": "buy",
  "type": "market",
  "quantity": 10,
  "filledQuantity": 0,
  "status": "pending",
  "createdAt": 1710155400000,
  "estimatedCost": 1502.50
}
```

**Error Responses**:
- `400 Bad Request`: Invalid order data
- `403 Forbidden`: Insufficient buying power
- `409 Conflict`: Account restrictions

---

#### DELETE /api/orders/{orderId}
**Purpose**: Cancel an order

**Response** (200 OK):
```json
{
  "id": "order_123",
  "status": "cancelled",
  "cancelledAt": 1710155500000,
  "message": "Order cancelled successfully"
}
```

---

### 2.6 Watchlist Endpoints

#### GET /api/watchlists
**Purpose**: List all watchlists

**Response** (200 OK):
```json
{
  "watchlists": [
    {
      "id": "wl_1",
      "name": "Tech Stocks",
      "description": "Major tech companies",
      "isDefault": true,
      "itemCount": 5,
      "createdAt": 1709894400000
    }
  ],
  "count": 1
}
```

---

#### POST /api/watchlists/{id}/symbols
**Purpose**: Add stock to watchlist

**Request**:
```json
{
  "symbol": "MSFT"
}
```

**Response** (200 OK):
```json
{
  "message": "Symbol added to watchlist",
  "symbol": "MSFT",
  "watchlistId": "wl_1"
}
```

---

### 2.7 Alert Endpoints

#### POST /api/alerts
**Purpose**: Create a new alert

**Request**:
```json
{
  "symbol": "AAPL",
  "alertType": "price_above",
  "triggerPrice": 155.00,
  "notificationMethods": ["push", "email"]
}
```

**Response** (201 Created):
```json
{
  "id": "alert_123",
  "symbol": "AAPL",
  "alertType": "price_above",
  "triggerPrice": 155.00,
  "isActive": true,
  "createdAt": 1710155400000
}
```

---

## Part 3: WebSocket Messages (Phase 2)

### 3.1 Quote Updates

**Server → Client**: Real-time quote updates
```json
{
  "type": "quote_update",
  "data": {
    "symbol": "AAPL",
    "price": 150.30,
    "bid": 150.25,
    "ask": 150.35,
    "change": 2.55,
    "changePercent": 1.72,
    "volume": 50500000,
    "timestamp": 1710155410000
  }
}
```

### 3.2 Indicator Updates

**Server → Client**: Technical indicator updates
```json
{
  "type": "indicator_update",
  "data": {
    "symbol": "AAPL",
    "indicator": "rsi",
    "value": 66.0,
    "signal": "overbought",
    "timestamp": 1710155410000
  }
}
```

### 3.3 Order Status Updates

**Server → Client**: Order execution updates
```json
{
  "type": "order_update",
  "data": {
    "orderId": "order_123",
    "status": "filled",
    "filledQuantity": 10,
    "averageFilledPrice": 150.26,
    "timestamp": 1710155420000
  }
}
```

---

## Part 4: Error Handling

### 4.1 Standard Error Response

```json
{
  "error": "Error message",
  "status": 400,
  "code": "INVALID_INPUT",
  "timestamp": 1710155400000,
  "details": {
    "field": "quantity",
    "reason": "Must be greater than 0"
  }
}
```

### 4.2 Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_INPUT` | 400 | Validation error |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | No permission |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Business logic conflict |
| `RATE_LIMIT` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Part 5: Rate Limiting & Pagination

### 5.1 Rate Limiting Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1710156400
```

**Limits by Endpoint Type**:
- Quotes: 1000/minute
- Orders: 100/minute
- Watchlists: 500/minute
- Analytics: 100/minute

### 5.2 Pagination

```
GET /api/positions?page=1&limit=20

Response:
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

---

## Part 6: Data Validation Rules

### 6.1 Stock Symbol Validation

```typescript
function isValidSymbol(symbol: string): boolean {
  // 1-5 uppercase letters, no spaces or special chars
  return /^[A-Z]{1,5}$/.test(symbol);
}
```

### 6.2 Price Validation

```typescript
function isValidPrice(price: number): boolean {
  // Must be positive, max 2 decimal places
  return price > 0 && Number.isFinite(price) &&
         Math.round(price * 100) / 100 === price;
}
```

### 6.3 Quantity Validation

```typescript
function isValidQuantity(quantity: number): boolean {
  // Must be positive integer
  return quantity > 0 && Number.isInteger(quantity) && quantity <= 1000000;
}
```

### 6.4 Order Validation

```typescript
function validateOrder(order: any): ValidationResult {
  const errors = [];

  if (!isValidSymbol(order.symbol)) {
    errors.push({ field: 'symbol', message: 'Invalid symbol' });
  }

  if (!['buy', 'sell'].includes(order.side)) {
    errors.push({ field: 'side', message: 'Must be buy or sell' });
  }

  if (!isValidQuantity(order.quantity)) {
    errors.push({ field: 'quantity', message: 'Invalid quantity' });
  }

  if (order.type === 'limit' && !isValidPrice(order.price)) {
    errors.push({ field: 'price', message: 'Invalid price' });
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}
```

---

## Part 7: Type Definitions Summary

### Frontend TypeScript Types

Place in `/src/types/index.ts`:

```typescript
// Quote types
export type MarketStatus = 'open' | 'closed' | 'pre-market' | 'after-hours';
export type Trend = 'up' | 'down' | 'neutral';
export interface Quote { /* ... */ }

// Order types
export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop_loss' | 'trailing_stop';
export type OrderStatus = 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected';
export interface Order { /* ... */ }

// Portfolio types
export interface Portfolio { /* ... */ }
export interface Holding { /* ... */ }

// Indicator types
export interface Indicators { /* ... */ }
export interface Signal { /* ... */ }
```

---

## Implementation Checklist

### Backend Developer Checklist

- [ ] Implement Quote endpoints
- [ ] Implement Chart data endpoints
- [ ] Implement Technical indicator calculation
- [ ] Implement Portfolio endpoints
- [ ] Implement Order endpoints
- [ ] Implement Watchlist endpoints
- [ ] Implement Alert endpoints
- [ ] Add input validation
- [ ] Add rate limiting
- [ ] Implement error handling
- [ ] Create API documentation (Swagger)
- [ ] Implement WebSocket support (Phase 2)

### Frontend Developer Checklist

- [ ] Create TypeScript type definitions
- [ ] Implement API client
- [ ] Create Zustand stores
- [ ] Implement Quote display components
- [ ] Implement Chart components
- [ ] Implement Portfolio components
- [ ] Implement Order components
- [ ] Implement Watchlist components
- [ ] Add loading states
- [ ] Add error states
- [ ] Implement real-time updates
- [ ] Add accessibility features

---

## Testing Data

### Sample Symbols
```
AAPL - Apple Inc.
GOOGL - Alphabet Inc.
MSFT - Microsoft Corporation
AMZN - Amazon.com Inc.
TSLA - Tesla Inc.
NVDA - NVIDIA Corporation
META - Meta Platforms Inc.
```

### Sample Prices
```
AAPL: $145 - $160 range
GOOGL: $135 - $150 range
MSFT: $370 - $390 range
AMZN: $170 - $190 range
```

---

**Last Updated**: March 11, 2026
**Status**: Complete
