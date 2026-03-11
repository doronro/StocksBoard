import { describe, it, expect } from 'vitest'
import {
  formatPrice,
  formatCurrency,
  formatVolume,
  formatPercent,
  formatMarketCap,
  getChangeColor,
  getChangeBgColor,
} from '../formatting'

describe('Formatting Utilities', () => {
  describe('formatPrice', () => {
    it('Should format price with 2 decimal places', () => {
      expect(formatPrice(123.456)).toBe('123.46')
    })

    it('Should handle zero price', () => {
      expect(formatPrice(0)).toBe('0.00')
    })

    it('Should handle negative price', () => {
      expect(formatPrice(-50.75)).toBe('-50.75')
    })

    it('Should respect custom decimal places', () => {
      expect(formatPrice(123.456789, 3)).toBe('123.457')
    })
  })

  describe('formatVolume', () => {
    it('Should format volume in billions', () => {
      expect(formatVolume(1_500_000_000)).toBe('1.50B')
    })

    it('Should format volume in millions', () => {
      expect(formatVolume(500_000)).toBe('500.00K')
    })

    it('Should format volume in thousands', () => {
      expect(formatVolume(5_000)).toBe('5.00K')
    })

    it('Should handle small volumes', () => {
      expect(formatVolume(100)).toBe('100')
    })
  })

  describe('formatPercent', () => {
    it('Should format positive percentage', () => {
      expect(formatPercent(5.123)).toBe('+5.12%')
    })

    it('Should format negative percentage', () => {
      expect(formatPercent(-3.456)).toBe('-3.46%')
    })

    it('Should handle zero percentage', () => {
      expect(formatPercent(0)).toBe('0.00%')
    })

    it('Should respect custom decimal places', () => {
      expect(formatPercent(5.6789, 3)).toBe('+5.679%')
    })
  })

  describe('formatMarketCap', () => {
    it('Should format market cap in trillions', () => {
      expect(formatMarketCap(2_000_000_000_000)).toBe('$2.00T')
    })

    it('Should format market cap in billions', () => {
      expect(formatMarketCap(500_000_000_000)).toBe('$500.00B')
    })

    it('Should format market cap in millions', () => {
      expect(formatMarketCap(100_000_000)).toBe('$100.00M')
    })
  })

  describe('getChangeColor', () => {
    it('Should return green for positive change', () => {
      expect(getChangeColor(5)).toBe('text-green-500')
    })

    it('Should return red for negative change', () => {
      expect(getChangeColor(-5)).toBe('text-red-500')
    })

    it('Should return neutral for zero change', () => {
      expect(getChangeColor(0)).toBe('text-neutral-400')
    })

    it('Should respect usePositiveGreen flag', () => {
      expect(getChangeColor(5, false)).toBe('text-red-500')
      expect(getChangeColor(-5, false)).toBe('text-green-500')
    })
  })

  describe('getChangeBgColor', () => {
    it('Should return green background for positive change', () => {
      expect(getChangeBgColor(5)).toBe('bg-green-500/10')
    })

    it('Should return red background for negative change', () => {
      expect(getChangeBgColor(-5)).toBe('bg-red-500/10')
    })

    it('Should return neutral background for zero change', () => {
      expect(getChangeBgColor(0)).toBe('bg-neutral-500/10')
    })
  })

  describe('formatCurrency', () => {
    it('Should format currency with default USD', () => {
      const result = formatCurrency(1234.56)
      expect(result).toMatch(/\$/)
      expect(result).toMatch(/1,234/)
    })

    it('Should handle large currency values', () => {
      const result = formatCurrency(1000000)
      expect(result).toMatch(/\$/)
      expect(result).toMatch(/1,000,000/)
    })
  })
})
