import { create } from 'zustand'
import type { Watchlist, Quote } from '@types'

interface WatchlistState {
  watchlists: Watchlist[]
  selectedWatchlistId: string | null
  watchlistQuotes: Map<string, Quote[]> // watchlistId -> quotes

  // Actions
  setWatchlists: (watchlists: Watchlist[]) => void
  addWatchlist: (watchlist: Watchlist) => void
  updateWatchlist: (watchlist: Watchlist) => void
  deleteWatchlist: (id: string) => void
  setSelectedWatchlist: (id: string | null) => void
  addSymbolToWatchlist: (watchlistId: string, symbol: string) => void
  removeSymbolFromWatchlist: (watchlistId: string, symbol: string) => void
  setWatchlistQuotes: (watchlistId: string, quotes: Quote[]) => void
  getWatchlist: (id: string) => Watchlist | undefined
  getWatchlistQuotes: (id: string) => Quote[]
  getSelectedWatchlist: () => Watchlist | undefined
}

export const useWatchlistStore = create<WatchlistState>((set, get) => ({
  watchlists: [],
  selectedWatchlistId: null,
  watchlistQuotes: new Map(),

  setWatchlists: (watchlists) => {
    set({ watchlists })
  },

  addWatchlist: (watchlist) => {
    set((state) => ({
      watchlists: [watchlist, ...state.watchlists],
    }))
  },

  updateWatchlist: (watchlist) => {
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlist.id ? watchlist : w
      ),
    }))
  },

  deleteWatchlist: (id) => {
    set((state) => ({
      watchlists: state.watchlists.filter((w) => w.id !== id),
      selectedWatchlistId:
        state.selectedWatchlistId === id ? null : state.selectedWatchlistId,
      watchlistQuotes: (() => {
        const quotes = new Map(state.watchlistQuotes)
        quotes.delete(id)
        return quotes
      })(),
    }))
  },

  setSelectedWatchlist: (id) => {
    set({ selectedWatchlistId: id })
  },

  addSymbolToWatchlist: (watchlistId, symbol) => {
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlistId
          ? {
              ...w,
              symbols: [...new Set([...w.symbols, symbol])],
              updatedAt: Date.now(),
            }
          : w
      ),
    }))
  },

  removeSymbolFromWatchlist: (watchlistId, symbol) => {
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlistId
          ? {
              ...w,
              symbols: w.symbols.filter((s) => s !== symbol),
              updatedAt: Date.now(),
            }
          : w
      ),
    }))
  },

  setWatchlistQuotes: (watchlistId, quotes) => {
    set((state) => {
      const newQuotes = new Map(state.watchlistQuotes)
      newQuotes.set(watchlistId, quotes)
      return { watchlistQuotes: newQuotes }
    })
  },

  getWatchlist: (id) => {
    return get().watchlists.find((w) => w.id === id)
  },

  getWatchlistQuotes: (id) => {
    return get().watchlistQuotes.get(id) || []
  },

  getSelectedWatchlist: () => {
    const state = get()
    return state.selectedWatchlistId
      ? state.watchlists.find((w) => w.id === state.selectedWatchlistId)
      : undefined
  },
}))
