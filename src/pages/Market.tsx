import { useState, useEffect } from 'react'
import { useMarketStore } from '@stores/market'
import { useWatchlistStore } from '@stores/watchlist'
import { useUIStore } from '@stores/ui'
import { QuoteCard } from '@components/market/QuoteCard'
import { MarketIndices } from '@components/market/MarketIndices'
import { SectorHeatmap } from '@components/market/SectorHeatmap'
import { EarningsCalendar } from '@components/calendar/EarningsCalendar'
import { AlertManager } from '@components/alerts/AlertManager'
import { generateMockEvents, generateMockAlerts } from '@services/mockData'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Input, Select } from '@components/common/Input'
import { Button } from '@components/common/Button'
import { Search, RotateCw } from 'lucide-react'

export const Market: React.FC = () => {
  const marketStore = useMarketStore()
  const watchlistStore = useWatchlistStore()
  const { setShowOrderPanel, addNotification } = useUIStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'price' | 'change' | 'volume'>('price')
  const [isLoading, setIsLoading] = useState(true)
  const [events, setEvents] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
      setEvents(generateMockEvents())
      setAlerts(generateMockAlerts())
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const selectedWatchlist = watchlistStore.getSelectedWatchlist()
  const watchlistSymbols = selectedWatchlist?.symbols || []

  const quotes = Array.from(marketStore.quotes.values())

  const filteredQuotes = quotes
    .filter((q) =>
      q.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      q.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'price':
          return b.price - a.price
        case 'change':
          return b.changePercent - a.changePercent
        case 'volume':
          return b.volume - a.volume
        default:
          return 0
      }
    })

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
          Market Data
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Real-time stock quotes and market overview
        </p>
      </div>

      {/* Indices & Sectors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MarketIndices indices={marketStore.indices} />
        <SectorHeatmap sectors={marketStore.sectors} />
      </div>

      {/* Search & Filter */}
      <Card>
        <CardBody className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              type="search"
              placeholder="Search by symbol or company name..."
              value={searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
              icon={<Search className="w-4 h-4" />}
            />
          </div>
          <Select
            options={[
              { value: 'price' as const, label: 'Sort by Price' },
              { value: 'change' as const, label: 'Sort by Change' },
              { value: 'volume' as const, label: 'Sort by Volume' },
            ]}
            value={sortBy}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSortBy(e.target.value as 'price' | 'change' | 'volume')}
            className="sm:max-w-xs"
          />
          <Button
            variant="secondary"
            size="md"
            icon={<RotateCw className="w-4 h-4" />}
            onClick={() => {
              // Refresh market data
            }}
          >
            Refresh
          </Button>
        </CardBody>
      </Card>

      {/* Quotes Grid */}
      <div className="space-y-2">
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Market Quotes ({filteredQuotes.length})
        </h2>
        {filteredQuotes.length === 0 ? (
          <Card>
            <CardBody>
              <p className="text-center text-neutral-500 py-8">
                No quotes found. Try searching for a different symbol.
              </p>
            </CardBody>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredQuotes.map((quote) => (
              <QuoteCard
                key={quote.symbol}
                quote={quote}
                showDetails={true}
                onClick={() => {
                  marketStore.setSelectedSymbol(quote.symbol)
                  setShowOrderPanel(true)
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Market Statistics */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Market Breadth
          </h2>
        </CardHeader>
        <CardBody>
          {marketStore.breadth ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                  Advancing
                </p>
                <p className="text-2xl font-bold text-green-500">
                  {marketStore.breadth.advancing}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                  Declining
                </p>
                <p className="text-2xl font-bold text-red-500">
                  {marketStore.breadth.declining}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                  Unchanged
                </p>
                <p className="text-2xl font-bold text-neutral-500">
                  {marketStore.breadth.unchanged}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                  VIX Level
                </p>
                <p className="text-2xl font-bold text-accent-600">
                  {marketStore.breadth.vixLevel.toFixed(2)}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-center text-neutral-500">Market breadth data unavailable</p>
          )}
        </CardBody>
      </Card>

      {/* Earnings Calendar & Alerts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Calendar */}
        <div className="lg:col-span-2">
          <EarningsCalendar
            events={events}
            isLoading={isLoading}
            watchlistSymbols={watchlistSymbols}
            onEventClick={(event) => {
              addNotification({
                type: 'info',
                message: `${event.symbol}: ${event.title}`,
                timestamp: Date.now(),
              })
            }}
          />
        </div>

        {/* Right Column - Alerts */}
        <div>
          <AlertManager
            alerts={alerts}
            isLoading={isLoading}
            watchlistSymbols={watchlistSymbols}
            onCreateAlert={(symbol) => {
              addNotification({
                type: 'success',
                message: `Alert created for ${symbol}`,
                timestamp: Date.now(),
              })
            }}
            onDeleteAlert={(alertId) => {
              setAlerts(alerts.filter(a => a.id !== alertId))
              addNotification({
                type: 'success',
                message: 'Alert deleted',
                timestamp: Date.now(),
              })
            }}
            onToggleAlert={(alertId, isActive) => {
              setAlerts(
                alerts.map(a =>
                  a.id === alertId ? { ...a, isActive } : a
                )
              )
            }}
          />
        </div>
      </div>
    </div>
  )
}
