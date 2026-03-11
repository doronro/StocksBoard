import type { TechnicalIndicator } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import classNames from 'classnames'

interface TechnicalIndicatorsProps {
  indicators: TechnicalIndicator | null
  isLoading?: boolean
  symbol?: string
}

interface IndicatorStatus {
  name: string
  value: string
  status: 'bullish' | 'bearish' | 'neutral'
  description: string
}

const getIndicatorStatus = (indicator: TechnicalIndicator): IndicatorStatus[] => {
  const statuses: IndicatorStatus[] = []

  // RSI Analysis
  if (indicator.rsi !== undefined) {
    let status: 'bullish' | 'bearish' | 'neutral' = 'neutral'
    let description = `RSI: ${indicator.rsi.toFixed(2)}`

    if (indicator.rsi > 70) {
      status = 'bearish'
      description = `Overbought (${indicator.rsi.toFixed(2)})`
    } else if (indicator.rsi < 30) {
      status = 'bullish'
      description = `Oversold (${indicator.rsi.toFixed(2)})`
    } else if (indicator.rsi > 50) {
      status = 'bullish'
      description = `Positive momentum`
    } else if (indicator.rsi < 50) {
      status = 'bearish'
      description = `Negative momentum`
    }

    statuses.push({
      name: 'RSI',
      value: indicator.rsi.toFixed(2),
      status,
      description,
    })
  }

  // MACD Analysis
  if (indicator.macd) {
    let status: 'bullish' | 'bearish' | 'neutral' = 'neutral'
    const { line, signal, histogram } = indicator.macd

    if (histogram > 0) {
      status = 'bullish'
    } else if (histogram < 0) {
      status = 'bearish'
    }

    if (line > signal) {
      status = 'bullish'
    } else if (line < signal) {
      status = 'bearish'
    }

    statuses.push({
      name: 'MACD',
      value: line.toFixed(4),
      status,
      description: `Signal: ${signal.toFixed(4)}, Histogram: ${histogram.toFixed(4)}`,
    })
  }

  // Moving Averages Analysis
  if (indicator.sma20 && indicator.sma50 && indicator.sma200) {
    const sma20Last = indicator.sma20[indicator.sma20.length - 1]
    const sma50Last = indicator.sma50[indicator.sma50.length - 1]
    const sma200Last = indicator.sma200[indicator.sma200.length - 1]

    let status: 'bullish' | 'bearish' | 'neutral' = 'neutral'

    // Golden Cross: SMA 20 > SMA 50 > SMA 200 (bullish)
    // Death Cross: SMA 20 < SMA 50 < SMA 200 (bearish)
    if (sma20Last > sma50Last && sma50Last > sma200Last) {
      status = 'bullish'
    } else if (sma20Last < sma50Last && sma50Last < sma200Last) {
      status = 'bearish'
    } else {
      status = 'neutral'
    }

    statuses.push({
      name: 'SMA Trend',
      value: status.toUpperCase(),
      status,
      description: `20: ${sma20Last.toFixed(2)}, 50: ${sma50Last.toFixed(2)}, 200: ${sma200Last.toFixed(2)}`,
    })
  }

  return statuses
}

export const TechnicalIndicators: React.FC<TechnicalIndicatorsProps> = ({
  indicators,
  isLoading = false,
  symbol,
}) => {
  if (isLoading || !indicators) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Technical Indicators
          </h3>
        </CardHeader>
        <CardBody>
          <div className="animate-pulse text-center text-neutral-500">
            Loading indicators...
          </div>
        </CardBody>
      </Card>
    )
  }

  const statuses = getIndicatorStatus(indicators)

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Technical Indicators {symbol && `- ${symbol}`}
        </h3>
      </CardHeader>
      <CardBody className="space-y-4">
        {statuses.length === 0 ? (
          <p className="text-center text-neutral-500 py-4">
            No indicators available
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {statuses.map((status) => (
              <div
                key={status.name}
                className={classNames(
                  'p-3 rounded-lg border',
                  status.status === 'bullish'
                    ? 'bg-green-500/10 border-green-500/30'
                    : status.status === 'bearish'
                    ? 'bg-red-500/10 border-red-500/30'
                    : 'bg-neutral-100 dark:bg-neutral-700/50 border-neutral-300 dark:border-neutral-600'
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
                    {status.name}
                  </h4>
                  <Badge
                    variant={
                      status.status === 'bullish'
                        ? 'success'
                        : status.status === 'bearish'
                        ? 'danger'
                        : 'info'
                    }
                    size="sm"
                  >
                    {status.status === 'bullish'
                      ? 'Bullish'
                      : status.status === 'bearish'
                      ? 'Bearish'
                      : 'Neutral'}
                  </Badge>
                </div>
                <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-1">
                  {status.value}
                </p>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">
                  {status.description}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Summary Analysis */}
        {statuses.length > 0 && (
          <div className="mt-4 p-3 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg border border-neutral-300 dark:border-neutral-600">
            <h4 className="text-sm font-bold text-neutral-900 dark:text-neutral-100 mb-2">
              Market Signal
            </h4>
            <div className="flex gap-2">
              {(() => {
                const bullishCount = statuses.filter((s) => s.status === 'bullish').length
                const bearishCount = statuses.filter((s) => s.status === 'bearish').length

                if (bullishCount > bearishCount) {
                  return (
                    <p className="text-sm text-green-600 dark:text-green-400">
                      Bullish sentiment detected. {bullishCount} of {statuses.length} indicators are bullish.
                    </p>
                  )
                } else if (bearishCount > bullishCount) {
                  return (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      Bearish sentiment detected. {bearishCount} of {statuses.length} indicators are bearish.
                    </p>
                  )
                } else {
                  return (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Mixed signals detected. Wait for confirmation.
                    </p>
                  )
                }
              })()}
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  )
}
