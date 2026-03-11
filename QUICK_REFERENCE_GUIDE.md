# Quick Reference Guide
## Investment Strategy Framework Implementation

**Date**: March 11, 2026
**Format**: Quick lookup for developers

---

## Document Index

### Main Documentation
1. **INVESTMENT_STRATEGY_FRAMEWORK.md** (60 pages)
   - Complete feature specifications
   - Investment strategy details
   - Board display requirements
   - Compliance and risk management

2. **UI_PATTERNS_REFERENCE.md** (40 pages)
   - React component patterns
   - Tailwind CSS examples
   - Accessibility guidelines
   - Responsive design patterns

3. **DATA_MODELS_AND_API_CONTRACTS.md** (50 pages)
   - TypeScript interfaces
   - API endpoint specifications
   - Error handling standards
   - Validation rules

4. **STRATEGY_FRAMEWORK_SUMMARY.md** (15 pages)
   - Executive overview
   - Implementation roadmap
   - Success metrics
   - Team guidance

---

## Core Investment Strategies at a Glance

| Strategy | Timeframe | Key Tools | Risk % |
|----------|-----------|-----------|--------|
| **Momentum** | Min-Days | MACD, RSI, Vol | 2-3% |
| **Value** | Months-Yrs | P/E, PEG, ROE | 3-5% |
| **Dividend** | Long-term | Yield, Payout | 2-3% |
| **Growth** | 3-10 yrs | Revenue, PEG | 4-5% |
| **Hedging** | Tactical | Inverse, Put | 1-2% |

---

## 7 Essential Technical Indicators

```
1. MACD (Momentum) → Bullish/Bearish crossovers
2. RSI (Momentum) → Overbought (>70) / Oversold (<30)
3. Bollinger Bands (Volatility) → Support/Resistance
4. SMA 20/50/200 (Trend) → Golden/Death Cross
5. EMA 12/26 (Trend) → Fast trend detection
6. ATR (Volatility) → Stop-loss placement
7. Volume (Confirmation) → Trend validation
```

**Aggregated Signal**:
- 80%+ agreement = Strong signal
- 60-80% = Moderate signal
- 40-60% = Neutral
- <40% = Weak signal

---

## API Endpoint Checklist

### Quotes
```
GET /api/quotes/{symbol}              ← Single quote
POST /api/quotes/batch                ← Multiple quotes
GET /api/indices                      ← Market indices
```

### Charts
```
GET /api/candles/{symbol}?interval=1d ← OHLC data
GET /api/indicators/{symbol}          ← Technical indicators
```

### Portfolio
```
GET /api/portfolio                    ← Summary
GET /api/portfolio/positions          ← Holdings
GET /api/portfolio/performance        ← Analytics
GET /api/portfolio/allocation         ← Sectors
```

### Orders
```
POST /api/orders                      ← Create
GET /api/orders                       ← List
DELETE /api/orders/{id}               ← Cancel
```

### Watchlists
```
GET /api/watchlists                   ← List
POST /api/watchlists/{id}/symbols     ← Add symbol
DELETE /api/watchlists/{id}/symbols/{symbol} ← Remove
```

### Alerts
```
POST /api/alerts                      ← Create
GET /api/alerts                       ← List
DELETE /api/alerts/{id}               ← Delete
```

---

## TypeScript Types Quick Lookup

### Quote
```typescript
interface Quote {
  symbol: string; price: number; bid: number; ask: number;
  open: number; high: number; low: number;
  change: number; changePercent: number;
  volume: number; avgVolume: number;
  marketCap?: number; pe?: number; eps?: number;
  timestamp: number;
}
```

### Holding
```typescript
interface Holding {
  symbol: string; quantity: number;
  averagePrice: number; currentPrice: number;
  unrealizedGain: number; unrealizedGainPercent: number;
  entryDate: number; weight: number;
}
```

### Order
```typescript
interface Order {
  id: string; symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop_loss' | 'trailing_stop';
  quantity: number; price?: number;
  status: 'pending' | 'partial' | 'filled' | 'cancelled';
  createdAt: number;
}
```

### Indicators
```typescript
interface Indicators {
  sma?: { period_20: number; period_50: number; period_200: number };
  rsi?: { value: number; signal: 'overbought' | 'neutral' | 'oversold' };
  macd?: { value: number; signalLine: number; histogram: number };
  bollinger?: { upper: number; middle: number; lower: number };
  atr?: { value: number; percentOfPrice: number };
  signal?: { consensus: string; confidence: number };
}
```

---

## UI Component Patterns

### Quote Card
```tsx
<Card>
  <div className="flex justify-between">
    <div>
      <p className="font-semibold">{quote.symbol}</p>
      <p className="text-2xl font-bold">${quote.price}</p>
      <p className={quote.change >= 0 ? 'text-green-600' : 'text-red-600'}>
        {quote.change > 0 ? '+' : ''}{quote.change.toFixed(2)}%
      </p>
    </div>
    <div className="flex gap-2">
      <Button variant="success">Buy</Button>
      <Button variant="danger">Sell</Button>
    </div>
  </div>
</Card>
```

### Metric Row
```tsx
<div className="flex justify-between py-2">
  <span className="text-neutral-600">Price</span>
  <span className="font-semibold">${quote.price}</span>
</div>
```

### Technical Alert
```tsx
<Alert
  type={rsi > 70 ? 'warning' : 'info'}
  title="RSI Signal"
  description={rsi > 70 ? 'Overbought condition' : 'Normal range'}
/>
```

---

## Common Validation Functions

```typescript
// Symbol validation
isValidSymbol(symbol: string): /^[A-Z]{1,5}$/.test(symbol)

// Price validation
isValidPrice(price: number):
  price > 0 && Number.isFinite(price)

// Quantity validation
isValidQuantity(qty: number):
  qty > 0 && Number.isInteger(qty) && qty <= 1000000

// Bid < Ask validation
isValidBidAsk(bid: number, ask: number): bid < ask

// P&L calculation
calculatePnL(quantity, avgCost, currentPrice):
  (quantity * currentPrice) - (quantity * avgCost)
```

---

## Color Coding Reference

| State | Color | Tailwind |
|-------|-------|----------|
| Bullish/Up | Green | `text-green-600` |
| Bearish/Down | Red | `text-red-600` |
| Neutral | Gray | `text-gray-600` |
| Warning | Yellow | `text-yellow-600` |
| Info | Blue | `text-blue-600` |

---

## Responsive Breakpoints

```tsx
// Mobile: <640px (single column)
<div className="grid grid-cols-1 ...">

// Tablet: 640-1024px (2 columns)
<div className="grid grid-cols-1 md:grid-cols-2 ...">

// Desktop: >1024px (3+ columns)
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 ...">
```

---

## Data Validation Checklist

- [ ] Symbol: 1-5 uppercase, no spaces
- [ ] Price: Positive, 2 decimal places
- [ ] Quantity: Positive integer, <= 1,000,000
- [ ] Bid < Ask: Always validate
- [ ] High >= Low: Always validate
- [ ] Volume: Non-negative
- [ ] P/E Ratio: Positive or null
- [ ] Dividend Yield: 0-100%

---

## Error Response Format

```json
{
  "error": "Error message",
  "status": 400,
  "code": "INVALID_INPUT",
  "timestamp": 1710155400000,
  "details": {
    "field": "fieldName",
    "reason": "Why it failed"
  }
}
```

**Common Error Codes**:
- `400` - INVALID_INPUT
- `401` - UNAUTHORIZED
- `403` - FORBIDDEN
- `404` - NOT_FOUND
- `409` - CONFLICT
- `429` - RATE_LIMIT
- `500` - SERVER_ERROR

---

## WebSocket Message Types (Phase 2)

```json
// Quote update
{"type": "quote_update", "data": {Quote}}

// Indicator update
{"type": "indicator_update", "data": {Indicators}}

// Order update
{"type": "order_update", "data": {Order}}

// Alert trigger
{"type": "alert_trigger", "data": {Alert}}
```

---

## Component Hierarchy

```
StockExchangeBoard (Main page)
├── Header
├── TradingProfile (Trader type selector)
├── PortfolioOverview
├── Main Grid
│   ├── WatchlistPanel
│   └── Right Column
│       ├── CandlestickChart
│       └── TechnicalIndicators
├── PositionsPanel
├── MarketIndices
└── Modals
    ├── OrderPanel
    └── OrderConfirmationModal
```

---

## Zustand Store Structure

```typescript
// market.ts
useMarketStore: {
  quotes: Map<string, Quote>
  indicators: Map<string, Indicators>
  indices: MarketIndex[]
  selectedSymbol: string
}

// portfolio.ts
usePortfolioStore: {
  portfolio: Portfolio
  holdings: Holding[]
  orders: Order[]
  isLoading: boolean
}

// watchlist.ts
useWatchlistStore: {
  watchlists: Watchlist[]
  selectedWatchlistId: string
}

// preferences.ts
usePreferencesStore: {
  traderType: TraderType
  timeHorizon: TimeHorizon
  chart: ChartPreferences
  theme: 'light' | 'dark'
}

// ui.ts
useUIStore: {
  theme: 'light' | 'dark'
  notifications: Notification[]
  modals: Map<string, boolean>
}
```

---

## Testing Patterns

### Component Test
```typescript
describe('QuoteCard', () => {
  it('displays quote data correctly', () => {
    const mockQuote = { symbol: 'AAPL', price: 150.25, ... }
    render(<QuoteCard quote={mockQuote} />)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('$150.25')).toBeInTheDocument()
  })
})
```

### Store Test
```typescript
describe('marketStore', () => {
  it('adds quote to store', () => {
    const store = useMarketStore()
    store.setQuote(mockQuote)
    expect(store.getQuote('AAPL')).toEqual(mockQuote)
  })
})
```

---

## Performance Targets

| Metric | Target | Tool |
|--------|--------|------|
| Quote Latency | <500ms | Network tab |
| Page Load | <2s | Lighthouse |
| Chart Render | <1s | DevTools |
| Memory | <100MB | Chrome DevTools |
| FPS (updates) | 60 | DevTools |

---

## Accessibility Checklist

- [ ] Semantic HTML (h1-h6, button, form)
- [ ] ARIA labels on icons
- [ ] Color not sole indicator
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus indicators visible (ring-2)
- [ ] Contrast 4.5:1 for text
- [ ] Form labels associated
- [ ] Error messages clear

---

## File Locations

```
/src/types/index.ts                 ← All TypeScript interfaces
/src/services/api.ts                ← API client
/src/services/websocket.ts          ← WebSocket client
/src/stores/market.ts               ← Market data store
/src/stores/portfolio.ts            ← Portfolio store
/src/hooks/useMarketData.ts         ← Market data hook
/src/components/charts/              ← Chart components
/src/components/common/              ← Button, Card, etc.
/src/pages/StockExchangeBoard.tsx   ← Main page
```

---

## Quick Problem Solving

### Quotes not updating?
1. Check WebSocket connection
2. Verify API endpoint returns data
3. Check store subscription
4. Verify component receiving updates

### Chart not displaying?
1. Verify candle data is loaded
2. Check interval parameter
3. Ensure data points > 2
4. Check chart container has height

### Indicators showing wrong signal?
1. Verify calculation algorithms
2. Check data period (20, 50, 200 days)
3. Validate input data (high >= low)
4. Check signal threshold values

### Orders not processing?
1. Verify available buying power
2. Check symbol validity
3. Validate quantity and price
4. Check account restrictions

---

## Performance Optimization Tips

1. **Memoize components**: `React.memo()` for expensive renders
2. **Virtualize lists**: 100+ items → use react-window
3. **Debounce inputs**: Search/filter with 300ms delay
4. **Lazy load**: Charts, heavy components
5. **Cache API**: Store.getState() for frequent access
6. **CSS optimization**: Use Tailwind's tree-shaking
7. **Code splitting**: Route-based splitting in main app

---

## Common Gotchas

❌ **Don't**:
- Use `any` types in TypeScript
- Calculate P&L with wrong formula
- Show stale quotes without timestamp
- Forget bid/ask validation
- Use hardcoded prices for calculations
- Forget to handle network errors

✅ **Do**:
- Use exact types from DATA_MODELS_AND_API_CONTRACTS.md
- Validate all user inputs
- Show last update time on quotes
- Always validate bid < ask
- Use API data for all calculations
- Implement error boundaries and retry logic

---

## Deployment Checklist

- [ ] Build size < 500KB gzipped
- [ ] All API endpoints working
- [ ] WebSocket fallback to polling
- [ ] Environment variables set
- [ ] Error tracking configured
- [ ] Performance monitoring enabled
- [ ] HTTPS/SSL configured
- [ ] CORS configured for API
- [ ] Rate limiting enabled
- [ ] Database indexed

---

## Support & Documentation Links

- **Strategy Details** → INVESTMENT_STRATEGY_FRAMEWORK.md (Part 1)
- **UI Components** → UI_PATTERNS_REFERENCE.md
- **API Specs** → DATA_MODELS_AND_API_CONTRACTS.md
- **Implementation** → PHASE1_MVP_GUIDE.md (existing)
- **Backend** → BACKEND_API_INTEGRATION_GUIDE.md (existing)

---

## Key Contacts by Role

| Role | Responsibility |
|------|-----------------|
| **Frontend Dev** | Implement UI components, integrate APIs |
| **Backend Dev** | Build API endpoints, database |
| **QA** | Test features, accessibility, performance |
| **Product** | Define priorities, strategy decisions |
| **DevOps** | Deployment, monitoring, infrastructure |

---

**Last Updated**: March 11, 2026
**Scope**: Complete MVP + Roadmap
**Status**: Production Ready for Development
