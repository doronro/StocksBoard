import { useState } from 'react'
import type { Order } from '@types'
import { Card, CardHeader, CardBody } from '@components/common/Card'
import { Badge } from '@components/common/Badge'
import { Button } from '@components/common/Button'
import { formatPrice, formatTime } from '@utils/formatting'
import { ChevronDown, ChevronUp, X } from 'lucide-react'

interface OrdersListProps {
  orders: Order[]
  isLoading?: boolean
  onCancelOrder?: (orderId: string) => void
}

const getStatusColor = (
  status: Order['status']
): 'default' | 'success' | 'danger' | 'warning' | 'info' => {
  switch (status) {
    case 'filled':
      return 'success'
    case 'pending':
      return 'info'
    case 'cancelled':
      return 'danger'
    case 'rejected':
      return 'danger'
    case 'partial':
      return 'warning'
    default:
      return 'default'
  }
}

export const OrdersList: React.FC<OrdersListProps> = ({
  orders,
  isLoading = false,
  onCancelOrder,
}) => {
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null)

  if (isLoading) {
    return (
      <Card>
        <div className="h-32 flex items-center justify-center">
          <div className="animate-pulse text-neutral-500">Loading orders...</div>
        </div>
      </Card>
    )
  }

  const pendingOrders = orders.filter((o) => o.status === 'pending')
  const recentOrders = orders.filter((o) => o.status !== 'pending').slice(0, 5)

  if (orders.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
            Orders
          </h2>
        </CardHeader>
        <CardBody>
          <p className="text-center text-neutral-500">No orders yet.</p>
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Orders
        </h2>
      </CardHeader>
      <CardBody className="space-y-2">
        {/* Pending Orders */}
        {pendingOrders.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              Pending Orders ({pendingOrders.length})
            </h3>
            {pendingOrders.map((order) => (
              <OrderRow
                key={order.id}
                order={order}
                isExpanded={expandedOrderId === order.id}
                onExpand={() =>
                  setExpandedOrderId(expandedOrderId === order.id ? null : order.id)
                }
                onCancel={onCancelOrder}
              />
            ))}
          </div>
        )}

        {/* Recent Orders */}
        {recentOrders.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 px-3 py-2 bg-neutral-100 dark:bg-neutral-700 rounded-lg">
              Recent Orders
            </h3>
            {recentOrders.map((order) => (
              <OrderRow
                key={order.id}
                order={order}
                isExpanded={expandedOrderId === order.id}
                onExpand={() =>
                  setExpandedOrderId(expandedOrderId === order.id ? null : order.id)
                }
              />
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  )
}

interface OrderRowProps {
  order: Order
  isExpanded: boolean
  onExpand: () => void
  onCancel?: (orderId: string) => void
}

const OrderRow: React.FC<OrderRowProps> = ({ order, isExpanded, onExpand, onCancel }) => {
  return (
    <div>
      <button
        onClick={onExpand}
        className="w-full p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors flex items-center justify-between"
      >
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-bold text-neutral-900 dark:text-neutral-100">
              {order.symbol}
            </h4>
            <Badge
              variant={order.side === 'buy' ? 'success' : 'danger'}
              size="sm"
            >
              {order.side === 'buy' ? '+' : '-'}{order.quantity}
            </Badge>
            <Badge variant={getStatusColor(order.status)} size="sm">
              {order.status}
            </Badge>
          </div>
          <p className="text-xs text-neutral-600 dark:text-neutral-400">
            {order.type === 'market'
              ? 'Market Order'
              : `${order.type} @ ${formatPrice(order.price || 0)}`}
          </p>
        </div>

        <div className="text-right mr-2">
          <p className="font-medium text-neutral-900 dark:text-neutral-100">
            {order.filledQuantity}/{order.quantity}
          </p>
          <p className="text-xs text-neutral-600 dark:text-neutral-400">
            {formatTime(order.createdAt)}
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
        <div className="bg-neutral-50 dark:bg-neutral-700/30 p-3 rounded-b-lg border-t border-neutral-200 dark:border-neutral-700 space-y-3 text-sm">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Order Type</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100 capitalize">
                {order.type.replace('_', ' ')}
              </p>
            </div>
            {order.price && (
              <div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Price</p>
                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                  {formatPrice(order.price)}
                </p>
              </div>
            )}
            <div>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Created</p>
              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                {formatTime(order.createdAt)}
              </p>
            </div>
            {order.completedAt && (
              <div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Completed</p>
                <p className="font-medium text-neutral-900 dark:text-neutral-100">
                  {formatTime(order.completedAt)}
                </p>
              </div>
            )}
          </div>

          {order.status === 'pending' && onCancel && (
            <Button
              variant="danger"
              size="sm"
              fullWidth
              onClick={() => onCancel(order.id)}
              icon={<X className="w-4 h-4" />}
            >
              Cancel Order
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
