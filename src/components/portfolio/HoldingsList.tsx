import { useState } from 'react'
import type { Holding } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { formatPrice, formatPercent, getChangeColor } from '@utils/formatting'
import { ChevronDown, ChevronUp } from 'lucide-react'
import classNames from 'classnames'

interface HoldingsListProps {
  holdings: Holding[]
  isLoading?: boolean
  onSelectHolding?: (holding: Holding) => void
}

export const HoldingsList: React.FC<HoldingsListProps> = ({
  holdings,
  isLoading = false,
  onSelectHolding,
}) => {
  const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null)

  if (isLoading) {
    return (
      <Card>
        <div className="h-32 flex items-center justify-center">
          <div className="animate-pulse text-neutral-500">Loading holdings...</div>
        </div>
      </Card>
    )
  }

  if (holdings.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Holdings
          </h2>
        </CardHeader>
        <CardBody>
          <p className="text-center text-neutral-500">No holdings yet. Start trading to build your portfolio.</p>
        </CardBody>
      </Card>
    )
  }

  const sortedHoldings = [...holdings].sort((a, b) => b.currentValue - a.currentValue)

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Holdings
        </h2>
      </CardHeader>
      <CardBody className="space-y-2">
        {sortedHoldings.map((holding) => {
          const isPositive = holding.pnl >= 0
          const isExpanded = expandedSymbol === holding.symbol

          return (
            <div key={holding.symbol}>
              <button
                onClick={() => {
                  setExpandedSymbol(isExpanded ? null : holding.symbol)
                  onSelectHolding?.(holding)
                }}
                className="w-full p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors flex items-center justify-between"
              >
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                      {holding.symbol}
                    </h4>
                    <Badge
                      variant={isPositive ? 'success' : 'danger'}
                      size="sm"
                    >
                      {holding.quantity} units
                    </Badge>
                  </div>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    {holding.name}
                  </p>
                </div>

                <div className="text-right mr-2">
                  <p className="font-bold text-neutral-900 dark:text-neutral-100">
                    {formatPrice(holding.currentValue)}
                  </p>
                  <p className={classNames('text-sm font-medium', getChangeColor(holding.pnl))}>
                    {isPositive ? '+' : ''}{formatPrice(holding.pnl)} ({formatPercent(holding.pnlPercent)})
                  </p>
                </div>

                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-neutral-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-neutral-500" />
                )}
              </button>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="bg-neutral-50 dark:bg-neutral-700/30 p-3 rounded-b-lg border-t border-neutral-200 dark:border-neutral-700 space-y-2 text-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">Current Price</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {formatPrice(holding.currentPrice)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">Average Price</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {formatPrice(holding.averagePrice)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">Total Cost</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {formatPrice(holding.totalCost)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">Current Value</p>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {formatPrice(holding.currentValue)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </CardBody>
    </Card>
  )
}
