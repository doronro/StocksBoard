import type { Portfolio } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { formatCurrency, formatPercent, getChangeColor } from '@utils/formatting'
import classNames from 'classnames'

interface PortfolioOverviewProps {
  portfolio: Portfolio | null
  isLoading?: boolean
}

export const PortfolioOverview: React.FC<PortfolioOverviewProps> = ({
  portfolio,
  isLoading = false,
}) => {
  if (isLoading || !portfolio) {
    return (
      <Card>
        <div className="h-40 flex items-center justify-center">
          <div className="animate-pulse text-neutral-500">Loading portfolio...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Portfolio Summary
        </h2>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* Total Value */}
        <div className="space-y-1">
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Portfolio Value</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
            {formatCurrency(portfolio.totalValue)}
          </p>
        </div>

        {/* Daily P&L */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-neutral-50 dark:bg-neutral-700/50 p-3 rounded-lg">
            <p className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Daily P&L</p>
            <p className={classNames('text-lg font-bold', getChangeColor(portfolio.dayPnL))}>
              {formatCurrency(portfolio.dayPnL)}
            </p>
            <p className={classNames('text-xs font-medium', getChangeColor(portfolio.dayPnLPercent))}>
              {formatPercent(portfolio.dayPnLPercent)}
            </p>
          </div>

          <div className="bg-neutral-50 dark:bg-neutral-700/50 p-3 rounded-lg">
            <p className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Unrealized Gain</p>
            <p
              className={classNames(
                'text-lg font-bold',
                getChangeColor(portfolio.unrealizedGain)
              )}
            >
              {formatCurrency(portfolio.unrealizedGain)}
            </p>
            <p
              className={classNames(
                'text-xs font-medium',
                getChangeColor(portfolio.unrealizedGainPercent)
              )}
            >
              {formatPercent(portfolio.unrealizedGainPercent)}
            </p>
          </div>
        </div>

        {/* Cost & Holdings */}
        <div className="border-t border-neutral-200 dark:border-neutral-700 pt-3">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-neutral-600 dark:text-neutral-400">Total Cost</span>
            <span className="font-medium text-neutral-900 dark:text-neutral-100">
              {formatCurrency(portfolio.totalCost)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-neutral-600 dark:text-neutral-400">Holdings</span>
            <Badge variant={portfolio.holdings.length > 0 ? 'info' : 'default'} size="sm">
              {portfolio.holdings.length} position{portfolio.holdings.length !== 1 ? 's' : ''}
            </Badge>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}
