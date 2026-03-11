import type { SectorPerformance } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { formatPercent, getChangeColor } from '@utils/formatting'
import classNames from 'classnames'

interface SectorHeatmapProps {
  sectors: SectorPerformance[]
  isLoading?: boolean
}

const getSectorColor = (changePercent: number): string => {
  if (changePercent > 2) return 'bg-green-600'
  if (changePercent > 0.5) return 'bg-green-400'
  if (changePercent > -0.5) return 'bg-neutral-400'
  if (changePercent > -2) return 'bg-red-400'
  return 'bg-red-600'
}

const getSectorTextColor = (changePercent: number): string => {
  if (Math.abs(changePercent) < 0.5) return 'text-neutral-900'
  return 'text-white'
}

export const SectorHeatmap: React.FC<SectorHeatmapProps> = ({ sectors, isLoading = false }) => {
  if (isLoading) {
    return (
      <Card>
        <div className="h-40 flex items-center justify-center">
          <div className="animate-pulse text-neutral-500">Loading sectors...</div>
        </div>
      </Card>
    )
  }

  const sortedSectors = [...sectors].sort((a, b) => b.changePercent - a.changePercent)

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Sector Performance
        </h2>
      </CardHeader>
      <CardBody className="space-y-2">
        {sortedSectors.map((sector) => (
          <div key={sector.name} className="space-y-1">
            <div className="flex justify-between items-center mb-1">
              <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                {sector.name}
              </p>
              <p
                className={classNames(
                  'text-sm font-bold',
                  getChangeColor(sector.changePercent)
                )}
              >
                {formatPercent(sector.changePercent)}
              </p>
            </div>
            <div
              className={classNames(
                'h-6 rounded-md transition-all',
                getSectorColor(sector.changePercent)
              )}
              style={{
                opacity: 0.8,
                width: `${Math.min(100, 50 + Math.abs(sector.changePercent) * 10)}%`,
              }}
            >
              <div
                className={classNames(
                  'h-full flex items-center justify-center text-xs font-bold',
                  getSectorTextColor(sector.changePercent)
                )}
              >
                {Math.abs(sector.changePercent).toFixed(2)}%
              </div>
            </div>
          </div>
        ))}
      </CardBody>
    </Card>
  )
}
