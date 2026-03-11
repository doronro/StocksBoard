import type { ChartDataPoint, TimeFrame } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { formatPrice, formatTime } from '@utils/formatting'

interface CandlestickChartProps {
  data: ChartDataPoint[]
  timeframe: TimeFrame
  onTimeframeChange?: (timeframe: TimeFrame) => void
  isLoading?: boolean
}

const TIMEFRAMES: TimeFrame[] = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  data,
  timeframe,
  onTimeframeChange,
  isLoading = false,
}) => {
  if (isLoading || !data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Price Chart
          </h2>
        </CardHeader>
        <CardBody>
          <div className="h-80 flex items-center justify-center">
            <div className="animate-pulse text-neutral-500">
              {isLoading ? 'Loading chart...' : 'No data available'}
            </div>
          </div>
        </CardBody>
      </Card>
    )
  }

  // Transform candlestick data for recharts
  const chartData = data.map((point) => ({
    timestamp: point.timestamp,
    time: formatTime(point.timestamp),
    open: point.open,
    high: point.high,
    low: point.low,
    close: point.close,
    volume: point.volume,
  }))

  return (
    <Card>
      <CardHeader
        action={
          <div className="flex gap-1 flex-wrap justify-end">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange?.(tf)}
                className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                  timeframe === tf
                    ? 'bg-accent-600 text-white dark:bg-accent-500'
                    : 'bg-neutral-200 text-neutral-900 hover:bg-neutral-300 dark:bg-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-600'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        }
      >
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Price Chart
        </h2>
      </CardHeader>
      <CardBody>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(107, 114, 128, 0.2)"
            />
            <XAxis
              dataKey="time"
              stroke="rgba(107, 114, 128, 0.5)"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="rgba(107, 114, 128, 0.5)"
              style={{ fontSize: '12px' }}
              domain={['dataMin - 5', 'dataMax + 5']}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(30, 41, 59, 0.9)',
                border: '1px solid rgba(107, 114, 128, 0.3)',
                borderRadius: '8px',
                color: '#f1f5f9',
              }}
              labelStyle={{ color: '#f1f5f9' }}
              cursor={{ stroke: 'rgba(255, 255, 255, 0.2)' }}
              formatter={(value: number) => formatPrice(value)}
              labelFormatter={(label) => `Time: ${label}`}
            />

            {/* Candlestick representation using bars */}
            <Bar
              dataKey="close"
              fill="rgba(16, 185, 129, 0.6)"
              shape={<CustomCandlestick />}
              isAnimationActive={false}
            />

            {/* Volume bar */}
            <Bar
              dataKey="volume"
              fill="rgba(107, 114, 128, 0.3)"
              yAxisId="volume"
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}

interface CustomCandlestickProps {
  x?: number
  y?: number
  width?: number
  height?: number
  payload?: {
    open: number
    high: number
    low: number
    close: number
  }
}

const CustomCandlestick: React.FC<CustomCandlestickProps> = ({
  x = 0,
  y = 0,
  width = 10,
  payload,
}) => {
  if (!payload) return null

  const isPositive = payload.close >= payload.open
  const color = isPositive ? '#10b981' : '#ef4444'

  // This is a simplified implementation
  // A full candlestick would need proper scale calculations
  return (
    <g>
      <rect x={x} y={y} width={width} height={10} fill={color} opacity={0.6} />
    </g>
  )
}
