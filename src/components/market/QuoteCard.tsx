import { TrendingUp, TrendingDown } from 'lucide-react'
import type { Quote } from '@types'
import { Card } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { formatPrice, formatPercent, formatVolume, getChangeColor } from '@utils/formatting'
import classNames from 'classnames'

interface QuoteCardProps {
  quote: Quote
  onClick?: () => void
  showDetails?: boolean
}

export const QuoteCard: React.FC<QuoteCardProps> = ({
  quote,
  onClick,
  showDetails = false,
}) => {
  const changeColor = getChangeColor(quote.change)
  const isPositive = quote.change >= 0

  return (
    <Card
      interactive={!!onClick}
      hoverable={!!onClick}
      onClick={onClick}
      className="cursor-default"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-lg text-neutral-900 dark:text-neutral-100">
              {quote.symbol}
            </h3>
            <Badge variant="info" size="sm">
              {quote.trend === 'up' ? 'Up' : quote.trend === 'down' ? 'Down' : 'Neutral'}
            </Badge>
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">{quote.name}</p>
        </div>
        <div className="text-right">
          {isPositive ? (
            <TrendingUp className="w-5 h-5 text-green-500" />
          ) : (
            <TrendingDown className="w-5 h-5 text-red-500" />
          )}
        </div>
      </div>

      {/* Price */}
      <div className="mb-4">
        <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          {formatPrice(quote.price)}
        </p>
        <p className={classNames('text-sm font-medium', changeColor)}>
          {isPositive ? '+' : ''}{formatPrice(quote.change)} ({formatPercent(quote.changePercent)})
        </p>
      </div>

      {/* Spreads */}
      <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
        <div className="bg-neutral-100 dark:bg-neutral-700 p-2 rounded">
          <p className="text-neutral-600 dark:text-neutral-400 text-xs">Bid</p>
          <p className="font-medium text-neutral-900 dark:text-neutral-100">
            {formatPrice(quote.bid)}
          </p>
        </div>
        <div className="bg-neutral-100 dark:bg-neutral-700 p-2 rounded">
          <p className="text-neutral-600 dark:text-neutral-400 text-xs">Ask</p>
          <p className="font-medium text-neutral-900 dark:text-neutral-100">
            {formatPrice(quote.ask)}
          </p>
        </div>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="space-y-2 text-sm border-t border-neutral-200 dark:border-neutral-700 pt-3">
          <div className="flex justify-between">
            <span className="text-neutral-600 dark:text-neutral-400">Volume</span>
            <span className="font-medium text-neutral-900 dark:text-neutral-100">
              {formatVolume(quote.volume)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-600 dark:text-neutral-400">Avg Volume</span>
            <span className="font-medium text-neutral-900 dark:text-neutral-100">
              {formatVolume(quote.avgVolume)}
            </span>
          </div>
          {quote.pe && (
            <div className="flex justify-between">
              <span className="text-neutral-600 dark:text-neutral-400">P/E</span>
              <span className="font-medium text-neutral-900 dark:text-neutral-100">
                {quote.pe.toFixed(2)}
              </span>
            </div>
          )}
          {quote.marketCap && (
            <div className="flex justify-between">
              <span className="text-neutral-600 dark:text-neutral-400">Market Cap</span>
              <span className="font-medium text-neutral-900 dark:text-neutral-100 text-xs">
                ${(quote.marketCap / 1e9).toFixed(2)}B
              </span>
            </div>
          )}
        </div>
      )}

      {/* Updated timestamp */}
      <div className="text-xs text-neutral-500 mt-3">
        Updated: {new Date(quote.timestamp).toLocaleTimeString()}
      </div>
    </Card>
  )
}
