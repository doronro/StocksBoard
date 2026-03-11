import { create } from 'zustand'
import type { Quote, MarketStatus, MarketIndex, SectorPerformance, MarketBreadth } from '@types'

interface MarketState {
  quotes: Map<string, Quote>
  indices: MarketIndex[]
  sectors: SectorPerformance[]
  breadth: MarketBreadth | null
  marketStatus: MarketStatus
  selectedSymbol: string | null
  lastUpdate: number

  // Actions
  updateQuote: (quote: Quote) => void
  updateQuotes: (quotes: Quote[]) => void
  updateIndices: (indices: MarketIndex[]) => void
  updateSectors: (sectors: SectorPerformance[]) => void
  updateBreadth: (breadth: MarketBreadth) => void
  setMarketStatus: (status: MarketStatus) => void
  setSelectedSymbol: (symbol: string | null) => void
  getQuote: (symbol: string) => Quote | undefined
  clearQuotes: () => void
}

export const useMarketStore = create<MarketState>((set, get) => ({
  quotes: new Map(),
  indices: [],
  sectors: [],
  breadth: null,
  marketStatus: 'closed',
  selectedSymbol: null,
  lastUpdate: 0,

  updateQuote: (quote) => {
    set((state) => {
      const newQuotes = new Map(state.quotes)
      newQuotes.set(quote.symbol, quote)
      return {
        quotes: newQuotes,
        lastUpdate: Date.now(),
      }
    })
  },

  updateQuotes: (quotes) => {
    set((state) => {
      const newQuotes = new Map(state.quotes)
      quotes.forEach((quote) => {
        newQuotes.set(quote.symbol, quote)
      })
      return {
        quotes: newQuotes,
        lastUpdate: Date.now(),
      }
    })
  },

  updateIndices: (indices) => {
    set({ indices, lastUpdate: Date.now() })
  },

  updateSectors: (sectors) => {
    set({ sectors, lastUpdate: Date.now() })
  },

  updateBreadth: (breadth) => {
    set({ breadth, lastUpdate: Date.now() })
  },

  setMarketStatus: (status) => {
    set({ marketStatus: status })
  },

  setSelectedSymbol: (symbol) => {
    set({ selectedSymbol: symbol })
  },

  getQuote: (symbol) => {
    return get().quotes.get(symbol)
  },

  clearQuotes: () => {
    set({ quotes: new Map(), lastUpdate: Date.now() })
  },
}))
