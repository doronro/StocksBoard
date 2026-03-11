import { useEffect, useCallback, useRef } from 'react'
import type { Quote } from '@types'
import { useMarketStore } from '@stores/market'
import { wsManager, subscribeToQuotes } from '@services/websocket'

interface UseRealtimeQuotesOptions {
  symbols?: string[]
  enabled?: boolean
  updateInterval?: number // fallback poll interval in ms
}

export const useRealtimeQuotes = ({
  symbols = [],
  enabled = true,
  updateInterval = 5000,
}: UseRealtimeQuotesOptions = {}) => {
  const marketStore = useMarketStore()
  const unsubscribeRef = useRef<(() => void) | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Setup WebSocket subscription
  useEffect(() => {
    if (!enabled || symbols.length === 0) return

    const setupSubscription = async () => {
      // Ensure WebSocket is connected
      if (!wsManager.isConnected()) {
        try {
          await wsManager.connect()
        } catch (error) {
          console.error('Failed to connect WebSocket:', error)
          // Fallback to polling
          setupPolling()
          return
        }
      }

      // Subscribe to real-time quote updates
      const handleQuoteUpdate = (quote: Quote) => {
        marketStore.updateQuote(quote)
      }

      unsubscribeRef.current = subscribeToQuotes(symbols, handleQuoteUpdate)
    }

    setupSubscription()

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current()
        unsubscribeRef.current = null
      }
    }
  }, [enabled, symbols, marketStore])

  // Fallback polling mechanism
  const setupPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
    }

    pollIntervalRef.current = setInterval(() => {
      // In a real app, fetch quotes here
      console.debug('[Polling] Fetching quotes:', symbols)
    }, updateInterval)
  }, [symbols, updateInterval])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [])

  return {
    quotes: marketStore.quotes,
    isConnected: wsManager.isConnected(),
  }
}
