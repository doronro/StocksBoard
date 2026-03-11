# QA Test Recommendations & Test Plan

**Date**: March 11, 2026
**Purpose**: Outline comprehensive testing strategy to achieve production readiness
**Target**: 95%+ test coverage of critical business logic

---

## 1. CRITICAL PATH INTEGRATION TESTS (MUST ADD)

### 1.1 Order Execution End-to-End
**Status**: NOT TESTED - HIGH PRIORITY

```typescript
// Test: Complete order lifecycle
describe('Order Execution Flow', () => {
  it('Should create order -> receive confirmation -> see in portfolio', async () => {
    // 1. User submits order form
    // 2. Frontend calls /api/orders POST
    // 3. Backend validates order
    // 4. Order saved to database
    // 5. Response returned with order ID
    // 6. Frontend displays confirmation
    // 7. Portfolio updates with pending order
    // 8. WebSocket sends order status update
    // 9. Portfolio shows filled order
    // Expected: Full order visible in portfolio
  })

  it('Should handle order rejection with error message', async () => {
    // 1. User tries to place invalid order (e.g., 0 quantity)
    // 2. Backend validation fails
    // 3. Error returned with clear message
    // 4. Frontend displays error to user
    // 5. Form remains open for correction
    // Expected: User can see and understand error
  })

  it('Should prevent duplicate orders on rapid clicks', async () => {
    // 1. User rapidly clicks "Place Order" button twice
    // 2. Only one order should be created
    // 3. Second request should be rejected or merged
    // Expected: Single order in system
  })
})
```

### 1.2 Portfolio Real-Time Sync
**Status**: NOT TESTED - HIGH PRIORITY

```typescript
describe('Portfolio Real-Time Updates', () => {
  it('Should update portfolio P&L when price changes', async () => {
    // Setup: Portfolio with 100 shares @ $50
    // 1. Price updates to $52
    // 2. WebSocket sends quote update
    // 3. Frontend receives update
    // 4. Store updates quote
    // 5. Portfolio re-calculates P&L
    // Expected: Portfolio shows +$200 gain, +4%
  })

  it('Should handle multiple price updates correctly', async () => {
    // Setup: 5 positions with quotes
    // 1. Receive quote updates for all 5 symbols
    // 2. P&L recalculates for each
    // 3. Portfolio total reflects all changes
    // Expected: Portfolio metrics accurate after all updates
  })

  it('Should recover from WebSocket disconnect', async () => {
    // 1. WebSocket connected, receiving updates
    // 2. Connection drops
    // 3. UI shows "Disconnected" indicator
    // 4. Fallback to polling starts
    // 5. Connection re-establishes
    // 6. Real-time updates resume
    // Expected: Seamless recovery, no data loss
  })
})
```

### 1.3 Compliance Check Integration
**Status**: NOT TESTED - HIGH PRIORITY

```typescript
describe('Compliance Rule Enforcement', () => {
  it('Should block order if PDT rule violated', async () => {
    // Setup: Account with $25k, 4 round trips in 5 days
    // 1. User tries to place 5th round trip
    // 2. Backend checks compliance
    // 3. Order rejected with PDT warning
    // 4. User informed of remaining day trades
    // Expected: Order blocked, user informed
  })

  it('Should detect wash sales', async () => {
    // Setup: User sold AAPL at $50 loss on Monday
    // 1. User tries to buy AAPL on Tuesday
    // 2. Compliance check detects wash sale
    // 3. User receives warning (not blocked)
    // Expected: Warning shown, allows user to decide
  })
})
```

---

## 2. DATA INTEGRITY TESTS (MUST ADD)

### 2.1 Portfolio Calculation Accuracy
**Status**: PARTIAL - NEEDS EXPANSION

```typescript
describe('Portfolio Calculations', () => {
  it('Should correctly calculate P&L with mixed gains and losses', () => {
    // Position 1: 100 shares @ $50 cost, now $55 = +$500
    // Position 2: 50 shares @ $100 cost, now $95 = -$250
    // Expected: Total = +$250 gain, +6.67%
  })

  it('Should handle position with 0 cost basis', () => {
    // Edge case: Position created with cost_basis = 0
    // Expected: No division by zero error, graceful handling
  })

  it('Should calculate concentration risk accurately', () => {
    // Portfolio with 10 equal positions = Herfindahl = 1/10 = 0.1
    // Portfolio with 1 position = Herfindahl = 1.0
    // Expected: Correct Herfindahl calculations
  })

  it('Should not count closed positions in open count', () => {
    // Setup: 10 open, 5 closed positions
    // Expected: open_positions_count = 10, closed_positions_count = 5
  })
})
```

### 2.2 Financial Precision Tests
**Status**: NOT TESTED - HIGH PRIORITY

```typescript
describe('Financial Precision', () => {
  it('Should maintain precision in margin calculations', () => {
    // Setup: Portfolio value = $1,234,567.8901234
    // Expected: Stored as Decimal, not float
    // Expected: API returns 2-decimal precision
  })

  it('Should correctly handle fractional shares', () => {
    // Setup: 1.5 shares @ $100 = $150
    // Expected: Total cost = $150.00, no rounding errors
  })

  it('Should calculate percentages without loss', () => {
    // Setup: P&L of $1 on $3 portfolio = 33.333...%
    // Expected: Rounded to 2 decimals: 33.33%
  })
})
```

---

## 3. ERROR & EDGE CASE TESTS (MUST ADD)

### 3.1 API Error Handling
**Status**: PARTIAL - NEEDS COVERAGE

```typescript
describe('API Error Scenarios', () => {
  it('Should handle 500 server error gracefully', () => {
    // API returns 500 error
    // Expected: User sees error message, can retry
  })

  it('Should handle timeout on slow API', () => {
    // API takes >10s to respond
    // Expected: Request timeout, user sees error
  })

  it('Should handle network failure', () => {
    // No network connection
    // Expected: Error message, suggests checking connection
  })

  it('Should handle invalid JSON response', () => {
    // API returns non-JSON response
    // Expected: Error caught, user informed
  })
})
```

### 3.2 Form Validation Edge Cases
**Status**: PARTIAL - NEEDS EXPANSION

```typescript
describe('Order Form Validation', () => {
  it('Should reject symbol "123" (numbers only)', () => {
    // Input: "123"
    // Expected: Error message
  })

  it('Should accept symbol "BRK.B" (with class)', () => {
    // Input: "BRK.B"
    // Expected: Accepted
  })

  it('Should handle symbol longer than 5 chars', () => {
    // Input: "TOOLONGSYMBOL"
    // Expected: Truncated or error
  })

  it('Should validate price fields', () => {
    // Input: -$50 (negative price)
    // Expected: Error
    // Input: $0.01 (valid minimum)
    // Expected: Accepted
    // Input: $999,999.99 (large value)
    // Expected: Accepted
  })

  it('Should validate quantity', () => {
    // Input: 0 shares
    // Expected: Error
    // Input: 0.5 shares (fractional)
    // Expected: Error (must be integer)
    // Input: 1,000,000 shares
    // Expected: Accepted
  })
})
```

---

## 4. PERFORMANCE TESTS (MUST ADD)

### 4.1 Large Portfolio Performance
**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Performance with Large Portfolios', () => {
  it('Should calculate risk metrics for 50+ positions in <500ms', () => {
    // Setup: Portfolio with 100 positions
    // 1. Call risk calculation endpoint
    // 2. Measure response time
    // Expected: <500ms response time
  })

  it('Should render portfolio with 100 holdings in <2s', () => {
    // Setup: Frontend loads portfolio with 100 holdings
    // 1. Measure initial render time
    // 2. Measure subsequent price updates
    // Expected: <2s initial, <100ms per update
  })

  it('Should handle WebSocket updates for 50+ symbols', () => {
    // Setup: Subscribe to 50 symbols
    // 1. Send rapid price updates for all
    // 2. Measure UI update latency
    // Expected: <100ms latency, no jank
  })
})
```

### 4.2 Database Query Performance
**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Database Performance', () => {
  it('Should not have N+1 query problem in portfolio', () => {
    // Expected query count: 2 (positions + stocks joined)
    // Actual query count if N+1: 101 (1 + 100 for each stock)
  })

  it('Should execute wash sale detection for 1000 orders in <2s', () => {
    // Setup: 1000 orders in history
    // 1. Call detect_wash_sales
    // 2. Measure execution time
    // Expected: <2s
  })
})
```

---

## 5. ACCESSIBILITY TESTS (MUST ADD)

### 5.1 Keyboard Navigation
**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Keyboard Navigation', () => {
  it('Should navigate order form with Tab key', () => {
    // 1. Tab through all form fields
    // 2. Expected order: Symbol -> Quantity -> Price -> Side -> Submit
    // 3. Should not skip any fields
    // Expected: All elements reachable via keyboard
  })

  it('Should submit form with Enter key', () => {
    // 1. Fill form
    // 2. Press Enter on submit button
    // Expected: Form submits
  })

  it('Should close modal with Escape key', () => {
    // 1. Open order panel
    // 2. Press Escape
    // Expected: Modal closes
  })
})
```

### 5.2 Screen Reader Support
**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Screen Reader Support', () => {
  it('Should announce form labels to screen readers', () => {
    // Expected: Each input has associated label
    // Expected: Labels use htmlFor attribute
  })

  it('Should announce error messages', () => {
    // 1. Form validation error occurs
    // 2. Expected: Error announced
    // 3. Expected: Error associated with input (aria-errormessage)
  })

  it('Should announce order status changes', () => {
    // 1. Order moves from pending to filled
    // 2. Expected: Status change announced
  })
})
```

### 5.3 Focus Management
**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Focus Management', () => {
  it('Should show visible focus indicator', () => {
    // 1. Tab to button
    // 2. Expected: Clear focus ring visible
  })

  it('Should restore focus after modal close', () => {
    // 1. Click button to open modal
    // 2. Close modal with Escape
    // 3. Expected: Focus returns to original button
  })
})
```

---

## 6. SECURITY TESTS (MUST ADD)

### 6.1 Authentication
**Status**: PARTIAL - NEEDS COVERAGE

```typescript
describe('Authentication', () => {
  it('Should require authentication for protected endpoints', () => {
    // 1. Call /api/portfolio without token
    // 2. Expected: 401 Unauthorized
  })

  it('Should reject invalid tokens', () => {
    // 1. Call with invalid JWT
    // 2. Expected: 401 Unauthorized
  })

  it('Should redirect to login on 401', () => {
    // 1. Token expires during session
    // 2. API returns 401
    // 3. Expected: Redirect to login page
  })
})
```

### 6.2 Authorization
**Status**: NOT TESTED - HIGH PRIORITY

```typescript
describe('Authorization', () => {
  it('Should not allow user to access other user portfolio', () => {
    // Setup: Two users (Alice, Bob)
    // 1. Alice's token
    // 2. Call /api/portfolio/456 (Bob's portfolio)
    // 3. Expected: 403 Forbidden
  })

  it('Should not allow user to modify other user orders', () => {
    // Setup: Two users
    // 1. User A's token
    // 2. Try to cancel User B's order
    // 3. Expected: 403 Forbidden
  })

  it('Should not allow user to delete other user alerts', () => {
    // Similar authorization check
    // Expected: 403 Forbidden
  })
})
```

### 6.3 Input Validation
**Status**: PARTIAL - NEEDS COVERAGE

```typescript
describe('Input Validation & XSS Prevention', () => {
  it('Should not execute JavaScript in symbol field', () => {
    // Input: "<script>alert('xss')</script>"
    // Expected: Treated as literal string, not executed
  })

  it('Should escape HTML in user input', () => {
    // Input: "<b>AAPL</b>"
    // Expected: Displayed as literal text, not bold
  })

  it('Should reject SQL injection attempts', () => {
    // Input: "AAPL'; DROP TABLE orders; --"
    // Expected: Treated as literal string, not executed
  })
})
```

---

## 7. CROSS-BROWSER TESTS (MUST ADD)

**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Cross-Browser Compatibility', () => {
  browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']

  it('Should render correctly in all browsers', () => {
    // 1. Load application
    // 2. Verify layout, colors, fonts
    // Expected: Consistent appearance
  })

  it('Should support WebSocket in all browsers', () => {
    // 1. Connect to WebSocket
    // 2. Send and receive messages
    // Expected: Works in all browsers
  })

  it('Should handle API calls in all browsers', () => {
    // 1. Make HTTP requests
    // Expected: Works in all browsers
  })
})
```

---

## 8. MOBILE TESTS (MUST ADD)

**Status**: NOT TESTED - MEDIUM PRIORITY

```typescript
describe('Mobile Responsiveness', () => {
  viewports = ['iPhone SE (375px)', 'iPhone 12 (390px)', 'iPad (768px)']

  it('Should render correctly on mobile', () => {
    // 1. Load on mobile viewport
    // 2. Verify layout adapted
    // Expected: No horizontal scroll, readable text
  })

  it('Should have touch-friendly buttons', () => {
    // 1. On mobile, button sizes
    // Expected: All buttons >= 44px height
  })

  it('Should work without hover', () => {
    // 1. On touchscreen device
    // 2. Test all interactions
    // Expected: No hover-only features
  })
})
```

---

## 9. LOAD TESTING (SHOULD ADD)

**Status**: NOT TESTED - LOW PRIORITY (After critical fixes)

```typescript
describe('Load Testing', () => {
  it('Should handle 100 concurrent users', () => {
    // 1. Simulate 100 users logging in
    // 2. Each fetches portfolio
    // 3. Each places order
    // Expected: <500ms response times
  })

  it('Should handle high-frequency updates', () => {
    // 1. WebSocket sends 100 quotes/second
    // 2. Frontend processes all
    // Expected: No dropped updates, <100ms latency
  })
})
```

---

## TESTING SUMMARY

### Total Tests to Add: ~80-100

| Category | Tests | Priority | Timeline |
|----------|-------|----------|----------|
| Integration | 12 | CRITICAL | Week 1 |
| Data Integrity | 8 | CRITICAL | Week 1 |
| Error Handling | 10 | HIGH | Week 1 |
| Performance | 6 | MEDIUM | Week 2 |
| Accessibility | 9 | MEDIUM | Week 2 |
| Security | 8 | HIGH | Week 1 |
| Cross-Browser | 5 | MEDIUM | Week 2 |
| Mobile | 6 | MEDIUM | Week 2 |
| Load | 4 | LOW | Week 3 |

### Coverage After Adding Tests
- Current: 168 (frontend) + 41 (backend) = **209 tests**
- After additions: **209 + 80-100 = 289-309 tests**
- Target coverage: **95%+ of critical business logic**

---

## Recommended Testing Tools

### Frontend
- **Vitest**: Already in use, good for unit tests
- **Cypress**: E2E testing (add)
- **Playwright**: Cross-browser E2E (add)
- **Testing Library**: Already in use
- **Axe-core**: Accessibility testing (add)

### Backend
- **pytest**: Already in use
- **pytest-asyncio**: Async test support (add)
- **pytest-cov**: Coverage reporting (enhance)
- **Factory Boy**: Test data generation (add)

### Load Testing
- **k6**: Lightweight load testing (add)
- **Locust**: Python-based load testing (add)

---

## Implementation Plan

### Phase 1 (Week 1): Critical Tests
1. Add integration tests for order execution
2. Add data integrity tests
3. Add security authorization tests
4. All pass before proceeding to Phase 2

### Phase 2 (Week 2): Functional Tests
1. Add accessibility tests
2. Add error handling tests
3. Add cross-browser tests
4. Add mobile tests

### Phase 3 (Week 3): Performance Tests
1. Add load tests
2. Establish performance baseline
3. Optimize hot paths if needed

---

**Target**: Achieve 95%+ test coverage of critical business logic before production deployment.

