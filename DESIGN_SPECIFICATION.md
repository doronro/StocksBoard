# Stock Exchange Board Application - UI/UX Design Specification

**Version**: 1.0.0
**Date**: March 11, 2026
**Status**: Comprehensive Design Specification for MVP
**Target Users**: Retail investors (beginner to intermediate)
**Primary Platforms**: Desktop (1920px+), Tablet (768px-1024px), Mobile (375px-767px)

---

## Table of Contents

1. [Design Philosophy & Principles](#design-philosophy--principles)
2. [Information Architecture](#information-architecture)
3. [Visual Design System](#visual-design-system)
4. [User Flows](#user-flows)
5. [Screen Layouts & Wireframes](#screen-layouts--wireframes)
6. [Component Specifications](#component-specifications)
7. [Interaction Patterns](#interaction-patterns)
8. [Mobile-First Approach](#mobile-first-approach)
9. [Accessibility & Compliance](#accessibility--compliance)
10. [Design Tokens](#design-tokens)
11. [Animation & Micro-interactions](#animation--micro-interactions)

---

## Design Philosophy & Principles

### Core Principles

1. **Clarity Over Cleverness**
   - Information hierarchy is explicit
   - Complex metrics explained with educational tooltips
   - No unnecessary visual decoration
   - Labels are always clear and precise

2. **Consistency Builds Trust**
   - Identical patterns repeated across all pages
   - Unified component library
   - Predictable interactions reduce cognitive load
   - Financial data demands visual consistency

3. **Progressive Disclosure**
   - Essential information always visible
   - Advanced metrics available on demand
   - Default views uncluttered but expandable
   - Beginner-friendly defaults with power-user access

4. **Real-Time Trust**
   - Immediate visual feedback for data changes
   - Clear indication of update frequency
   - Historical context for price movements
   - Transparent about data freshness

5. **Risk Visibility**
   - Losses highlighted (red) without shame
   - Portfolio risk metrics easily accessible
   - Alerts and warnings prominent but non-intrusive
   - Stop-loss and risk controls discoverable

### Design Values

- **Professional**: Financial domain demands trustworthiness and precision
- **Accessible**: Retail investors vary in financial literacy; design accommodates all levels
- **Responsive**: Works flawlessly across all device sizes
- **Fast**: Real-time data feels immediate; no sluggish interactions
- **Inclusive**: Color-blind friendly, keyboard navigable, screen reader compatible

---

## Information Architecture

### Site Structure (Hierarchical)

```
Stock Exchange Board Application
├── Dashboard / Home
│   ├── Portfolio Summary
│   ├── Market Indices
│   ├── Trending Stocks
│   └── Quick Actions
├── Market Discovery
│   ├── Market Indices Detail
│   ├── Gainers & Losers
│   ├── Market Sectors
│   ├── Stock Search & Screening
│   └── Trending Feed
├── Stock Detail Pages
│   ├── Price Chart (with indicators)
│   ├── Key Metrics Panel
│   ├── Company Info
│   ├── News Feed
│   ├── Order Execution
│   └── Technical Analysis
├── Portfolio Management
│   ├── Holdings List
│   ├── Allocation Breakdown
│   ├── Performance Metrics
│   ├── Position Details
│   └── Transaction History
├── Watchlist Management
│   ├── My Watchlists
│   ├── Watchlist Items
│   ├── Price Alerts
│   └── Quick Actions
├── Alerts & Notifications
│   ├── Price Alerts
│   ├── Technical Indicator Alerts
│   ├── Portfolio Alerts
│   └── Alert History
└── Tools & Settings
    ├── Portfolio Tools (position sizing, risk calc)
    ├── Technical Analysis Preferences
    ├── Theme & Display Settings
    └── Notification Preferences
```

### Navigation Model

**Primary Navigation** (persistent, left sidebar on desktop / hamburger on mobile):
- Dashboard
- Market
- Watchlists
- Portfolio
- Alerts

**Secondary Navigation** (contextual, within pages):
- Stock detail pages: Related stocks, news, similar companies
- Portfolio: Holdings, allocation, metrics tabs
- Watchlist: Multiple watchlist selection

**Tertiary Navigation** (utility, top right):
- Search (global stock search)
- Settings/Preferences
- User account
- Help/Support

---

## Visual Design System

### Color Palette

#### Primary Colors

| Usage | Light Mode | Dark Mode | Hex Light | Hex Dark | Notes |
|-------|-----------|-----------|-----------|----------|-------|
| Primary Action | Blue-600 | Blue-400 | #2563EB | #60A5FA | Buttons, links, interactive elements |
| Positive Change | Green-600 | Green-400 | #16A34A | #4ADE80 | Gains, bullish signals, up movements |
| Negative Change | Red-600 | Red-400 | #DC2626 | #F87171 | Losses, bearish signals, down movements |
| Neutral | Gray-600 | Gray-400 | #4B5563 | #9CA3AF | No change, neutral signals |
| Background | White | Gray-950 | #FFFFFF | #030712 | Main page background |
| Surface | Gray-50 | Gray-900 | #F9FAFB | #111827 | Cards, panels |
| Border | Gray-200 | Gray-800 | #E5E7EB | #1F2937 | Dividers, borders |
| Text Primary | Gray-900 | Gray-50 | #111827 | #F9FAFB | Main text |
| Text Secondary | Gray-600 | Gray-400 | #4B5563 | #9CA3AF | Secondary text, labels |
| Text Tertiary | Gray-500 | Gray-500 | #6B7280 | #6B7280 | Disabled text, hints |

#### Semantic Color Usage

- **Green (#16A34A / #4ADE80)**: Profits, gains, bullish indicators, up movements
- **Red (#DC2626 / #F87171)**: Losses, bearish indicators, down movements
- **Blue (#2563EB / #60A5FA)**: Primary actions, selection, focus states
- **Yellow (#FBBF24 / #FBBF24)**: Warnings, pending states, caution alerts
- **Gray**: Neutral UI elements, disabled states, secondary information

#### Accessibility Compliance

- **Contrast Ratios**:
  - Primary text on background: 7:1+ (AAA)
  - Secondary text: 4.5:1+ (AA)
  - UI components: 3:1+ (AA)
  - Critical financial data: 7:1+ (AAA)

- **Color-Blind Friendly**:
  - Don't rely on color alone to convey meaning
  - Use patterns/icons alongside colors
  - Green/red with additional visual indicators (arrows, badges)
  - Test with deuteranopia and protanopia simulators

### Typography

#### Font Stack

**Primary Font**: Inter (system fallback: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif)

Rationale: Inter is highly legible at all sizes, excellent for financial dashboards, professional appearance, and strong technical rendering.

#### Type Scale & Hierarchy

| Level | Name | Size | Weight | Line Height | Usage |
|-------|------|------|--------|-------------|-------|
| H1 | Page Title | 32px (2.0rem) | 700 Bold | 1.2 | Main page headings |
| H2 | Section Title | 24px (1.5rem) | 600 SemiBold | 1.3 | Major sections |
| H3 | Subsection | 20px (1.25rem) | 600 SemiBold | 1.4 | Card headers |
| H4 | Card Title | 18px (1.125rem) | 600 SemiBold | 1.4 | Component headers |
| Body LG | Primary Text | 16px (1.0rem) | 400 Regular | 1.5 | Main content, descriptions |
| Body MD | Secondary Text | 14px (0.875rem) | 400 Regular | 1.5 | Secondary descriptions |
| Body SM | Tertiary Text | 12px (0.75rem) | 400 Regular | 1.5 | Labels, hints, captions |
| Label | Form Labels | 14px (0.875rem) | 500 Medium | 1.5 | Form field labels |
| Mono | Numbers/Code | 14px (0.875rem) | 400 Regular | 1.5 | Stock symbols, prices, code |
| Mono LG | Large Numbers | 24px+ | 400 Regular | 1.2 | Portfolio values, prices |
| Mono XL | Price Display | 32px (2.0rem) | 400 Regular | 1.2 | Stock price in header |

#### Mobile Typography Adjustments

- H1: 24px → 20px
- H2: 20px → 18px
- H3: 18px → 16px
- Body LG: 16px (no change, minimum readable)
- Mono LG: 20px → 18px
- Mono XL: 28px → 24px

### Spacing System

**8px Grid Base** - All spacing uses multiples of 8px for consistency.

| Token | Value | Usage |
|-------|-------|-------|
| XS | 4px | Tight spacing within components |
| SM | 8px | Spacing between small elements, icon margins |
| MD | 12px | Standard spacing between elements |
| LG | 16px | Spacing between sections |
| XL | 24px | Large spacing, card padding |
| 2XL | 32px | Section breaks, major padding |
| 3XL | 48px | Page margins, major sections |
| 4XL | 64px | Hero sections, large gaps |

**Application**:
- Card padding: 16px (LG) / 24px (XL) on desktop, 12px (MD) / 16px (LG) on mobile
- Gap between cards: 16px (LG) desktop, 12px (MD) mobile
- Page padding: 32px (2XL) desktop, 16px (LG) mobile
- Section gaps: 24px-32px (XL-2XL) desktop, 16px (LG) mobile

### Layout Grid

**Desktop (>1024px)**:
- Max width: 1920px
- Sidebar width: 280px (collapsible to 60px)
- Main content width: remaining
- Column grid: 12-column system
- Gutter: 16px

**Tablet (768px-1024px)**:
- Full width content with reduced padding
- Sidebar collapses to icon-only mode
- Column grid: 8-column system
- Gutter: 12px

**Mobile (<768px)**:
- Full width with padding
- Single column layout
- Sidebar collapses to bottom navigation
- Bottom nav height: 64px
- Gutter: 8px

### Corner Radius

| Size | Value | Usage |
|------|-------|-------|
| None | 0px | Cards, panels (flat design) |
| SM | 4px | Small UI elements, badges |
| MD | 6px | Buttons, inputs, small cards |
| LG | 8px | Large cards, modals |
| XL | 12px | Feature cards, hero sections |
| Full | 9999px | Pills, avatars, circular buttons |

**Application**: Most UI uses 4-8px (SM-MD) for slightly modern, slightly flat look. Larger radius (8px) for emphasis cards.

### Shadows

| Level | Light Mode | Dark Mode | Usage |
|-------|-----------|----------|-------|
| Subtle | 0 1px 2px rgba(0,0,0,0.05) | 0 1px 3px rgba(0,0,0,0.3) | Borders, subtle elevation |
| Light | 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06) | 0 4px 6px rgba(0,0,0,0.4) | Card shadows |
| Medium | 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06) | 0 10px 15px rgba(0,0,0,0.5) | Elevated cards, dropdowns |
| Heavy | 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05) | 0 20px 25px rgba(0,0,0,0.6) | Modals, popovers |

**Philosophy**: Minimal shadows for clean look. Shadows used for elevation hierarchy, not decoration.

---

## User Flows

### Primary User Flows

#### Flow 1: Browse Stock → Check Metrics → Set Alert → Execute Order

**Scenario**: Retail investor researching a stock before trading

```
Start: Dashboard or Market page
  ↓
[1] Search for stock (or click from watchlist/trending)
  ↓
[2] Stock Detail Page loads
    - Auto-scroll to price chart
    - Display key metrics
    - Show technical indicators
  ↓
[3] Review metrics and analysis
    - Read key metrics panel
    - Check technical indicators
    - Review news/company info
  ↓
[4] Decision point: Need more time?
    - YES → Add to watchlist + Set price alert → Exit
    - NO → Continue to order
  ↓
[5] Configure price alert (if chosen)
    - Set alert type (above/below)
    - Set target price
    - Enable/disable notification
  ↓
[6] Execute order (if ready)
    - Click "Buy" or "Sell"
    - Order modal opens
    - Enter quantity
    - Select order type (market/limit)
    - Review order
    - Confirm execution
  ↓
[7] Order confirmation
    - Show order receipt
    - Offer to view position or continue trading
  ↓
End: Return to Dashboard or continue trading
```

#### Flow 2: Portfolio Review → Analyze Holdings → Rebalance Exposure

**Scenario**: Investor reviewing portfolio performance

```
Start: Dashboard (portfolio summary visible)
  ↓
[1] Click "Portfolio" or see summary on Dashboard
  ↓
[2] Portfolio Page loads
    - Show total value and P&L
    - Display allocation pie chart
    - List all holdings with metrics
  ↓
[3] Analyze performance
    - Sort holdings by gain/loss
    - Review individual position details
    - Check allocation percentages
  ↓
[4] Decision point: Rebalance needed?
    - YES → Click position → Adjust quantity
    - NO → Review metrics
  ↓
[5] (If rebalancing) Modify position
    - Sell some shares or buy more
    - Follow order execution flow
  ↓
[6] Review updated portfolio
    - See new allocation
    - Check updated metrics
  ↓
End: Return to Dashboard or continue managing
```

#### Flow 3: Market Discovery → Add to Watchlist → Monitor

**Scenario**: Investor discovering new investment opportunities

```
Start: Market page
  ↓
[1] Browse market indices and trending stocks
  ↓
[2] Filter by sector or metric (P/E, market cap, etc.)
  ↓
[3] View stock details
    - Quick preview card
    - Click for full stock detail
  ↓
[4] Add to watchlist
    - Select which watchlist
    - Or create new watchlist
  ↓
[5] (Optional) Set price alert
    - Define alert parameters
    - Enable notifications
  ↓
[6] Return to watchlist or continue browsing
  ↓
End: Monitor watchlist for price movement
```

#### Flow 4: Alert Triggered → Review → Take Action

**Scenario**: Investor receives notification that price target is reached

```
Start: Notification appears (in-app, push, or email)
  ↓
[1] Click notification
  ↓
[2] Navigate to stock detail page
  ↓
[3] Review current market conditions
    - Check chart
    - Review technical indicators
    - Look at news
  ↓
[4] Decision point: Take action?
    - YES → Execute buy/sell order
    - NO → Update alert or dismiss
  ↓
[5] If updating alert
    - Adjust target price
    - Change alert type
    - Re-enable for another trigger
  ↓
End: Execute order or continue monitoring
```

#### Flow 5: First-Time Setup → Portfolio Import → Training

**Scenario**: New investor setting up account

```
Start: Sign up / onboarding
  ↓
[1] Complete trader type questionnaire
    - Beginner/Intermediate/Advanced
    - Investment goal (growth/income/balance)
    - Time horizon (short/medium/long)
  ↓
[2] Import portfolio (optional)
    - Upload holdings list
    - Or manually add holdings
    - Set cost basis
  ↓
[3] Learn interface (onboarding)
    - Guided tour of dashboard
    - Tooltip-based introduction
    - Link to educational resources
  ↓
[4] Set preferences
    - Chart preferences (candlestick, time frame)
    - Alert preferences (notification method)
    - Display preferences (light/dark mode)
  ↓
[5] Create default watchlist
    - Add favorite stocks or indices
    - Market suggestions if new
  ↓
End: Dashboard ready, onboarding complete
```

---

## Screen Layouts & Wireframes

### 1. Dashboard / Home Screen

**Purpose**: Portfolio overview, quick stats, market snapshot, quick actions

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                         HEADER / SEARCH BAR                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SIDEBAR]    DASHBOARD - Portfolio & Market Overview            │
│               ┌──────────────────────────────────────────────┐   │
│               │ Quick Stats Row (4 columns)                  │   │
│               │ [Total Value] [Today P&L] [Total Return]     │   │
│               │ [Buying Power]                               │   │
│               └──────────────────────────────────────────────┘   │
│                                                                   │
│               ┌─────────────────────┬──────────────────────────┐ │
│               │ Portfolio Overview  │ Market Indices Widget    │ │
│               │ (Small pie chart)   │ [SPY] [QQQ] [DIA]       │ │
│               │ 5 top holdings      │ With prices & % change   │ │
│               │ Show allocation %   │                          │ │
│               └─────────────────────┴──────────────────────────┘ │
│                                                                   │
│               ┌──────────────────────────────────────────────┐   │
│               │ Trending Stocks Feed                         │   │
│               │ [Gainers] [Losers] [Most Active]            │   │
│               │ 5 stocks with price, change, chart sparkline│   │
│               └──────────────────────────────────────────────┘   │
│                                                                   │
│               ┌──────────────────────────────────────────────┐   │
│               │ Recent Activity                              │   │
│               │ Last 5 orders/transactions                   │   │
│               │ Link to full portfolio view                  │   │
│               └──────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components**:

**Quick Stats Row** (4 columns, responsive to 2x2 on tablet, stacked on mobile):
- Total Portfolio Value: Large number, with daily change badge below
- Today's P&L: Number with color (green/red), % change
- Total Return: Lifetime return %, with trend
- Buying Power/Cash: Available cash for trading

**Portfolio Overview Card**:
- Small pie chart (200x200px) showing sector allocation
- Click for full allocation view
- 5 top holdings with position size %
- Total positions count

**Market Indices Widget**:
- 3-4 major indices: SPY (S&P 500), QQQ (Nasdaq), DIA (Dow)
- Current price, change %, sparkline (7-day)
- Status indicator (open/closed/pre-market)
- Color-coded (green for up, red for down)

**Trending Stocks Feed**:
- Tabs: Gainers, Losers, Most Active
- 5 stocks per section
- Columns: Symbol, Name, Price, Change %, Sparkline chart
- Click to view stock detail
- "View More" link to full market view

**Recent Activity**:
- Last 5 orders/transactions
- Columns: Date, Symbol, Action (Buy/Sell), Quantity, Price, Status
- Link to full portfolio/order history

**Mobile Adjustments**:
- Quick stats stack vertically
- Single column layout
- Charts reduced in size
- Trending feed shows only 3 stocks
- Swipe-able trend tabs

---

### 2. Stock Detail Page

**Purpose**: Detailed stock research, technical analysis, order execution

**Layout Structure** (3-column desktop, 1-column mobile):

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEADER / SEARCH BAR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SIDEBAR]  STOCK DETAIL: AAPL - Apple Inc.                      │
│             ┌────────────────────────────────────────┐           │
│             │ Price Header Row                       │           │
│             │ Price: $172.50  [↑ +1.25 (0.73%)]     │           │
│             │ Bid: $172.48 | Ask: $172.52            │           │
│             │ Market Status: [Open] Volume: 42.3M    │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│  ┌─────────────────────────────────┬──────┬────────────────────┐ │
│  │ Left Column (65%)               │ Gap  │ Right Column (35%) │ │
│  │ ┌───────────────────────────┐  │      │ ┌────────────────┐ │ │
│  │ │ Candlestick Chart         │  │      │ │ Key Metrics    │ │ │
│  │ │ (800x400px)               │  │      │ │ [Card]         │ │ │
│  │ │ [Timeframe buttons]       │  │      │ │ P/E: 28.5      │ │ │
│  │ │ [1m] [5m] [15m] [1h] [1d] │  │      │ │ Div Yield: 0.4%│ │ │
│  │ │ [1w] [1m]                │  │      │ │ 52W High: $189 │ │ │
│  │ │ [Volume underneath]       │  │      │ │ 52W Low: $154  │ │ │
│  │ │ Moving Avg toggle buttons │  │      │ │ Market Cap: 2.8T │ │
│  │ └───────────────────────────┘  │      │ │ Sector: Tech   │ │ │
│  │                                 │      │ └────────────────┘ │ │
│  │ ┌───────────────────────────┐  │      │ ┌────────────────┐ │ │
│  │ │ Technical Indicators      │  │      │ │ Company Info   │ │ │
│  │ │ [RSI Sub-chart]           │  │      │ │ [Card]         │ │ │
│  │ │ [MACD Sub-chart]          │  │      │ │ Description    │ │ │
│  │ │ Signal Aggregation Score  │  │      │ │ Website        │ │ │
│  │ │ Bullish (7/7 agree)       │  │      │ │ Industry       │ │ │
│  │ └───────────────────────────┘  │      │ │ Employees      │ │ │
│  │                                 │      │ └────────────────┘ │ │
│  │ ┌───────────────────────────┐  │      │ ┌────────────────┐ │ │
│  │ │ News Feed                 │  │      │ │ Order Panel    │ │ │
│  │ │ Recent news articles       │  │      │ │ [Card]         │ │ │
│  │ │ [Headline] [Date] [Source] │  │      │ │ [Order form]   │ │ │
│  │ │ [Show more link]           │  │      │ │ Type: Market   │ │ │
│  │ └───────────────────────────┘  │      │ │ Qty: [_______] │ │ │
│  │                                 │      │ │ Price: Auto    │ │ │
│  │ ┌───────────────────────────┐  │      │ │ [Buy] [Sell]   │ │ │
│  │ │ Related Stocks            │  │      │ │ [More options] │ │ │
│  │ │ Similar companies by      │  │      │ └────────────────┘ │ │
│  │ │ sector/market cap         │  │      │ ┌────────────────┐ │ │
│  │ │ [Stock card] [Stock card] │  │      │ │ Risk Tools     │ │ │
│  │ │ [Stock card] [Stock card] │  │      │ │ [Card]         │ │ │
│  │ └───────────────────────────┘  │      │ │ Set Alert      │ │ │
│  │                                 │      │ │ Stop Loss Calc │ │ │
│  │                                 │      │ │ Position Size  │ │ │
│  │                                 │      │ └────────────────┘ │ │
│  └─────────────────────────────────┴──────┴────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Section Details**:

**Price Header Section**:
- Large price display (32px)
- Change badge with color and icon (arrow)
- Bid/Ask spread (smaller text below)
- Market status and volume

**Candlestick Chart** (Primary focus):
- Default: 1-day chart for most users, 1-hour for day traders
- Timeframe buttons: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1m
- Toggle buttons for moving averages (20, 50, 200 SMA)
- Toggle buttons for Bollinger Bands
- Volume bars below price
- 800x400px on desktop, full width on mobile

**Technical Indicators Panel**:
- RSI (Relative Strength Index) subplot - shows overbought/oversold
- MACD (Moving Average Convergence Divergence) subplot
- Bollinger Bands overlay on main chart
- Signal aggregation score: "Bullish (7/7 agree)" with confidence bar
- Indicator descriptions on hover (tooltips)

**Key Metrics Card** (Right column):
- P/E Ratio with tooltip ("Price-to-Earnings ratio helps determine valuation")
- Dividend Yield (if applicable)
- 52-Week High/Low range
- Market Cap with readable format (T = trillion, B = billion, M = million)
- Sector classification
- EPS (Earnings Per Share)

**Company Info Card**:
- Brief company description (2-3 sentences)
- Website link
- Industry/Sector
- Number of employees
- "Learn more" link

**News Feed**:
- Recent news articles (5-10 most recent)
- Headline, date, source
- Click to open external link
- Filter by sentiment (optional phase 2)

**Related Stocks**:
- 4 similar companies by sector and market cap
- Thumbnail cards with price and change
- Quick comparison

**Order Panel** (Right column, sticky on desktop):
- Tab: Market Order (default)
- Quantity input
- Price (auto-filled for market orders, editable for limit)
- Action buttons: [Buy] [Sell] or [Buy Market] [Sell Market]
- "Advanced Options" link for limit/stop orders
- Clear indication of buying power

**Risk Tools** (Right column):
- "Set Price Alert" button → opens modal
- "Calculate Stop Loss" link → calculator
- "Position Sizing Tool" link → calculator

**Mobile Adjustments**:
- Single column (stack right column below left)
- Chart full width, reduced height (300px)
- Key metrics inline (horizontal scroll or tabs)
- Order panel below chart, sticky footer on mobile
- Collapse/expand news and related stocks

---

### 3. Portfolio Page

**Purpose**: View all holdings, allocation, performance metrics

**Layout Structure**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEADER / SEARCH BAR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SIDEBAR]  PORTFOLIO                                            │
│             ┌────────────────────────────────────────┐           │
│             │ Portfolio Summary Stats (4 columns)    │           │
│             │ [Total Value] [P&L] [Return %]         │           │
│             │ [Cash Balance]                         │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌──────────────────────┬─────────────────┐           │
│             │ Allocation Chart     │ Portfolio Metrics          │
│             │ Pie chart by sector  │ Sharpe Ratio               │
│             │ Legend below         │ Max Drawdown               │
│             │ Click for details    │ Win Rate                   │
│             │                      │ Avg Win/Loss               │
│             │                      │ Concentration Risk         │
│             └──────────────────────┴─────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Performance Chart (Time filter)        │           │
│             │ [Daily] [Weekly] [Monthly] [YTD]       │           │
│             │ Line chart showing cumulative return   │           │
│             │ Hover for daily values                 │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Holdings Table                         │           │
│             │ Sort by: Symbol | Qty | Entry | Current | Gain % │ │
│             ├────────────────────────────────────────┤           │
│             │ AAPL | 100  | $150 | $172.50 | +22.5% [E] [BUY]   │ │
│             │ MSFT | 50   | $320 | $372.15 | +16.3% [E] [BUY]   │ │
│             │ TSLA | 25   | $680 | $245.32 | -63.9% [E] [SELL]  │ │
│             │ ... (more holdings)                    │           │
│             │                                        │           │
│             │ [Expand] Show transaction history      │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Sector Allocation Breakdown            │           │
│             │ Technology:  45% [████████████]        │           │
│             │ Healthcare:  25% [███████]             │           │
│             │ Finance:     20% [██████]              │           │
│             │ Energy:      10% [███]                 │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Section Details**:

**Portfolio Summary Stats**:
- Total Portfolio Value: Largest number
- Daily P&L: With % and color
- Total Return: Lifetime % return
- Cash Balance: Buying power available

**Allocation Chart**:
- Pie chart by sector (not by individual stock, as that's too granular)
- Clickable slices → drill into holdings in that sector
- Colors for sectors (consistent across app)
- Legend below with %

**Portfolio Metrics Card**:
- Sharpe Ratio (tooltip explains: risk-adjusted return)
- Max Drawdown (tooltip: largest peak-to-trough decline)
- Win Rate (% of profitable positions)
- Avg Win/Loss (average profit vs loss)
- Concentration Risk (shows if too much in one stock)

**Performance Chart**:
- Time filter buttons: Daily, Weekly, Monthly, YTD
- Line chart showing cumulative return over time
- Hover detail showing date and value
- Compare to index (optional benchmark line)

**Holdings Table**:
- Columns: Symbol | Name | Quantity | Entry Price | Current Price | Gain/Loss $ | Gain/Loss % | Actions
- Sortable by clicking column headers
- Color-coded gains (green) and losses (red)
- Click row to view position detail
- Action buttons (expand to see more):
  - [E] = Expand detail
  - [BUY] = Buy more shares
  - [SELL] = Sell shares
- Pagination if >20 holdings

**Sector Breakdown**:
- Horizontal bar chart
- Sector | Allocation % | Number of holdings
- Click to filter holdings by sector

**Mobile Adjustments**:
- Summary stats stack vertically
- Pie chart smaller (200x200)
- Holdings table becomes card-based list
- Each holding: Symbol, Current Price, Change, with expand arrow

---

### 4. Watchlist Page

**Purpose**: Manage custom watchlists, monitor prices, set alerts

**Layout Structure**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEADER / SEARCH BAR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SIDEBAR]  WATCHLISTS                                           │
│             ┌────────────────────────────────────────┐           │
│             │ Watchlist Manager (Left 20%)           │           │
│             │ [All Stocks]  (45 items)              │           │
│             │ [Dividend Stocks] (12)                 │           │
│             │ [Tech Leaders] (8)                     │           │
│             │ [Growth Plays] (15)                    │           │
│             │ [+ New Watchlist]                      │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Selected: All Stocks (45 items)        │           │
│             ├────────────────────────────────────────┤           │
│             │ Sort: [Symbol ▼] | View: [List ▼]     │           │
│             │ Filter: [All] [Gainers] [Losers]      │           │
│             ├────────────────────────────────────────┤           │
│             │                                        │           │
│             │ Symbol | Price | Change % | Volume   │ [Alert]   │ │
│             ├────────────────────────────────────────┤           │ │
│             │ AAPL   | $172.50 | +0.73% | 42.3M    │ [Bell]    │ │
│             │ MSFT   | $372.15 | -0.32% | 21.5M    │ [Bell]    │ │
│             │ GOOGL  | $138.42 | +1.20% | 19.8M    │ [Bell]    │ │
│             │ TSLA   | $245.32 | +2.15% | 125.2M   │ [Bell]    │ │
│             │ META   | $323.18 | +0.95% | 18.2M    │ [Bell]    │ │
│             │ ... (more items, paginated)           │           │ │
│             │                                        │           │ │
│             │ [← Prev] [1] [2] [3] ... [Next →]     │           │ │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Quick Stats for Selected Watchlist     │           │
│             │ Avg Price: $250.43                     │           │
│             │ Best Performer: TSLA (+2.15%)          │           │
│             │ Worst Performer: MSFT (-0.32%)         │           │
│             │ Avg Change: +0.89%                     │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Section Details**:

**Watchlist Manager** (Left sidebar, sticky):
- List of all user watchlists
- Count of items in each
- Selected watchlist highlighted
- [+ New Watchlist] button

**Main Watchlist Table**:
- Headers: Symbol | Name | Price | Change $ | Change % | Volume | Alert Status
- Sortable columns
- Click row to view stock detail
- Alert bell icon (hollow = no alert, solid = alert set)
- Actions menu (right-click or three dots):
  - View stock detail
  - Set/Edit alert
  - Remove from watchlist
  - Add to portfolio (if exists)

**Filter Options**:
- [All] [Gainers] [Losers] [Most Active]
- Shows filtered subset of watchlist

**View Options** (dropdown):
- List view (default) - table format
- Card view - larger card for each stock with more info
- Compact view - minimal columns

**Quick Stats**:
- Statistics for current watchlist
- Avg price, best/worst performers
- Avg change percentage

**Pagination**:
- Show 10, 25, or 50 items per page
- Pagination controls

**Mobile Adjustments**:
- Watchlist manager becomes dropdown or tabs
- Table becomes card-based list
- Columns: Symbol, Price, Change (simplified)
- Alert bell and actions in card

---

### 5. Market / Discovery Page

**Purpose**: Discover stocks, view market indices, filter by criteria

**Layout Structure**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEADER / SEARCH BAR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SIDEBAR]  MARKET OVERVIEW                                      │
│             ┌────────────────────────────────────────┐           │
│             │ Market Indices (4-column row)          │           │
│             │ [SPY S&P 500] [QQQ Nasdaq]             │           │
│             │ $450.23 | +0.85%  | $375.12 | -0.20%  │           │
│             │ [DIA Dow] [VIX Volatility]             │           │
│             │ [Data]         | [Data]                │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Market Status                          │           │
│             │ [Open] | Hours: 9:30 AM - 4:00 PM EST │           │
│             │ Pre-market: 4:00 AM - 9:30 AM EST     │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Tab Navigation                         │           │
│             │ [Gainers] [Losers] [Most Active]       │           │
│             │ [Sectors] [Screening]                  │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Quick Filters (Gainers tab shown)      │           │
│             │ [All Sectors ▼] [Market Cap: ▼]       │           │
│             │ [P/E Range: ▼] [Sort: % Change ▼]     │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Top Gainers                            │           │
│             ├────────────────────────────────────────┤           │
│             │ Symbol | Price | Change | % | Volume  │           │ │
│             ├────────────────────────────────────────┤           │ │
│             │ NVDA   | $875.50 | +12.30 | +1.41%    │           │ │
│             │ SOFI   | $8.24   | +0.85  | +11.50%   │           │ │
│             │ COIN   | $142.33 | +8.50  | +6.35%    │           │ │
│             │ ... (more stocks)                      │           │ │
│             │                                        │           │ │
│             │ [← Prev] [1] [2] [3] [Next →]         │           │ │
│             └────────────────────────────────────────┘           │
│                                                                   │
│             ┌────────────────────────────────────────┐           │
│             │ Sector Performance Heatmap             │           │
│             │ [Tech ↑ +1.2%] [Healthcare ↓ -0.5%]   │           │
│             │ [Finance ↑ +0.8%] [Energy ↑ +1.5%]    │           │
│             │ [Utilities ↓ -0.3%] [Discretionary ↑] │           │
│             │ (Each sector is a clickable button)    │           │
│             └────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Section Details**:

**Market Indices**:
- SPY (S&P 500), QQQ (Nasdaq), DIA (Dow), VIX (Volatility)
- Current price, change %, % change
- Click to view index detail (chart, components, etc.)
- Color-coded (green up, red down)

**Market Status**:
- Current status: Open / Closed / Pre-market / After-hours
- Market hours and countdown to close (if open)
- Pre-market hours display

**Tab Navigation**:
- [Gainers] - Top gaining stocks today
- [Losers] - Top losing stocks today
- [Most Active] - Highest volume stocks
- [Sectors] - Sector performance heatmap
- [Screening] - Advanced stock screener (MVP: basic filters)

**Quick Filters** (Context-dependent):
- For Gainers/Losers/Most Active:
  - Sector filter (all or specific)
  - Market cap filter (micro, small, mid, large, mega cap)
  - P/E range (optional)
  - Minimum price/maximum price
  - Sort options (% change, price, volume)

**Stock Lists**:
- Table format: Symbol | Name | Price | Change | % Change | Volume
- Sortable columns
- Click row to view stock detail
- Pagination (50 stocks per page by default)
- Color-coded changes (green/red)

**Sector Heatmap** (Tab view):
- Grid of sector buttons
- Size/color indicates performance
- Sectors: Technology, Healthcare, Financials, Industrials, Consumer, Energy, Utilities, Real Estate, Materials, Communication
- Click sector to view top stocks in that sector

**Mobile Adjustments**:
- Single column, full width
- Indices in horizontal scrollable row
- Tabs remain at top
- Table becomes card-based list
- Filters collapse into drawer

---

### 6. Alert Setup Modal

**Purpose**: Configure price and technical alerts

**Layout Structure**:

```
╔═════════════════════════════════════════════════╗
║                SET PRICE ALERT                  ║  (Modal overlay)
║                                                 ║
║  Symbol: AAPL        Current Price: $172.50    ║
║                                                 ║
║  Alert Type:                                    ║
║  ⊚ Price above target                          ║
║  ⊚ Price below target                          ║
║                                                 ║
║  Target Price: [$_________] (e.g., $180.00)    ║
║                                                 ║
║  When price reaches this target, send:          ║
║  ☐ In-app notification                         ║
║  ☐ Push notification (if enabled)              ║
║  ☐ Email notification                          ║
║                                                 ║
║  Notification Label:                            ║
║  [____________] (e.g., "Entry point for AAPL")║
║                                                 ║
║  One-time alert:  ⊚ Yes   ◉ No (repeat)       ║
║                                                 ║
║  ┌──────────────────────────────────────────┐  ║
║  │ [Save Alert]  [Cancel]  [Learn more] ↗  │  ║
║  └──────────────────────────────────────────┘  ║
║                                                 ║
╚═════════════════════════════════════════════════╝
```

**Form Fields**:

1. **Alert Type** (Radio buttons):
   - Price above target (bullish case)
   - Price below target (stop loss case)
   - Technical indicator signal (phase 2)

2. **Target Price** (Input field):
   - Numeric input with $ prefix
   - Suggestion based on current price
   - Min/max validators
   - Helps investor compare to current price ("X% above current")

3. **Notification Methods** (Checkboxes):
   - In-app notification (always available)
   - Push notification (if browser supports)
   - Email notification (if user enabled)

4. **Label** (Optional text input):
   - User-defined label for the alert
   - Helps remember why alert was set

5. **Alert Frequency**:
   - One-time: Alert fires once, then disables
   - Repeating: Alert can fire multiple times

**Accessibility**:
- Clear labels for all inputs
- Instructions for each field
- Tab order is logical
- Error messages clear
- Success confirmation

**Mobile Adjustments**:
- Full-screen modal (not overlay on mobile)
- Larger input fields (44px minimum height)
- Button row stacks vertically

---

## Component Specifications

### Button Component

**States**:
1. **Default (Idle)**
   - Light Mode: Gray-900 text, white background, gray border
   - Dark Mode: Gray-50 text, gray-900 background, gray-800 border

2. **Hover**
   - Light Mode: Gray-900 text, gray-50 background
   - Dark Mode: Gray-50 text, gray-800 background

3. **Active/Pressed**
   - Light Mode: Gray-900 text, gray-100 background
   - Dark Mode: Gray-50 text, gray-700 background

4. **Disabled**
   - Light Mode: Gray-400 text, white background, gray-200 border
   - Dark Mode: Gray-600 text, gray-900 background, gray-700 border
   - Cursor: not-allowed

**Variants**:

| Variant | Usage | Colors | Size |
|---------|-------|--------|------|
| **Primary** | Main actions (Buy, Sell, Submit) | Blue background, white text | 44px height, 120px width |
| **Secondary** | Alternative actions (Cancel, Skip) | Transparent, border, text | 44px height, 120px width |
| **Success** | Positive actions (Confirm) | Green background, white text | 44px height, 120px width |
| **Danger** | Destructive actions (Delete, Sell) | Red background, white text | 44px height, 120px width |
| **Ghost** | Tertiary actions (Learn more, Dismiss) | Transparent, text only | 44px height, auto width |
| **Icon** | Icon-only buttons | Transparent, icon color | 44px x 44px |
| **Pill** | Tags, quick filters | Rounded (full border-radius) | 32px height, auto width |

**Text Inside Button**:
- Bold (600 weight)
- Centered
- 14px-16px font size
- All caps for primary actions (optional)
- Icon + text allowed

**Touch Target**:
- Minimum 44x44px (WCAG AAA)
- More padding on mobile

**Interactions**:
- Immediate visual feedback on hover/click
- Smooth color transition (150ms)
- Clear focus indicator (outline or shadow)
- Ripple effect (optional micro-interaction)

---

### Card Component

**Structure**:
```
┌──────────────────────────────┐
│ Header (optional)             │  (16px padding)
├──────────────────────────────┤
│ Content Area                  │  (16px-24px padding)
│ [Flexible content]            │
│                               │
└──────────────────────────────┘
```

**Properties**:
- Border: 1px, gray-200 (light) / gray-800 (dark)
- Border-radius: 6px-8px
- Background: white (light) / gray-900 (dark)
- Shadow: Subtle to light (see shadows table)
- Padding: 16px default, 24px for emphasis
- Margin-bottom: 16px between cards

**Variants**:
1. **Default Card**: Standard content container
2. **Elevated Card**: Higher shadow, used for key information
3. **Interactive Card**: Hoverable, clickable, with hover state
4. **Outline Card**: No background, just border (subtle)
5. **Accent Card**: Blue border, used for important notices

**Mobile Adjustments**:
- Padding: 12px-16px
- Border-radius: 4px-6px
- Shadows reduced (subtle only)

---

### Input Field Component

**Structure**:
```
Label (14px, gray-600)
↓
┌──────────────────────────────┐
│ Input text here              │  (16px padding, 44px height)
└──────────────────────────────┘
↓
Helper text (12px, gray-500) or error (12px, red-600)
```

**Properties**:
- Height: 44px (mobile friendly)
- Padding: 12px 16px
- Border: 1px, gray-300 (light) / gray-700 (dark)
- Border-radius: 4px-6px
- Font: 14px-16px
- Placeholder: Light gray, 50% opacity

**States**:
1. **Default (Idle)**: Border gray-300, no shadow
2. **Focus**: Border blue-500, blue glow shadow (2-4px blur)
3. **Filled**: Border gray-400, indicator showing valid
4. **Error**: Border red-500, red error message below
5. **Disabled**: Gray-100 background, gray-400 border, not focusable

**Interactions**:
- Clear, immediate border color change on focus
- Smooth transition (100-150ms)
- Error state shows inline error message
- Validation can be real-time or on blur

**Mobile Adjustments**:
- Height: 48px (larger touch target)
- Font size: 16px (prevents mobile zoom)
- Padding: 12px-16px (generous spacing)

---

### Badge Component

**Usage**: Status indicators, tag labels, counts

**Variants**:

| Type | Background | Text | Usage |
|------|-----------|------|-------|
| Success | Green-100 (light) / Green-900 (dark) | Green-700 / Green-300 | Gains, active, bullish |
| Danger | Red-100 / Red-900 | Red-700 / Red-300 | Losses, inactive, bearish |
| Warning | Yellow-100 / Yellow-900 | Yellow-700 / Yellow-300 | Caution, pending |
| Info | Blue-100 / Blue-900 | Blue-700 / Blue-300 | Information, neutral |
| Gray | Gray-100 / Gray-800 | Gray-700 / Gray-300 | Default, tags |

**Styling**:
- Padding: 4px 8px (small), 8px 12px (large)
- Border-radius: 4px (slightly rounded) or 12px (pill)
- Font-size: 12px-14px
- Font-weight: 500 (medium)
- Inline element, no block width

**Examples**:
- "+1.25%" badge in green
- "Bullish" badge in blue
- "Alert triggered" in yellow
- "AAPL" tag in gray

---

### Dropdown / Select Component

**Structure**:
```
Label (optional)
↓
┌──────────────────────────────────────┐
│ Selected Value                    [▼] │  (44px height)
└──────────────────────────────────────┘
        ↓ (on click)
┌──────────────────────────────────────┐
│ Option 1 (clickable row)              │
│ Option 2 (clickable row)              │
│ Option 3 (clickable row)              │
└──────────────────────────────────────┘
```

**Properties**:
- Height: 44px
- Padding: 12px 16px
- Border: Similar to input field
- Focus: Blue border + glow
- Dropdown position: Below field, full width or fixed
- Max-height: 5 items visible, then scrollable

**States**:
1. Closed (default)
2. Hovered (slight background change)
3. Open (dropdown visible)
4. Selected (item highlighted)
5. Disabled (grayed out, not clickable)

**Keyboard Interaction**:
- Tab to focus
- Enter/Space to open
- Arrow keys to navigate
- Enter to select
- Escape to close

---

### Modal / Dialog Component

**Structure**:
```
┌─────────────────────────────────────────────┐
│  [Title]                              [×]   │  Header
├─────────────────────────────────────────────┤
│  Content area                                │  Body (scrollable if tall)
│  [Flexible content]                         │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  [Action 1]        [Action 2]  [Action 3]   │  Footer (sticky)
└─────────────────────────────────────────────┘
```

**Properties**:
- Width: 90% on mobile (max 600px), 600px on desktop
- Max-height: 90vh (scrollable content if larger)
- Background: white (light) / gray-900 (dark)
- Border: 1px gray-200 / gray-800 (optional)
- Border-radius: 8px-12px
- Shadow: Heavy (see shadows table)
- Padding: 24px (header/footer), 16px-24px (body)

**Overlay**:
- Dark semi-transparent background (rgba(0,0,0,0.5))
- Click outside to dismiss (if allowed)
- Esc key to close (if allowed)

**Accessibility**:
- Focus trapped inside modal
- Heading (h2 or h3) for title
- Action buttons labeled clearly
- Close button ([×]) and "Cancel" button both available

---

### Tooltip Component

**Usage**: Explain metrics, show additional information on hover

**Structure**:
```
[Element with ?]
     ↓ (on hover/focus)
 ┌─────────────────────────────┐
 │ Tooltip text explaining     │
 │ the metric or term          │
 └─────────────────────────────┘
```

**Properties**:
- Background: Gray-800 (light) / Gray-200 (dark)
- Text: White / Gray-900
- Padding: 8px 12px
- Border-radius: 4px
- Font-size: 12px-13px
- Max-width: 300px
- Position: Auto-positioned (above/below/left/right to avoid edges)
- Delay: 500ms before showing (prevent flashing)
- Arrow pointing to element

**Trigger**:
- Hover on element (desktop)
- Long-press on element (mobile)
- Focus on element (keyboard)

**Educational Tooltips** (for beginner investors):
- Appear on first visit to page
- Optional "Don't show again" checkbox
- Contextual and non-dismissive

---

### Chart Components

#### Candlestick Chart

**Dimensions**:
- Default: 800px wide x 400px tall (desktop)
- Responsive: Full width on mobile, 60vh height
- Padding: 40px (left for Y-axis), 20px (others)

**Elements**:
1. **Candlesticks**: OHLC bars, color-coded (green up, red down)
2. **Volume**: Column chart below price, semi-transparent
3. **Moving Averages**: Overlay lines (20, 50, 200 SMA)
4. **Bollinger Bands**: Semi-transparent channel around price
5. **Axes**: X-axis (time), Y-axis (price)
6. **Grid**: Subtle (light gray, opacity 20%)
7. **Crosshair**: On hover, shows price and date
8. **Legend**: Top right, showing what's displayed

**Interactions**:
- Hover to see detail (price, date, volume)
- Zoom (pinch on mobile, scroll wheel or UI buttons on desktop)
- Pan (drag left/right to scroll through time)
- Click and drag to draw trend lines (phase 2)

**Mobile Adjustments**:
- Smaller font for axis labels
- Simplified grid (fewer lines)
- Tap to see detail instead of hover
- Simplified toolbar (fewer indicators)

#### Technical Indicator Subcharts

**RSI (Relative Strength Index)**:
- Small chart below main chart (200px height)
- Y-axis: 0-100, with bands at 30 and 70
- Overbought zone (70+) in red tint
- Oversold zone (<30) in green tint
- RSI line in blue

**MACD (Moving Average Convergence Divergence)**:
- Small chart below RSI (200px height)
- Two lines: MACD and Signal line
- Histogram showing difference
- Zero line marked

#### Allocation Pie Chart

**Dimensions**:
- 250px x 250px (default), responsive
- Center label showing total or selected slice

**Interactions**:
- Click slice to highlight
- Hover to show %, value
- Legend clickable to toggle slices
- Color scheme consistent with sector colors

---

## Interaction Patterns

### Real-Time Data Updates

**Price Updates** (in quote/watchlist views):

1. **Initial Load**:
   - Show last known price
   - Indicate freshness: "Price from 2 min ago" in subtle gray

2. **Update Arrives**:
   - Flash background color briefly (100-200ms)
   - If up: green flash
   - If down: red flash
   - Change badge immediately updates

3. **Change Indicator**:
   - Arrow icon: Up (↑) or Down (↓)
   - Animated: Subtle bounce or glow when updating
   - Color: Green for up, red for down

4. **Volume Change**:
   - Animate volume bars when new data arrives
   - Smooth transition (300ms)

**Implementation**:
```typescript
// Pseudo-code for real-time update
const handlePriceUpdate = (newPrice) => {
  // Flash background
  element.classList.add('price-flash-up'); // or 'price-flash-down'

  // Smooth number transition
  animateValue(oldPrice, newPrice, 200);

  // Update change badge
  updateChangeBadge(newPrice);

  // Remove flash class
  setTimeout(() => element.classList.remove('price-flash-up'), 200);
}
```

### Order Execution Flow

**Step-by-Step Modal Progression**:

**Step 1: Order Type & Quantity**
```
┌────────────────────────────────┐
│ Buy AAPL (Step 1 of 3)          │
├────────────────────────────────┤
│ Order Type:                     │
│ ◉ Market Order (immediate)      │
│ ⊚ Limit Order (target price)    │
│                                 │
│ Quantity: [____________]        │
│ (with +/- buttons)              │
│                                 │
│ Estimated Cost: $17,250.00      │
│ Available: $50,000.00           │
│                                 │
│           [Next →]              │
└────────────────────────────────┘
```

**Step 2: Order Review**
```
┌────────────────────────────────┐
│ Review Order (Step 2 of 3)      │
├────────────────────────────────┤
│ Symbol: AAPL                    │
│ Type: Market Order              │
│ Side: Buy                       │
│ Quantity: 100 shares            │
│ Estimated Price: $172.50/share  │
│ Estimated Total: $17,250.00     │
│                                 │
│ ☐ Accept market conditions      │
│ (Market orders may fill above   │
│  listed price)                  │
│                                 │
│ [← Back]  [Next →]              │
└────────────────────────────────┘
```

**Step 3: Confirmation**
```
┌────────────────────────────────┐
│ Confirm & Execute (Step 3 of 3)│
├────────────────────────────────┤
│ Ready to submit order           │
│                                 │
│ ☐ I understand the risks        │
│                                 │
│                                 │
│ [← Back] [Submit Order] [Cancel]│
└────────────────────────────────┘
```

**After Submission**:
- Show loading state (spinner)
- "Submitting order..." message
- On success: "Order placed! Order #12345"
- Show position in portfolio if buy
- Return to dashboard or stock detail

### Alert Setup Flow

**Inline vs. Modal**:

**Inline Alert Setup** (on Stock Detail Page):
- Card with form fields
- Title: "Set Price Alert"
- Fields: Target price, notification method, label
- Buttons: [Save Alert] [Cancel]
- Takes up fixed space, always visible

**Modal Alert Setup** (from quick action):
- Pop-up dialog
- More prominent
- Helpful tooltips
- Success confirmation after saving

### Navigation & State Transitions

**URL Structure** (using React Router or similar):
```
/                          Dashboard
/market                    Market Discovery
/market/gainers            Market Gainers
/stocks/:symbol            Stock Detail (e.g., /stocks/AAPL)
/portfolio                 Portfolio Page
/watchlists                Watchlist Management
/alerts                    Alert Management
/settings                  Settings
```

**Breadcrumbs** (optional):
- Home > Market > Gainers > Tech Sector
- Show on mobile too, but collapsed

**Back Navigation**:
- Browser back button works as expected
- "Back" button in header (mobile and tablet)
- Logo always links to home/dashboard

---

## Mobile-First Approach

### Responsive Breakpoints

```css
Mobile:    < 640px   (Baseline, single column)
Tablet:    640px - 1024px
Desktop:   > 1024px
```

### Mobile Layout Transformations

#### Dashboard (Mobile Layout)
```
┌────────────────────────────┐
│      HEADER / SEARCH       │
├────────────────────────────┤
│  Quick Stats (Stacked)      │
│  ┌──────────────────────┐  │
│  │ Total Value: $52k    │  │
│  │ Daily P&L: +$125     │  │
│  │ Total Return: +8.5%  │  │
│  │ Cash: $8,500         │  │
│  └──────────────────────┘  │
├────────────────────────────┤
│ Portfolio Overview (Card)   │
│  Pie chart (smaller)        │
│  Top 3 holdings            │
├────────────────────────────┤
│ Indices Widget (Scrollable) │
│ [SPY] [QQQ] [DIA]          │
├────────────────────────────┤
│ Trending Stocks (Cards)    │
│ Swipeable carousel         │
├────────────────────────────┤
│ Recent Activity (Compact)   │
│ Last 3 transactions        │
├────────────────────────────┤
│ Bottom Navigation (64px)    │
│ [Dashboard] [Market] ...    │
└────────────────────────────┘
```

#### Stock Detail (Mobile Layout)
```
┌────────────────────────────┐
│      HEADER / SEARCH       │
├────────────────────────────┤
│ Price Header (AAPL $172.50)│
├────────────────────────────┤
│ Price Chart (Full width)   │
│ (300px height)             │
│ [1h] [1d] [1w] [1m]        │
├────────────────────────────┤
│ Key Metrics (Scrollable)   │
│ [P/E: 28.5] [Div: 0.4%]    │
├────────────────────────────┤
│ Technical Indicators       │
│ RSI and MACD (compact)     │
├────────────────────────────┤
│ Company Info (Expandable)  │
├────────────────────────────┤
│ News (Scrollable list)     │
├────────────────────────────┤
│ Order Panel (Sticky bottom)│
│ [Quantity] [Buy] [Sell]    │
│ [More options...]          │
├────────────────────────────┤
│ Set Alert, Stop Loss tools │
└────────────────────────────┘
```

#### Portfolio (Mobile Layout)
```
┌────────────────────────────┐
│      HEADER / SEARCH       │
├────────────────────────────┤
│ Portfolio Summary          │
│ Total: $52,000             │
│ P&L: +$1,250 (+2.5%)       │
├────────────────────────────┤
│ Holdings List (Cards)      │
│ Each card:                 │
│ AAPL | $172.50             │
│ 100 @ $150  | +$2,250 ↑    │
│ [Expand ↓]                 │
├────────────────────────────┤
│ Allocation (Pie, smaller)  │
├────────────────────────────┤
│ Metrics (Scrollable)       │
├────────────────────────────┤
│ Performance Chart (Compact)│
├────────────────────────────┤
│ Bottom Navigation          │
└────────────────────────────┘
```

### Touch Interactions

**Touch-Friendly Design**:
- Minimum button size: 44x44px (WCAG AAA)
- Spacing between clickable elements: 8px minimum
- Form fields: 48px height on mobile
- No hover states on mobile (use active state instead)

**Gesture Support**:
- Swipe left/right: Carousel (trending stocks, carousel lists)
- Swipe up: Scroll down (pull up portfolio details, etc.)
- Long-press: Context menu (watchlist actions)
- Pinch-zoom: Chart zoom (optional, browser native works too)
- Double-tap: Zoom in on chart

**Mobile Form Best Practices**:
- Auto-focus first input
- Show relevant keyboard (number for price, phone for contact)
- Large input fields (48px)
- Clear label placement
- One input per line on mobile
- Submit button takes full width
- Clear error messages

### Font Sizes for Mobile

**Minimum readable**: 16px base font (prevents mobile zoom)

Adjust type scale for mobile:
- H1: 24px (down from 32px)
- H2: 20px (down from 24px)
- Body: 16px (unchanged)
- Label: 14px (unchanged)
- Mono (prices): 24px (down from 32px)

### Image & Chart Responsiveness

**Charts**:
- Desktop: Full width (with max-width 1200px)
- Tablet: Full width with padding
- Mobile: Full width, height reduced by ~30%
- Aspect ratio: Maintain 2:1 for candlestick charts

**Icons**:
- Desktop: 24px
- Mobile: 20px-24px
- Buttons: 24px (inside 44px touch target)

---

## Accessibility & Compliance

### WCAG 2.1 AA Compliance

**Level AA Requirements**:
- Contrast ratio: 4.5:1 for text, 3:1 for UI components
- Level AAA for critical financial info: 7:1

### Color & Contrast

**Text Color Combinations** (Light Mode):
- Gray-900 (text) on White (bg): 18:1 ✓ AAA
- Gray-900 (text) on Gray-50 (bg): 15:1 ✓ AAA
- Gray-600 (secondary) on White (bg): 7:1 ✓ AAA
- Green-600 (positive) on Gray-50: 6:1 ✓ AA
- Red-600 (negative) on Gray-50: 6:1 ✓ AA

**UI Component Borders**:
- Gray-200 border on white: 2.5:1 ✗ (not sufficient)
- Use: Gray-300 for better contrast, or reduce reliance on color alone

### Semantic HTML

**Structure**:
- Use semantic tags: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- Proper heading hierarchy: `<h1>` (one per page), `<h2>`, `<h3>`, etc.
- Form elements: `<label>` linked to `<input>` via `for` attribute
- Buttons: Use `<button>` or role="button" on divs with keydown handlers
- Tables: Use `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>`

**ARIA Attributes**:
- Live regions: `aria-live="polite"` for price updates
- Labels: `aria-label` for icon-only buttons
- Descriptions: `aria-describedby` for complex components
- Status: `aria-pressed`, `aria-selected` for state
- Navigation: `aria-current="page"` for active nav item

### Keyboard Navigation

**Full Keyboard Access**:
- All interactive elements focusable with Tab
- Focus order logical (left to right, top to bottom)
- Visible focus indicator: 2px outline, 4px offset, blue color
- Escape to close modals/dropdowns
- Enter/Space to activate buttons
- Arrow keys for list/menu navigation

**Keyboard Shortcuts** (optional):
- `/` to search
- `?` for help
- `b` to focus on Buy button
- `s` to focus on Sell button

### Screen Reader Support

**Announcements**:
- Price updates: Use `aria-live="polite"` and `aria-atomic="true"`
- Alerts: Use `role="alert"` or `aria-live="assertive"`
- Loading: Show loading text, not just spinner

**List/Table Labeling**:
- Watchlist: `<h2>Watchlist: My Tech Stocks</h2>` before list
- Holdings table: Header row uses `<th>` with scope="col"
- Row headers: First column `<th scope="row">`

**Chart Accessibility**:
- Provide text alternative: "AAPL price chart, 1-day view: Price range $170-$175, current $172.50"
- Data table underneath chart with key values
- Keyboard navigation for chart (arrow keys to navigate timepoints)

### Form Accessibility

**Input Fields**:
```html
<div class="form-group">
  <label for="quantity">Quantity (number of shares)</label>
  <input
    id="quantity"
    type="number"
    min="1"
    required
    aria-required="true"
    aria-describedby="qty-help"
  />
  <small id="qty-help">Enter whole shares only, max 10,000</small>
</div>
```

**Error States**:
- Link errors to fields with `aria-describedby`
- Color + text (not color alone)
- `aria-invalid="true"` on invalid inputs
- Error message at top of form or near field

### Color-Blind Friendly Design

**Avoid Color-Only Indicators**:
- Green + ✓ (checkmark) or ↑ (up arrow)
- Red + ✗ (X) or ↓ (down arrow)
- Blue + circled question mark (?)

**Test Colors**:
- Use tools like Color Contrast Analyzer
- Simulate with Coblis (color blindness simulator)
- Test prototypes with color-blind users

### Loading & Empty States

**Loading State**:
- Show loading spinner with text
- "Loading market data..."
- Estimated time if available
- Allow cancellation if possible
- Don't show old data while loading

**Empty State**:
- Illustration (optional)
- Clear message: "No holdings yet"
- Call to action: "Buy your first stock"
- Link to relevant page

**Error State**:
- Error icon + message
- Specific error explanation
- Recovery action: "Retry", "Go back", "Contact support"

---

## Design Tokens

### Token Organization

**File Structure**:
```
tokens/
├── colors.js         (color tokens)
├── typography.js     (font, size, weight)
├── spacing.js        (margin, padding)
├── shadows.js        (elevation)
├── border-radius.js  (corner radius)
└── transitions.js    (duration, easing)
```

### Color Tokens

```javascript
const colors = {
  // Neutral
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
    950: '#030712',
  },

  // Semantic
  success: {
    light: '#DCF6E8',
    main: '#16A34A',
    dark: '#15803D',
    darkMode: '#4ADE80',
  },
  danger: {
    light: '#FEE2E2',
    main: '#DC2626',
    dark: '#B91C1C',
    darkMode: '#F87171',
  },
  warning: {
    light: '#FEF3C7',
    main: '#F59E0B',
    dark: '#D97706',
    darkMode: '#FBBF24',
  },
  primary: {
    light: '#DBEAFE',
    main: '#2563EB',
    dark: '#1D4ED8',
    darkMode: '#60A5FA',
  },
}
```

### Spacing Tokens

```javascript
const spacing = {
  xs: '4px',    // 0.25rem
  sm: '8px',    // 0.5rem
  md: '12px',   // 0.75rem
  lg: '16px',   // 1rem
  xl: '24px',   // 1.5rem
  '2xl': '32px',// 2rem
  '3xl': '48px',// 3rem
  '4xl': '64px',// 4rem
}
```

### Typography Tokens

```javascript
const typography = {
  family: {
    base: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"SF Mono", Monaco, "Cascadia Code", monospace',
  },

  scale: {
    h1: { size: '32px', weight: 700, lineHeight: '1.2' },
    h2: { size: '24px', weight: 600, lineHeight: '1.3' },
    h3: { size: '20px', weight: 600, lineHeight: '1.4' },
    body: { size: '16px', weight: 400, lineHeight: '1.5' },
    small: { size: '14px', weight: 400, lineHeight: '1.5' },
    label: { size: '14px', weight: 500, lineHeight: '1.5' },
  },
}
```

---

## Animation & Micro-interactions

### Transition Timings

| Duration | Usage | Easing |
|----------|-------|--------|
| **100ms** | Hover states, button feedback | ease-out |
| **150ms** | Color changes, simple transitions | ease-in-out |
| **200ms** | Price flash, quick updates | ease-in-out |
| **300ms** | Modal open/close, chart transitions | ease-out |
| **500ms** | Slide animations, drawer open | ease-out |

### Easing Functions

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-linear: linear;
```

### Micro-interactions

**Button Interaction**:
```
Hover: Scale 1.02, shadow elevation
Active: Scale 0.98, shadow depression
Transition: 100-150ms ease-out
```

**Price Update Flash**:
```
0%: background-color: white
50%: background-color: #DCF6E8 (green) or #FEE2E2 (red)
100%: background-color: white
Duration: 200ms
```

**Modal Open**:
```
Overlay: Fade in 300ms (opacity 0 → 0.5)
Modal: Slide + fade 300ms
Scale: 0.95 → 1.0
Opacity: 0 → 1
```

**Chart Zoom Transition**:
```
Duration: 300ms
Easing: ease-out
Update axis labels smoothly
Animate bars/candlesticks
```

### Accessibility with Animations

**Reduced Motion**:
- Respect `prefers-reduced-motion` media query
- Remove animations if user prefers reduced motion
- Keep essential feedback (color changes, focus indicators)

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Summary

This comprehensive design specification provides:

1. **Clear Visual Direction**: Color palette, typography, spacing, shadows all defined with light/dark mode support
2. **Responsive Framework**: Mobile-first approach with breakpoints for tablet and desktop
3. **Component Library**: Reusable components with states, interactions, and accessibility considerations
4. **User-Centric Flows**: Step-by-step journeys for common tasks (trading, portfolio review, alerts)
5. **Accessibility-First**: WCAG 2.1 AA compliance, keyboard navigation, screen reader support
6. **Interaction Patterns**: Real-time updates, micro-interactions, animations with performance in mind
7. **Mobile Optimization**: Touch-friendly interfaces, mobile-specific layouts, gesture support

**Implementation Priority**:
1. Core components (Button, Card, Input, Badge)
2. Layout system (Header, Sidebar, Grid)
3. Pages (Dashboard, Stock Detail, Portfolio)
4. Features (Charts, Alerts, Orders)
5. Polish (Animations, Micro-interactions, Dark mode)

**Design Tokens File**: Ready to be implemented in design tools (Figma, Storybook) and exported to code (CSS-in-JS, Tailwind, SCSS variables)

**Next Steps**:
- Create Figma component library based on specifications
- Build Storybook for component documentation
- Implement design tokens in codebase
- Create visual regressions tests
- Conduct accessibility audit
- Test with real users (retail investors)

---

**Document Version**: 1.0
**Last Updated**: March 11, 2026
**Status**: Ready for Implementation
