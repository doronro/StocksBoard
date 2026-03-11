# UI/UX Patterns Reference Guide
## Stock Exchange Board Application

**For**: Frontend Developers
**Version**: 1.0
**Date**: March 11, 2026

This document provides detailed UI/UX pattern specifications and implementation examples for financial trading applications.

---

## Table of Contents

1. Card & Container Patterns
2. Data Display Patterns
3. Real-Time Update Indicators
4. Alert & Notification Patterns
5. Form & Input Patterns
6. Interactive Control Patterns
7. Chart & Graph Patterns
8. Navigation Patterns
9. Loading & Error States
10. Responsive Design Patterns

---

## 1. Card & Container Patterns

### 1.1 Quote Card Pattern

**Purpose**: Display a single stock quote with key metrics
**Usage**: Watchlist items, quote lookups, market overview

**Structure**:
```
┌─────────────────────────────────────┐
│ [Icon] AAPL - Apple Inc.      [Pin] │ ← Header (clickable)
├─────────────────────────────────────┤
│ Price:    $150.25                   │
│ Change:   +2.50 (+1.70%) ▲          │ ← Color: Green
│ Bid/Ask:  150.20 / 150.30           │
├─────────────────────────────────────┤
│ Volume:   50.2M (avg: 45.0M)        │
│ 52W Range: $140.00 - $180.00        │
│ Mkt Cap:  $2.50T                    │
├─────────────────────────────────────┤
│ [Buy] [Sell] [Add to Watchlist]     │ ← Action buttons
└─────────────────────────────────────┘
```

**CSS Classes** (Tailwind):
```tsx
<div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4 hover:shadow-md transition-shadow">
  {/* Header */}
  <div className="flex justify-between items-start mb-4">
    <div className="flex items-center gap-2">
      <span className="font-semibold text-neutral-900 dark:text-neutral-100">
        {quote.symbol}
      </span>
      <span className="text-sm text-neutral-600 dark:text-neutral-400">
        {quote.name}
      </span>
    </div>
    <button className="text-neutral-400 hover:text-neutral-600">
      <Star className="w-4 h-4" />
    </button>
  </div>

  {/* Price Section */}
  <div className="space-y-2 mb-4">
    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
      ${quote.price.toFixed(2)}
    </p>
    <p className={classNames(
      'text-sm font-medium',
      quote.change >= 0 ? 'text-green-600' : 'text-red-600'
    )}>
      {quote.change > 0 ? '+' : ''}{quote.change.toFixed(2)}
      ({quote.changePercent.toFixed(2)}%)
      {quote.change >= 0 ? <TrendingUp className="inline w-4 h-4 ml-1" /> : <TrendingDown className="inline w-4 h-4 ml-1" />}
    </p>
  </div>

  {/* Actions */}
  <div className="flex gap-2">
    <button className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium">
      Buy
    </button>
    <button className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-medium">
      Sell
    </button>
  </div>
</div>
```

### 1.2 Metric Card Pattern

**Purpose**: Display a single metric with context
**Usage**: Portfolio value, daily P&L, risk metrics

**Structure**:
```
┌──────────────────────────────┐
│ Portfolio Value              │ ← Label (muted)
├──────────────────────────────┤
│ $250,000.00                  │ ← Value (bold)
│ +$5,000.00 (+2.04%) ▲ (Green)│ ← Change with context
└──────────────────────────────┘
```

**Implementation**:
```tsx
interface MetricCardProps {
  label: string
  value: string | number
  change?: number
  changePercent?: number
  format?: 'currency' | 'percent' | 'number'
  unit?: string
  subtext?: string
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  changePercent,
  format = 'number'
}) => (
  <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
      {label}
    </p>
    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
      {value}
    </p>
    {change !== undefined && (
      <p className={classNames(
        'text-sm font-medium flex items-center gap-1',
        change >= 0 ? 'text-green-600' : 'text-red-600'
      )}>
        {change > 0 ? '+' : ''}{change.toFixed(2)}
        ({changePercent?.toFixed(2)}%)
        {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
      </p>
    )}
  </div>
)
```

### 1.3 Section Card Pattern

**Purpose**: Group related metrics and controls
**Usage**: Technical indicators, position details, risk metrics

**Structure**:
```
┌─────────────────────────────────────┐
│ Section Title            [Controls] │ ← Header with optional actions
├─────────────────────────────────────┤
│                                     │
│  Content area (flexible layout)     │
│                                     │
└─────────────────────────────────────┘
```

**Implementation**:
```tsx
interface CardProps {
  title: string
  subtitle?: string
  actions?: React.ReactNode
  children: React.ReactNode
  variant?: 'default' | 'compact'
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  actions,
  children,
  variant = 'default'
}) => (
  <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
    <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700 flex justify-between items-start">
      <div>
        <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
          {title}
        </h3>
        {subtitle && (
          <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </div>
    <div className={variant === 'compact' ? 'p-3' : 'p-4'}>
      {children}
    </div>
  </div>
)
```

---

## 2. Data Display Patterns

### 2.1 Metric Row Pattern

**Purpose**: Display label-value pair
**Usage**: Quote data, metrics, properties

**Structure**:
```
Label                Value
Label                Value with change indicator
Label                Value (muted secondary)
```

**Implementation**:
```tsx
interface MetricRowProps {
  label: string
  value: string | number
  secondary?: string
  change?: number
  changePercent?: number
  highlighted?: boolean
}

export const MetricRow: React.FC<MetricRowProps> = ({
  label,
  value,
  secondary,
  change,
  changePercent,
  highlighted = false
}) => (
  <div className={classNames(
    'flex justify-between items-center py-2',
    highlighted && 'bg-neutral-50 dark:bg-neutral-700/30 px-2 rounded'
  )}>
    <span className="text-sm text-neutral-600 dark:text-neutral-400">
      {label}
    </span>
    <div className="flex items-center gap-2">
      <span className="font-semibold text-neutral-900 dark:text-neutral-100">
        {value}
      </span>
      {secondary && (
        <span className="text-xs text-neutral-500 dark:text-neutral-500">
          {secondary}
        </span>
      )}
      {change !== undefined && (
        <span className={classNames(
          'text-xs font-medium',
          change >= 0 ? 'text-green-600' : 'text-red-600'
        )}>
          {change > 0 ? '+' : ''}{change.toFixed(2)}%
        </span>
      )}
    </div>
  </div>
)
```

**Usage**:
```tsx
<MetricRow label="Price" value="$150.25" change={1.70} />
<MetricRow label="Bid / Ask" value="150.20 / 150.30" />
<MetricRow label="Volume" value="50.2M" secondary="avg: 45.0M" />
```

### 2.2 Data Table Pattern

**Purpose**: Display multiple rows of data
**Usage**: Holdings list, order history, watchlist

**Structure**:
```
Symbol  Name          Price    Change    Volume
────────────────────────────────────────────────
AAPL    Apple Inc.    $150.25  +1.70%    50.2M
GOOGL   Alphabet Inc. $140.50  -0.88%    35.5M
MSFT    Microsoft     $380.25  +2.15%    28.3M
```

**Implementation**:
```tsx
interface DataTableProps {
  columns: ColumnDef<any>[]
  data: any[]
  onRowClick?: (row: any) => void
  variant?: 'compact' | 'comfortable'
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  onRowClick,
  variant = 'comfortable'
}) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-neutral-200 dark:border-neutral-700">
          {columns.map((col) => (
            <th
              key={col.key}
              className="text-left px-4 py-3 font-semibold text-neutral-700 dark:text-neutral-300"
            >
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr
            key={idx}
            onClick={() => onRowClick?.(row)}
            className={classNames(
              'border-b border-neutral-100 dark:border-neutral-700',
              variant === 'comfortable' && 'hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors',
              onRowClick && 'cursor-pointer'
            )}
          >
            {columns.map((col) => (
              <td
                key={col.key}
                className={classNames(
                  variant === 'comfortable' ? 'px-4 py-3' : 'px-3 py-2',
                  'text-neutral-900 dark:text-neutral-100'
                )}
              >
                {col.render ? col.render(row) : row[col.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)
```

---

## 3. Real-Time Update Indicators

### 3.1 Flash Animation Pattern

**Purpose**: Draw attention to changed values
**Usage**: Price updates, volume spikes, alert triggers

**Implementation**:
```tsx
interface FlashableValueProps {
  value: string | number
  previousValue?: string | number
  format?: 'currency' | 'percent' | 'number'
}

export const FlashableValue: React.FC<FlashableValueProps> = ({
  value,
  previousValue,
  format = 'number'
}) => {
  const [isFlashing, setIsFlashing] = useState(false)

  useEffect(() => {
    if (previousValue !== undefined && value !== previousValue) {
      setIsFlashing(true)
      const timer = setTimeout(() => setIsFlashing(false), 1000)
      return () => clearTimeout(timer)
    }
  }, [value, previousValue])

  const hasChanged = previousValue !== undefined && value !== previousValue
  const isUp = hasChanged && Number(value) > Number(previousValue)

  return (
    <span
      className={classNames(
        'transition-colors duration-300',
        isFlashing && (isUp ? 'bg-green-200 dark:bg-green-900/30' : 'bg-red-200 dark:bg-red-900/30'),
        'px-1 rounded'
      )}
    >
      {formatValue(value, format)}
    </span>
  )
}
```

**CSS Animation**:
```css
@keyframes flash {
  0% { background-color: rgb(220, 38, 38); }
  100% { background-color: transparent; }
}

.flash-red {
  animation: flash 1s ease-out;
}

.flash-green {
  animation: flash 1s ease-out;
  --color-start: rgb(34, 197, 94);
}
```

### 3.2 Update Indicator Pattern

**Purpose**: Show timestamp of last update
**Usage**: Quote freshness, data age indicator

**Structure**:
```
Last Update: 10:30:45 (2s ago)  [Icon]
```

**Implementation**:
```tsx
export const UpdateIndicator: React.FC<{
  timestamp: number
  isLive?: boolean
}> = ({ timestamp, isLive = false }) => {
  const [relativeTime, setRelativeTime] = useState('')

  useEffect(() => {
    const update = () => {
      const now = Date.now()
      const diff = Math.round((now - timestamp) / 1000)
      if (diff < 60) {
        setRelativeTime(`${diff}s ago`)
      } else if (diff < 3600) {
        setRelativeTime(`${Math.round(diff / 60)}m ago`)
      } else {
        setRelativeTime(new Date(timestamp).toLocaleTimeString())
      }
    }

    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [timestamp])

  return (
    <div className="flex items-center gap-1 text-xs text-neutral-500 dark:text-neutral-400">
      {isLive && <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />}
      <span>{relativeTime}</span>
    </div>
  )
}
```

---

## 4. Alert & Notification Patterns

### 4.1 Toast Notification Pattern

**Purpose**: Inform user of actions without disruption
**Usage**: Order confirmations, error messages, system alerts

**Structure**:
```
┌─ [Icon] Message Text [X] ─┐
└──────────────────────────┘
```

**Implementation**:
```tsx
interface ToastProps {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
  onClose: (id: string) => void
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  duration = 5000,
  onClose
}) => {
  useEffect(() => {
    const timer = setTimeout(() => onClose(id), duration)
    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const bgColor = {
    success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800',
    error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800',
    warning: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800',
    info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800'
  }

  const textColor = {
    success: 'text-green-800 dark:text-green-200',
    error: 'text-red-800 dark:text-red-200',
    warning: 'text-yellow-800 dark:text-yellow-200',
    info: 'text-blue-800 dark:text-blue-200'
  }

  const iconColor = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600'
  }

  return (
    <div className={classNames(
      'border rounded-lg p-4 flex items-start gap-3',
      bgColor[type]
    )}>
      <div className={classNames('mt-0.5', iconColor[type])}>
        {type === 'success' && <CheckCircle className="w-5 h-5" />}
        {type === 'error' && <AlertCircle className="w-5 h-5" />}
        {type === 'warning' && <AlertTriangle className="w-5 h-5" />}
        {type === 'info' && <Info className="w-5 h-5" />}
      </div>
      <div className="flex-1">
        <p className={classNames('text-sm font-medium', textColor[type])}>
          {message}
        </p>
      </div>
      <button
        onClick={() => onClose(id)}
        className={classNames('text-neutral-400 hover:text-neutral-600 transition-colors', textColor[type])}
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
```

### 4.2 Inline Alert Pattern

**Purpose**: Provide contextual warnings or information
**Usage**: Form validation, trading warnings, compliance notices

**Structure**:
```
┌─ [Icon] Alert Title
│ Alert description with additional context
└─ [Optional Action Link]
```

**Implementation**:
```tsx
interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
}

export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  description,
  action
}) => (
  <div className={classNames(
    'border border-l-4 rounded p-4',
    type === 'success' && 'border-l-green-500 border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/30',
    type === 'error' && 'border-l-red-500 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/30',
    type === 'warning' && 'border-l-yellow-500 border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/30',
    type === 'info' && 'border-l-blue-500 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/30'
  )}>
    <div className="flex items-start gap-3">
      <div className={
        type === 'success' ? 'text-green-600' :
        type === 'error' ? 'text-red-600' :
        type === 'warning' ? 'text-yellow-600' :
        'text-blue-600'
      }>
        {type === 'success' && <CheckCircle className="w-5 h-5 mt-0.5" />}
        {type === 'error' && <AlertCircle className="w-5 h-5 mt-0.5" />}
        {type === 'warning' && <AlertTriangle className="w-5 h-5 mt-0.5" />}
        {type === 'info' && <Info className="w-5 h-5 mt-0.5" />}
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">
          {title}
        </h4>
        {description && (
          <p className="text-sm text-neutral-700 dark:text-neutral-300 mb-3">
            {description}
          </p>
        )}
        {action && (
          <button
            onClick={action.onClick}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            {action.label} →
          </button>
        )}
      </div>
    </div>
  </div>
)
```

---

## 5. Form & Input Patterns

### 5.1 Text Input Pattern

**Purpose**: Capture user text input
**Usage**: Symbol search, amounts, notes

**Structure**:
```
Label                          [Required]
[========== Input Field ========== ]
(Helper text or error message)
```

**Implementation**:
```tsx
interface TextInputProps {
  label: string
  value: string
  onChange: (value: string) => void
  error?: string
  helper?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  icon?: React.ReactNode
}

export const TextInput: React.FC<TextInputProps> = ({
  label,
  value,
  onChange,
  error,
  helper,
  placeholder,
  required,
  disabled,
  icon
}) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-neutral-900 dark:text-neutral-100">
      {label}
      {required && <span className="text-red-600 ml-1">*</span>}
    </label>
    <div className="relative">
      {icon && (
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
          {icon}
        </div>
      )}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={classNames(
          'w-full px-4 py-2 rounded-lg border bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 transition-colors',
          error
            ? 'border-red-500 focus:ring-red-500'
            : 'border-neutral-300 dark:border-neutral-600 focus:ring-blue-500',
          'focus:outline-none focus:ring-2',
          disabled && 'opacity-50 cursor-not-allowed',
          icon && 'pl-10'
        )}
      />
    </div>
    {error && <p className="text-xs text-red-600">{error}</p>}
    {helper && <p className="text-xs text-neutral-500">{helper}</p>}
  </div>
)
```

### 5.2 Number Input Pattern

**Purpose**: Capture numeric values (prices, quantities)
**Usage**: Order amounts, prices, percentages

**Implementation**:
```tsx
interface NumberInputProps {
  label: string
  value: number | ''
  onChange: (value: number | '') => void
  min?: number
  max?: number
  step?: number
  error?: string
  suffix?: string
}

export const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  min = 0,
  max,
  step = 1,
  error,
  suffix
}) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-neutral-900 dark:text-neutral-100">
      {label}
    </label>
    <div className="relative">
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value === '' ? '' : parseFloat(e.target.value))}
        min={min}
        max={max}
        step={step}
        className={classNames(
          'w-full px-4 py-2 rounded-lg border bg-white dark:bg-neutral-800',
          error ? 'border-red-500' : 'border-neutral-300 dark:border-neutral-600',
          'focus:outline-none focus:ring-2 focus:ring-blue-500',
          suffix && 'pr-10'
        )}
      />
      {suffix && (
        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-neutral-500">
          {suffix}
        </span>
      )}
    </div>
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
)
```

---

## 6. Interactive Control Patterns

### 6.1 Button Pattern

**Purpose**: Trigger actions
**Usage**: Form submission, navigation, trading actions

**Variants**:
```
[Primary] - Main action (blue)
[Secondary] - Alternative action (gray)
[Danger] - Destructive action (red)
[Success] - Positive action (green)
[Outline] - Low emphasis (bordered)
[Disabled] - Unavailable (gray, no pointer)
```

**Implementation**:
```tsx
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  disabled?: boolean
  loading?: boolean
  icon?: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  loading = false,
  icon
}) => {
  const baseStyles = 'font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'

  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-neutral-200 dark:bg-neutral-700 hover:bg-neutral-300 dark:hover:bg-neutral-600 text-neutral-900 dark:text-neutral-100',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
    outline: 'border-2 border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
  }

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={classNames(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        fullWidth && 'w-full',
        (disabled || loading) && 'opacity-50 cursor-not-allowed',
        'flex items-center justify-center gap-2'
      )}
    >
      {loading && <Spinner className="w-4 h-4" />}
      {icon && <span>{icon}</span>}
      {children}
    </button>
  )
}
```

### 6.2 Toggle Switch Pattern

**Purpose**: Binary on/off control
**Usage**: Alert enable/disable, feature toggles

**Implementation**:
```tsx
interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  disabled
}) => (
  <label className="flex items-center gap-3 cursor-pointer">
    <div className="relative inline-flex items-center w-11 h-6">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="sr-only"
      />
      <div className={classNames(
        'block w-full h-full rounded-full transition-colors',
        checked ? 'bg-blue-600' : 'bg-neutral-300 dark:bg-neutral-600',
        disabled && 'opacity-50 cursor-not-allowed'
      )} />
      <span className={classNames(
        'absolute w-5 h-5 bg-white rounded-full shadow transition-transform',
        checked ? 'translate-x-5' : 'translate-x-0'
      )} />
    </div>
    {label && (
      <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
        {label}
      </span>
    )}
  </label>
)
```

---

## 7. Chart & Graph Patterns

### 7.1 Candlestick Chart Pattern

**Purpose**: Display OHLC price data
**Usage**: Technical analysis, price trends

**Key Elements**:
- Green candles: Close > Open (bullish)
- Red candles: Close < Open (bearish)
- Wicks: High/Low range
- Volume bars: Underneath
- Moving averages: Overlaid

**Implementation Libraries**:
- Recharts (current - lightweight)
- TradingView Lightweight Charts (Phase 2 - professional)

### 7.2 Indicator Panel Pattern

**Purpose**: Display technical indicator values
**Usage**: MACD, RSI, Bollinger Bands, etc.

**Structure**:
```
┌─ Indicator Name [━━━━] Value ─┐
├─────────────────────────────────┤
│ Signal: Bullish/Bearish/Neutral │
│ Line 1: ██████░░░░ 65%          │
│ Line 2: ████░░░░░░ 40%          │
│ Status: Overbought/Normal       │
└─────────────────────────────────┘
```

---

## 8. Navigation Patterns

### 8.1 Tab Navigation Pattern

**Purpose**: Switch between views/timeframes
**Usage**: Timeframe selection, view modes

**Implementation**:
```tsx
interface TabsProps {
  tabs: Array<{ id: string; label: string }>
  activeTab: string
  onChange: (tabId: string) => void
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange
}) => (
  <div className="flex gap-2 border-b border-neutral-200 dark:border-neutral-700">
    {tabs.map((tab) => (
      <button
        key={tab.id}
        onClick={() => onChange(tab.id)}
        className={classNames(
          'px-4 py-3 font-medium text-sm transition-colors relative',
          activeTab === tab.id
            ? 'text-blue-600 dark:text-blue-400'
            : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200',
          activeTab === tab.id && 'after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600 dark:after:bg-blue-400'
        )}
      >
        {tab.label}
      </button>
    ))}
  </div>
)
```

---

## 9. Loading & Error States

### 9.1 Skeleton Loading Pattern

**Purpose**: Show loading state with visual placeholder
**Usage**: Data loading, chart preparation

**Implementation**:
```tsx
export const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={classNames(
    'bg-neutral-200 dark:bg-neutral-700 rounded animate-pulse',
    className
  )} />
)

export const QuoteSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-40" />
    <Skeleton className="h-10 w-32" />
    <div className="space-y-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-full" />
    </div>
  </div>
)
```

### 9.2 Empty State Pattern

**Purpose**: Handle no data scenario
**Usage**: Empty watchlist, no positions

**Implementation**:
```tsx
interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: { label: string; onClick: () => void }
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action
}) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="text-neutral-400 mb-4">
      {icon}
    </div>
    <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
      {title}
    </h3>
    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-6 max-w-sm">
      {description}
    </p>
    {action && (
      <Button onClick={action.onClick}>
        {action.label}
      </Button>
    )}
  </div>
)
```

---

## 10. Responsive Design Patterns

### 10.1 Responsive Grid Pattern

**Purpose**: Adapt layout to screen size
**Usage**: Dashboard, cards, metrics

**Implementation**:
```tsx
export const ResponsiveGrid: React.FC<{
  children: React.ReactNode
  columns?: { mobile: number; tablet: number; desktop: number }
}> = ({ children, columns = { mobile: 1, tablet: 2, desktop: 3 } }) => (
  <div className={classNames(
    'grid gap-4',
    `grid-cols-${columns.mobile}`,
    `md:grid-cols-${columns.tablet}`,
    `lg:grid-cols-${columns.desktop}`
  )}>
    {children}
  </div>
)
```

---

## Accessibility Guidelines

### 10.1 Focus Management
- Visible focus indicators (ring-2)
- Logical tab order
- Skip navigation links

### 10.2 Semantic HTML
- Use proper heading hierarchy
- Button/link distinction
- Form labels and associations

### 10.3 ARIA Support
- aria-label for icon buttons
- aria-describedby for help text
- aria-live for updates
- role attributes where needed

---

## Dark Mode Support

All patterns include dark mode support via `dark:` Tailwind classes.

Example:
```tsx
className={classNames(
  'bg-white dark:bg-neutral-800',
  'text-neutral-900 dark:text-neutral-100',
  'border-neutral-200 dark:border-neutral-700'
)}
```

---

## Performance Considerations

1. Memoize frequently re-rendered components
2. Virtualize long lists (100+ items)
3. Debounce search and filter inputs
4. Lazy load charts and heavy components
5. Use CSS animations instead of JS where possible

---

## Testing Patterns

All components should include:
- Unit tests for logic
- Integration tests for interactions
- Accessibility tests (screen reader, keyboard)
- Visual regression tests (design changes)

---

## Summary

These UI/UX patterns provide a consistent, professional interface for financial trading applications. Follow these patterns to ensure:
- Consistency across the platform
- Accessibility for all users
- Professional appearance
- Rapid development
- Easy maintenance

**Last Updated**: March 11, 2026
