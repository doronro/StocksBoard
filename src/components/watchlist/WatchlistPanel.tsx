import { useState, useCallback } from 'react'
import type { Quote, Watchlist } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Input } from '@components/common/Input'
import { Button } from '@components/common/Button'
import { WatchlistCard } from './WatchlistCard'
import { Badge } from '@components/common/Badge'
import { Plus, Search, RefreshCw } from 'lucide-react'
import { quoteAPI } from '@services/api'
import classNames from 'classnames'

export type TimeHorizon = 'day_trading' | 'swing' | 'position' | 'long_term'

interface WatchlistPanelProps {
  watchlist?: Watchlist
  quotes: Map<string, Quote>
  isLoading?: boolean
  onSelectSymbol?: (symbol: string) => void
  onAddToWatchlist?: (symbol: string) => void
  onRemoveFromWatchlist?: (symbol: string) => void
  onBuySymbol?: (symbol: string) => void
  onSellSymbol?: (symbol: string) => void
  selectedSymbol?: string | null
  showTechnicalDetails?: boolean
  timeHorizon?: TimeHorizon
  onTimeHorizonChange?: (horizon: TimeHorizon) => void
}

const TIME_HORIZON_FILTERS: { value: TimeHorizon; label: string; indicators: string[] }[] = [
  {
    value: 'day_trading',
    label: 'Day Trading',
    indicators: ['RSI', 'Volume', 'MACD'],
  },
  {
    value: 'swing',
    label: 'Swing Trading',
    indicators: ['SMA20/50', 'RSI', 'Support/Resistance'],
  },
  {
    value: 'position',
    label: 'Position Trading',
    indicators: ['SMA50/200', 'Bollinger Bands', 'Trend'],
  },
  {
    value: 'long_term',
    label: 'Long-Term',
    indicators: ['Fundamentals', 'Dividend', 'Growth'],
  },
]

export const WatchlistPanel: React.FC<WatchlistPanelProps> = ({
  watchlist,
  quotes,
  isLoading = false,
  onSelectSymbol,
  onAddToWatchlist,
  onRemoveFromWatchlist,
  onBuySymbol,
  onSellSymbol,
  selectedSymbol,
  showTechnicalDetails = true,
  timeHorizon = 'swing',
  onTimeHorizonChange,
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'change_percent' | 'volume' | 'name'>('change_percent')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = useCallback(async () => {
    if (!watchlist?.symbols) return

    setIsRefreshing(true)
    try {
      await quoteAPI.getQuotes(watchlist.symbols)
    } catch (error) {
      console.error('Failed to refresh watchlist quotes:', error)
    } finally {
      setIsRefreshing(false)
    }
  }, [watchlist?.symbols])

  // Filter and sort symbols
  const filteredSymbols = (watchlist?.symbols || [])
    .filter((symbol) => symbol.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      const quoteA = quotes.get(a)
      const quoteB = quotes.get(b)

      if (!quoteA || !quoteB) return 0

      switch (sortBy) {
        case 'change_percent':
          return quoteB.changePercent - quoteA.changePercent
        case 'volume':
          return quoteB.volume - quoteA.volume
        case 'name':
          return quoteA.name.localeCompare(quoteB.name)
        default:
          return 0
      }
    })

  const selectedHorizonConfig = TIME_HORIZON_FILTERS.find((h) => h.value === timeHorizon)
  const gainers = filteredSymbols.filter(
    (s) => (quotes.get(s)?.changePercent || 0) > 0
  ).length
  const losers = filteredSymbols.filter((s) => (quotes.get(s)?.changePercent || 0) < 0).length

  return (
    <Card>
      <CardHeader
        action={
          <div className="flex gap-2">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors disabled:opacity-50"
              aria-label="Refresh watchlist"
            >
              <RefreshCw
                className={classNames('w-4 h-4', isRefreshing && 'animate-spin')}
              />
            </button>
            {onAddToWatchlist && (
              <Button size="sm" variant="secondary" onClick={() => onAddToWatchlist('')}>
                <Plus className="w-4 h-4" />
                Add
              </Button>
            )}
          </div>
        }
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
              Watchlist
            </h2>
            <p className="text-xs text-neutral-600 dark:text-neutral-400">
              {watchlist?.name || 'Default'} · {filteredSymbols.length} symbols
            </p>
          </div>
        </div>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Time Horizon Filter */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
            Trading Timeframe
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {TIME_HORIZON_FILTERS.map((horizon) => (
              <button
                key={horizon.value}
                onClick={() => onTimeHorizonChange?.(horizon.value)}
                className={classNames(
                  'p-2 rounded text-xs font-medium transition-all border',
                  timeHorizon === horizon.value
                    ? 'bg-accent-600 text-white border-accent-600'
                    : 'bg-neutral-50 text-neutral-900 border-neutral-200 hover:border-neutral-300 dark:bg-neutral-700 dark:text-neutral-100 dark:border-neutral-600'
                )}
              >
                {horizon.label}
              </button>
            ))}
          </div>
          {selectedHorizonConfig && (
            <div className="flex flex-wrap gap-1">
              {selectedHorizonConfig.indicators.map((indicator) => (
                <Badge key={indicator} variant="info" size="sm">
                  {indicator}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Search */}
        <Input
          type="text"
          placeholder="Search symbols..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          icon={<Search className="w-4 h-4" />}
        />

        {/* Sort Options */}
        <div className="flex gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'change_percent' | 'volume' | 'name')}
            className="px-3 py-2 border rounded-lg bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 border-neutral-300 dark:border-neutral-600 focus:outline-none focus:ring-2 focus:ring-accent-500 dark:focus:ring-accent-400 text-sm"
          >
            <option value="change_percent">Sort by % Change</option>
            <option value="volume">Sort by Volume</option>
            <option value="name">Sort by Name</option>
          </select>
          <div className="flex gap-2 text-xs">
            <Badge variant="success" size="sm">
              {gainers} Up
            </Badge>
            <Badge variant="danger" size="sm">
              {losers} Down
            </Badge>
          </div>
        </div>

        {/* Watchlist Items */}
        {filteredSymbols.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-neutral-500 dark:text-neutral-400">
              {searchQuery ? 'No symbols match your search' : 'Add symbols to your watchlist'}
            </p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filteredSymbols.map((symbol) => (
              <WatchlistCard
                key={symbol}
                symbol={symbol}
                quote={quotes.get(symbol)}
                isLoading={isLoading}
                onSelect={onSelectSymbol}
                isSelected={selectedSymbol === symbol}
                onBuy={onBuySymbol}
                onSell={onSellSymbol}
                onRemove={onRemoveFromWatchlist}
                showTechnicalDetails={showTechnicalDetails}
              />
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  )
}
