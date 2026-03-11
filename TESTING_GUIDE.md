# Testing Guide - Stock Exchange Board Frontend

**Version**: 1.0
**Framework**: Vitest + @testing-library/react
**Coverage Target**: 80%+ on business logic
**Last Updated**: March 11, 2026

---

## 1. Testing Overview

### Test Stack
- **Framework**: Vitest (Jest-compatible, Vite-native)
- **Testing Library**: @testing-library/react
- **DOM Environment**: jsdom
- **Assertions**: Vitest built-in expect()
- **User Interactions**: @testing-library/user-event

### Test Pyramid
```
        /\
       /  \  Integration Tests (10-15%)
      /    \
     /______\
    /        \
   /  Unit    \ Unit Tests (60-70%)
  /  Tests     \
 /______________\
/                 \
/ Snapshot Tests   \ Snapshot Tests (10-15%)
/__________________\
```

---

## 2. Running Tests

### Basic Commands
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test Button.test.tsx

# Run tests matching pattern
npm test -- --grep "Button"

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run coverage

# Check coverage
npm run coverage -- --reporter=text
```

### CI/CD Integration
```bash
# Run tests with coverage (CI mode)
npm test -- --coverage --reporter=verbose
```

---

## 3. Test Structure

### Directory Organization
```
src/
├── components/
│   ├── Button.tsx
│   ├── Card.tsx
│   └── __tests__/
│       ├── Button.test.tsx
│       ├── Card.test.tsx
│       └── shared.test-utils.tsx
├── hooks/
│   ├── useMarketData.ts
│   └── __tests__/
│       └── useMarketData.test.ts
├── services/
│   ├── api.ts
│   └── __tests__/
│       └── api.test.ts
└── stores/
    ├── market.ts
    └── __tests__/
        └── market.test.ts
```

### Test File Naming
- Test files: `*.test.ts` or `*.test.tsx`
- Utils: `*.test-utils.ts` or `*.test-utils.tsx`
- Fixtures: `*.fixtures.ts`

---

## 4. Component Testing

### Example: Button Component Test

```typescript
// src/components/common/__tests__/Button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../Button'

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders with text content', () => {
      render(<Button>Click me</Button>)
      expect(screen.getByText('Click me')).toBeTruthy()
    })

    it('renders with icon', () => {
      const icon = <span data-testid="icon">Icon</span>
      render(<Button icon={icon}>Button</Button>)
      expect(screen.getByTestId('icon')).toBeTruthy()
    })

    it('renders in disabled state', () => {
      render(<Button disabled>Disabled</Button>)
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('disabled')
    })
  })

  describe('Variants', () => {
    it('applies primary variant styles', () => {
      render(<Button variant="primary">Primary</Button>)
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-accent-600')
    })

    it('applies danger variant styles', () => {
      render(<Button variant="danger">Delete</Button>)
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-danger')
    })
  })

  describe('Interactions', () => {
    it('calls onClick handler when clicked', async () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click</Button>)

      await userEvent.click(screen.getByRole('button'))
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('does not call onClick when disabled', async () => {
      const handleClick = vi.fn()
      render(
        <Button disabled onClick={handleClick}>
          Click
        </Button>
      )

      const button = screen.getByRole('button')
      await userEvent.click(button)
      expect(handleClick).not.toHaveBeenCalled()
    })

    it('shows loading state', () => {
      render(<Button isLoading>Loading</Button>)
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('disabled')
    })
  })

  describe('Accessibility', () => {
    it('is keyboard accessible', async () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Button</Button>)

      const button = screen.getByRole('button')
      button.focus()
      expect(button).toHaveFocus()

      await userEvent.keyboard('{Enter}')
      expect(handleClick).toHaveBeenCalled()
    })

    it('has proper ARIA attributes', () => {
      render(<Button aria-label="Close modal">X</Button>)
      expect(screen.getByLabelText('Close modal')).toBeTruthy()
    })
  })
})
```

### Example: Card Component Test

```typescript
// src/components/common/__tests__/Card.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Card } from '../Card'

describe('Card Component', () => {
  it('renders children', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card content')).toBeTruthy()
  })

  it('renders with header', () => {
    render(
      <Card header={<h2>Card Header</h2>}>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card Header')).toBeTruthy()
  })

  it('renders with footer', () => {
    render(
      <Card footer={<div>Card Footer</div>}>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card Footer')).toBeTruthy()
  })

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">Content</Card>
    )
    expect(container.firstChild).toHaveClass('custom-class')
  })
})
```

---

## 5. Hook Testing

### Example: useMarketData Hook Test

```typescript
// src/hooks/__tests__/useMarketData.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useMarketData } from '../useMarketData'
import * as api from '@services/api'

vi.mock('@services/api')

describe('useMarketData Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads market data on mount', async () => {
    const mockQuotes = {
      AAPL: { symbol: 'AAPL', price: 150.25, change: 2.50 }
    }

    vi.mocked(api.getQuotes).mockResolvedValue(mockQuotes)

    renderHook(() => useMarketData())

    await waitFor(() => {
      expect(api.getQuotes).toHaveBeenCalled()
    })
  })

  it('handles loading state', async () => {
    const { result } = renderHook(() => useMarketData())

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
  })

  it('handles errors gracefully', async () => {
    const error = new Error('API Error')
    vi.mocked(api.getQuotes).mockRejectedValue(error)

    const { result } = renderHook(() => useMarketData())

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
    })
  })
})
```

---

## 6. Store Testing (Zustand)

### Example: Market Store Test

```typescript
// src/stores/__tests__/market.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useMarketStore } from '../market'

describe('Market Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useMarketStore.setState({
      quotes: {},
      selectedSymbol: null,
      indices: [],
    })
  })

  describe('Quote Management', () => {
    it('sets a single quote', () => {
      const store = useMarketStore.getState()
      const newQuote = {
        symbol: 'AAPL',
        price: 150.25,
        change: 2.50,
        changePercent: 1.70,
      }

      store.setQuote(newQuote)

      const state = useMarketStore.getState()
      expect(state.quotes['AAPL']).toEqual(newQuote)
    })

    it('updates multiple quotes', () => {
      const store = useMarketStore.getState()
      const quotes = [
        { symbol: 'AAPL', price: 150.25 },
        { symbol: 'GOOGL', price: 140.50 },
      ]

      store.setQuotes(quotes)

      const state = useMarketStore.getState()
      expect(Object.keys(state.quotes).length).toBe(2)
      expect(state.quotes['AAPL']).toBeTruthy()
      expect(state.quotes['GOOGL']).toBeTruthy()
    })

    it('selects a symbol', () => {
      const store = useMarketStore.getState()
      store.setSelectedSymbol('AAPL')

      const state = useMarketStore.getState()
      expect(state.selectedSymbol).toBe('AAPL')
    })
  })

  describe('Indices', () => {
    it('sets market indices', () => {
      const store = useMarketStore.getState()
      const indices = [
        { symbol: '^GSPC', name: 'S&P 500', value: 4500.25, change: 25.50 },
      ]

      store.setIndices(indices)

      const state = useMarketStore.getState()
      expect(state.indices.length).toBe(1)
      expect(state.indices[0].symbol).toBe('^GSPC')
    })
  })
})
```

---

## 7. Service Testing

### Example: API Service Test

```typescript
// src/services/__tests__/api.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import { apiClient } from '../api'

vi.mock('axios')

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Quote API', () => {
    it('fetches a single quote', async () => {
      const mockQuote = {
        symbol: 'AAPL',
        price: 150.25,
        change: 2.50,
      }

      vi.mocked(axios.get).mockResolvedValue({ data: mockQuote })

      const result = await apiClient.get('/quotes/AAPL')
      expect(result.data).toEqual(mockQuote)
    })

    it('handles API errors', async () => {
      const error = new Error('Not Found')
      vi.mocked(axios.get).mockRejectedValue(error)

      await expect(apiClient.get('/quotes/INVALID')).rejects.toThrow()
    })
  })

  describe('Authentication', () => {
    it('includes auth token in headers', async () => {
      localStorage.setItem('access_token', 'test-token')

      await apiClient.get('/portfolio')

      const calls = vi.mocked(axios.get).mock.calls
      expect(calls[0][1].headers.Authorization).toContain('Bearer')
    })

    it('redirects to login on 401', async () => {
      const error = new Error('Unauthorized')
      ;(error as any).response = { status: 401 }
      vi.mocked(axios.get).mockRejectedValue(error)

      await expect(apiClient.get('/portfolio')).rejects.toThrow()
    })
  })
})
```

---

## 8. Page Testing

### Example: Dashboard Page Test

```typescript
// src/pages/__tests__/Dashboard.test.tsx
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { Dashboard } from '../Dashboard'
import * as marketService from '@services/api'

vi.mock('@services/api')

describe('Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    render(<Dashboard />)
    expect(screen.getByText('Dashboard')).toBeTruthy()
  })

  it('renders portfolio overview', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Portfolio Overview')).toBeTruthy()
    })
  })

  it('renders market indices', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Market Indices')).toBeTruthy()
    })
  })

  it('renders holdings list', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Your Holdings')).toBeTruthy()
    })
  })

  it('has place order button', () => {
    render(<Dashboard />)
    expect(screen.getByRole('button', { name: /place order/i })).toBeTruthy()
  })
})
```

---

## 9. Test Utilities

### Setup Helpers

```typescript
// src/__tests__/test-utils.tsx
import React from 'react'
import { render } from '@testing-library/react'

// Provider wrapper for tests that need store access
export function renderWithProviders(
  ui: React.ReactElement,
  options = {}
) {
  return render(ui, { wrapper: TestProviders, ...options })
}

function TestProviders({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
```

### Mock Data Helpers

```typescript
// src/services/__tests__/fixtures.ts
export const mockQuote = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 150.25,
  change: 2.50,
  changePercent: 1.70,
  bid: 150.20,
  ask: 150.30,
  volume: 50000000,
  avgVolume: 45000000,
  timestamp: Date.now(),
  trend: 'up' as const,
}

export const mockPortfolio = {
  id: '1',
  userId: 'user1',
  name: 'Main Portfolio',
  totalValue: 100000,
  totalCost: 95000,
  dayPnL: 500,
  dayPnLPercent: 0.5,
  unrealizedGain: 5000,
  unrealizedGainPercent: 5.26,
  lastUpdated: Date.now(),
  holdings: [],
}

export const mockOrder = {
  id: '1',
  symbol: 'AAPL',
  side: 'buy' as const,
  type: 'market' as const,
  quantity: 10,
  filledQuantity: 10,
  status: 'filled' as const,
  createdAt: Date.now(),
  updatedAt: Date.now(),
}
```

---

## 10. Integration Testing

### Example: Order Flow Test

```typescript
// src/__tests__/integration/order-flow.test.tsx
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { StockExchangeBoard } from '@pages/StockExchangeBoard'
import * as api from '@services/api'

vi.mock('@services/api')

describe('Order Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('completes full order workflow', async () => {
    const user = userEvent.setup()

    vi.mocked(api.getQuotes).mockResolvedValue({
      AAPL: {
        symbol: 'AAPL',
        price: 150.25,
        change: 2.50,
      },
    })

    vi.mocked(api.createOrder).mockResolvedValue({
      id: '1',
      symbol: 'AAPL',
      side: 'buy',
      quantity: 10,
      status: 'pending',
    })

    render(<StockExchangeBoard />)

    // Click place order button
    const placeOrderBtn = screen.getByRole('button', {
      name: /place order/i,
    })
    await user.click(placeOrderBtn)

    // Wait for order form
    await waitFor(() => {
      expect(screen.getByLabelText(/symbol/i)).toBeTruthy()
    })

    // Fill in order details
    const symbolInput = screen.getByLabelText(/symbol/i)
    await user.type(symbolInput, 'AAPL')

    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.type(quantityInput, '10')

    // Submit order
    const submitBtn = screen.getByRole('button', { name: /submit|confirm/i })
    await user.click(submitBtn)

    // Verify API call
    await waitFor(() => {
      expect(api.createOrder).toHaveBeenCalledWith(
        expect.objectContaining({
          symbol: 'AAPL',
          quantity: 10,
        })
      )
    })

    // Verify success message
    expect(screen.getByText(/success|confirmed/i)).toBeTruthy()
  })
})
```

---

## 11. Coverage Reports

### Generating Coverage

```bash
# Generate coverage report
npm run coverage

# Output: coverage/
#   ├── lcov.info
#   ├── lcov-report/index.html
#   └── coverage-summary.json
```

### Coverage Goals by Type

**Critical Business Logic**: 90%+
- Store actions
- Validation functions
- Calculation functions

**Components**: 80%+
- User interactions
- Conditional rendering
- Props handling

**Utilities**: 85%+
- Formatting functions
- Constants usage
- Edge cases

**Overall Target**: 80%+

### Improving Coverage

```bash
# Check uncovered lines
npm run coverage -- --reporter=text

# Generate HTML report
npm run coverage
open coverage/lcov-report/index.html
```

---

## 12. Best Practices

### Do's
✓ Test user interactions, not implementation details
✓ Use semantic queries (getByRole, getByLabelText)
✓ Test accessibility requirements
✓ Mock external dependencies
✓ Use descriptive test names
✓ Keep tests focused and isolated
✓ Test error states and edge cases

### Don'ts
✗ Test implementation details (internal state)
✗ Use shallow rendering
✗ Test third-party library internals
✗ Write brittle snapshot tests
✗ Make real API calls
✗ Skip async operations with await
✗ Test CSS directly

### Example: Good vs Bad

**Bad Test:**
```typescript
// Tests implementation, not user behavior
it('button state updates', () => {
  const { result } = renderHook(() => useState(false))
  act(() => result.current[1](true))
  expect(result.current[0]).toBe(true)
})
```

**Good Test:**
```typescript
// Tests user interaction and outcome
it('places order when submit clicked', async () => {
  const user = userEvent.setup()
  render(<OrderForm onSubmit={vi.fn()} />)

  await user.click(screen.getByRole('button', { name: /submit/i }))

  expect(screen.getByText(/success/i)).toBeTruthy()
})
```

---

## 13. Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

---

## 14. Debugging Tests

### Debug Mode

```bash
# Run tests with debug output
npm test -- --reporter=verbose

# Debug in VS Code
# Add breakpoint and run with debugger
node --inspect-brk ./node_modules/vitest/vitest.mjs
```

### Inspect Rendered Output

```typescript
it('renders correctly', () => {
  const { debug } = render(<Component />)
  debug() // Logs rendered HTML
})
```

### Wait for Elements

```typescript
// Good - waits for element
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeTruthy()
})

// Bad - doesn't wait, flaky
expect(screen.getByText('Loaded')).toBeTruthy()
```

---

## 15. Testing Checklist

Before committing code:

- [ ] All tests pass: `npm test`
- [ ] Coverage is 80%+: `npm run coverage`
- [ ] No console errors in test output
- [ ] Tests follow naming conventions
- [ ] Mocks are cleaned up between tests
- [ ] No hardcoded timeouts (use waitFor)
- [ ] Tests are isolated and deterministic
- [ ] Accessibility tested (roles, labels)
- [ ] Error states are tested
- [ ] Edge cases are covered

---

## Conclusion

Comprehensive testing ensures the frontend is reliable, maintainable, and accessible. Follow these guidelines and best practices to maintain high code quality.

**Key Points:**
- Arrange-Act-Assert pattern for clarity
- Test behavior, not implementation
- Mock external dependencies
- Aim for 80%+ coverage on business logic
- Use semantic queries for accessibility
- Keep tests fast and focused

---

**Document Version**: 1.0
**Last Updated**: March 11, 2026
**Maintainer**: Frontend QA Team
