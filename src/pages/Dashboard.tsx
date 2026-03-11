import { useEffect, useState } from 'react'
import { useMarketStore } from '@stores/market'
import { usePortfolioStore } from '@stores/portfolio'
import { useUIStore } from '@stores/ui'
import { PortfolioOverview } from '@components/portfolio/PortfolioOverview'
import { MarketIndices } from '@components/market/MarketIndices'
import { SectorHeatmap } from '@components/market/SectorHeatmap'
import { HoldingsList } from '@components/portfolio/HoldingsList'
import { OrdersList } from '@components/orders/OrdersList'
import { CandlestickChart } from '@components/charts/CandlestickChart'
import { Card } from '@components/common/Card'
import { Button } from '@components/common/Button'
import { Plus } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const marketStore = useMarketStore()
  const portfolioStore = usePortfolioStore()
  const { setShowOrderPanel } = useUIStore()

  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setIsLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
            Dashboard
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Welcome back to your trading platform
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          icon={<Plus className="w-5 h-5" />}
          onClick={() => setShowOrderPanel(true)}
        >
          Place Order
        </Button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Portfolio & Holdings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Portfolio Overview */}
          <PortfolioOverview
            portfolio={portfolioStore.portfolio}
            isLoading={isLoading}
          />

          {/* Chart */}
          <CandlestickChart
            data={[]}
            timeframe="1d"
            isLoading={isLoading}
          />

          {/* Holdings */}
          <HoldingsList
            holdings={portfolioStore.holdings}
            isLoading={isLoading}
            onSelectHolding={(holding) => portfolioStore.setSelectedHolding(holding)}
          />
        </div>

        {/* Right Column - Market Info & Orders */}
        <div className="space-y-6">
          {/* Market Indices */}
          <MarketIndices
            indices={marketStore.indices}
            isLoading={isLoading}
          />

          {/* Sector Heatmap */}
          <SectorHeatmap
            sectors={marketStore.sectors}
            isLoading={isLoading}
          />

          {/* Orders */}
          <OrdersList
            orders={portfolioStore.orders}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <div className="space-y-1">
            <p className="text-xs text-neutral-600 dark:text-neutral-400">Watchlists</p>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">3</p>
          </div>
        </Card>
        <Card>
          <div className="space-y-1">
            <p className="text-xs text-neutral-600 dark:text-neutral-400">Pending Orders</p>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              {portfolioStore.getPendingOrders().length}
            </p>
          </div>
        </Card>
        <Card>
          <div className="space-y-1">
            <p className="text-xs text-neutral-600 dark:text-neutral-400">Price Alerts</p>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">5</p>
          </div>
        </Card>
        <Card>
          <div className="space-y-1">
            <p className="text-xs text-neutral-600 dark:text-neutral-400">Market Status</p>
            <p className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
              {marketStore.marketStatus === 'open' ? (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Open
                </span>
              ) : (
                <span className="text-neutral-600">Closed</span>
              )}
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
