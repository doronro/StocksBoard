import { useState } from 'react'
import type { Holding, Order } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Button } from '@components/common/Button'
import { Badge } from '@components/common/Badge'
import { formatPrice, formatPercent, formatTime, getChangeColor } from '@utils/formatting'
import { ChevronDown, ChevronUp, Edit2, TrendingUp, TrendingDown } from 'lucide-react'
import classNames from 'classnames'

interface PositionsPanelProps {
  holdings: Holding[]
  orders: Order[]
  isLoading?: boolean
  onClosePosition?: (symbol: string) => void
  onModifyOrder?: (orderId: string) => void
  onCancelOrder?: (orderId: string) => void
}

export const PositionsPanel: React.FC<PositionsPanelProps> = ({
  holdings,
  orders,
  onClosePosition,
  onModifyOrder,
  onCancelOrder,
}) => {
  const [activeTab, setActiveTab] = useState<'positions' | 'pending' | 'history'>('positions')
  const [expandedHolding, setExpandedHolding] = useState<string | null>(null)

  const pendingOrders = orders.filter((o) => o.status === 'pending')
  const filledOrders = orders.filter((o) => o.status === 'filled')

  const totalPositionValue = holdings.reduce((sum, h) => sum + h.currentValue, 0)
  const totalPositionCost = holdings.reduce((sum, h) => sum + h.totalCost, 0)
  const totalPnL = totalPositionValue - totalPositionCost

  return (
    <Card>
      <CardHeader>
        <div>
          <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Positions & Orders
          </h3>
          <p className="text-xs text-neutral-600 dark:text-neutral-400">
            {holdings.length} positions, {pendingOrders.length} pending orders
          </p>
        </div>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-neutral-200 dark:border-neutral-700">
          {[
            { id: 'positions', label: `Positions (${holdings.length})` },
            { id: 'pending', label: `Pending (${pendingOrders.length})` },
            { id: 'history', label: `History (${filledOrders.length})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={classNames(
                'px-3 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === tab.id
                  ? 'border-accent-600 text-accent-600'
                  : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200'
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Positions Tab */}
        {activeTab === 'positions' && (
          <div className="space-y-3">
            {holdings.length === 0 ? (
              <p className="text-center text-neutral-500 py-4">No open positions</p>
            ) : (
              <>
                {/* Portfolio Summary */}
                <div className="grid grid-cols-3 gap-2 p-3 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg text-xs">
                  <div>
                    <p className="text-neutral-600 dark:text-neutral-400">Total Value</p>
                    <p className="font-bold text-neutral-900 dark:text-neutral-100">
                      {formatPrice(totalPositionValue)}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-600 dark:text-neutral-400">Total Cost</p>
                    <p className="font-bold text-neutral-900 dark:text-neutral-100">
                      {formatPrice(totalPositionCost)}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-600 dark:text-neutral-400">Total P&L</p>
                    <p
                      className={classNames(
                        'font-bold',
                        totalPnL >= 0
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-600 dark:text-red-400'
                      )}
                    >
                      {totalPnL >= 0 ? '+' : ''}{formatPrice(totalPnL)}
                    </p>
                  </div>
                </div>

                {/* Individual Positions */}
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {holdings.map((holding) => {
                    const isExpanded = expandedHolding === holding.symbol
                    const isPositive = holding.pnl >= 0

                    return (
                      <div key={holding.symbol} className="border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden">
                        <button
                          onClick={() =>
                            setExpandedHolding(isExpanded ? null : holding.symbol)
                          }
                          className="w-full p-3 flex items-center justify-between hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
                        >
                          <div className="flex-1 text-left">
                            <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                              {holding.symbol}
                            </h4>
                            <p className="text-xs text-neutral-600 dark:text-neutral-400">
                              {holding.quantity} units @ {formatPrice(holding.averagePrice)}
                            </p>
                          </div>

                          <div className="text-right mr-2">
                            <p className="font-bold text-neutral-900 dark:text-neutral-100">
                              {formatPrice(holding.currentValue)}
                            </p>
                            <p className={classNames('text-sm', getChangeColor(holding.pnl))}>
                              {isPositive ? '+' : ''}{formatPrice(holding.pnl)}
                            </p>
                          </div>

                          <div
                            className={classNames(
                              'px-2 py-1 rounded text-xs font-medium',
                              isPositive
                                ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                                : 'bg-red-500/10 text-red-600 dark:text-red-400'
                            )}
                          >
                            {isPositive ? '+' : ''}{formatPercent(holding.pnlPercent)}
                          </div>

                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-neutral-500" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-neutral-500" />
                          )}
                        </button>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <div className="bg-neutral-50 dark:bg-neutral-700/30 p-3 border-t border-neutral-200 dark:border-neutral-700 space-y-3">
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div>
                                <p className="text-neutral-600 dark:text-neutral-400">
                                  Current Price
                                </p>
                                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                  {formatPrice(holding.currentPrice)}
                                </p>
                              </div>
                              <div>
                                <p className="text-neutral-600 dark:text-neutral-400">
                                  Entry Price
                                </p>
                                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                  {formatPrice(holding.averagePrice)}
                                </p>
                              </div>
                              <div>
                                <p className="text-neutral-600 dark:text-neutral-400">
                                  Gain/Loss
                                </p>
                                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                  {isPositive ? '+' : ''}{formatPrice(holding.pnl)}
                                </p>
                              </div>
                              <div>
                                <p className="text-neutral-600 dark:text-neutral-400">
                                  Return %
                                </p>
                                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                  {isPositive ? '+' : ''}{formatPercent(holding.pnlPercent)}
                                </p>
                              </div>
                            </div>

                            <Button
                              size="sm"
                              variant="danger"
                              fullWidth
                              onClick={() => onClosePosition?.(holding.symbol)}
                            >
                              Close Position
                            </Button>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </>
            )}
          </div>
        )}

        {/* Pending Orders Tab */}
        {activeTab === 'pending' && (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {pendingOrders.length === 0 ? (
              <p className="text-center text-neutral-500 py-4">No pending orders</p>
            ) : (
              pendingOrders.map((order) => (
                <div
                  key={order.id}
                  className="p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg space-y-2"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                        {order.symbol}
                      </h4>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">
                        {order.type.replace('_', ' ').toUpperCase()} ORDER
                      </p>
                    </div>
                    <Badge
                      variant={order.side === 'buy' ? 'success' : 'danger'}
                      size="sm"
                    >
                      {order.side.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <p className="text-neutral-600 dark:text-neutral-400">Quantity</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {order.quantity} / {order.filledQuantity} filled
                      </p>
                    </div>
                    <div>
                      <p className="text-neutral-600 dark:text-neutral-400">Price</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {order.price ? formatPrice(order.price) : 'Market'}
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    Created: {formatTime(order.createdAt)}
                  </p>

                  <div className="flex gap-2">
                    {onModifyOrder && (
                      <Button
                        size="sm"
                        variant="secondary"
                        fullWidth
                        onClick={() => onModifyOrder(order.id)}
                      >
                        <Edit2 className="w-3 h-3" />
                        Modify
                      </Button>
                    )}
                    {onCancelOrder && (
                      <Button
                        size="sm"
                        variant="danger"
                        fullWidth
                        onClick={() => onCancelOrder(order.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Trade History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {filledOrders.length === 0 ? (
              <p className="text-center text-neutral-500 py-4">No trade history</p>
            ) : (
              filledOrders.slice(0, 10).map((order) => (
                <div
                  key={order.id}
                  className="p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {order.side === 'buy' ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span className="font-bold text-neutral-900 dark:text-neutral-100">
                        {order.symbol}
                      </span>
                    </div>
                    <span className="text-neutral-600 dark:text-neutral-400">
                      {formatTime(order.completedAt || order.updatedAt)}
                    </span>
                  </div>
                  <p className="text-neutral-600 dark:text-neutral-400">
                    {order.side === 'buy' ? 'Bought' : 'Sold'} {order.filledQuantity} @ {order.price ? formatPrice(order.price) : 'Market'}
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </CardBody>
    </Card>
  )
}
