import { useState } from 'react'
import type { Quote } from '@types'
import { Button } from '@components/common/Button'
import { formatPrice, formatPercent, formatVolume, getChangeColor } from '@utils/formatting'
import { TrendingUp, TrendingDown, X } from 'lucide-react'
import classNames from 'classnames'

interface WatchlistCardProps {
  symbol: string
  quote?: Quote
  isLoading?: boolean
  onBuy?: (symbol: string) => void
  onSell?: (symbol: string) => void
  onRemove?: (symbol: string) => void
  onSelect?: (symbol: string) => void
  isSelected?: boolean
  showTechnicalDetails?: boolean
}

export const WatchlistCard: React.FC<WatchlistCardProps> = ({
  symbol,
  quote,
  isLoading = false,
  onBuy,
  onSell,
  onRemove,
  onSelect,
  isSelected = false,
  showTechnicalDetails = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (isLoading || !quote) {
    return (
      <div className="p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg animate-pulse h-20" />
    )
  }

  const isPositive = quote.change >= 0
  const trend = quote.trend

  return (
    <div
      className={classNames(
        'p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-all border-l-4',
        isSelected ? 'border-l-accent-600' : 'border-l-transparent',
        isPositive ? 'border-t border-r border-b border-green-500/20' : 'border-t border-r border-b border-red-500/20'
      )}
    >
      {/* Main Row */}
      <div
        className="flex items-center justify-between gap-3 cursor-pointer"
        onClick={() => {
          setIsExpanded(!isExpanded)
          onSelect?.(symbol)
        }}
      >
        {/* Symbol and Name */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-bold text-neutral-900 dark:text-neutral-100 text-sm">
              {symbol}
            </h4>
            {trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}
            {trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
          </div>
          <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate">
            {quote.name}
          </p>
        </div>

        {/* Price and Change */}
        <div className="text-right">
          <p className="font-bold text-neutral-900 dark:text-neutral-100 text-sm">
            {formatPrice(quote.price)}
          </p>
          <p className={classNames('text-xs font-medium', getChangeColor(quote.change))}>
            {quote.change > 0 ? '+' : ''}{formatPrice(quote.change)}
          </p>
        </div>

        {/* Change Percent */}
        <div
          className={classNames(
            'px-2 py-1 rounded text-xs font-medium min-w-[60px] text-center',
            isPositive
              ? 'bg-green-500/10 text-green-600 dark:text-green-400'
              : 'bg-red-500/10 text-red-600 dark:text-red-400'
          )}
        >
          {quote.changePercent > 0 ? '+' : ''}{formatPercent(quote.changePercent)}
        </div>

        {/* Remove Button */}
        {onRemove && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onRemove(symbol)
            }}
            className="p-1 text-neutral-400 hover:text-red-500 transition-colors"
            aria-label={`Remove ${symbol} from watchlist`}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700 space-y-3">
          {/* Volume and Market Data */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p className="text-neutral-600 dark:text-neutral-400">Volume</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatVolume(quote.volume)}
              </p>
            </div>
            <div>
              <p className="text-neutral-600 dark:text-neutral-400">Avg Volume</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatVolume(quote.avgVolume)}
              </p>
            </div>
            <div>
              <p className="text-neutral-600 dark:text-neutral-400">Bid</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatPrice(quote.bid)}
              </p>
            </div>
            <div>
              <p className="text-neutral-600 dark:text-neutral-400">Ask</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatPrice(quote.ask)}
              </p>
            </div>
          </div>

          {/* Technical Indicators (if available) */}
          {showTechnicalDetails && quote.pe !== undefined && (
            <div className="grid grid-cols-2 gap-3 text-xs border-t border-neutral-200 dark:border-neutral-700 pt-3">
              {quote.pe !== undefined && (
                <div>
                  <p className="text-neutral-600 dark:text-neutral-400">P/E Ratio</p>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {quote.pe.toFixed(2)}
                  </p>
                </div>
              )}
              {quote.eps !== undefined && (
                <div>
                  <p className="text-neutral-600 dark:text-neutral-400">EPS</p>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {formatPrice(quote.eps)}
                  </p>
                </div>
              )}
              {quote.high52w !== undefined && (
                <div>
                  <p className="text-neutral-600 dark:text-neutral-400">52W High</p>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {formatPrice(quote.high52w)}
                  </p>
                </div>
              )}
              {quote.low52w !== undefined && (
                <div>
                  <p className="text-neutral-600 dark:text-neutral-400">52W Low</p>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {formatPrice(quote.low52w)}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2 border-t border-neutral-200 dark:border-neutral-700">
            {onBuy && (
              <Button
                size="sm"
                variant="success"
                fullWidth
                onClick={() => onBuy(symbol)}
              >
                Buy
              </Button>
            )}
            {onSell && (
              <Button
                size="sm"
                variant="danger"
                fullWidth
                onClick={() => onSell(symbol)}
              >
                Sell
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
