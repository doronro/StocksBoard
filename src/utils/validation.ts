export const validateOrderQuantity = (quantity: number): boolean => {
  return Number.isInteger(quantity) && quantity > 0
}

export const validateOrderPrice = (price: number): boolean => {
  return price > 0 && !isNaN(price) && isFinite(price)
}

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validateSymbol = (symbol: string): boolean => {
  const symbolRegex = /^[A-Z]{1,5}(\.[A-Z])?$/
  return symbolRegex.test(symbol.toUpperCase())
}

export const validateWatchlistName = (name: string): boolean => {
  return name.trim().length > 0 && name.length <= 50
}

export const validatePercentage = (value: number): boolean => {
  return value >= 0 && value <= 100
}

export const validatePriceAlert = (price: number, currentPrice: number): boolean => {
  return price > 0 && price !== currentPrice && !isNaN(price) && isFinite(price)
}

export const validateTrailingStop = (trailingPercent: number): boolean => {
  return trailingPercent > 0 && trailingPercent < 100
}

export const sanitizeSymbol = (symbol: string): string => {
  return symbol.toUpperCase().trim().split(/[^\w.-]/)[0].slice(0, 5)
}

export const getOrderValidationError = (
  side: 'buy' | 'sell',
  quantity: number,
  price: number | null,
  type: string,
  balance: number,
  _currentPrice: number
): string | null => {
  if (!validateOrderQuantity(quantity)) {
    return 'Quantity must be a positive integer'
  }

  if (type === 'limit' || type === 'stop_loss') {
    if (price === null || !validateOrderPrice(price)) {
      return 'Price must be a positive number'
    }
  }

  if (side === 'buy' && price) {
    const estimatedCost = quantity * price
    if (estimatedCost > balance) {
      return 'Insufficient balance for this order'
    }
  }

  return null
}
