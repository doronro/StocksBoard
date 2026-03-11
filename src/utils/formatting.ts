export const formatPrice = (price: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(price)
}

export const formatCurrency = (
  value: number,
  currency: string = 'USD',
  decimals: number = 2
): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export const formatVolume = (volume: number): string => {
  if (volume >= 1_000_000_000) {
    return `${(volume / 1_000_000_000).toFixed(2)}B`
  }
  if (volume >= 1_000_000) {
    return `${(volume / 1_000_000).toFixed(2)}M`
  }
  if (volume >= 1_000) {
    return `${(volume / 1_000).toFixed(2)}K`
  }
  return volume.toString()
}

export const formatPercent = (value: number, decimals: number = 2): string => {
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

export const formatMarketCap = (value: number): string => {
  if (value >= 1_000_000_000_000) {
    return `$${(value / 1_000_000_000_000).toFixed(2)}T`
  }
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`
  }
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`
  }
  return `$${value.toFixed(2)}`
}

export const formatTime = (timestamp: number | Date, format: '12h' | '24h' = '12h'): string => {
  const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp
  return new Intl.DateTimeFormat('en-US', {
    hour: format === '24h' ? '2-digit' : 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: format === '12h',
  }).format(date)
}

export const formatDate = (timestamp: number | Date): string => {
  const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

export const formatDateTime = (timestamp: number | Date, format: '12h' | '24h' = '12h'): string => {
  const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: format === '24h' ? '2-digit' : 'numeric',
    minute: '2-digit',
    hour12: format === '12h',
  }).format(date)
}

export const getChangeColor = (
  value: number,
  usePositiveGreen: boolean = true
): 'text-green-500' | 'text-red-500' | 'text-neutral-400' => {
  if (value > 0) return usePositiveGreen ? 'text-green-500' : 'text-red-500'
  if (value < 0) return usePositiveGreen ? 'text-red-500' : 'text-green-500'
  return 'text-neutral-400'
}

export const getChangeBgColor = (
  value: number,
  usePositiveGreen: boolean = true
): 'bg-green-500/10' | 'bg-red-500/10' | 'bg-neutral-500/10' => {
  if (value > 0) return usePositiveGreen ? 'bg-green-500/10' : 'bg-red-500/10'
  if (value < 0) return usePositiveGreen ? 'bg-red-500/10' : 'bg-green-500/10'
  return 'bg-neutral-500/10'
}

export const getFormattedChange = (change: number, changePercent: number): string => {
  const sign = change >= 0 ? '+' : ''
  return `${sign}${formatPrice(change)} (${sign}${changePercent.toFixed(2)}%)`
}

export const getRelativeTime = (timestamp: number): string => {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`

  return formatDate(timestamp)
}
