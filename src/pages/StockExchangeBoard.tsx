import { useState } from 'react'
import { useMarketStore } from '@stores/market'
import { usePortfolioStore } from '@stores/portfolio'
import { useWatchlistStore } from '@stores/watchlist'
import { usePreferencesStore, type TimeHorizon, type TraderType } from '@stores/preferences'
import { useUIStore } from '@stores/ui'
import { useRealtimeQuotes } from '@hooks/useRealtimeQuotes'
import { PortfolioOverview } from '@components/portfolio/PortfolioOverview'
import { WatchlistPanel } from '@components/watchlist/WatchlistPanel'
import { CandlestickChart } from '@components/charts/CandlestickChart'
import { TechnicalIndicators } from '@components/charts/TechnicalIndicators'
import { PositionsPanel } from '@components/orders/PositionsPanel'
import { OrderPanel } from '@components/orders/OrderPanel'
import { OrderConfirmationModal } from '@components/orders/OrderConfirmationModal'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { TrendingUp, TrendingDown } from 'lucide-react'
import classNames from 'classnames'

type OrderFormData = {
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit' | 'stop_loss' | 'trailing_stop'
  quantity: number
  price?: number
  stopPrice?: number
  trailingPercent?: number
}

export const StockExchangeBoard: React.FC = () => {
  const marketStore = useMarketStore()
  const portfolioStore = usePortfolioStore()
  const watchlistStore = useWatchlistStore()
  const preferencesStore = usePreferencesStore()
  const uiStore = useUIStore()

  // State
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null)
  const [timeframe, setTimeframe] = useState<any>(preferencesStore.chart.defaultTimeframe)
  const [showOrderConfirmation, setShowOrderConfirmation] = useState(false)
  const [pendingOrder, setPendingOrder] = useState<OrderFormData | null>(null)

  // Get selected watchlist
  const selectedWatchlist = watchlistStore.getSelectedWatchlist()

  // Real-time quotes
  const symbols = selectedWatchlist?.symbols || []
  useRealtimeQuotes({
    symbols,
    enabled: symbols.length > 0,
  })

  // Build quotes map for selected watchlist
  const watchlistQuotes = new Map<string, any>()
  symbols.forEach((symbol) => {
    const quote = marketStore.getQuote(symbol)
    if (quote) {
      watchlistQuotes.set(symbol, quote)
    }
  })

  // Handle trader type change
  const handleTraderTypeChange = (type: TraderType) => {
    preferencesStore.setTraderType(type)
  }

  // Handle time horizon change
  const handleTimeHorizonChange = (horizon: TimeHorizon) => {
    preferencesStore.setTimeHorizon(horizon)
  }

  // Handle symbol selection
  const handleSelectSymbol = (symbol: string) => {
    setSelectedSymbol(symbol)
    marketStore.setSelectedSymbol(symbol)
  }

  // Handle order placement
  const handlePlaceOrder = (orderData: OrderFormData) => {
    setPendingOrder(orderData)
    setShowOrderConfirmation(true)
  }

  // Confirm order
  const handleConfirmOrder = async () => {
    if (!pendingOrder) return

    try {
      // Submit order to API
      console.log('Order submitted:', pendingOrder)
      uiStore.addNotification({
        type: 'success',
        message: `${pendingOrder.side.toUpperCase()} order placed for ${pendingOrder.symbol}`,
        timestamp: Date.now(),
      })

      setShowOrderConfirmation(false)
      setPendingOrder(null)
      uiStore.setShowOrderPanel(false)
    } catch (error) {
      console.error('Failed to place order:', error)
      uiStore.addNotification({
        type: 'error',
        message: 'Failed to place order',
        timestamp: Date.now(),
      })
    }
  }

  // Get trader type label
  const getTraderTypeLabel = (type: TraderType): string => {
    const labels: Record<TraderType, string> = {
      day_trader: 'Day Trader',
      swing_trader: 'Swing Trader',
      value_investor: 'Value Investor',
      institutional: 'Institutional',
    }
    return labels[type]
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Header */}
      <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 sticky top-0 z-40">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              Stock Exchange Board
            </h1>
            <Badge variant="info" size="sm">
              {getTraderTypeLabel(preferencesStore.traderType)}
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            {marketStore.marketStatus === 'open' && (
              <div className="flex items-center gap-2 text-sm">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-neutral-600 dark:text-neutral-400">Market Open</span>
              </div>
            )}
            <button
              onClick={() => uiStore.toggleTheme()}
              className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            >
              {uiStore.theme === 'dark' ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* Trader Type Selector */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
              Trading Profile
            </h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {[
                { value: 'day_trader', label: 'Day Trading' },
                { value: 'swing_trader', label: 'Swing Trading' },
                { value: 'value_investor', label: 'Value Investing' },
                { value: 'institutional', label: 'Institutional' },
              ].map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleTraderTypeChange(type.value as TraderType)}
                  className={classNames(
                    'p-3 rounded-lg border-2 transition-all text-sm font-medium',
                    preferencesStore.traderType === type.value
                      ? 'border-accent-600 bg-accent-50 dark:bg-accent-900/30 text-accent-600'
                      : 'border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
                  )}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Portfolio Overview */}
        <PortfolioOverview
          portfolio={portfolioStore.portfolio}
          isLoading={portfolioStore.isLoading}
        />

        {/* Main Grid - Watchlist and Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Watchlist - Left Column */}
          <div className="lg:col-span-1">
            <WatchlistPanel
              watchlist={selectedWatchlist}
              quotes={watchlistQuotes}
              selectedSymbol={selectedSymbol}
              onSelectSymbol={handleSelectSymbol}
              onTimeHorizonChange={handleTimeHorizonChange}
              timeHorizon={preferencesStore.timeHorizon}
              showTechnicalDetails={true}
              onBuySymbol={(symbol) => {
                setSelectedSymbol(symbol)
                uiStore.setShowOrderPanel(true)
              }}
              onSellSymbol={(symbol) => {
                setSelectedSymbol(symbol)
                uiStore.setShowOrderPanel(true)
              }}
            />
          </div>

          {/* Chart and Indicators - Right Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Chart */}
            <CandlestickChart
              data={[]}
              timeframe={timeframe as any}
              onTimeframeChange={setTimeframe}
              isLoading={false}
            />

            {/* Technical Indicators */}
            {selectedSymbol && (
              <TechnicalIndicators
                indicators={null}
                isLoading={false}
                symbol={selectedSymbol}
              />
            )}
          </div>
        </div>

        {/* Positions and Orders */}
        <PositionsPanel
          holdings={portfolioStore.holdings}
          orders={portfolioStore.orders}
          isLoading={portfolioStore.isLoading}
          onClosePosition={(symbol) => {
            uiStore.addNotification({
              type: 'info',
              message: `Closing position for ${symbol}`,
              timestamp: Date.now(),
            })
          }}
          onCancelOrder={(orderId) => {
            portfolioStore.removeOrder(orderId)
            uiStore.addNotification({
              type: 'success',
              message: 'Order cancelled',
              timestamp: Date.now(),
            })
          }}
        />

        {/* Market Indices Summary */}
        {marketStore.indices.length > 0 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                Market Indices
              </h2>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {marketStore.indices.slice(0, 3).map((index) => (
                  <div
                    key={index.symbol}
                    className="p-3 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg"
                  >
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {index.name}
                    </p>
                    <p className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                      {index.value.toFixed(2)}
                    </p>
                    <div className="flex items-center gap-1 mt-1">
                      {index.change >= 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span
                        className={index.change >= 0 ? 'text-green-600' : 'text-red-600'}
                      >
                        {index.change > 0 ? '+' : ''}{index.changePercent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}
      </main>

      {/* Order Panel Modal */}
      {uiStore.showOrderPanel && (
        <OrderPanel
          onClose={() => uiStore.setShowOrderPanel(false)}
          onSubmit={handlePlaceOrder}
        />
      )}

      {/* Order Confirmation Modal */}
      {showOrderConfirmation && pendingOrder && (
        <OrderConfirmationModal
          order={pendingOrder}
          quote={selectedSymbol ? marketStore.getQuote(selectedSymbol) : undefined}
          availableBuyingPower={100000} // Mock value
          onConfirm={handleConfirmOrder}
          onCancel={() => {
            setShowOrderConfirmation(false)
            setPendingOrder(null)
          }}
          isSubmitting={false}
        />
      )}
    </div>
  )
}
