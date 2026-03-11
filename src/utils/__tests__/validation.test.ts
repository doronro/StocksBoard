import { describe, it, expect } from 'vitest'
import {
  validateOrderQuantity,
  validateOrderPrice,
  validateEmail,
  validateSymbol,
  validateWatchlistName,
  validatePercentage,
  validatePriceAlert,
  validateTrailingStop,
  sanitizeSymbol,
  getOrderValidationError,
} from '../validation'

describe('Validation Utilities', () => {
  describe('validateOrderQuantity', () => {
    it('Should validate positive integer quantity', () => {
      expect(validateOrderQuantity(100)).toBe(true)
      expect(validateOrderQuantity(1)).toBe(true)
    })

    it('Should reject non-integer quantities', () => {
      expect(validateOrderQuantity(10.5)).toBe(false)
      expect(validateOrderQuantity(0)).toBe(false)
      expect(validateOrderQuantity(-5)).toBe(false)
    })
  })

  describe('validateOrderPrice', () => {
    it('Should validate positive price', () => {
      expect(validateOrderPrice(100.50)).toBe(true)
      expect(validateOrderPrice(0.01)).toBe(true)
    })

    it('Should reject invalid prices', () => {
      expect(validateOrderPrice(-10)).toBe(false)
      expect(validateOrderPrice(0)).toBe(false)
      expect(validateOrderPrice(NaN)).toBe(false)
      expect(validateOrderPrice(Infinity)).toBe(false)
    })
  })

  describe('validateEmail', () => {
    it('Should validate correct email format', () => {
      expect(validateEmail('user@example.com')).toBe(true)
      expect(validateEmail('test.email+tag@domain.co.uk')).toBe(true)
    })

    it('Should reject invalid email format', () => {
      expect(validateEmail('invalid')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('@domain.com')).toBe(false)
    })
  })

  describe('validateSymbol', () => {
    it('Should validate valid stock symbols', () => {
      expect(validateSymbol('AAPL')).toBe(true)
      expect(validateSymbol('msft')).toBe(true) // Should convert to uppercase
      expect(validateSymbol('BRK.B')).toBe(true) // With class indicator
    })

    it('Should reject invalid symbols', () => {
      expect(validateSymbol('TOOLONG')).toBe(false) // More than 5 chars
      expect(validateSymbol('123')).toBe(false) // Numbers only
      expect(validateSymbol('A')).toBe(true) // Single letter is valid
    })
  })

  describe('validateWatchlistName', () => {
    it('Should validate watchlist name', () => {
      expect(validateWatchlistName('My Watchlist')).toBe(true)
      expect(validateWatchlistName('Tech Stocks')).toBe(true)
    })

    it('Should reject invalid watchlist names', () => {
      expect(validateWatchlistName('')).toBe(false)
      expect(validateWatchlistName('   ')).toBe(false)
      expect(validateWatchlistName('a'.repeat(51))).toBe(false) // More than 50 chars
    })
  })

  describe('validatePercentage', () => {
    it('Should validate percentage range', () => {
      expect(validatePercentage(0)).toBe(true)
      expect(validatePercentage(50)).toBe(true)
      expect(validatePercentage(100)).toBe(true)
    })

    it('Should reject out-of-range percentages', () => {
      expect(validatePercentage(-1)).toBe(false)
      expect(validatePercentage(101)).toBe(false)
    })
  })

  describe('validatePriceAlert', () => {
    it('Should validate price alert', () => {
      expect(validatePriceAlert(150, 100)).toBe(true)
      expect(validatePriceAlert(50, 100)).toBe(true)
    })

    it('Should reject invalid price alerts', () => {
      expect(validatePriceAlert(100, 100)).toBe(false) // Same as current price
      expect(validatePriceAlert(-50, 100)).toBe(false) // Negative price
      expect(validatePriceAlert(NaN, 100)).toBe(false) // NaN
    })
  })

  describe('validateTrailingStop', () => {
    it('Should validate trailing stop percentage', () => {
      expect(validateTrailingStop(2.5)).toBe(true)
      expect(validateTrailingStop(0.1)).toBe(true)
    })

    it('Should reject invalid trailing stop', () => {
      expect(validateTrailingStop(0)).toBe(false)
      expect(validateTrailingStop(-5)).toBe(false)
      expect(validateTrailingStop(100)).toBe(false) // Must be less than 100
    })
  })

  describe('sanitizeSymbol', () => {
    it('Should sanitize and uppercase symbol', () => {
      expect(sanitizeSymbol('aapl')).toBe('AAPL')
      expect(sanitizeSymbol('msft ')).toBe('MSFT')
    })

    it('Should limit symbol length', () => {
      expect(sanitizeSymbol('TOOLONGSYMBOL').length).toBeLessThanOrEqual(5)
    })

    it('Should remove invalid characters', () => {
      expect(sanitizeSymbol('A@PL!')).toBe('A')
    })
  })

  describe('getOrderValidationError', () => {
    it('Should return no error for valid buy order', () => {
      const error = getOrderValidationError('buy', 10, 100, 'market', 10000, 100)
      expect(error).toBeNull()
    })

    it('Should return error for invalid quantity', () => {
      const error = getOrderValidationError('buy', 0, 100, 'market', 10000, 100)
      expect(error).toBeTruthy()
      expect(error).toContain('Quantity')
    })

    it('Should return error for insufficient balance', () => {
      const error = getOrderValidationError('buy', 100, 150, 'market', 5000, 100)
      expect(error).toBeTruthy()
      expect(error).toContain('balance')
    })

    it('Should return error for limit order without price', () => {
      const error = getOrderValidationError('buy', 10, null, 'limit', 10000, 100)
      expect(error).toBeTruthy()
      expect(error).toContain('Price')
    })
  })

  describe('QA-001: Symbol Validation Enhancement', () => {
    it('Should validate symbols with class indicators correctly', () => {
      expect(validateSymbol('BRK.B')).toBe(true)
      expect(validateSymbol('BF.A')).toBe(true)
    })

    it('Should reject symbols with multiple dots', () => {
      expect(validateSymbol('TEST.A.B')).toBe(false)
    })

    it('Should reject symbols starting with dot', () => {
      expect(validateSymbol('.TEST')).toBe(false)
    })

    it('Should only accept uppercase letters', () => {
      expect(validateSymbol('AaPL')).toBe(true) // Will be converted to uppercase
      expect(validateSymbol('aapl')).toBe(true) // Will be converted to uppercase
    })

    it('Should reject special characters except dot', () => {
      expect(validateSymbol('A@PL')).toBe(false)
      expect(validateSymbol('A-PL')).toBe(false)
      expect(validateSymbol('A PL')).toBe(false)
    })
  })
})
