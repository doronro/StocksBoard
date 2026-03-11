import { useEffect, useCallback } from 'react'
import { usePortfolioStore } from '@stores/portfolio'
import type { Portfolio, Holding, Order } from '@types'

export const usePortfolioData = () => {
  const portfolioStore = usePortfolioStore()

  const fetchPortfolio = useCallback(async () => {
    try {
      // Mock portfolio data
      const mockPortfolio: Portfolio = {
        id: 'portfolio-1',
        userId: 'user-1',
        name: 'Main Portfolio',
        totalValue: 125000,
        totalCost: 100000,
        dayPnL: 2500,
        dayPnLPercent: 2.0,
        unrealizedGain: 25000,
        unrealizedGainPercent: 25.0,
        lastUpdated: Date.now(),
        holdings: [],
      }

      portfolioStore.setPortfolio(mockPortfolio)
    } catch (error) {
      console.error('Failed to fetch portfolio:', error)
      portfolioStore.setError('Failed to load portfolio')
    }
  }, [portfolioStore])

  const fetchHoldings = useCallback(async () => {
    try {
      const mockHoldings: Holding[] = [
        {
          id: 'h1',
          symbol: 'AAPL',
          name: 'Apple Inc.',
          quantity: 50,
          averagePrice: 145.30,
          currentPrice: 185.50,
          totalCost: 7265,
          currentValue: 9275,
          pnl: 2010,
          pnlPercent: 27.66,
          updatedAt: Date.now(),
        },
        {
          id: 'h2',
          symbol: 'MSFT',
          name: 'Microsoft Corporation',
          quantity: 30,
          averagePrice: 320.00,
          currentPrice: 380.00,
          totalCost: 9600,
          currentValue: 11400,
          pnl: 1800,
          pnlPercent: 18.75,
          updatedAt: Date.now(),
        },
        {
          id: 'h3',
          symbol: 'GOOGL',
          name: 'Alphabet Inc.',
          quantity: 25,
          averagePrice: 100.00,
          currentPrice: 120.00,
          totalCost: 2500,
          currentValue: 3000,
          pnl: 500,
          pnlPercent: 20.0,
          updatedAt: Date.now(),
        },
      ]

      portfolioStore.setHoldings(mockHoldings)
    } catch (error) {
      console.error('Failed to fetch holdings:', error)
      portfolioStore.setError('Failed to load holdings')
    }
  }, [portfolioStore])

  const fetchOrders = useCallback(async () => {
    try {
      const mockOrders: Order[] = [
        {
          id: 'o1',
          symbol: 'TSLA',
          side: 'buy',
          type: 'limit',
          quantity: 10,
          filledQuantity: 10,
          price: 250.00,
          status: 'filled',
          createdAt: Date.now() - 3600000,
          updatedAt: Date.now() - 3600000,
          completedAt: Date.now() - 3600000,
        },
        {
          id: 'o2',
          symbol: 'NVDA',
          side: 'buy',
          type: 'market',
          quantity: 5,
          filledQuantity: 5,
          status: 'filled',
          createdAt: Date.now() - 7200000,
          updatedAt: Date.now() - 7200000,
          completedAt: Date.now() - 7200000,
        },
        {
          id: 'o3',
          symbol: 'META',
          side: 'sell',
          type: 'limit',
          quantity: 15,
          filledQuantity: 8,
          price: 300.00,
          status: 'partial',
          createdAt: Date.now() - 1800000,
          updatedAt: Date.now(),
        },
      ]

      portfolioStore.setOrders(mockOrders)
    } catch (error) {
      console.error('Failed to fetch orders:', error)
      portfolioStore.setError('Failed to load orders')
    }
  }, [portfolioStore])

  useEffect(() => {
    portfolioStore.setLoading(true)
    Promise.all([fetchPortfolio(), fetchHoldings(), fetchOrders()]).finally(() => {
      portfolioStore.setLoading(false)
    })
  }, [fetchPortfolio, fetchHoldings, fetchOrders, portfolioStore])

  return { fetchPortfolio, fetchHoldings, fetchOrders }
}
