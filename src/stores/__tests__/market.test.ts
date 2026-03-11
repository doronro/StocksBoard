import { describe, it, expect, beforeEach } from 'vitest'
import { useMarketStore } from '../market'
import type { Quote } from '@types'

describe('Market Store', () => {
  beforeEach(() => {
    const store = useMarketStore.getState()
    store.clearQuotes()
  })

  it('Should initialize with empty quotes', () => {
    const store = useMarketStore.getState()
    expect(store.quotes.size).toBe(0)
  })

  it('Should update a single quote', () => {
    const quote: Quote = {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 150,
      change: 2.5,
      changePercent: 1.7,
      bid: 149.9,
      ask: 150.1,
      volume: 50000000,
      avgVolume: 40000000,
      timestamp: Date.now(),
      trend: 'up',
    }

    useMarketStore.getState().updateQuote(quote)
    const store = useMarketStore.getState()
    expect(store.quotes.size).toBe(1)
    expect(store.getQuote('AAPL')).toEqual(quote)
  })

  it('Should update multiple quotes', () => {
    const quotes: Quote[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 150,
        change: 2.5,
        changePercent: 1.7,
        bid: 149.9,
        ask: 150.1,
        volume: 50000000,
        avgVolume: 40000000,
        timestamp: Date.now(),
        trend: 'up',
      },
      {
        symbol: 'MSFT',
        name: 'Microsoft',
        price: 300,
        change: -1,
        changePercent: -0.33,
        bid: 299.9,
        ask: 300.1,
        volume: 30000000,
        avgVolume: 35000000,
        timestamp: Date.now(),
        trend: 'down',
      },
    ]

    useMarketStore.getState().updateQuotes(quotes)
    const store = useMarketStore.getState()
    expect(store.quotes.size).toBe(2)
    expect(store.getQuote('AAPL')).toBeDefined()
    expect(store.getQuote('MSFT')).toBeDefined()
  })

  it('Should set market status', () => {
    useMarketStore.getState().setMarketStatus('open')
    expect(useMarketStore.getState().marketStatus).toBe('open')

    useMarketStore.getState().setMarketStatus('closed')
    expect(useMarketStore.getState().marketStatus).toBe('closed')
  })

  it('Should set selected symbol', () => {
    useMarketStore.getState().setSelectedSymbol('AAPL')
    expect(useMarketStore.getState().selectedSymbol).toBe('AAPL')

    useMarketStore.getState().setSelectedSymbol(null)
    expect(useMarketStore.getState().selectedSymbol).toBeNull()
  })

  it('Should return undefined for non-existent quote', () => {
    expect(useMarketStore.getState().getQuote('NONEXISTENT')).toBeUndefined()
  })

  it('Should update last update timestamp', () => {
    const beforeTime = useMarketStore.getState().lastUpdate
    const quote: Quote = {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 150,
      change: 2.5,
      changePercent: 1.7,
      bid: 149.9,
      ask: 150.1,
      volume: 50000000,
      avgVolume: 40000000,
      timestamp: Date.now(),
      trend: 'up',
    }

    useMarketStore.getState().updateQuote(quote)
    expect(useMarketStore.getState().lastUpdate).toBeGreaterThanOrEqual(beforeTime)
  })

  it('Should clear all quotes', () => {
    const quote: Quote = {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 150,
      change: 2.5,
      changePercent: 1.7,
      bid: 149.9,
      ask: 150.1,
      volume: 50000000,
      avgVolume: 40000000,
      timestamp: Date.now(),
      trend: 'up',
    }

    useMarketStore.getState().updateQuote(quote)
    expect(useMarketStore.getState().quotes.size).toBe(1)

    useMarketStore.getState().clearQuotes()
    expect(useMarketStore.getState().quotes.size).toBe(0)
  })
})
