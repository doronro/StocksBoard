# Developer Quick Start Guide - Stock Exchange Board Frontend

**Last Updated**: March 11, 2026
**Version**: 1.0

Quick reference for developers getting started with the Stock Exchange Board frontend.

---

## 1. Project Setup

### Clone and Install
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Visit http://localhost:3000
```

### Verify Setup
```bash
# Type checking
npm run type-check

# Run tests
npm test

# Build production
npm run build
```

---

## 2. Key Commands

### Development
```bash
npm run dev          # Start dev server (port 3000)
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # Check TypeScript types
npm run lint         # Run ESLint
```

### Testing
```bash
npm test             # Run all tests
npm test -- --watch  # Watch mode
npm run test:ui      # Visual test UI
npm run coverage     # Coverage report
```

---

## 3. Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Atomic components (Button, Card, Badge, Input, etc.)
│   ├── layout/         # Layout (Header, Sidebar, NotificationCenter)
│   ├── market/         # Market components (MarketIndices, QuoteCard, etc.)
│   ├── charts/         # Charts (CandlestickChart, TechnicalIndicators)
│   ├── portfolio/      # Portfolio (PortfolioOverview, HoldingsList)
│   ├── orders/         # Orders (OrderPanel, OrderConfirmationModal, etc.)
│   ├── watchlist/      # Watchlist (WatchlistPanel, WatchlistCard)
│   ├── alerts/         # Alerts (AlertManager)
│   └── calendar/       # Calendar (EarningsCalendar)
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── Market.tsx
│   └── StockExchangeBoard.tsx
├── hooks/              # Custom hooks
│   ├── useMarketData.ts
│   ├── usePortfolioData.ts
│   └── useRealtimeQuotes.ts
├── stores/             # Zustand state management
│   ├── market.ts       # Market data state
│   ├── portfolio.ts    # Portfolio state
│   ├── watchlist.ts    # Watchlist state
│   ├── ui.ts           # UI state
│   └── preferences.ts  # User preferences
├── services/           # API and utilities
│   ├── api.ts          # API client (axios)
│   ├── mockData.ts     # Mock data generation
│   └── websocket.ts    # WebSocket client
├── utils/              # Utilities
│   ├── formatting.ts   # Number/date formatting
│   ├── validation.ts   # Input validation
│   └── constants.ts    # App constants
├── types/              # TypeScript definitions
│   └── index.ts
└── test/               # Test configuration
    └── setup.ts
```

---

## 4. Creating New Components

### Atomic Component (e.g., Toggle)
```typescript
// src/components/common/Toggle.tsx
import React from 'react'

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
}

export const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
}) => {
  return (
    <div className="flex items-center gap-2">
      <button
        role="switch"
        aria-checked={checked}
        aria-label={label}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`w-10 h-6 rounded-full transition-colors ${
          checked ? 'bg-accent-600' : 'bg-neutral-300'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <div
          className={`w-5 h-5 rounded-full bg-white transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
      {label && <label className="text-sm font-medium">{label}</label>}
    </div>
  )
}
```

### With Tests
```typescript
// src/components/common/__tests__/Toggle.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Toggle } from '../Toggle'

describe('Toggle Component', () => {
  it('renders checked state', () => {
    render(<Toggle checked={true} onChange={vi.fn()} />)
    const button = screen.getByRole('switch')
    expect(button).toHaveAttribute('aria-checked', 'true')
  })

  it('calls onChange when clicked', async () => {
    const handleChange = vi.fn()
    const user = userEvent.setup()
    render(<Toggle checked={false} onChange={handleChange} />)

    await user.click(screen.getByRole('switch'))
    expect(handleChange).toHaveBeenCalledWith(true)
  })
})
```

---

## 5. State Management (Zustand)

### Creating a Store
```typescript
// src/stores/alerts.ts
import { create } from 'zustand'

interface Alert {
  id: string
  symbol: string
  targetPrice: number
  type: 'above' | 'below'
  active: boolean
}

interface AlertsState {
  alerts: Alert[]

  // Actions
  addAlert: (alert: Alert) => void
  removeAlert: (id: string) => void
  updateAlert: (id: string, alert: Partial<Alert>) => void
}

export const useAlertsStore = create<AlertsState>((set) => ({
  alerts: [],

  addAlert: (alert) => {
    set((state) => ({
      alerts: [...state.alerts, alert],
    }))
  },

  removeAlert: (id) => {
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    }))
  },

  updateAlert: (id, updates) => {
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, ...updates } : a
      ),
    }))
  },
}))
```

### Using in Components
```typescript
import { useAlertsStore } from '@stores/alerts'

export function AlertList() {
  const { alerts, removeAlert } = useAlertsStore()

  return (
    <div>
      {alerts.map((alert) => (
        <div key={alert.id}>
          <span>{alert.symbol} @ ${alert.targetPrice}</span>
          <button onClick={() => removeAlert(alert.id)}>Remove</button>
        </div>
      ))}
    </div>
  )
}
```

---

## 6. Custom Hooks

### Creating a Hook
```typescript
// src/hooks/useFormData.ts
import { useState, useCallback } from 'react'

interface UseFormDataReturn<T> {
  data: T
  setData: (newData: Partial<T>) => void
  reset: () => void
  isDirty: boolean
}

export function useFormData<T extends Record<string, any>>(
  initialData: T
): UseFormDataReturn<T> {
  const [data, setDataState] = useState(initialData)
  const [isDirty, setIsDirty] = useState(false)

  const setData = useCallback((newData: Partial<T>) => {
    setDataState((prev) => ({ ...prev, ...newData }))
    setIsDirty(true)
  }, [])

  const reset = useCallback(() => {
    setDataState(initialData)
    setIsDirty(false)
  }, [initialData])

  return { data, setData, reset, isDirty }
}
```

### Using in Components
```typescript
function MyForm() {
  const { data, setData, reset, isDirty } = useFormData({
    name: '',
    email: '',
  })

  return (
    <form>
      <input
        value={data.name}
        onChange={(e) => setData({ name: e.target.value })}
      />
      <button disabled={!isDirty}>Save</button>
      <button type="button" onClick={reset}>Reset</button>
    </form>
  )
}
```

---

## 7. API Integration

### Making API Calls
```typescript
import { apiClient } from '@services/api'

// In a component
async function loadQuotes() {
  try {
    const data = await apiClient.get('/quotes/AAPL')
    console.log(data)
  } catch (error) {
    console.error('Failed to load quote:', error)
  }
}

// In a hook
export function useQuote(symbol: string) {
  const [quote, setQuote] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient
      .get(`/quotes/${symbol}`)
      .then(setQuote)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [symbol])

  return { quote, error, loading }
}
```

### Mock Data (During Development)
```typescript
import { generateMockQuote, generateMockPortfolioData } from '@services/mockData'

// Use mock data while backend is in development
const mockQuote = generateMockQuote('AAPL')
const mockPortfolio = generateMockPortfolioData()
```

---

## 8. Formatting & Validation

### Using Utilities
```typescript
import {
  formatPrice,
  formatPercent,
  formatVolume,
  formatCurrency,
} from '@utils/formatting'

import {
  isValidEmail,
  isValidSymbol,
  isValidQuantity,
} from '@utils/validation'

// Formatting
const price = formatPrice(150.25)       // "150.25"
const percent = formatPercent(2.5)      // "+2.50%"
const volume = formatVolume(50000000)   // "50.0M"
const currency = formatCurrency(1000)   // "$1,000.00"

// Validation
const emailValid = isValidEmail('user@example.com')        // true
const symbolValid = isValidSymbol('AAPL')                  // true
const quantityValid = isValidQuantity(10)                  // true
```

---

## 9. Styling with TailwindCSS

### Common Classes
```tsx
// Spacing (4px grid)
className="p-4 m-2 gap-6"

// Colors
className="text-accent-600 bg-neutral-100 border-red-500"

// Dark mode
className="bg-white dark:bg-neutral-800 text-black dark:text-white"

// Responsive
className="w-full md:w-1/2 lg:w-1/3"

// Flexbox
className="flex items-center justify-between gap-4"

// Typography
className="text-lg font-bold text-neutral-900"
```

### Creating Reusable Classes
```tsx
const buttonClasses = 'px-4 py-2 rounded-lg font-medium transition-colors'
const primaryButton = `${buttonClasses} bg-accent-600 hover:bg-accent-700`
const secondaryButton = `${buttonClasses} bg-neutral-200 hover:bg-neutral-300`

// Or use within component
export const Button = ({ variant, children }) => (
  <button
    className={variant === 'primary' ? primaryButton : secondaryButton}
  >
    {children}
  </button>
)
```

---

## 10. Debugging

### Debug Logging
```typescript
// Enable debug mode in localStorage
localStorage.setItem('DEBUG', 'app:*')

// Use in code
if (localStorage.getItem('DEBUG')) {
  console.log('Store state:', useMarketStore.getState())
}
```

### React DevTools
```bash
# Install React DevTools browser extension
# Then inspect components and props in browser
```

### Zustand DevTools
```typescript
import { devtools } from 'zustand/middleware'

export const useMarketStore = create<MarketState>(
  devtools((set) => ({
    // ... store definition
  }), { name: 'MarketStore' })
)
```

---

## 11. Performance Tips

### Memoization
```typescript
// Memoize expensive components
export const ExpensiveChart = React.memo(
  ({ data }) => <Chart data={data} />,
  (prevProps, nextProps) => {
    return prevProps.data === nextProps.data
  }
)

// Memoize calculated values
const totalValue = useMemo(() => {
  return positions.reduce((sum, p) => sum + p.value, 0)
}, [positions])

// Memoize callbacks
const handleClick = useCallback(() => {
  doSomething()
}, [dependency])
```

### Image Optimization
```tsx
// Lazy load images
<img src="large.jpg" loading="lazy" alt="Description" />

// Use SVG for icons (from lucide-react)
import { Search, Settings } from 'lucide-react'
```

---

## 12. Common Patterns

### Loading States with Skeleton
```tsx
{isLoading ? (
  <div className="animate-pulse">
    <div className="h-12 bg-neutral-200 rounded" />
    <div className="h-4 bg-neutral-200 rounded mt-4" />
  </div>
) : (
  <Card>{content}</Card>
)}
```

### Error Handling
```tsx
{error ? (
  <div className="p-4 bg-danger/10 text-danger rounded">
    <p>{error.message}</p>
    <button onClick={retry}>Try again</button>
  </div>
) : (
  <Content />
)}
```

### Conditional Rendering
```tsx
{user ? (
  <Dashboard />
) : (
  <LoginPage />
)}
```

### Lists with Keys
```tsx
{items.map((item) => (
  <Item key={item.id} {...item} />
))}
```

---

## 13. Git Workflow

### Feature Development
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
```

### Commit Message Format
```
feat:  add new feature
fix:   fix bug
refactor: refactor code
test:  add tests
docs:  update documentation
style: fix formatting
chore: update dependencies
```

---

## 14. Useful Resources

### Documentation
- `FRONTEND_IMPLEMENTATION_GUIDE.md` - Complete architecture guide
- `TESTING_GUIDE.md` - Testing best practices
- `BACKEND_API_INTEGRATION_GUIDE.md` - API reference

### External Resources
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Vite Docs](https://vitejs.dev)

---

## 15. Troubleshooting

### Build Issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Type errors
npm run type-check

# Linting errors
npm run lint
```

### Dev Server Issues
```bash
# Kill port 3000
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Start again
npm run dev
```

### Test Failures
```bash
# Run specific test
npm test Button.test.tsx

# Watch mode
npm test -- --watch

# Clear cache
npm test -- --clearCache
```

---

## 16. IDE Setup

### Recommended Extensions (VS Code)
- **ES7+ React/Redux/React-Native snippets**
- **Prettier - Code formatter**
- **ESLint**
- **Tailwind CSS IntelliSense**
- **TypeScript Vue Plugin (Volar)**

### VS Code Settings
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

## 17. Component Checklist

Before committing a component:

- [ ] Component is exported in index.ts
- [ ] Props interface is defined
- [ ] Accessibility features added (roles, labels, keyboard nav)
- [ ] Dark mode styling applied
- [ ] Responsive design tested
- [ ] Loading and error states handled
- [ ] Unit tests written (80%+ coverage)
- [ ] TypeScript has no `any` types
- [ ] No console warnings in development
- [ ] Styling uses TailwindCSS classes

---

## 18. Release Checklist

Before deploying to production:

- [ ] All tests passing: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] No ESLint warnings: `npm run lint`
- [ ] Coverage is 80%+: `npm run coverage`
- [ ] No console errors in build
- [ ] Performance metrics acceptable
- [ ] Accessibility audit passed
- [ ] Browser compatibility tested
- [ ] Documentation updated

---

## Quick Command Reference

```bash
# Development
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build

# Testing
npm test                   # Run all tests
npm test -- --watch       # Watch mode
npm run test:ui           # Visual test UI
npm run coverage          # Coverage report

# Quality
npm run type-check        # TypeScript check
npm run lint              # ESLint check

# Utilities
npm install               # Install dependencies
npm run clean             # Clear build artifacts
npm run format            # Format code (if configured)
```

---

**Need Help?**
- Check the full documentation in `FRONTEND_IMPLEMENTATION_GUIDE.md`
- Review existing components for patterns
- Check test files for usage examples
- Ask team members or create an issue

Good luck with development!
