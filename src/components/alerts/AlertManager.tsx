/**
 * Alert Manager Component
 * Allows users to create and manage price and technical alerts
 */

import { useState, useMemo } from 'react'
import type { PriceAlert } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Button } from '@components/common/Button'
import { Badge } from '@components/common/Badge'
import { Bell, X, Plus, CheckCircle, AlertTriangle } from 'lucide-react'
import classNames from 'classnames'
import { formatPrice } from '@utils/formatting'

interface AlertManagerProps {
  alerts?: PriceAlert[]
  isLoading?: boolean
  onCreateAlert?: (symbol: string, type: 'above' | 'below', price: number) => void
  onDeleteAlert?: (alertId: string) => void
  onToggleAlert?: (alertId: string, isActive: boolean) => void
  watchlistSymbols?: string[]
}

export const AlertManager: React.FC<AlertManagerProps> = ({
  alerts = [],
  isLoading = false,
  onCreateAlert,
  onDeleteAlert,
  onToggleAlert,
  watchlistSymbols = [],
}) => {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    symbol: watchlistSymbols[0] || '',
    type: 'above' as 'above' | 'below',
    price: '',
  })
  const [filterActive, setFilterActive] = useState(true)

  // Group alerts by symbol
  const groupedAlerts = useMemo(() => {
    const grouped = new Map<string, PriceAlert[]>()

    alerts.forEach(alert => {
      if (!grouped.has(alert.symbol)) {
        grouped.set(alert.symbol, [])
      }
      grouped.get(alert.symbol)!.push(alert)
    })

    // Filter by active status if needed
    if (filterActive) {
      const filtered = new Map<string, PriceAlert[]>()
      grouped.forEach((alerts, symbol) => {
        const activeAlerts = alerts.filter(a => a.isActive)
        if (activeAlerts.length > 0) {
          filtered.set(symbol, activeAlerts)
        }
      })
      return filtered
    }

    return grouped
  }, [alerts, filterActive])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.symbol || !formData.price) {
      return
    }

    onCreateAlert?.(formData.symbol, formData.type, parseFloat(formData.price))

    // Reset form
    setFormData({
      symbol: watchlistSymbols[0] || '',
      type: 'above',
      price: '',
    })
    setShowForm(false)
  }

  const activeCount = alerts.filter(a => a.isActive).length
  const triggeredCount = alerts.filter(a => a.triggered).length

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Price Alerts
          </h3>
        </CardHeader>
        <CardBody>
          <div className="animate-pulse h-40 bg-neutral-100 dark:bg-neutral-700 rounded-lg" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Price Alerts
            </h3>
            {activeCount > 0 && (
              <Badge variant="success" size="sm">
                {activeCount} Active
              </Badge>
            )}
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setFilterActive(!filterActive)}
              className={classNames(
                'px-3 py-1 text-xs font-medium rounded transition-colors',
                filterActive
                  ? 'bg-accent-600 text-white dark:bg-accent-500'
                  : 'bg-neutral-200 text-neutral-900 hover:bg-neutral-300 dark:bg-neutral-700 dark:text-neutral-100'
              )}
            >
              {filterActive ? 'Active' : 'All'}
            </button>
            <Button
              variant="success"
              size="sm"
              onClick={() => setShowForm(!showForm)}
              icon={<Plus className="w-4 h-4" />}
            >
              New Alert
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Create Alert Form */}
        {showForm && (
          <form
            onSubmit={handleSubmit}
            className="p-4 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg border border-neutral-300 dark:border-neutral-600 space-y-3"
          >
            <h4 className="font-medium text-neutral-900 dark:text-neutral-100">Create New Alert</h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Symbol */}
              <div>
                <label className="block text-xs font-medium text-neutral-600 dark:text-neutral-400 mb-1">
                  Symbol
                </label>
                <select
                  value={formData.symbol}
                  onChange={e => setFormData({ ...formData, symbol: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-neutral-100 text-sm"
                >
                  {watchlistSymbols.map(symbol => (
                    <option key={symbol} value={symbol}>
                      {symbol}
                    </option>
                  ))}
                </select>
              </div>

              {/* Type */}
              <div>
                <label className="block text-xs font-medium text-neutral-600 dark:text-neutral-400 mb-1">
                  Condition
                </label>
                <select
                  value={formData.type}
                  onChange={e => setFormData({ ...formData, type: e.target.value as 'above' | 'below' })}
                  className="w-full px-3 py-2 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-neutral-100 text-sm"
                >
                  <option value="above">Price Above</option>
                  <option value="below">Price Below</option>
                </select>
              </div>

              {/* Price */}
              <div>
                <label className="block text-xs font-medium text-neutral-600 dark:text-neutral-400 mb-1">
                  Target Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={e => setFormData({ ...formData, price: e.target.value })}
                  placeholder="Enter price"
                  className="w-full px-3 py-2 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-neutral-100 text-sm"
                />
              </div>
            </div>

            <div className="flex gap-2 justify-end">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <Button
                variant="success"
                size="sm"
                type="submit"
                disabled={!formData.symbol || !formData.price}
              >
                Create Alert
              </Button>
            </div>
          </form>
        )}

        {/* Alerts List */}
        {groupedAlerts.size === 0 ? (
          <div className="text-center py-8">
            <Bell className="w-8 h-8 mx-auto mb-2 text-neutral-400" />
            <p className="text-neutral-600 dark:text-neutral-400">
              {filterActive ? 'No active alerts' : 'No alerts created'}
            </p>
            <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
              Create an alert to get notified about price movements
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {Array.from(groupedAlerts.entries()).map(([symbol, symbolAlerts]) => (
              <div key={symbol} className="space-y-2">
                <h4 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                  {symbol}
                </h4>
                <div className="space-y-2">
                  {symbolAlerts.map(alert => (
                    <div
                      key={alert.id}
                      className={classNames(
                        'p-3 rounded-lg border flex items-start justify-between',
                        alert.triggered
                          ? 'bg-yellow-500/10 border-yellow-500/30'
                          : alert.isActive
                          ? 'bg-blue-500/10 border-blue-500/30'
                          : 'bg-neutral-100 dark:bg-neutral-700/50 border-neutral-300 dark:border-neutral-600'
                      )}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {alert.triggered ? (
                            <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          )}
                          <span className="font-medium text-neutral-900 dark:text-neutral-100">
                            Price {alert.type === 'above' ? 'above' : 'below'} {formatPrice(alert.targetPrice)}
                          </span>
                          {alert.triggered && (
                            <Badge variant="warning" size="sm">
                              Triggered
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          Created {new Date(alert.createdAt).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>

                      <div className="flex gap-2 ml-2">
                        <button
                          onClick={() => onToggleAlert?.(alert.id, !alert.isActive)}
                          className="px-2 py-1 text-xs font-medium rounded bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors"
                        >
                          {alert.isActive ? 'Disable' : 'Enable'}
                        </button>
                        <button
                          onClick={() => onDeleteAlert?.(alert.id)}
                          className="p-1 text-neutral-600 dark:text-neutral-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {alerts.length > 0 && (
          <div className="grid grid-cols-3 gap-2 border-t border-neutral-200 dark:border-neutral-700 pt-4">
            <div className="p-2 bg-neutral-100 dark:bg-neutral-700/50 rounded">
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Total Alerts</p>
              <p className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                {alerts.length}
              </p>
            </div>
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded">
              <p className="text-xs text-blue-600 dark:text-blue-400">Active</p>
              <p className="text-lg font-bold text-blue-900 dark:text-blue-100">
                {activeCount}
              </p>
            </div>
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded">
              <p className="text-xs text-yellow-600 dark:text-yellow-400">Triggered</p>
              <p className="text-lg font-bold text-yellow-900 dark:text-yellow-100">
                {triggeredCount}
              </p>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  )
}
