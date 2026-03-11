export type TimeFrame = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w'
export type OrderType = 'market' | 'limit' | 'stop_loss' | 'trailing_stop'
export type OrderSide = 'buy' | 'sell'
export type OrderStatus = 'pending' | 'filled' | 'cancelled' | 'rejected' | 'partial'
export type MarketStatus = 'open' | 'closed' | 'pre_market' | 'after_hours'
export type Theme = 'light' | 'dark'
export type AlertType = 'price' | 'volume' | 'technical' | 'news'

export interface Quote {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  bid: number
  ask: number
  volume: number
  avgVolume: number
  marketCap?: number
  pe?: number
  eps?: number
  high52w?: number
  low52w?: number
  timestamp: number
  trend: 'up' | 'down' | 'neutral'
}

export interface ChartDataPoint {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface TechnicalIndicator {
  sma20?: number[]
  sma50?: number[]
  sma200?: number[]
  ema12?: number[]
  ema26?: number[]
  rsi?: number
  macd?: {
    line: number
    signal: number
    histogram: number
  }
}

export interface Portfolio {
  id: string
  userId: string
  name: string
  totalValue: number
  totalCost: number
  dayPnL: number
  dayPnLPercent: number
  unrealizedGain: number
  unrealizedGainPercent: number
  lastUpdated: number
  holdings: Holding[]
}

export interface Holding {
  id: string
  symbol: string
  name: string
  quantity: number
  averagePrice: number
  currentPrice: number
  totalCost: number
  currentValue: number
  pnl: number
  pnlPercent: number
  updatedAt: number
}

export interface Order {
  id: string
  symbol: string
  side: OrderSide
  type: OrderType
  quantity: number
  filledQuantity: number
  price?: number
  stopPrice?: number
  trailingPercent?: number
  status: OrderStatus
  createdAt: number
  updatedAt: number
  completedAt?: number
}

export interface Watchlist {
  id: string
  userId: string
  name: string
  symbols: string[]
  createdAt: number
  updatedAt: number
}

export interface MarketIndex {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
  timestamp: number
}

export interface SectorPerformance {
  name: string
  change: number
  changePercent: number
}

export interface PriceAlert {
  id: string
  userId: string
  symbol: string
  name: string
  type: 'above' | 'below'
  targetPrice: number
  isActive: boolean
  triggered: boolean
  createdAt: number
  triggeredAt?: number
}

export interface ScreenerCriteria {
  gapUp?: boolean
  gapDown?: boolean
  breakout?: boolean
  breakdown?: boolean
  smaGoldenCross?: boolean
  smaDeathCross?: boolean
  rsiOverbought?: boolean
  rsiOversold?: boolean
  volumeSpike?: number // percentage above average
  priceRange?: {
    min: number
    max: number
  }
}

export interface ScreenerResult {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  matchedCriteria: string[]
  timestamp: number
}

export interface User {
  id: string
  email: string
  name: string
  createdAt: number
  lastLogin: number
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: Theme
  currency: string
  dateFormat: string
  timeFormat: 'h12' | 'h24'
  language: string
  enableNotifications: boolean
  enableSound: boolean
}

export interface MarketBreadth {
  advancing: number
  declining: number
  unchanged: number
  vixLevel: number
  vixChange: number
  timestamp: number
}
