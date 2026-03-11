/**
 * Market Dashboard Component
 * Displays market overview with indices, top movers, and sector performance
 */

import { useMemo } from 'react'
import type { Quote, MarketIndex, SectorPerformance, MarketStatus } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { TrendingUp, TrendingDown, Activity, Zap } from 'lucide-react'
import { formatPrice, formatPercent, formatVolume } from '@utils/formatting'
import classNames from 'classnames'

interface MarketDashboardProps {
  indices?: MarketIndex[]
  quotes?: Map<string, Quote>
  sectors?: SectorPerformance[]
  marketStatus?: MarketStatus
  isLoading?: boolean
  onQuoteClick?: (symbol: string) => void
}

export const MarketDashboard: React.FC<MarketDashboardProps> = ({
  indices = [],
  quotes = new Map(),
  sectors = [],
  marketStatus = 'closed',
  isLoading = false,
  onQuoteClick,
}) => {
  // Get top gainers and losers
  const { gainers, losers } = useMemo(() => {
    const quotesArray = Array.from(quotes.values()).sort((a, b) => {
      return Math.abs(b.changePercent) - Math.abs(a.changePercent)
    })

    const gainers = quotesArray
      .filter(q => q.changePercent > 0)
      .slice(0, 5)
    const losers = quotesArray
      .filter(q => q.changePercent < 0)
      .slice(0, 5)

    return { gainers, losers }
  }, [quotes])

  // Get top sectors
  const topSectors = useMemo(() => {
    return [...sectors].sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent))
  }, [sectors])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map(i => (
          <Card key={i}>
            <CardBody>
              <div className="animate-pulse h-40 bg-neutral-100 dark:bg-neutral-700 rounded-lg" />
            </CardBody>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Market Indices */}
      {indices.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Market Indices
              </h3>
              <div className={classNames(
                'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium',
                marketStatus === 'open'
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                  : marketStatus === 'pre_market'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
              )}>
                <span className={classNames(
                  'w-2 h-2 rounded-full',
                  marketStatus === 'open'
                    ? 'bg-green-500 animate-pulse'
                    : marketStatus === 'pre_market'
                    ? 'bg-blue-500 animate-pulse'
                    : 'bg-neutral-400'
                )} />
                {marketStatus === 'open'
                  ? 'Market Open'
                  : marketStatus === 'pre_market'
                  ? 'Pre-Market'
                  : marketStatus === 'after_hours'
                  ? 'After Hours'
                  : 'Market Closed'}
              </div>
            </div>
          </CardHeader>

          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {indices.map(index => (
                <div
                  key={index.symbol}
                  className="p-4 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg border border-neutral-200 dark:border-neutral-700"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400 uppercase tracking-wide">
                        {index.name}
                      </p>
                      <h4 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                        {formatPrice(index.value)}
                      </h4>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {index.change >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-600 dark:text-red-400" />
                    )}
                    <span
                      className={classNames(
                        'font-medium',
                        index.change >= 0
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-600 dark:text-red-400'
                      )}
                    >
                      {index.change >= 0 ? '+' : ''}{formatPrice(index.change)}
                    </span>
                    <span
                      className={classNames(
                        'text-sm font-medium',
                        index.change >= 0
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-600 dark:text-red-400'
                      )}
                    >
                      ({formatPercent(index.changePercent)})
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Gainers and Losers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Top Gainers
            </h3>
          </CardHeader>

          <CardBody>
            {gainers.length === 0 ? (
              <p className="text-center text-neutral-500 py-4 text-sm">No gainers available</p>
            ) : (
              <div className="space-y-2">
                {gainers.map(quote => (
                  <button
                    key={quote.symbol}
                    onClick={() => onQuoteClick?.(quote.symbol)}
                    className="w-full p-3 rounded-lg bg-neutral-50 dark:bg-neutral-800/50 hover:bg-neutral-100 dark:hover:bg-neutral-700/50 border border-neutral-200 dark:border-neutral-700 transition-colors text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                          {quote.symbol}
                        </h4>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          {formatPrice(quote.price)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600 dark:text-green-400">
                          +{formatPercent(quote.changePercent)}
                        </p>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          Vol: {formatVolume(quote.volume)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Top Losers */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-red-600" />
              Top Losers
            </h3>
          </CardHeader>

          <CardBody>
            {losers.length === 0 ? (
              <p className="text-center text-neutral-500 py-4 text-sm">No losers available</p>
            ) : (
              <div className="space-y-2">
                {losers.map(quote => (
                  <button
                    key={quote.symbol}
                    onClick={() => onQuoteClick?.(quote.symbol)}
                    className="w-full p-3 rounded-lg bg-neutral-50 dark:bg-neutral-800/50 hover:bg-neutral-100 dark:hover:bg-neutral-700/50 border border-neutral-200 dark:border-neutral-700 transition-colors text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                          {quote.symbol}
                        </h4>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          {formatPrice(quote.price)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-red-600 dark:text-red-400">
                          {formatPercent(quote.changePercent)}
                        </p>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          Vol: {formatVolume(quote.volume)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Sector Performance */}
      {topSectors.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Sector Performance
            </h3>
          </CardHeader>

          <CardBody>
            <div className="space-y-3">
              {topSectors.map(sector => (
                <div key={sector.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">
                      {sector.name}
                    </h4>
                    <span className={classNames(
                      'font-bold',
                      sector.changePercent >= 0
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-red-600 dark:text-red-400'
                    )}>
                      {sector.changePercent >= 0 ? '+' : ''}{formatPercent(sector.changePercent)}
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                    <div
                      className={classNames(
                        'h-full transition-all duration-300',
                        sector.changePercent >= 0
                          ? 'bg-green-500'
                          : 'bg-red-500'
                      )}
                      style={{
                        width: `${Math.min(Math.abs(sector.changePercent) * 5, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
