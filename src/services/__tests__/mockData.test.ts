/**
 * Unit tests for mock data service
 */

import { describe, it, expect } from 'vitest'
import {
  generateMockQuote,
  generateMockChartData,
  generateMockTechnicalIndicators,
  generateMockIndices,
  generateMockSectorPerformance,
  generateMockEvents,
  getSymbols,
  generateMockPortfolioData,
  generateMockAlerts,
  generateMockOrders,
} from '../mockData'

describe('Mock Data Service', () => {
  describe('generateMockQuote', () => {
    it('should generate a valid quote with required fields', () => {
      const quote = generateMockQuote('AAPL')

      expect(quote.symbol).toBe('AAPL')
      expect(quote.name).toBeDefined()
      expect(typeof quote.price).toBe('number')
      expect(typeof quote.change).toBe('number')
      expect(typeof quote.changePercent).toBe('number')
      expect(typeof quote.volume).toBe('number')
      expect(typeof quote.timestamp).toBe('number')
      expect(['up', 'down']).toContain(quote.trend)
    })

    it('should generate positive prices', () => {
      for (let i = 0; i < 10; i++) {
        const quote = generateMockQuote('MSFT')
        expect(quote.price).toBeGreaterThan(0)
        expect(quote.bid).toBeGreaterThan(0)
        expect(quote.ask).toBeGreaterThan(0)
      }
    })

    it('should match bid < price < ask', () => {
      const quote = generateMockQuote('GOOGL')
      expect(quote.bid).toBeLessThan(quote.price)
      expect(quote.price).toBeLessThan(quote.ask)
    })

    it('should generate trend based on price change', () => {
      const quote = generateMockQuote('TSLA')
      if (quote.change >= 0) {
        expect(quote.trend).toBe('up')
      } else {
        expect(quote.trend).toBe('down')
      }
    })
  })

  describe('generateMockChartData', () => {
    it('should generate correct number of candles', () => {
      const data = generateMockChartData('1d', 50)
      expect(data).toHaveLength(50)
    })

    it('should have valid OHLC structure', () => {
      const data = generateMockChartData('1d', 10)

      data.forEach(candle => {
        expect(typeof candle.timestamp).toBe('number')
        expect(typeof candle.open).toBe('number')
        expect(typeof candle.high).toBe('number')
        expect(typeof candle.low).toBe('number')
        expect(typeof candle.close).toBe('number')
        expect(typeof candle.volume).toBe('number')
      })
    })

    it('should have high >= low', () => {
      const data = generateMockChartData('1d', 20)

      data.forEach(candle => {
        expect(candle.high).toBeGreaterThanOrEqual(candle.low)
      })
    })

    it('should generate data in chronological order', () => {
      const data = generateMockChartData('1d', 20)

      for (let i = 1; i < data.length; i++) {
        expect(data[i].timestamp).toBeGreaterThan(data[i - 1].timestamp)
      }
    })

    it('should respect timeframe intervals', () => {
      const data1h = generateMockChartData('1h', 24)
      const data1d = generateMockChartData('1d', 30)

      // 1h data should have smaller intervals than 1d data
      const interval1h = data1h[1].timestamp - data1h[0].timestamp
      const interval1d = data1d[1].timestamp - data1d[0].timestamp

      expect(interval1h).toBeLessThan(interval1d)
    })
  })

  describe('generateMockTechnicalIndicators', () => {
    it('should generate all required indicators', () => {
      const indicators = generateMockTechnicalIndicators()

      expect(indicators.rsi).toBeDefined()
      expect(indicators.macd).toBeDefined()
      expect(indicators.sma20).toBeDefined()
      expect(indicators.sma50).toBeDefined()
      expect(indicators.sma200).toBeDefined()
      expect(indicators.ema12).toBeDefined()
      expect(indicators.ema26).toBeDefined()
    })

    it('should generate RSI between 0 and 100', () => {
      for (let i = 0; i < 10; i++) {
        const indicators = generateMockTechnicalIndicators()
        expect(indicators.rsi).toBeGreaterThanOrEqual(0)
        expect(indicators.rsi).toBeLessThanOrEqual(100)
      }
    })

    it('should have valid moving average arrays', () => {
      const indicators = generateMockTechnicalIndicators()

      expect(Array.isArray(indicators.sma20)).toBe(true)
      expect(Array.isArray(indicators.sma50)).toBe(true)
      expect(Array.isArray(indicators.sma200)).toBe(true)
      expect(indicators.sma20!.length).toBeLessThanOrEqual(20)
      expect(indicators.sma50!.length).toBeLessThanOrEqual(50)
    })

    it('should have valid MACD structure', () => {
      const indicators = generateMockTechnicalIndicators()

      expect(indicators.macd).toBeDefined()
      expect(typeof indicators.macd!.line).toBe('number')
      expect(typeof indicators.macd!.signal).toBe('number')
      expect(typeof indicators.macd!.histogram).toBe('number')
    })
  })

  describe('generateMockIndices', () => {
    it('should generate 3 market indices', () => {
      const indices = generateMockIndices()
      expect(indices).toHaveLength(3)
    })

    it('should have valid index data', () => {
      const indices = generateMockIndices()

      indices.forEach(index => {
        expect(index.symbol).toBeDefined()
        expect(index.name).toBeDefined()
        expect(typeof index.value).toBe('number')
        expect(typeof index.change).toBe('number')
        expect(typeof index.changePercent).toBe('number')
        expect(typeof index.timestamp).toBe('number')
      })
    })

    it('should include S&P 500, Nasdaq, and Dow Jones', () => {
      const indices = generateMockIndices()
      const symbols = indices.map(i => i.symbol)

      expect(symbols).toContain('^GSPC') // S&P 500
      expect(symbols).toContain('^IXIC') // Nasdaq
      expect(symbols).toContain('^DJI') // Dow Jones
    })
  })

  describe('generateMockSectorPerformance', () => {
    it('should generate sector performance data', () => {
      const sectors = generateMockSectorPerformance()

      expect(sectors.length).toBeGreaterThan(0)
      sectors.forEach(sector => {
        expect(sector.name).toBeDefined()
        expect(typeof sector.change).toBe('number')
        expect(typeof sector.changePercent).toBe('number')
      })
    })
  })

  describe('generateMockEvents', () => {
    it('should generate calendar events', () => {
      const events = generateMockEvents()

      expect(events.length).toBeGreaterThan(0)
      events.forEach(event => {
        expect(event.date).toBeInstanceOf(Date)
        expect(event.symbol).toBeDefined()
        expect(['earnings', 'news']).toContain(event.type)
        expect(event.title).toBeDefined()
        expect(event.description).toBeDefined()
      })
    })

    it('should sort events chronologically', () => {
      const events = generateMockEvents()

      for (let i = 1; i < events.length; i++) {
        expect(events[i].date.getTime()).toBeGreaterThanOrEqual(events[i - 1].date.getTime())
      }
    })
  })

  describe('getSymbols', () => {
    it('should return array of symbols', () => {
      const symbols = getSymbols()

      expect(Array.isArray(symbols)).toBe(true)
      expect(symbols.length).toBeGreaterThan(0)
      symbols.forEach(symbol => {
        expect(typeof symbol).toBe('string')
        expect(symbol.length).toBeGreaterThan(0)
      })
    })

    it('should return consistent symbols', () => {
      const symbols1 = getSymbols()
      const symbols2 = getSymbols()

      expect(symbols1).toEqual(symbols2)
    })
  })

  describe('generateMockPortfolioData', () => {
    it('should generate valid portfolio data', () => {
      const portfolio = generateMockPortfolioData()

      expect(portfolio.holdings).toBeInstanceOf(Array)
      expect(typeof portfolio.totalValue).toBe('number')
      expect(typeof portfolio.totalCost).toBe('number')
    })

    it('should have matching total calculations', () => {
      const portfolio = generateMockPortfolioData()

      const calculatedCost = portfolio.holdings.reduce(
        (sum, h) => sum + h.quantity * h.averagePrice,
        0
      )
      const calculatedValue = portfolio.holdings.reduce(
        (sum, h) => sum + h.quantity * h.currentPrice,
        0
      )

      expect(calculatedCost).toBeCloseTo(portfolio.totalCost, 0)
      expect(calculatedValue).toBeCloseTo(portfolio.totalValue, 0)
    })
  })

  describe('generateMockAlerts', () => {
    it('should generate price alerts', () => {
      const alerts = generateMockAlerts()

      expect(Array.isArray(alerts)).toBe(true)
      alerts.forEach(alert => {
        expect(alert.id).toBeDefined()
        expect(alert.symbol).toBeDefined()
        expect(['above', 'below']).toContain(alert.type)
        expect(typeof alert.targetPrice).toBe('number')
        expect(typeof alert.isActive).toBe('boolean')
        expect(typeof alert.triggered).toBe('boolean')
      })
    })
  })

  describe('generateMockOrders', () => {
    it('should generate orders with valid structure', () => {
      const orders = generateMockOrders()

      expect(Array.isArray(orders)).toBe(true)
      orders.forEach(order => {
        expect(order.id).toBeDefined()
        expect(order.symbol).toBeDefined()
        expect(['buy', 'sell']).toContain(order.side)
        expect(['market', 'limit', 'stop_loss', 'trailing_stop']).toContain(order.type)
        expect(typeof order.quantity).toBe('number')
        expect(order.quantity).toBeGreaterThan(0)
      })
    })

    it('should have valid filled quantities', () => {
      const orders = generateMockOrders()

      orders.forEach(order => {
        expect(order.filledQuantity).toBeLessThanOrEqual(order.quantity)
        expect(order.filledQuantity).toBeGreaterThanOrEqual(0)
      })
    })
  })
})
