/**
 * Mock data service for development and testing
 * Provides realistic stock data, charts, and market information
 */

import type { Quote, ChartDataPoint, TechnicalIndicator, MarketIndex, SectorPerformance, PriceAlert, Order } from '@types'

// List of popular stocks for mock data
const MOCK_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BAC', 'GS']

/**
 * Generate mock quote data for a stock
 */
export function generateMockQuote(symbol: string): Quote {
  const basePrice = Math.random() * 300 + 50
  const change = (Math.random() - 0.5) * 10
  const changePercent = (change / basePrice) * 100

  return {
    symbol,
    name: `${symbol} Inc.`,
    price: basePrice,
    change,
    changePercent,
    bid: basePrice - 0.05,
    ask: basePrice + 0.05,
    volume: Math.floor(Math.random() * 50000000) + 1000000,
    avgVolume: Math.floor(Math.random() * 40000000) + 2000000,
    marketCap: Math.random() * 3000 + 100,
    pe: Math.random() * 30 + 10,
    eps: Math.random() * 5 + 0.5,
    high52w: basePrice * (1 + Math.random() * 0.3),
    low52w: basePrice * (1 - Math.random() * 0.3),
    timestamp: Date.now(),
    trend: change >= 0 ? 'up' : 'down',
  }
}

/**
 * Generate mock candlestick data for a chart
 */
export function generateMockChartData(timeframe: string, count: number = 50): ChartDataPoint[] {
  const data: ChartDataPoint[] = []
  let basePrice = 100 + Math.random() * 200
  const now = Date.now()

  // Determine interval based on timeframe
  const intervalMs = getTimeframeInterval(timeframe)

  for (let i = count - 1; i >= 0; i--) {
    const timestamp = now - i * intervalMs

    // Random walk for realistic price movement
    const trend = Math.random() - 0.45 // Slight upward bias
    basePrice = basePrice * (1 + trend * 0.02)

    const open = basePrice
    const close = basePrice * (1 + (Math.random() - 0.5) * 0.01)
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)
    const volume = Math.floor(Math.random() * 5000000) + 500000

    data.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume,
    })
  }

  return data
}

/**
 * Generate mock technical indicators
 */
export function generateMockTechnicalIndicators(): TechnicalIndicator {
  const rsi = Math.random() * 100
  const macdLine = Math.random() * 10 - 5
  const macdSignal = Math.random() * 10 - 5

  // Generate moving averages
  const sma20: number[] = []
  const sma50: number[] = []
  const sma200: number[] = []

  let base = 100
  for (let i = 0; i < 200; i++) {
    base = base * (1 + (Math.random() - 0.5) * 0.01)
    sma200.push(base)

    if (i >= 50) {
      sma50.push(base * (1 + (Math.random() - 0.5) * 0.005))
    }
    if (i >= 180) {
      sma20.push(base * (1 + (Math.random() - 0.5) * 0.003))
    }
  }

  // EMA values
  const ema12: number[] = sma20.map(v => v * (1 + (Math.random() - 0.5) * 0.01))
  const ema26: number[] = sma50.map(v => v * (1 + (Math.random() - 0.5) * 0.01))

  return {
    sma20: sma20.slice(-20),
    sma50: sma50.slice(-50),
    sma200: sma200.slice(-200),
    ema12: ema12.slice(-20),
    ema26: ema26.slice(-50),
    rsi,
    macd: {
      line: macdLine,
      signal: macdSignal,
      histogram: macdLine - macdSignal,
    },
  }
}

/**
 * Generate mock market indices
 */
export function generateMockIndices(): MarketIndex[] {
  return [
    {
      symbol: '^GSPC',
      name: 'S&P 500',
      value: 4500 + Math.random() * 200,
      change: (Math.random() - 0.5) * 50,
      changePercent: (Math.random() - 0.5) * 2,
      timestamp: Date.now(),
    },
    {
      symbol: '^IXIC',
      name: 'Nasdaq',
      value: 14000 + Math.random() * 500,
      change: (Math.random() - 0.5) * 100,
      changePercent: (Math.random() - 0.5) * 2.5,
      timestamp: Date.now(),
    },
    {
      symbol: '^DJI',
      name: 'Dow Jones',
      value: 35000 + Math.random() * 500,
      change: (Math.random() - 0.5) * 100,
      changePercent: (Math.random() - 0.5) * 1.5,
      timestamp: Date.now(),
    },
  ]
}

/**
 * Generate mock sector performance data
 */
export function generateMockSectorPerformance(): SectorPerformance[] {
  const sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrials', 'Materials', 'Utilities']
  return sectors.map(sector => ({
    name: sector,
    change: (Math.random() - 0.5) * 100,
    changePercent: (Math.random() - 0.5) * 3,
  }))
}

/**
 * Generate mock news/earnings events
 */
export function generateMockEvents(): Array<{
  date: Date
  symbol: string
  type: 'earnings' | 'news'
  title: string
  description: string
}> {
  const today = new Date()
  const events: Array<{
    date: Date
    symbol: string
    type: 'earnings' | 'news'
    title: string
    description: string
  }> = []

  MOCK_SYMBOLS.forEach((symbol) => {
    // Earnings events
    for (let i = 0; i < 4; i++) {
      const daysFromNow = Math.floor(Math.random() * 90) + 1
      const eventDate = new Date(today)
      eventDate.setDate(eventDate.getDate() + daysFromNow)

      events.push({
        date: eventDate,
        symbol,
        type: 'earnings',
        title: `${symbol} Q${Math.floor(Math.random() * 4) + 1} Earnings`,
        description: `${symbol} will report quarterly earnings. Expected EPS: $${(Math.random() * 5 + 0.5).toFixed(2)}`,
      })
    }

    // News events
    for (let i = 0; i < 3; i++) {
      const daysFromNow = Math.floor(Math.random() * 30)
      const eventDate = new Date(today)
      eventDate.setDate(eventDate.getDate() + daysFromNow)

      events.push({
        date: eventDate,
        symbol,
        type: 'news',
        title: `${symbol} News Update`,
        description: `Latest news and developments for ${symbol}. Market analysts remain ${Math.random() > 0.5 ? 'bullish' : 'bearish'}.`,
      })
    }
  })

  return events.sort((a, b) => a.date.getTime() - b.date.getTime())
}

/**
 * Convert timeframe string to milliseconds
 */
function getTimeframeInterval(timeframe: string): number {
  const intervals: Record<string, number> = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '30m': 30 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
    '1w': 7 * 24 * 60 * 60 * 1000,
  }
  return intervals[timeframe] || 60 * 60 * 1000 // Default to 1 hour
}

/**
 * Get list of symbols for seeding data
 */
export function getSymbols(): string[] {
  return MOCK_SYMBOLS
}

/**
 * Generate mock portfolio holdings
 */
export function generateMockPortfolioData(): {
  holdings: Array<{
    symbol: string
    name: string
    quantity: number
    averagePrice: number
    currentPrice: number
  }>
  totalValue: number
  totalCost: number
} {
  const holdings = MOCK_SYMBOLS.slice(0, 5).map(symbol => {
    const quantity = Math.floor(Math.random() * 100) + 10
    const averagePrice = Math.random() * 200 + 50
    const currentPrice = averagePrice * (1 + (Math.random() - 0.5) * 0.1)

    return {
      symbol,
      name: `${symbol} Inc.`,
      quantity,
      averagePrice,
      currentPrice,
    }
  })

  const totalCost = holdings.reduce((sum, h) => sum + h.quantity * h.averagePrice, 0)
  const totalValue = holdings.reduce((sum, h) => sum + h.quantity * h.currentPrice, 0)

  return {
    holdings,
    totalValue,
    totalCost,
  }
}

/**
 * Generate mock price alerts
 */
export function generateMockAlerts(): PriceAlert[] {
  const alerts: PriceAlert[] = []

  MOCK_SYMBOLS.slice(0, 5).forEach(symbol => {
    for (let i = 0; i < 2; i++) {
      const basePrice = Math.random() * 300 + 50
      alerts.push({
        id: `alert-${symbol}-${i}`,
        userId: 'user-1',
        symbol,
        name: `${symbol} Inc.`,
        type: Math.random() > 0.5 ? 'above' : 'below',
        targetPrice: basePrice * (1 + (Math.random() - 0.5) * 0.2),
        isActive: Math.random() > 0.3,
        triggered: false,
        createdAt: Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000,
      })
    }
  })

  return alerts
}

/**
 * Generate mock orders
 */
export function generateMockOrders(): Order[] {
  const orders: Order[] = []
  const statuses: Array<'pending' | 'filled' | 'cancelled'> = ['filled', 'filled', 'filled', 'pending', 'cancelled']
  const sides: Array<'buy' | 'sell'> = ['buy', 'sell']
  const types: Array<'market' | 'limit'> = ['market', 'limit']

  for (let i = 0; i < 10; i++) {
    const symbol = MOCK_SYMBOLS[Math.floor(Math.random() * MOCK_SYMBOLS.length)]
    const quantity = Math.floor(Math.random() * 100) + 10
    const price = Math.random() * 300 + 50

    orders.push({
      id: `order-${i}`,
      symbol,
      side: sides[Math.floor(Math.random() * sides.length)],
      type: types[Math.floor(Math.random() * types.length)],
      quantity,
      filledQuantity: Math.floor(quantity * Math.random()),
      price: types[Math.floor(Math.random() * types.length)] === 'limit' ? price : undefined,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      createdAt: Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000,
      updatedAt: Date.now(),
    })
  }

  return orders
}
