# Stock Exchange Board - Architecture Documentation

## Overview

This document describes the architectural decisions, design patterns, and component hierarchy of the Stock Exchange Board frontend application.

## Design Principles

1. **Component-Based Architecture**: Modular, reusable components with single responsibilities
2. **State Management**: Centralized state with Zustand for predictable data flow
3. **Separation of Concerns**: Clear separation between UI, business logic, and data management
4. **Accessibility First**: WCAG 2.1 AA compliance from the start
5. **Performance**: Optimized for speed with < 2 second dashboard load
6. **Testability**: Unit tests for critical business logic and utilities
7. **Type Safety**: Full TypeScript coverage for runtime safety

## Directory Structure

```
src/
├── components/
│   ├── common/              # Base UI components (reusable across app)
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Toast.tsx
│   │   ├── index.ts         # Barrel export
│   │   └── __tests__/
│   │       └── Button.test.tsx
│   ├── layout/              # Application layout components
│   │   ├── Header.tsx       # Top navigation
│   │   ├── Sidebar.tsx      # Side navigation
│   │   └── NotificationCenter.tsx
│   ├── market/              # Market data components
│   │   ├── QuoteCard.tsx
│   │   ├── MarketIndices.tsx
│   │   └── SectorHeatmap.tsx
│   ├── portfolio/           # Portfolio management components
│   │   ├── PortfolioOverview.tsx
│   │   └── HoldingsList.tsx
│   ├── orders/              # Order management components
│   │   ├── OrderPanel.tsx
│   │   └── OrdersList.tsx
│   └── charts/              # Charting components
│       └── CandlestickChart.tsx
├── pages/                   # Page-level layouts
│   ├── Dashboard.tsx
│   └── Market.tsx
├── stores/                  # Zustand state management
│   ├── market.ts
│   ├── portfolio.ts
│   ├── watchlist.ts
│   ├── ui.ts
│   └── __tests__/
│       └── market.test.ts
├── hooks/                   # Custom React hooks
│   ├── useMarketData.ts
│   └── usePortfolioData.ts
├── utils/                   # Utility functions
│   ├── formatting.ts        # Format prices, volumes, times
│   ├── validation.ts        # Form and data validation
│   ├── constants.ts         # App-wide constants
│   └── __tests__/
│       ├── formatting.test.ts
│       └── validation.test.ts
├── types/                   # TypeScript type definitions
│   └── index.ts
├── test/
│   └── setup.ts             # Test configuration
├── App.tsx                  # Main application component
├── main.tsx                 # React DOM entry point
└── index.css                # Tailwind CSS imports

```

## Component Hierarchy

### Component Levels

#### Level 1: Presentational Components
Stateless UI components that render data without managing their own state.

- `Button` - Reusable button with variants
- `Card` - Container with optional header/footer
- `Badge` - Small status indicators
- `Input` / `Select` - Form inputs
- `Toast` - Notification display

#### Level 2: Composite Components
Components combining multiple presentational components with local state.

- `QuoteCard` - Quote display with expandable details
- `OrderPanel` - Order form with validation
- `HoldingsList` - Expandable holdings list
- `MarketIndices` - Indices display grid

#### Level 3: Container Components
Components that connect to stores and manage complex logic.

- `Dashboard` - Main dashboard page
- `Market` - Market data page
- `Header` - App header with search and notifications
- `Sidebar` - Navigation and user menu

#### Level 4: App Level
- `App` - Root component with routing and global setup
- `NotificationCenter` - Centralized toast management

## State Management Architecture

### Zustand Stores

Each store manages a specific domain:

#### Market Store (`useMarketStore`)
Manages real-time market data.

**State:**
- `quotes: Map<string, Quote>` - Stock quotes by symbol
- `indices: MarketIndex[]` - Market indices
- `sectors: SectorPerformance[]` - Sector data
- `breadth: MarketBreadth` - Market breadth metrics
- `marketStatus: MarketStatus` - Open/closed/pre-market
- `selectedSymbol: string | null` - Currently selected stock
- `lastUpdate: number` - Timestamp of last update

**Actions:**
- `updateQuote(quote)` - Update single quote
- `updateQuotes(quotes)` - Batch update quotes
- `updateIndices(indices)` - Update market indices
- `setMarketStatus(status)` - Update market status
- `setSelectedSymbol(symbol)` - Select stock for detail view

#### Portfolio Store (`usePortfolioStore`)
Manages portfolio, holdings, and orders.

**State:**
- `portfolio: Portfolio | null` - Portfolio overview
- `holdings: Holding[]` - Current positions
- `orders: Order[]` - Order history and pending
- `selectedHolding: Holding | null` - Currently selected position
- `isLoading: boolean` - Loading state
- `error: string | null` - Error message

**Actions:**
- `setPortfolio(portfolio)` - Set portfolio data
- `setHoldings(holdings)` - Update holdings list
- `addOrder(order)` - Add new order
- `updateOrder(order)` - Update order status
- `getFilledOrders()` - Get completed orders
- `getPendingOrders()` - Get open orders

#### Watchlist Store (`useWatchlistStore`)
Manages user watchlists and their quotes.

**State:**
- `watchlists: Watchlist[]` - User's watchlists
- `selectedWatchlistId: string | null` - Currently selected
- `watchlistQuotes: Map<string, Quote[]>` - Quotes per watchlist

**Actions:**
- `addWatchlist(watchlist)` - Create new watchlist
- `deleteWatchlist(id)` - Remove watchlist
- `addSymbolToWatchlist(id, symbol)` - Add stock to list
- `removeSymbolFromWatchlist(id, symbol)` - Remove stock

#### UI Store (`useUIStore`)
Manages application UI state.

**State:**
- `theme: 'light' | 'dark'` - Current theme
- `sidebarOpen: boolean` - Sidebar visibility
- `selectedPanel: string | null` - Active panel
- `showOrderPanel: boolean` - Order form visibility
- `notifications: Notification[]` - Active toasts

**Actions:**
- `toggleTheme()` - Switch light/dark mode
- `toggleSidebar()` - Open/close sidebar
- `setShowOrderPanel(show)` - Show/hide order form
- `addNotification(notification)` - Show toast
- `removeNotification(id)` - Hide toast

## Data Flow

### Real-Time Quote Updates

```
API/WebSocket
    ↓
useMarketData hook
    ↓
marketStore.updateQuote()
    ↓
Components subscribe to store
    ↓
Re-render with new data
```

### Order Submission

```
User Form Input
    ↓
OrderPanel validation
    ↓
Order submitted to API
    ↓
Portfolio store updated
    ↓
UI notifications + order list updated
```

### Navigation Flow

```
User clicks Sidebar item
    ↓
App.tsx sets currentPage state
    ↓
renderPage() returns appropriate component
    ↓
Page component loads its data via hooks
    ↓
Store subscriptions trigger component updates
```

## Type System

All types are defined in `src/types/index.ts`:

### Market Types
- `Quote` - Single stock quote
- `MarketIndex` - Index data
- `SectorPerformance` - Sector metrics
- `MarketBreadth` - Market breadth indicators
- `ChartDataPoint` - OHLCV data

### Portfolio Types
- `Portfolio` - Portfolio overview
- `Holding` - Stock position
- `Order` - Trade order
- `OrderType` - Limit, market, stop-loss, trailing stop
- `OrderStatus` - Pending, filled, cancelled, etc.

### Utility Types
- `TimeFrame` - Chart timeframes
- `Theme` - Light/dark mode
- `AlertType` - Price/volume/technical/news

## Styling Architecture

### Tailwind CSS Configuration

- **Color Palette**: Semantic colors (accent, success, danger, neutral)
- **Spacing Scale**: 4px base unit (standard Tailwind)
- **Typography**: System font stack
- **Breakpoints**: Mobile-first (sm: 640px, md: 768px, lg: 1024px)

### Dark Mode

Implemented using `class` strategy:
- `.dark` class on `<html>` element
- Dark variants for all components
- Toggle via `useUIStore.toggleTheme()`

### Component Styling Patterns

1. **Base Styles**: Common to all component instances
   ```tsx
   className="px-4 py-2 rounded-lg transition-colors"
   ```

2. **Variant Styles**: Different visual presentations
   ```tsx
   const variantStyles = { primary: '...', danger: '...' }
   ```

3. **Responsive Styles**: Mobile-first breakpoints
   ```tsx
   className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
   ```

4. **State Styles**: Active, hover, disabled states
   ```tsx
   className="hover:bg-blue-600 disabled:opacity-50"
   ```

## Custom Hooks

### useMarketData
Fetches and updates market quotes and indices.
- Simulates API calls with mock data
- Sets up 5-second refresh interval
- Returns fetch functions for manual updates

### usePortfolioData
Loads portfolio, holdings, and orders on mount.
- Calls all three data fetch functions
- Sets loading state during fetch
- Error handling with store error state

## Utilities

### Formatting Functions
Convert raw data to display-ready strings:
- `formatPrice(150.123)` → "150.12"
- `formatVolume(50000000)` → "50.00M"
- `formatPercent(2.5)` → "+2.50%"
- `formatCurrency(1000)` → "$1,000.00"

### Validation Functions
Validate user input before submission:
- `validateOrderQuantity(10)` → true/false
- `validateOrderPrice(150.50)` → true/false
- `validateSymbol("AAPL")` → true/false
- `getOrderValidationError(...)` → error message or null

## Testing Strategy

### Unit Testing
Test individual functions in isolation:
- Formatting utilities (12 tests)
- Validation utilities (16 tests)
- Store actions (market store)
- Component rendering (Button)

### Test Patterns
- **Arrange-Act-Assert**: Setup, execute, verify
- **Mocking**: Mock stores, API calls, user interactions
- **Coverage**: 80%+ target for critical paths

### Test Organization
```
component/
├── Component.tsx
└── __tests__/
    └── Component.test.tsx
```

## Performance Optimization

### Code Splitting
- Vite automatic chunking
- Vendor bundle separate
- Charts in own bundle

### Rendering Optimization
- Zustand for minimal re-renders
- Memoization for expensive calculations
- Lazy loading for routes (future)

### Bundle Size
- Tree-shaking of unused code
- Tailwind CSS purging
- Icon optimization with Lucide React

## Error Handling

### Error Boundaries (Future)
- Wrap pages with error boundary
- Fallback UI for errors
- Error logging

### Form Validation
- Real-time validation feedback
- Field-level error messages
- Form-level submission validation

### API Error Handling
- User-friendly error messages
- Retry logic for failures
- Error logging and tracking

## Accessibility

### Keyboard Navigation
- Tab order follows visual flow
- Keyboard shortcuts (future)
- Escape key closes modals/panels

### Screen Readers
- Semantic HTML (`<button>`, `<form>`, etc.)
- ARIA labels on icons and interactive elements
- Form labels associated with inputs

### Visual
- Color contrast ratios > 4.5:1
- Focus indicators on interactive elements
- Readable font sizes (minimum 12px)

## Security Considerations

- Input sanitization in validation functions
- XSS prevention through React auto-escaping
- CSRF tokens (when backend implemented)
- Secure API communication (HTTPS)

## Future Enhancements

### Short Term (Phase 2)
- WebSocket for real-time updates
- Advanced charting (TradingView)
- Technical indicators
- Stock screener
- Price alerts
- Paper trading simulator

### Medium Term (Phase 3)
- User authentication
- Data persistence
- Social features
- AI recommendations
- Mobile app
- Desktop app (Electron)

### Long Term
- Regulatory compliance (SEC, FINRA)
- Institutional features
- API for partners
- Machine learning models
- Global market coverage
