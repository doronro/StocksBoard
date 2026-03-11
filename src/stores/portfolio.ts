import { create } from 'zustand'
import type { Portfolio, Holding, Order } from '@types'

interface PortfolioState {
  portfolio: Portfolio | null
  holdings: Holding[]
  orders: Order[]
  selectedHolding: Holding | null
  isLoading: boolean
  error: string | null

  // Actions
  setPortfolio: (portfolio: Portfolio | null) => void
  setHoldings: (holdings: Holding[]) => void
  updateHolding: (holding: Holding) => void
  removeHolding: (symbol: string) => void
  setOrders: (orders: Order[]) => void
  addOrder: (order: Order) => void
  updateOrder: (order: Order) => void
  removeOrder: (orderId: string) => void
  setSelectedHolding: (holding: Holding | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  getHolding: (symbol: string) => Holding | undefined
  getFilledOrders: () => Order[]
  getPendingOrders: () => Order[]
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  portfolio: null,
  holdings: [],
  orders: [],
  selectedHolding: null,
  isLoading: false,
  error: null,

  setPortfolio: (portfolio) => {
    set({ portfolio })
  },

  setHoldings: (holdings) => {
    set({ holdings })
  },

  updateHolding: (holding) => {
    set((state) => {
      const holdings = state.holdings.map((h) =>
        h.symbol === holding.symbol ? holding : h
      )
      return { holdings }
    })
  },

  removeHolding: (symbol) => {
    set((state) => ({
      holdings: state.holdings.filter((h) => h.symbol !== symbol),
    }))
  },

  setOrders: (orders) => {
    set({ orders })
  },

  addOrder: (order) => {
    set((state) => ({
      orders: [order, ...state.orders],
    }))
  },

  updateOrder: (order) => {
    set((state) => ({
      orders: state.orders.map((o) => (o.id === order.id ? order : o)),
    }))
  },

  removeOrder: (orderId) => {
    set((state) => ({
      orders: state.orders.filter((o) => o.id !== orderId),
    }))
  },

  setSelectedHolding: (holding) => {
    set({ selectedHolding: holding })
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },

  setError: (error) => {
    set({ error })
  },

  getHolding: (symbol) => {
    return get().holdings.find((h) => h.symbol === symbol)
  },

  getFilledOrders: () => {
    return get().orders.filter((o) => o.status === 'filled')
  },

  getPendingOrders: () => {
    return get().orders.filter((o) => o.status === 'pending')
  },
}))
