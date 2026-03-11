import { useEffect, useCallback } from 'react'
import { useMarketStore } from '@stores/market'
import type { Quote, MarketIndex } from '@types'

export const useMarketData = () => {
  const marketStore = useMarketStore()

  // Simulate fetching market data
  const fetchQuotes = useCallback(async (symbols: string[]) => {
    try {
      // In a real application, this would call an API
      // For now, we'll use mock data
      const mockQuotes: Quote[] = symbols.map((symbol) => ({
        symbol,
        name: `${symbol} Inc.`,
        price: Math.random() * 300 + 50,
        change: (Math.random() - 0.5) * 10,
        changePercent: (Math.random() - 0.5) * 5,
        bid: Math.random() * 300 + 50,
        ask: Math.random() * 300 + 50,
        volume: Math.floor(Math.random() * 100000000),
        avgVolume: Math.floor(Math.random() * 50000000),
        timestamp: Date.now(),
        trend: Math.random() > 0.5 ? 'up' : 'down',
      }))

      marketStore.updateQuotes(mockQuotes)
    } catch (error) {
      console.error('Failed to fetch quotes:', error)
    }
  }, [marketStore])

  // Simulate fetching indices
  const fetchIndices = useCallback(async () => {
    try {
      const mockIndices: MarketIndex[] = [
        {
          symbol: '^GSPC',
          name: 'S&P 500',
          value: 4200 + Math.random() * 100,
          change: (Math.random() - 0.5) * 50,
          changePercent: (Math.random() - 0.5) * 2,
          timestamp: Date.now(),
        },
        {
          symbol: '^IXIC',
          name: 'NASDAQ-100',
          value: 14000 + Math.random() * 200,
          change: (Math.random() - 0.5) * 100,
          changePercent: (Math.random() - 0.5) * 2.5,
          timestamp: Date.now(),
        },
        {
          symbol: '^RUT',
          name: 'Russell 2000',
          value: 1900 + Math.random() * 50,
          change: (Math.random() - 0.5) * 30,
          changePercent: (Math.random() - 0.5) * 2,
          timestamp: Date.now(),
        },
      ]

      marketStore.updateIndices(mockIndices)
    } catch (error) {
      console.error('Failed to fetch indices:', error)
    }
  }, [marketStore])

  // Initial fetch
  useEffect(() => {
    fetchIndices()
    fetchQuotes(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX'])

    // Set up periodic updates (simulated)
    const interval = setInterval(() => {
      fetchQuotes(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX'])
    }, 5000)

    return () => clearInterval(interval)
  }, [fetchQuotes, fetchIndices])

  return { fetchQuotes, fetchIndices }
}
