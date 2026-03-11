# QA Testing Guide - Stock Exchange Board Frontend

## Overview

This document provides comprehensive testing guidance for QA teams to validate the Stock Exchange Board frontend implementation across all features, browsers, and devices.

## Test Environment Setup

### Prerequisites
- Node.js 16+ installed
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Mobile device or mobile emulation tools
- Screen reader software (optional, for accessibility testing)

### Development Environment
```bash
npm install
npm run dev
```

Server runs at: http://localhost:3000

### Build & Preview
```bash
npm run build
npm run preview
```

Serves at: http://localhost:4173

## Automated Testing

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in UI mode
npm run test:ui

# Generate coverage report
npm run coverage

# Run specific test file
npm run test -- formatting.test.ts
```

### Current Test Coverage
- **Formatting Utilities**: 12 tests
- **Validation Utilities**: 16 tests
- **Button Component**: 8 tests
- **Market Store**: 6 tests
- **Total**: 42 unit tests

### Coverage Expectations
- Utilities: 100% coverage
- Components: Core component coverage
- Stores: Key action testing
- Overall: 80%+ coverage target

## Manual Testing Scenarios

### 1. Dashboard Page Testing

#### 1.1 Portfolio Overview Display
**Test Case**: PO-001 Portfolio metrics display
- [ ] Portfolio total value displays correctly
- [ ] Daily P&L shows positive/negative with correct color
- [ ] Daily P&L percentage is calculated accurately
- [ ] Unrealized gain displays with correct styling
- [ ] Total cost basis is accurate
- [ ] Holdings count is correct
- [ ] Last update timestamp is visible

**Test Case**: PO-002 Portfolio loading state
- [ ] Loading spinner appears on initial load
- [ ] Loading state completes within 2 seconds
- [ ] Data populates without flashing
- [ ] No console errors during load

#### 1.2 Holdings List
**Test Case**: HL-001 Holdings display and expansion
- [ ] All holdings display in order of value (highest first)
- [ ] Each holding shows symbol, quantity, and current value
- [ ] Daily P&L displays with correct color (green/red)
- [ ] Click on holding expands to show details
- [ ] Expanded details include:
  - [ ] Current price
  - [ ] Average cost price
  - [ ] Total cost basis
  - [ ] Current total value
- [ ] Click again collapses the details
- [ ] No holdings state message displays when empty

#### 1.3 Portfolio Chart
**Test Case**: CH-001 Chart timeframe switching
- [ ] Chart displays on load
- [ ] All 8 timeframe buttons are visible (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
- [ ] Clicking timeframe button updates chart
- [ ] Active timeframe button is highlighted
- [ ] Chart updates without freezing
- [ ] X and Y axes display correctly
- [ ] Chart is responsive on mobile (adjusts height/width)

**Test Case**: CH-002 Chart interactivity
- [ ] Hover over chart shows tooltip
- [ ] Tooltip displays correct OHLCV data
- [ ] Chart renders at smooth 60fps
- [ ] No lag when updating timeframes

### 2. Market Page Testing

#### 2.1 Market Indices
**Test Case**: MI-001 Indices display
- [ ] All 4 major indices display (S&P 500, NASDAQ, Russell 2000, Dow Jones)
- [ ] Each index shows:
  - [ ] Symbol (e.g., ^GSPC)
  - [ ] Current value
  - [ ] Change amount
  - [ ] Change percentage
  - [ ] Trend badge (Up/Down)
- [ ] Green color for positive changes
- [ ] Red color for negative changes
- [ ] Neutral gray for zero changes
- [ ] Indices update in real-time (5 second intervals)

#### 2.2 Sector Heatmap
**Test Case**: SH-001 Sector visualization
- [ ] All 11 sectors display
- [ ] Bar width represents change percentage
- [ ] Color intensity represents change magnitude
- [ ] Green for positive changes (>0%)
- [ ] Red for negative changes (<0%)
- [ ] Gray for neutral changes
- [ ] Percentage values display in bars
- [ ] Sectors sorted by percentage change (highest to lowest)
- [ ] Bar labels are readable on all screen sizes

**Test Case**: SH-002 Responsive behavior
- [ ] Heatmap responsive on mobile (<640px)
- [ ] Bar labels don't overflow on small screens
- [ ] Percentage values readable on all sizes

#### 2.3 Stock Search & Filtering
**Test Case**: SF-001 Search functionality
- [ ] Search input accepts stock symbols (e.g., "AAPL")
- [ ] Search accepts company names (e.g., "Apple")
- [ ] Search is case-insensitive
- [ ] Results filter in real-time as typing
- [ ] No results message when no matches found
- [ ] Search can be cleared to show all stocks

**Test Case**: SF-002 Sorting
- [ ] "Sort by Price" - displays highest to lowest price
- [ ] "Sort by Change" - displays highest to lowest change %
- [ ] "Sort by Volume" - displays highest to lowest volume
- [ ] Sorting works on filtered results
- [ ] Sorting persists when changing filters

#### 2.4 Stock Quotes
**Test Case**: SQ-001 Individual quote cards
- [ ] Quote card displays:
  - [ ] Symbol (bold, large)
  - [ ] Company name
  - [ ] Current price
  - [ ] Change amount and percentage
  - [ ] Bid/Ask spreads
  - [ ] Trend indicator (up/down/neutral badge)
  - [ ] Updated timestamp
- [ ] Card has hover effect
- [ ] Card clickable (opens order panel)
- [ ] Color coding:
  - [ ] Green for positive change
  - [ ] Red for negative change
  - [ ] Neutral gray for zero change

**Test Case**: SQ-002 Quote details
- [ ] Click "More Details" expands card
- [ ] Shows volume and average volume
- [ ] Shows P/E ratio if available
- [ ] Shows market cap if available
- [ ] Details collapse on second click

#### 2.5 Market Breadth
**Test Case**: MB-001 Breadth indicators
- [ ] Advancing stocks count displays
- [ ] Declining stocks count displays
- [ ] Unchanged stocks count displays
- [ ] VIX level displays
- [ ] Colors: Green for advancing, Red for declining, Gray for unchanged

### 3. Order Panel Testing

#### 3.1 Order Form Display
**Test Case**: OP-001 Form fields
- [ ] Order panel appears as floating window
- [ ] Correct positioning (bottom-right)
- [ ] Close button (X) in top-right
- [ ] All required fields visible:
  - [ ] Symbol input
  - [ ] Buy/Sell toggle buttons
  - [ ] Order Type dropdown
  - [ ] Quantity input
  - [ ] Price input (conditional)
- [ ] Form has clear styling (dark card)
- [ ] Submit and Cancel buttons visible

#### 3.2 Order Type Behavior
**Test Case**: OP-002 Order type conditional fields
- [ ] Market Order: No price field shown
- [ ] Limit Order: Price field appears
- [ ] Stop-Loss Order: Stop price field appears
- [ ] Trailing Stop Order: Trailing % field appears
- [ ] Switching types updates fields appropriately

**Test Case**: OP-003 Buy/Sell selection
- [ ] Buy button toggles to active state
- [ ] Sell button toggles to active state
- [ ] Only one can be active at a time
- [ ] Submit button color changes:
  - [ ] Green for Buy
  - [ ] Red for Sell

#### 3.3 Form Validation
**Test Case**: OP-004 Validation rules
- [ ] Symbol field:
  - [ ] Required (shows error if empty)
  - [ ] Uppercase conversion (ABC, not abc)
  - [ ] Invalid format rejected (123, A@B, etc.)
  - [ ] Error message displayed
- [ ] Quantity field:
  - [ ] Required
  - [ ] Must be positive integer
  - [ ] Decimal values rejected
  - [ ] Zero rejected
  - [ ] Error message for each case
- [ ] Price field (when required):
  - [ ] Required for limit/stop orders
  - [ ] Must be positive number
  - [ ] Decimal values accepted
  - [ ] Error message displayed

**Test Case**: OP-005 Form submission
- [ ] All validation passes, submit enabled
- [ ] Submit shows loading spinner
- [ ] Form clears on successful submit
- [ ] Close button closes form
- [ ] Clicking outside closes form (optional)

### 4. Orders List Testing

#### 4.1 Pending Orders
**Test Case**: OL-001 Pending orders display
- [ ] Pending orders section visible
- [ ] Shows count of pending orders
- [ ] Each pending order displays:
  - [ ] Symbol
  - [ ] Quantity with badge
  - [ ] Order type (market/limit/stop-loss)
  - [ ] Price (if applicable)
  - [ ] "Pending" badge in blue
  - [ ] Created timestamp
- [ ] Click pending order to expand
- [ ] Expanded shows Cancel Order button
- [ ] Cancel button removes order

**Test Case**: OL-002 Recent orders
- [ ] Recent orders section visible
- [ ] Shows completed/cancelled orders
- [ ] Last 5 recent orders displayed
- [ ] Each shows:
  - [ ] Symbol and quantity
  - [ ] Status badge (filled/cancelled/rejected/partial)
  - [ ] Filled quantity progress
  - [ ] Created timestamp
- [ ] Colored status badges:
  - [ ] Green for filled
  - [ ] Gray for cancelled
  - [ ] Red for rejected
  - [ ] Yellow for partial

#### 4.2 Order Details
**Test Case**: OL-003 Expanded order details
- [ ] Click order to expand
- [ ] Shows detailed information:
  - [ ] Order type (capitalized)
  - [ ] Price (if applicable)
  - [ ] Created time
  - [ ] Completed time (if applicable)
- [ ] Collapse on second click
- [ ] Smooth expand/collapse animation

### 5. Header & Navigation Testing

#### 5.1 Header Layout
**Test Case**: HD-001 Header components
- [ ] Logo/app name displays (SX - Stock Exchange)
- [ ] Search input visible (hidden on mobile)
- [ ] Theme toggle button visible
- [ ] Notifications bell icon visible
- [ ] Settings icon visible
- [ ] Sticky positioning (stays at top)
- [ ] No overlap with content below

**Test Case**: HD-002 Search functionality
- [ ] Search input has placeholder "Search stocks..."
- [ ] Type to search for symbol or company
- [ ] Enter/click to submit search
- [ ] Clear search to reset
- [ ] Mobile search bar appears below header

#### 5.3 Theme Toggle
**Test Case**: HD-003 Dark/Light mode
- [ ] Theme toggle button visible (moon/sun icon)
- [ ] Click toggles between light and dark
- [ ] Theme changes applied to:
  - [ ] Background colors
  - [ ] Text colors
  - [ ] Card backgrounds
  - [ ] Border colors
  - [ ] All UI elements
- [ ] Theme persists (check localStorage)
- [ ] All colors visible in both modes
- [ ] Contrast ratios maintained

### 6. Sidebar Navigation Testing

#### 6.1 Desktop Navigation
**Test Case**: SB-001 Desktop sidebar
- [ ] Sidebar visible on desktop (1024px+)
- [ ] Fixed width (not collapsing)
- [ ] Nav items visible:
  - [ ] Dashboard
  - [ ] Market Data
  - [ ] Portfolio
  - [ ] Orders
  - [ ] Watchlist
  - [ ] Price Alerts
  - [ ] Settings
- [ ] Current page highlighted
- [ ] Hover effect on items
- [ ] Click navigates to page
- [ ] Logout button at bottom

#### 6.2 Mobile Navigation
**Test Case**: SB-002 Mobile sidebar
- [ ] Hamburger menu visible on mobile (<1024px)
- [ ] Click opens sidebar overlay
- [ ] Sidebar slides in from left
- [ ] Dark overlay behind sidebar
- [ ] Click overlay closes sidebar
- [ ] Click nav item closes sidebar
- [ ] All items accessible
- [ ] Logout button visible

**Test Case**: SB-003 Sidebar functionality
- [ ] Navigation updates current page
- [ ] URL structure follows navigation (future enhancement)
- [ ] Navigation smooth without flickering

### 7. Responsive Design Testing

#### 7.1 Mobile (320px - 640px)
**Test Case**: RD-001 Mobile layout
- [ ] All content fits without horizontal scroll
- [ ] Cards stack vertically
- [ ] Buttons are touch-sized (minimum 44px)
- [ ] Text is readable (minimum 12px)
- [ ] Images scale appropriately
- [ ] Form inputs are spacious
- [ ] Grid collapses to single column
- [ ] Quote cards display properly in grid

**Test Case**: RD-002 Mobile interactions
- [ ] Tap targets are large enough
- [ ] No hover-only interactions
- [ ] Modals/panels display full screen or large overlay
- [ ] Order panel is accessible on mobile
- [ ] Search bar expands properly

#### 7.2 Tablet (640px - 1024px)
**Test Case**: RD-003 Tablet layout
- [ ] Sidebar collapses/expands
- [ ] Two-column layouts for cards
- [ ] Charts render with adequate height
- [ ] Grid displays 2-3 columns
- [ ] Touch interactions work

#### 7.3 Desktop (1024px+)
**Test Case**: RD-004 Desktop layout
- [ ] Full sidebar visible
- [ ] Multi-column grids display correctly
- [ ] Three+ column layouts work
- [ ] Charts render full size
- [ ] Mouse interactions functional

### 8. Accessibility Testing

#### 8.1 Keyboard Navigation
**Test Case**: AC-001 Keyboard navigation
- [ ] Tab moves focus through interactive elements
- [ ] Shift+Tab moves backward
- [ ] Enter/Space activates buttons
- [ ] Tab order is logical (left-to-right, top-to-bottom)
- [ ] Focus indicator visible on all elements
- [ ] Escape closes modals/panels
- [ ] Tab trap prevention in modals

**Test Case**: AC-002 Form accessibility
- [ ] Form labels associated with inputs
- [ ] Error messages linked to fields
- [ ] Help text readable by screen readers
- [ ] Required fields marked
- [ ] Form can be submitted via Enter key

#### 8.2 Screen Reader Testing
**Test Case**: AC-003 ARIA labels (with screen reader)
- [ ] Icons have aria-label or title
- [ ] Buttons announce their purpose
- [ ] Form fields announce their labels
- [ ] Error messages announce
- [ ] Status badges announce
- [ ] Charts announce data
- [ ] Dynamic updates announced

#### 8.3 Color Contrast
**Test Case**: AC-004 Contrast verification
- [ ] Text on background passes 4.5:1 ratio
- [ ] Large text passes 3:1 ratio
- [ ] Color not sole means of conveying information
- [ ] Status colors have text labels
- [ ] Both light and dark modes pass

#### 8.4 Visual Design
**Test Case**: AC-005 Visual accessibility
- [ ] Text is 12px minimum
- [ ] Line height adequate (1.5 or more)
- [ ] Focus indicators clear (2px minimum)
- [ ] No text color < #666 on white background
- [ ] Icons accompanied by text labels

### 9. Performance Testing

#### 9.1 Load Time
**Test Case**: PF-001 Initial load
- [ ] First paint: < 1.5 seconds
- [ ] First contentful paint: < 2 seconds
- [ ] Interactive: < 3 seconds
- [ ] Dashboard fully loaded: < 2 seconds
- [ ] No significant blocking

**Test Case**: PF-002 Component rendering
- [ ] Quote cards render immediately
- [ ] Chart renders without flashing
- [ ] Holdings list loads quickly
- [ ] No jank when scrolling

#### 9.2 Real-Time Updates
**Test Case**: PF-003 Quote updates
- [ ] Quotes update every 5 seconds
- [ ] Updates < 100ms to display
- [ ] No lag with 20+ quote updates
- [ ] Smooth transitions
- [ ] No memory leaks

**Test Case**: PF-004 Interaction responsiveness
- [ ] Button clicks respond immediately
- [ ] Form input updates instantaneous
- [ ] Search filters in real-time
- [ ] Modal open/close instant
- [ ] Theme toggle instant

### 10. Browser & Device Compatibility

#### 10.1 Browsers (Desktop)
**Test Case**: BC-001 Chrome/Edge (Chromium)
- [ ] All features work
- [ ] Styling correct
- [ ] No console errors
- [ ] Charts render properly
- [ ] Performance optimal

**Test Case**: BC-002 Firefox
- [ ] All features work
- [ ] Styling correct
- [ ] No console errors
- [ ] Form validation works
- [ ] Animations smooth

**Test Case**: BC-003 Safari
- [ ] All features work
- [ ] Styling correct
- [ ] No webkit-specific issues
- [ ] Touch interactions work
- [ ] Responsive design works

**Test Case**: BC-004 Edge
- [ ] All features work
- [ ] Styling consistent
- [ ] No errors

#### 10.2 Mobile Devices
**Test Case**: BD-001 iOS (iPad/iPhone)
- [ ] Safari browser: Full functionality
- [ ] Touch interactions responsive
- [ ] Viewport scaling correct
- [ ] No iOS-specific bugs
- [ ] Safe area (notch) respected

**Test Case**: BD-002 Android
- [ ] Chrome browser: Full functionality
- [ ] Touch interactions responsive
- [ ] Viewport scaling correct
- [ ] No Android-specific bugs
- [ ] Back button behavior correct

### 11. Data Validation Testing

#### 11.1 Form Input Validation
**Test Case**: DV-001 Symbol validation
- [ ] "AAPL" - Valid (accepted)
- [ ] "aapl" - Valid (converted to uppercase)
- [ ] "123" - Invalid (rejected)
- [ ] "A" - Valid (single letter accepted)
- [ ] "TOOLONG" - Invalid (> 5 chars rejected)
- [ ] "A@PL" - Invalid (special chars rejected)

**Test Case**: DV-002 Quantity validation
- [ ] "100" - Valid
- [ ] "1" - Valid
- [ ] "0" - Invalid (zero rejected)
- [ ] "-5" - Invalid (negative rejected)
- [ ] "10.5" - Invalid (decimals rejected)
- [ ] "abc" - Invalid (non-numeric rejected)

**Test Case**: DV-003 Price validation
- [ ] "150.50" - Valid
- [ ] "0.01" - Valid
- [ ] "0" - Invalid (zero rejected)
- [ ] "-50" - Invalid (negative rejected)
- [ ] "abc" - Invalid (non-numeric rejected)

**Test Case**: DV-004 Comprehensive order validation
- [ ] Valid buy order: All validations pass, submit enabled
- [ ] Invalid symbol: Error displays, submit disabled
- [ ] Invalid quantity: Error displays, submit disabled
- [ ] Missing price for limit: Error displays, submit disabled
- [ ] Insufficient balance (future): Error displays

### 12. Data Display Accuracy

#### 12.1 Number Formatting
**Test Case**: DD-001 Price formatting
- [ ] "123.456" displays as "123.46"
- [ ] "100" displays as "100.00"
- [ ] "0.5" displays as "0.50"
- [ ] "12345.6789" displays as "12,345.68"

**Test Case**: DD-002 Volume formatting
- [ ] "50000000" displays as "50.00M"
- [ ] "1500000000" displays as "1.50B"
- [ ] "5000" displays as "5.00K"
- [ ] "100" displays as "100"

**Test Case**: DD-003 Percentage formatting
- [ ] "2.5" displays as "+2.50%"
- [ ] "-3.456" displays as "-3.46%"
- [ ] "0" displays as "+0.00%"

**Test Case**: DD-004 Calculations
- [ ] Daily P&L = Current Value - Cost Basis
- [ ] P&L % = (P&L / Cost Basis) × 100
- [ ] Portfolio Total = Sum of Holdings
- [ ] Unrealized Gain = Current - Cost across all holdings

### 13. State Management Testing

#### 13.1 Store Updates
**Test Case**: SM-001 Market store updates
- [ ] Quote updates reflect immediately
- [ ] Multiple quotes update in batch
- [ ] Market status changes reflect
- [ ] Selected symbol changes reflect
- [ ] Indices update reflect

**Test Case**: SM-002 Portfolio store updates
- [ ] Holdings update reflect
- [ ] Orders update reflect
- [ ] Selected holding reflects
- [ ] Portfolio overview updates

**Test Case**: SM-003 UI store updates
- [ ] Theme toggle works
- [ ] Sidebar open/close works
- [ ] Modal visibility toggles
- [ ] Notifications appear/disappear
- [ ] Order panel shows/hides

#### 13.2 Store Persistence
**Test Case**: SM-004 Data persistence
- [ ] Refresh page - quote data resets (expected, simulated)
- [ ] Navigation between pages - data persists
- [ ] Close modal - store state maintained
- [ ] Multiple store updates - all synchronized

### 14. Error Handling Testing

#### 14.1 Validation Errors
**Test Case**: EH-001 Form error display
- [ ] Validation errors show immediately
- [ ] Error messages are clear
- [ ] Error colors are visible
- [ ] Multiple errors display together
- [ ] Errors clear when corrected

**Test Case**: EH-002 No errors with valid data
- [ ] Valid data submits without errors
- [ ] No false positive errors
- [ ] Form ready for submission

#### 14.2 API Error Handling (Future)
**Test Case**: EH-003 Network error handling
- [ ] Network error message displayed
- [ ] User can retry
- [ ] Loading state managed
- [ ] No data loss on error

### 15. User Experience Testing

#### 15.1 Visual Feedback
**Test Case**: UX-001 Interaction feedback
- [ ] Buttons show hover state
- [ ] Buttons show active state
- [ ] Buttons show disabled state
- [ ] Form inputs show focus state
- [ ] Cards show hover effect
- [ ] Loading state has spinner

**Test Case**: UX-002 Notifications
- [ ] Toast notifications appear
- [ ] Toast has correct message
- [ ] Toast auto-dismisses after 3 seconds
- [ ] Multiple toasts stack properly
- [ ] Close button works
- [ ] Colors indicate type (success/error/info)

#### 15.2 Consistency
**Test Case**: UX-003 Design consistency
- [ ] Button styling consistent
- [ ] Card styling consistent
- [ ] Color palette consistent
- [ ] Spacing consistent
- [ ] Typography consistent
- [ ] Icons style consistent

**Test Case**: UX-004 User expectations
- [ ] Navigation behaves as expected
- [ ] Form submission works as expected
- [ ] Modals close as expected
- [ ] Data displays as expected
- [ ] Updates happen as expected

## Test Execution Plan

### Phase 1: Automated Tests
1. Run all unit tests: `npm run test`
2. Review coverage report: `npm run coverage`
3. Fix any failing tests

### Phase 2: Manual Core Features
1. Test Dashboard (Sections 1, 5)
2. Test Market (Sections 2)
3. Test Orders (Sections 3, 4)
4. Test Responsive Design (Section 7)

### Phase 3: Cross-Browser
1. Chrome/Edge (Desktop)
2. Firefox (Desktop)
3. Safari (macOS, iOS)
4. Android browsers

### Phase 4: Accessibility & Performance
1. Keyboard navigation (Section 8)
2. Screen reader testing (Section 8)
3. Performance testing (Section 9)
4. Contrast verification (Section 8)

### Phase 5: Edge Cases & Validation
1. Data validation (Section 11)
2. Error handling (Section 14)
3. State management (Section 13)
4. User experience (Section 15)

## Known Issues & Limitations

### Current Limitations (Phase 1 MVP)
- Mock data used (real API integration in Phase 2)
- No user authentication yet
- No data persistence
- WebSocket not implemented
- Limited technical indicators
- No paper trading simulator
- No advanced charting features

### Planned Enhancements (Phase 2)
- Real API integration
- WebSocket for real-time updates
- Advanced charting with indicators
- Stock screener
- Price alerts
- Paper trading

## Regression Testing

After each update or fix:
1. Run automated tests: `npm run test`
2. Test modified components
3. Test related features
4. Verify no new issues

## Bug Reporting Template

```
Title: [COMPONENT] Brief description

Description:
- What happened
- What was expected
- Steps to reproduce
- Actual vs expected behavior

Screenshots/Video:
- Attach if visual issue

Environment:
- Browser: Chrome 120
- OS: macOS 14.2
- Device: Desktop/Mobile/Tablet
- Screen size: 1920x1080

Severity: Critical/High/Medium/Low
```

## Sign-Off Checklist

- [ ] All unit tests passing
- [ ] All manual test cases passing
- [ ] Browser compatibility verified
- [ ] Mobile responsiveness verified
- [ ] Accessibility standards met
- [ ] Performance targets met
- [ ] No console errors
- [ ] No visual issues
- [ ] Documentation complete
- [ ] Ready for deployment

## Contact & Support

For questions or issues during testing:
1. Review ARCHITECTURE.md for technical details
2. Review README.md for feature documentation
3. Check test files for implementation details
4. Report bugs using template above

---

**Last Updated**: March 10, 2026
**Test Suite Version**: 1.0
**Coverage**: 42 automated tests + 200+ manual test cases
