import { useState, useEffect } from 'react'
import type { OrderFormData } from './OrderPanel'
import type { Quote } from '@types'
import { Card, CardHeader, CardBody, CardFooter } from '@components/common/Card'
import { Button } from '@components/common/Button'
import { Badge } from '@components/common/Badge'
import { formatPrice, formatCurrency } from '@utils/formatting'
import { AlertCircle, CheckCircle, X } from 'lucide-react'
import classNames from 'classnames'

interface OrderConfirmationModalProps {
  order: OrderFormData
  quote?: Quote
  availableBuyingPower?: number
  onConfirm?: () => void
  onCancel?: () => void
  isSubmitting?: boolean
}

export const OrderConfirmationModal: React.FC<OrderConfirmationModalProps> = ({
  order,
  quote,
  availableBuyingPower = 0,
  onConfirm,
  onCancel,
  isSubmitting = false,
}) => {
  const [confirmationCountdown, setConfirmationCountdown] = useState(2)
  const [isCountingDown] = useState(true)

  useEffect(() => {
    if (!isCountingDown || confirmationCountdown <= 0) return

    const timer = setTimeout(() => {
      setConfirmationCountdown((prev) => prev - 1)
    }, 1000)

    return () => clearTimeout(timer)
  }, [confirmationCountdown, isCountingDown])

  // Calculate order details
  const pricePerShare = order.price || quote?.price || 0
  const totalCost = pricePerShare * order.quantity
  const hasSufficientFunds = totalCost <= availableBuyingPower || order.side === 'sell'
  const spreadCost = order.side === 'buy' && quote ? (quote.ask - quote.bid) * order.quantity : 0

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader
          action={
            <button
              onClick={onCancel}
              disabled={isSubmitting}
              className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 disabled:opacity-50"
            >
              <X className="w-5 h-5" />
            </button>
          }
        >
          <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Confirm Order
          </h2>
        </CardHeader>

        <CardBody className="space-y-4">
          {/* Order Summary */}
          <div className="space-y-3 p-3 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg">
            {/* Symbol and Side */}
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                {order.symbol}
              </h3>
              <Badge
                variant={order.side === 'buy' ? 'success' : 'danger'}
                size="md"
              >
                {order.side.toUpperCase()}
              </Badge>
            </div>

            {/* Quantity and Price */}
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-neutral-600 dark:text-neutral-400">Quantity</p>
                <p className="font-bold text-neutral-900 dark:text-neutral-100">
                  {order.quantity} shares
                </p>
              </div>
              <div>
                <p className="text-neutral-600 dark:text-neutral-400">Price</p>
                <p className="font-bold text-neutral-900 dark:text-neutral-100">
                  {order.type === 'market' ? 'Market' : formatPrice(pricePerShare)}
                </p>
              </div>
            </div>

            {/* Current Market Price */}
            {quote && (
              <div className="text-xs border-t border-neutral-300 dark:border-neutral-600 pt-2">
                <p className="text-neutral-600 dark:text-neutral-400">Current Market Price</p>
                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                  {formatPrice(quote.price)}
                </p>
              </div>
            )}
          </div>

          {/* Order Details */}
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-neutral-600 dark:text-neutral-400">Estimated Cost</span>
              <span className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatCurrency(totalCost)}
              </span>
            </div>

            {spreadCost > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-neutral-600 dark:text-neutral-400">Bid-Ask Spread</span>
                <span className="font-medium text-neutral-900 dark:text-neutral-100">
                  {formatCurrency(spreadCost)}
                </span>
              </div>
            )}

            {order.type === 'limit' && order.price && (
              <div className="flex items-center justify-between">
                <span className="text-neutral-600 dark:text-neutral-400">Order Type</span>
                <span className="font-medium text-neutral-900 dark:text-neutral-100">
                  Limit @ {formatPrice(order.price)}
                </span>
              </div>
            )}

            {order.type === 'stop_loss' && order.stopPrice && (
              <div className="flex items-center justify-between">
                <span className="text-neutral-600 dark:text-neutral-400">Order Type</span>
                <span className="font-medium text-neutral-900 dark:text-neutral-100">
                  Stop Loss @ {formatPrice(order.stopPrice)}
                </span>
              </div>
            )}
          </div>

          {/* Buying Power Check */}
          {order.side === 'buy' && (
            <div
              className={classNames(
                'p-3 rounded-lg border flex items-start gap-2',
                hasSufficientFunds
                  ? 'bg-green-500/10 border-green-500/30'
                  : 'bg-red-500/10 border-red-500/30'
              )}
            >
              {hasSufficientFunds ? (
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              )}
              <div className="text-xs">
                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                  {hasSufficientFunds ? 'Sufficient Buying Power' : 'Insufficient Buying Power'}
                </p>
                <p className="text-neutral-600 dark:text-neutral-400 mt-1">
                  Available: {formatCurrency(availableBuyingPower)}
                </p>
                {!hasSufficientFunds && (
                  <p className="text-red-600 dark:text-red-400 mt-1">
                    Shortfall: {formatCurrency(totalCost - availableBuyingPower)}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Risk Warning */}
          {order.side === 'sell' && (
            <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-xs">
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                Selling will close your position in {order.symbol}
              </p>
            </div>
          )}

          {/* Confirmation Countdown */}
          {isCountingDown && confirmationCountdown > 0 && (
            <div className="p-3 bg-neutral-100 dark:bg-neutral-700/50 rounded-lg text-center">
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Confirming in{' '}
                <span className="font-bold text-neutral-900 dark:text-neutral-100">
                  {confirmationCountdown}s
                </span>
              </p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                (Safety feature: prevents accidental execution)
              </p>
            </div>
          )}
        </CardBody>

        <CardFooter className="flex gap-2">
          <Button
            variant="secondary"
            fullWidth
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel Order
          </Button>
          <Button
            variant={order.side === 'buy' ? 'success' : 'danger'}
            fullWidth
            onClick={onConfirm}
            disabled={
              isSubmitting ||
              (isCountingDown && confirmationCountdown > 0) ||
              !hasSufficientFunds
            }
            isLoading={isSubmitting}
          >
            Confirm {order.side === 'buy' ? 'Buy' : 'Sell'}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
