# Stock Exchange Board - Component Library Specification

**Version**: 1.0.0
**Date**: March 11, 2026
**Status**: Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Composite Components](#composite-components)
4. [Page-Level Components](#page-level-components)
5. [Props & Variants](#props--variants)
6. [Accessibility Checklist](#accessibility-checklist)

---

## Overview

### Component Hierarchy

The component library follows an atomic design approach:

```
Atoms (Core UI elements)
├── Button, Badge, Icon
├── Input, Checkbox, Radio
├── Card, Spacer, Divider

Molecules (Simple combinations)
├── InputGroup (Label + Input + Help text)
├── FormField (Label + Input + Validation)
├── QuoteCard (Symbol + Price + Change)
├── PriceHeader (Symbol + Large Price + Bid/Ask)

Organisms (Complex combinations)
├── OrderPanel (Form + Buttons + Validation)
├── AlertManager (List + Edit + Create)
├── PortfolioOverview (Charts + Stats + Metrics)
├── CandlestickChart (Chart + Indicators + Timeframes)

Templates (Page layouts)
├── StockDetailTemplate
├── PortfolioTemplate
├── DashboardTemplate
├── WatchlistTemplate

Pages (Full pages)
├── Dashboard.tsx
├── Market.tsx
├── StockExchangeBoard.tsx
```

---

## Core Components

### 1. Button Component

**File Location**: `src/components/common/Button.tsx`

**Props Interface**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  // Core props
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  isDisabled?: boolean;
  fullWidth?: boolean;

  // Content
  children: React.ReactNode;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';

  // Callbacks
  onClick?: (e: React.MouseEvent) => void;

  // Styling
  className?: string;
  ariaLabel?: string;
}
```

**Variants**:

| Variant | Usage | Colors | Example |
|---------|-------|--------|---------|
| **primary** | Main actions | Blue background, white text | "Buy AAPL" |
| **secondary** | Alternative actions | Transparent, border, text | "Cancel" |
| **success** | Positive outcomes | Green background, white text | "Confirm" |
| **danger** | Destructive actions | Red background, white text | "Sell All" |
| **ghost** | Tertiary, minimal | Transparent, text only | "Learn More" |
| **icon** | Icon-only actions | Transparent, icon color | Bell icon for alerts |

**Implementation Example**:
```tsx
<Button variant="primary" size="md" onClick={handleBuy}>
  Buy {symbol}
</Button>

<Button variant="secondary" size="md">
  Cancel
</Button>

<Button variant="icon" ariaLabel="Set alert">
  <BellIcon />
</Button>

<Button variant="primary" isLoading>
  Submitting Order...
</Button>
```

**States**:
- Default (idle)
- Hover (color change, slight elevation)
- Active (pressed appearance)
- Disabled (grayed out, no cursor)
- Loading (spinner + text)
- Focus (2px outline, 2px offset)

**Accessibility**:
- Semantic `<button>` element
- `aria-label` for icon-only buttons
- `aria-disabled` for disabled state
- Keyboard focusable (Tab)
- Minimum 44x44px touch target

---

### 2. Card Component

**File Location**: `src/components/common/Card.tsx`

**Props Interface**:
```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  // Layout
  variant?: 'default' | 'elevated' | 'interactive' | 'outline' | 'accent';
  padding?: 'sm' | 'md' | 'lg';
  noBorder?: boolean;
  hoverable?: boolean;

  // Content structure
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;

  // Interactions
  onClick?: () => void;
  isSelected?: boolean;

  // Styling
  className?: string;
}
```

**Variants**:

```tsx
// Default card - standard container
<Card padding="lg">
  <Card.Header>Stock Performance</Card.Header>
  <p>Performance data here</p>
</Card>

// Elevated card - higher prominence
<Card variant="elevated" padding="xl">
  <h3>Portfolio Overview</h3>
  <div>Key metrics</div>
</Card>

// Interactive card - clickable
<Card variant="interactive" onClick={() => navigate('/stock/AAPL')}>
  <Card.Header>AAPL</Card.Header>
  <p>$172.50</p>
</Card>

// Outline card - subtle
<Card variant="outline">
  <p>This is a subtle container</p>
</Card>

// Accent card - important notice
<Card variant="accent">
  <p>Important information here</p>
</Card>
```

**Responsive**:
- Desktop: 24px padding (lg)
- Tablet: 20px padding (md)
- Mobile: 16px padding (md)

**Accessibility**:
- Semantic `<div>` with proper heading hierarchy
- Interactive cards: `role="button"`, `onClick`, keyboard support
- Focus indicator for interactive cards

---

### 3. Input Component

**File Location**: `src/components/common/Input.tsx`

**Props Interface**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  // Core props
  label?: string;
  labelSize?: 'sm' | 'md';
  placeholder?: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;

  // Variants
  type?: 'text' | 'number' | 'email' | 'password' | 'tel';
  size?: 'sm' | 'md' | 'lg';

  // Validation
  error?: string;
  isInvalid?: boolean;
  isValid?: boolean;
  required?: boolean;

  // Help text
  helperText?: string;
  ariaDescribedBy?: string;

  // Styling
  prefix?: string;
  suffix?: string;
  fullWidth?: boolean;
  disabled?: boolean;

  // Callbacks
  onBlur?: () => void;
  onFocus?: () => void;
}
```

**Usage Examples**:

```tsx
// Basic input
<Input
  label="Quantity"
  type="number"
  value={quantity}
  onChange={(e) => setQuantity(e.target.value)}
  placeholder="Enter number of shares"
  min={1}
/>

// With error state
<Input
  label="Target Price"
  type="number"
  value={targetPrice}
  onChange={(e) => setTargetPrice(e.target.value)}
  error="Price must be greater than current price"
  isInvalid={error !== null}
  prefix="$"
/>

// With helper text
<Input
  label="Stop Loss"
  type="number"
  helperText="Set price at which to automatically sell"
  prefix="$"
/>

// With validation
<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  isValid={isValidEmail(email)}
/>
```

**States**:
- Idle (default)
- Focused (blue border, glow)
- Filled (value present)
- Error (red border, error message)
- Valid (green indicator)
- Disabled (grayed out)

**Accessibility**:
- Label linked with `htmlFor`
- `aria-invalid` for error state
- `aria-describedby` for helper/error text
- Minimum 44px height on mobile
- 16px font on mobile (prevents zoom)

---

### 4. Badge Component

**File Location**: `src/components/common/Badge.tsx`

**Props Interface**:
```typescript
interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  // Content
  children: React.ReactNode;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';

  // Variants
  variant?: 'success' | 'danger' | 'warning' | 'info' | 'gray';
  size?: 'sm' | 'md';
  shape?: 'default' | 'pill';

  // Styling
  className?: string;
}
```

**Usage Examples**:

```tsx
// Gain badge (success)
<Badge variant="success" size="md">
  +1.25%
</Badge>

// Loss badge (danger)
<Badge variant="danger" size="md">
  -0.85%
</Badge>

// With icon
<Badge variant="success" icon={<ArrowUpIcon />} iconPosition="left">
  Bullish
</Badge>

// Pill shape
<Badge variant="info" shape="pill">
  AAPL
</Badge>

// Gray tag
<Badge variant="gray">
  Technology
</Badge>
```

**Variants & Colors**:
- **success**: Green background, green text
- **danger**: Red background, red text
- **warning**: Yellow background, yellow text
- **info**: Blue background, blue text
- **gray**: Gray background, gray text

**Accessibility**:
- Semantic `<span>` element
- `aria-label` if icon-only
- Sufficient color contrast
- Color + text/icon (not color alone)

---

### 5. Icon Component

**File Location**: `src/components/common/Icon.tsx`

**Props Interface**:
```typescript
interface IconProps extends React.SVGAttributes<SVGElement> {
  // Icon reference
  name: string; // Icon name from library
  size?: 'sm' | 'md' | 'lg' | number;
  color?: string; // Hex or token name

  // Styling
  className?: string;
  ariaLabel?: string;
  ariaHidden?: boolean;
}
```

**Icon Set** (to be created):

| Icon | Name | Usage |
|------|------|-------|
| ↑ | arrow-up | Gains, bullish |
| ↓ | arrow-down | Losses, bearish |
| ↗ | trending-up | Bullish trend |
| ↘ | trending-down | Bearish trend |
| 🔔 | bell | Alerts |
| 👁 | eye | View/Watch |
| ✓ | check | Success |
| ✕ | close | Close/Delete |
| ⚙ | settings | Settings |
| 🔍 | search | Search |
| + | plus | Add |
| − | minus | Remove |
| ≡ | menu | Navigation |
| ▲ | chevron-up | Expand |
| ▼ | chevron-down | Collapse |

**Usage**:

```tsx
// Sized icon
<Icon name="arrow-up" size="md" />
<Icon name="arrow-down" size={24} />

// Colored icon
<Icon name="bell" color="#2563EB" />
<Icon name="check" color="var(--color-success)" />

// Icon button (within Button)
<Button icon={<Icon name="bell" />} variant="icon" />

// Icon with accessibility
<Icon name="search" ariaLabel="Search stocks" />
<Icon name="decorative-line" ariaHidden />
```

---

### 6. Badge Component (Status/Count)

**File Location**: `src/components/common/Badge.tsx` (count variant)

**Props Interface**:
```typescript
interface CountBadgeProps {
  // Content
  count: number;
  variant?: 'primary' | 'success' | 'danger' | 'warning';

  // Display
  showZero?: boolean;
  max?: number; // Shows "9+" if count > max

  // Styling
  className?: string;
}
```

**Usage**:

```tsx
// Notification count
<div className="relative">
  <Button icon={<BellIcon />} />
  <CountBadge count={5} variant="danger" />
</div>

// Alert count
<div>
  <h3>Active Alerts</h3>
  <CountBadge count={12} max={9} />
</div>
```

---

### 7. Divider Component

**File Location**: `src/components/common/Divider.tsx`

**Props Interface**:
```typescript
interface DividerProps {
  // Direction
  orientation?: 'horizontal' | 'vertical';

  // Content
  label?: string;

  // Styling
  className?: string;
  spacing?: 'sm' | 'md' | 'lg';
}
```

**Usage**:

```tsx
// Simple divider
<Card>
  <p>Section 1</p>
  <Divider spacing="md" />
  <p>Section 2</p>
</Card>

// With label
<Divider label="Or" spacing="lg" />

// Vertical divider
<div className="flex">
  <Column>Stats 1</Column>
  <Divider orientation="vertical" />
  <Column>Stats 2</Column>
</div>
```

---

### 8. Spacer Component

**File Location**: `src/components/common/Spacer.tsx`

**Props Interface**:
```typescript
interface SpacerProps {
  // Dimensions
  width?: string | number;
  height?: string | number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}
```

**Usage**:

```tsx
// Create vertical space
<h2>Title</h2>
<Spacer size="lg" />
<p>Content</p>

// Horizontal space
<span>Label</span>
<Spacer width={12} />
<span>Value</span>
```

---

## Composite Components

### 1. PriceHeader Component

**File Location**: `src/components/market/PriceHeader.tsx`

**Props Interface**:
```typescript
interface PriceHeaderProps {
  // Data
  symbol: string;
  name?: string;
  price: number;
  change: number;
  changePercent: number;
  bid?: number;
  ask?: number;
  volume?: number;
  time?: Date;

  // Display options
  showBidAsk?: boolean;
  showVolume?: boolean;

  // Styling
  className?: string;
}
```

**Display Layout**:
```
┌──────────────────────────────────────┐
│ AAPL - Apple Inc.                    │
├──────────────────────────────────────┤
│ Price:  $172.50                      │
│ Change: +$1.25 (+0.73%) ↑            │
│ Bid: $172.48 | Ask: $172.52          │
│ Volume: 42.3M | Time: 3:45 PM        │
└──────────────────────────────────────┘
```

**Usage**:

```tsx
<PriceHeader
  symbol="AAPL"
  name="Apple Inc."
  price={172.50}
  change={1.25}
  changePercent={0.73}
  bid={172.48}
  ask={172.52}
  volume={42300000}
  showBidAsk
  showVolume
/>
```

**Accessibility**:
- Use semantic heading for symbol
- Aria-label for price changes
- Color + arrow icon (not color alone)

---

### 2. QuoteCard Component

**File Location**: `src/components/market/QuoteCard.tsx`

**Props Interface**:
```typescript
interface QuoteCardProps {
  // Data
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  marketCap?: string;

  // Display options
  showSparkline?: boolean;
  sparklineData?: number[];
  compactMode?: boolean;

  // Interactions
  onClick?: () => void;
  onAlert?: () => void;

  // Styling
  className?: string;
}
```

**Display Layout** (Full):
```
┌──────────────────────┐
│ AAPL                 │
│ Apple Inc.           │
├──────────────────────┤
│ Price:      $172.50  │
│ Change:     +1.25%   │
│ Volume:     42.3M    │
│ Market Cap: $2.8T    │
├──────────────────────┤
│ [Sparkline chart]    │
│                      │
│ [View] [Alert]       │
└──────────────────────┘
```

**Display Layout** (Compact):
```
AAPL | $172.50 | +1.25% | [Bell]
```

**Usage**:

```tsx
// Full card
<QuoteCard
  symbol="AAPL"
  name="Apple Inc."
  price={172.50}
  change={1.25}
  changePercent={0.73}
  volume={42300000}
  marketCap="$2.8T"
  showSparkline
  onClick={() => navigate('/stocks/AAPL')}
/>

// Compact (in watchlist row)
<QuoteCard
  symbol="AAPL"
  name="Apple Inc."
  price={172.50}
  change={1.25}
  changePercent={0.73}
  compactMode
/>
```

---

### 3. AlertBadge Component

**File Location**: `src/components/alerts/AlertBadge.tsx`

**Props Interface**:
```typescript
interface AlertBadgeProps {
  // Alert state
  hasAlert: boolean;
  alertCount?: number;

  // Styling
  size?: 'sm' | 'md' | 'lg';
  className?: string;

  // Interactions
  onClick?: () => void;
}
```

**Display**:
```
Hollow bell = no alert
Solid bell = alert active
Badge showing "3" = 3 active alerts
```

**Usage**:

```tsx
<AlertBadge hasAlert={true} alertCount={3} onClick={() => openAlerts()} />
```

---

### 4. ChangeIndicator Component

**File Location**: `src/components/market/ChangeIndicator.tsx`

**Props Interface**:
```typescript
interface ChangeIndicatorProps {
  // Data
  change: number;
  changePercent: number;

  // Display options
  showIcon?: boolean;
  showPercent?: boolean;
  format?: 'full' | 'compact';

  // Styling
  className?: string;
  textSize?: 'sm' | 'md' | 'lg';
}
```

**Display Examples**:
```
Full:     ↑ +1.25 (+0.73%)      [Green color]
Compact:  +0.73%                 [Green color]
Icon:     ↑                      [Green color]
```

**Color Logic**:
- Positive (up): Green (#16A34A)
- Negative (down): Red (#DC2626)
- Zero/Neutral: Gray (#6B7280)

**Accessibility**:
- Icon + text (not icon alone)
- Aria-label for screen readers

---

## Page-Level Components

### 1. DashboardLayout

**File Location**: `src/components/layout/DashboardLayout.tsx`

**Props**:
```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}
```

**Structure**:
```
┌─────────────────────────────────────────┐
│ Header (Logo, Search, User, Theme)      │
├─────────┬───────────────────────────────┤
│         │ Page Title                    │
│ Sidebar │ ┌────────────────────────────┤
│ (280px) │ │ Main Content (responsive)  │
│         │ │                            │
│ [Nav    │ │                            │
│  Items] │ └────────────────────────────┤
│         │                              │
├─────────┴───────────────────────────────┤
│ Footer (optional)                       │
└─────────────────────────────────────────┘
```

---

### 2. StockDetailLayout

**File Location**: `src/components/layout/StockDetailLayout.tsx`

**Desktop Layout** (3-column):
```
Left Column (65%)     | Gap  | Right Column (35%)
─────────────────────────────────────────────────
Price Header
─────────────────────────────────────────────────
Candlestick Chart    | Gap  | Key Metrics Card
─────────────────────────────────────────────────
Technical Indicators | Gap  | Company Info Card
─────────────────────────────────────────────────
News Feed           | Gap  | Order Panel
─────────────────────────────────────────────────
Related Stocks      | Gap  | Risk Tools
```

**Mobile Layout** (single column):
```
Price Header
─────────────
Candlestick Chart
─────────────
Technical Indicators
─────────────
Key Metrics (Scrollable)
─────────────
Company Info
─────────────
News Feed
─────────────
Order Panel (Sticky bottom)
─────────────
Risk Tools
```

---

### 3. PortfolioLayout

**File Location**: `src/components/layout/PortfolioLayout.tsx`

**Structure**:
```
Portfolio Summary Stats
─────────────────────────────────────────
┌───────────────────┬──────────────────┐
│ Allocation Chart  │ Portfolio Metrics │
└───────────────────┴──────────────────┘
─────────────────────────────────────────
Performance Chart (with time filters)
─────────────────────────────────────────
Holdings Table/Cards
─────────────────────────────────────────
Sector Breakdown
```

---

## Props & Variants

### Button Variants Table

| Variant | Default | Hover | Active | Disabled |
|---------|---------|-------|--------|----------|
| primary | Blue bg, white | Darker blue | Pressed blue | Gray bg, gray text |
| secondary | White bg, border | Gray-50 bg | Gray-100 bg | Gray bg, border |
| success | Green bg, white | Darker green | Pressed green | Gray bg, gray text |
| danger | Red bg, white | Darker red | Pressed red | Gray bg, gray text |
| ghost | Transparent | Gray-100 bg | Gray-200 bg | Transparent |
| icon | Transparent | Gray-100 bg | Gray-200 bg | Gray-300 |

### Input States Table

| State | Border | Background | Text | Helper |
|-------|--------|-----------|------|--------|
| idle | gray-300 | white | gray-900 | gray-500 |
| focused | blue-500 (glow) | white | gray-900 | gray-500 |
| filled | gray-400 | white | gray-900 | gray-500 |
| error | red-500 | white | red-600 | red-600 |
| valid | green-500 | white | gray-900 | green-600 |
| disabled | gray-300 | gray-100 | gray-400 | gray-400 |

### Badge Variants Table

| Variant | Background | Text | Icon Color |
|---------|-----------|------|-----------|
| success | green-100 | green-700 | green-600 |
| danger | red-100 | red-700 | red-600 |
| warning | yellow-100 | yellow-700 | yellow-600 |
| info | blue-100 | blue-700 | blue-600 |
| gray | gray-100 | gray-700 | gray-600 |

---

## Accessibility Checklist

### For Each Component

- [ ] **Semantic HTML**: Use appropriate semantic elements (`<button>`, `<input>`, etc.)
- [ ] **ARIA Labels**: `aria-label` for icon-only elements
- [ ] **ARIA Descriptions**: `aria-describedby` for helper text
- [ ] **Color Contrast**: Test with WCAG contrast checker (minimum 4.5:1)
- [ ] **Keyboard Navigation**: All interactive elements focusable with Tab
- [ ] **Focus Indicator**: Visible 2px outline or equivalent
- [ ] **Focus Order**: Logical left-to-right, top-to-bottom
- [ ] **Screen Reader**: Announce state changes with live regions
- [ ] **Mobile Touch**: Minimum 44x44px touch targets
- [ ] **Disabled State**: Use `disabled` attribute, not just visual
- [ ] **Form Validation**: Error messages linked to fields
- [ ] **Dark Mode**: Test color contrast in both modes
- [ ] **Reduced Motion**: Respect `prefers-reduced-motion`

### Testing Tools

- **Color Contrast**: WebAIM Contrast Checker
- **Screen Reader**: NVDA (Windows), JAWS (Windows), VoiceOver (Mac/iOS)
- **Accessibility Audit**: axe DevTools, Lighthouse
- **Color Blindness**: Coblis simulator
- **Keyboard Navigation**: Tab through entire app, no keyboard traps

---

## Component Documentation Example

### Button Component Documentation

```markdown
# Button Component

## Purpose
Primary interaction element for user actions across the application.

## Usage
```tsx
import { Button } from '@/components/common'

<Button variant="primary" onClick={handleAction}>
  Click Me
</Button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | string | 'primary' | Visual style variant |
| size | string | 'md' | Button size |
| onClick | function | - | Click handler |
| disabled | boolean | false | Disable button |
| loading | boolean | false | Show loading state |
| fullWidth | boolean | false | Stretch to container |

## States

### Default
- Normal appearance

### Hover
- Color brightening
- Shadow elevation

### Active
- Pressed appearance
- Darker color

### Disabled
- Grayed out
- No cursor
- No interaction

### Loading
- Spinner animation
- Text change

## Accessibility

- Keyboard focusable
- Focus visible indicator
- ARIA labels for icon-only
- Proper color contrast

## Examples

See Storybook for live examples.
```

---

## Summary

This component library provides:

1. **Core Components**: Reusable building blocks (Button, Input, Card, Badge, Icon)
2. **Composite Components**: Combinations for specific domains (PriceHeader, QuoteCard, AlertBadge)
3. **Page Components**: Full page layouts (Dashboard, Stock Detail, Portfolio)
4. **Consistent Props**: Predictable interfaces across all components
5. **Accessibility-First**: Every component designed for WCAG AA compliance
6. **Responsive Design**: Mobile, tablet, and desktop variants included
7. **Variant System**: Multiple visual styles for different contexts

**Implementation Priority**:
1. Core components (Button, Input, Card, Badge)
2. Composite components (PriceHeader, QuoteCard, ChangeIndicator)
3. Layout components (DashboardLayout, StockDetailLayout)
4. Page-level features (Charts, Tables, Forms)

**Next Steps**:
1. Create Storybook stories for each component
2. Implement in React/TypeScript with Tailwind CSS
3. Build component library documentation
4. Test all components for accessibility
5. Set up visual regression testing

---

**Document Version**: 1.0
**Last Updated**: March 11, 2026
**Status**: Ready for Implementation
