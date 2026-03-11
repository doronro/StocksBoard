import type { MarketIndex } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { formatPrice, formatPercent, getChangeColor } from '@utils/formatting'
import { TrendingUp, TrendingDown } from 'lucide-react'
import classNames from 'classnames'

interface MarketIndicesProps {
  indices: MarketIndex[]
  isLoading?: boolean
}

export const MarketIndices: React.FC<MarketIndicesProps> = ({ indices, isLoading = false }) => {
  if (isLoading) {
    return (
      <Card>
        <div className="h-32 flex items-center justify-center">
          <div className="animate-pulse text-neutral-500">Loading indices...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Market Indices
        </h2>
      </CardHeader>
      <CardBody className="space-y-3">
        {indices.map((index) => {
          const changeColor = getChangeColor(index.change)
          const isPositive = index.change >= 0

          return (
            <div
              key={index.symbol}
              className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {index.name}
                  </p>
                  <Badge
                    variant={isPositive ? 'success' : 'danger'}
                    size="sm"
                  >
                    {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  </Badge>
                </div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  {index.symbol}
                </p>
              </div>
              <div className="text-right">
                <p className="font-bold text-lg text-neutral-900 dark:text-neutral-100">
                  {formatPrice(index.value)}
                </p>
                <p className={classNames('text-sm font-medium', changeColor)}>
                  {isPositive ? '+' : ''}{formatPrice(index.change)} ({formatPercent(index.changePercent)})
                </p>
              </div>
            </div>
          )
        })}
      </CardBody>
    </Card>
  )
}
