import axios, { AxiosInstance } from 'axios'
import type {
  Quote,
  ChartDataPoint,
  TechnicalIndicator,
  Portfolio,
  Order,
  Watchlist,
  MarketIndex,
  ScreenerResult,
  ScreenerCriteria,
} from '@types'

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:3001/api'

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,  // Send httpOnly cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
})

// Note: Authentication is handled via httpOnly cookies set by the backend
// Frontend should NOT attempt to access or store tokens directly
// Cookies are automatically sent with all requests via withCredentials: true

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const quoteAPI = {
  getQuote: async (symbol: string): Promise<Quote> => {
    const response = await apiClient.get(`/quotes/${symbol}`)
    return response.data
  },

  getQuotes: async (symbols: string[]): Promise<Quote[]> => {
    const response = await apiClient.post('/quotes/batch', { symbols })
    return response.data
  },

  // Note: WebSocket subscriptions should use wsManager from websocket service
  // This avoids creating multiple connections and ensures proper authentication
  subscribeToQuotes: (_symbols: string[], _callback: (quote: Quote) => void): (() => void) => {
    // This is deprecated - use wsManager.subscribeToQuotes instead
    // Left for backward compatibility
    console.warn('[API] Direct WebSocket subscription deprecated. Use wsManager instead.')
    return () => {}
  },
}

export const chartAPI = {
  getChartData: async (
    symbol: string,
    timeframe: string,
    limit: number = 100
  ): Promise<ChartDataPoint[]> => {
    const response = await apiClient.get(`/charts/${symbol}`, {
      params: { timeframe, limit },
    })
    return response.data
  },

  getIndicators: async (
    symbol: string,
    timeframe: string
  ): Promise<TechnicalIndicator> => {
    const response = await apiClient.get(`/indicators/${symbol}`, {
      params: { timeframe },
    })
    return response.data
  },
}

export const portfolioAPI = {
  getPortfolio: async (): Promise<Portfolio> => {
    const response = await apiClient.get('/portfolio')
    return response.data
  },

  updatePortfolio: async (portfolio: Partial<Portfolio>): Promise<Portfolio> => {
    const response = await apiClient.put('/portfolio', portfolio)
    return response.data
  },

  getHoldings: async () => {
    const response = await apiClient.get('/portfolio/holdings')
    return response.data
  },
}

export const orderAPI = {
  getOrders: async (status?: string): Promise<Order[]> => {
    const response = await apiClient.get('/orders', {
      params: { status },
    })
    return response.data
  },

  getOrder: async (orderId: string): Promise<Order> => {
    const response = await apiClient.get(`/orders/${orderId}`)
    return response.data
  },

  createOrder: async (order: Partial<Order>): Promise<Order> => {
    const response = await apiClient.post('/orders', order)
    return response.data
  },

  cancelOrder: async (orderId: string): Promise<Order> => {
    const response = await apiClient.delete(`/orders/${orderId}`)
    return response.data
  },

  updateOrder: async (orderId: string, updates: Partial<Order>): Promise<Order> => {
    const response = await apiClient.patch(`/orders/${orderId}`, updates)
    return response.data
  },

  getOrderHistory: async (limit: number = 100): Promise<Order[]> => {
    const response = await apiClient.get('/orders/history', {
      params: { limit },
    })
    return response.data
  },
}

export const watchlistAPI = {
  getWatchlists: async (): Promise<Watchlist[]> => {
    const response = await apiClient.get('/watchlists')
    return response.data
  },

  createWatchlist: async (name: string, symbols: string[]): Promise<Watchlist> => {
    const response = await apiClient.post('/watchlists', { name, symbols })
    return response.data
  },

  updateWatchlist: async (
    watchlistId: string,
    updates: Partial<Watchlist>
  ): Promise<Watchlist> => {
    const response = await apiClient.put(`/watchlists/${watchlistId}`, updates)
    return response.data
  },

  deleteWatchlist: async (watchlistId: string): Promise<void> => {
    await apiClient.delete(`/watchlists/${watchlistId}`)
  },

  addSymbolToWatchlist: async (watchlistId: string, symbol: string): Promise<Watchlist> => {
    const response = await apiClient.post(`/watchlists/${watchlistId}/symbols`, { symbol })
    return response.data
  },

  removeSymbolFromWatchlist: async (watchlistId: string, symbol: string): Promise<Watchlist> => {
    const response = await apiClient.delete(`/watchlists/${watchlistId}/symbols/${symbol}`)
    return response.data
  },
}

export const marketAPI = {
  getIndices: async (): Promise<MarketIndex[]> => {
    const response = await apiClient.get('/market/indices')
    return response.data
  },

  getMarketStatus: async () => {
    const response = await apiClient.get('/market/status')
    return response.data
  },

  getMarketBreadth: async () => {
    const response = await apiClient.get('/market/breadth')
    return response.data
  },

  getSectors: async () => {
    const response = await apiClient.get('/market/sectors')
    return response.data
  },
}

export const screenerAPI = {
  runScreener: async (criteria: ScreenerCriteria): Promise<ScreenerResult[]> => {
    const response = await apiClient.post('/screener/run', criteria)
    return response.data
  },

  getScreenerResults: async (screenerName: string): Promise<ScreenerResult[]> => {
    const response = await apiClient.get(`/screener/${screenerName}`)
    return response.data
  },
}

export default apiClient
