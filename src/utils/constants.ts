export const MARKET_INDICES = [
  { symbol: '^GSPC', name: 'S&P 500' },
  { symbol: '^IXIC', name: 'NASDAQ-100' },
  { symbol: '^RUT', name: 'Russell 2000' },
  { symbol: '^DJI', name: 'Dow Jones' },
]

export const SECTORS = [
  'Technology',
  'Healthcare',
  'Financials',
  'Industrials',
  'Consumer Discretionary',
  'Consumer Staples',
  'Energy',
  'Materials',
  'Utilities',
  'Real Estate',
  'Communication Services',
]

export const TIME_FRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'] as const

export const ORDER_TYPES = ['market', 'limit', 'stop_loss', 'trailing_stop'] as const

export const ORDER_SIDES = ['buy', 'sell'] as const

export const PRICE_PRECISION = 2
export const VOLUME_PRECISION = 0
export const PERCENT_PRECISION = 2

export const MARKET_HOURS = {
  PREMARKET_START: 4, // 4 AM ET
  MARKET_OPEN: 9.5, // 9:30 AM ET
  MARKET_CLOSE: 16, // 4 PM ET
  AFTER_HOURS_END: 20, // 8 PM ET
}

export const DEFAULT_WATCHLIST_SYMBOLS = [
  'AAPL',
  'MSFT',
  'GOOGL',
  'AMZN',
  'NVDA',
  'TSLA',
  'META',
  'NFLX',
]

export const KEYBOARD_SHORTCUTS = {
  SEARCH: 'cmd+k',
  NEW_ORDER: 'cmd+n',
  CLOSE_ORDER: 'escape',
  TOGGLE_THEME: 'cmd+shift+d',
}

export const NOTIFICATION_DURATION = 3000 // ms

export const CHART_CONFIG = {
  MIN_POINTS: 20,
  MAX_POINTS: 500,
  ANIMATION_DURATION: 300,
}

export const API_ENDPOINTS = {
  QUOTES: '/api/quotes',
  CHARTS: '/api/charts',
  PORTFOLIO: '/api/portfolio',
  ORDERS: '/api/orders',
  WATCHLISTS: '/api/watchlists',
  ALERTS: '/api/alerts',
  SCREENER: '/api/screener',
  INDICES: '/api/indices',
}

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  INVALID_INPUT: 'Invalid input. Please check your entries.',
  NOT_FOUND: 'Resource not found.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  INTERNAL_ERROR: 'An internal error occurred. Please try again later.',
  INSUFFICIENT_BALANCE: 'Insufficient balance to execute this order.',
  INVALID_ORDER: 'Order validation failed. Please check your entries.',
}

export const SUCCESS_MESSAGES = {
  ORDER_PLACED: 'Order placed successfully.',
  ORDER_CANCELLED: 'Order cancelled successfully.',
  WATCHLIST_CREATED: 'Watchlist created successfully.',
  WATCHLIST_DELETED: 'Watchlist deleted successfully.',
  ALERT_SET: 'Price alert set successfully.',
  ALERT_DELETED: 'Price alert deleted successfully.',
}
