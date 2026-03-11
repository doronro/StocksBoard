import { useState } from 'react'
import type { OrderType, OrderSide } from '@types'
import { Card, CardHeader, CardBody, CardFooter } from '@components/common/Card'
import { Button } from '@components/common/Button'
import { Input, Select } from '@components/common/Input'
import { X } from 'lucide-react'
import { validateOrderQuantity, validateOrderPrice, validateSymbol, sanitizeSymbol } from '@utils/validation'

interface OrderPanelProps {
  onClose?: () => void
  onSubmit?: (order: OrderFormData) => void
}

export interface OrderFormData {
  symbol: string
  side: OrderSide
  type: OrderType
  quantity: number
  price?: number
  stopPrice?: number
  trailingPercent?: number
}

export const OrderPanel: React.FC<OrderPanelProps> = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState<OrderFormData>({
    symbol: '',
    side: 'buy',
    type: 'market',
    quantity: 1,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.symbol.trim()) {
      newErrors.symbol = 'Symbol is required'
    } else if (!validateSymbol(formData.symbol)) {
      newErrors.symbol = 'Invalid symbol format (1-5 uppercase letters)'
    }

    if (!validateOrderQuantity(formData.quantity)) {
      newErrors.quantity = 'Quantity must be a positive integer'
    }

    if (formData.type !== 'market') {
      if (!formData.price || !validateOrderPrice(formData.price)) {
        newErrors.price = 'Valid price required'
      }
    }

    if (formData.type === 'stop_loss' && !formData.stopPrice) {
      newErrors.stopPrice = 'Stop price required'
    }

    if (formData.type === 'trailing_stop' && !formData.trailingPercent) {
      newErrors.trailingPercent = 'Trailing percent required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setIsSubmitting(true)
    try {
      onSubmit?.(formData)
      // Reset form on success
      setFormData({
        symbol: '',
        side: 'buy',
        type: 'market',
        quantity: 1,
      })
      setErrors({})
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="fixed bottom-4 right-4 w-96 shadow-2xl z-50">
      <CardHeader
        action={
          <button
            onClick={onClose}
            className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
            aria-label="Close order panel"
          >
            <X className="w-5 h-5" />
          </button>
        }
      >
        <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          Place Order
        </h2>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardBody className="space-y-4">
          {/* Symbol */}
          <Input
            label="Symbol"
            placeholder="e.g., AAPL"
            value={formData.symbol}
            onChange={(e) =>
              setFormData({
                ...formData,
                symbol: sanitizeSymbol(e.target.value),
              })
            }
            error={errors.symbol}
            autoFocus
          />

          {/* Side Selection */}
          <div className="flex gap-2">
            <Button
              type="button"
              variant={formData.side === 'buy' ? 'success' : 'secondary'}
              fullWidth
              onClick={() => setFormData({ ...formData, side: 'buy' })}
            >
              Buy
            </Button>
            <Button
              type="button"
              variant={formData.side === 'sell' ? 'danger' : 'secondary'}
              fullWidth
              onClick={() => setFormData({ ...formData, side: 'sell' })}
            >
              Sell
            </Button>
          </div>

          {/* Order Type */}
          <Select
            label="Order Type"
            options={[
              { value: 'market', label: 'Market' },
              { value: 'limit', label: 'Limit' },
              { value: 'stop_loss', label: 'Stop Loss' },
              { value: 'trailing_stop', label: 'Trailing Stop' },
            ]}
            value={formData.type}
            onChange={(e) =>
              setFormData({
                ...formData,
                type: e.target.value as OrderType,
              })
            }
          />

          {/* Quantity */}
          <Input
            type="number"
            label="Quantity"
            placeholder="1"
            min="1"
            step="1"
            value={formData.quantity}
            onChange={(e) =>
              setFormData({
                ...formData,
                quantity: parseInt(e.target.value) || 1,
              })
            }
            error={errors.quantity}
          />

          {/* Price (for non-market orders) */}
          {formData.type !== 'market' && (
            <>
              {formData.type === 'trailing_stop' ? (
                <Input
                  type="number"
                  label="Trailing %"
                  placeholder="2.5"
                  min="0.01"
                  step="0.01"
                  value={formData.trailingPercent || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      trailingPercent: parseFloat(e.target.value) || undefined,
                    })
                  }
                  error={errors.trailingPercent}
                />
              ) : formData.type === 'stop_loss' ? (
                <Input
                  type="number"
                  label="Stop Price"
                  placeholder="0.00"
                  step="0.01"
                  value={formData.stopPrice || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      stopPrice: parseFloat(e.target.value) || undefined,
                    })
                  }
                  error={errors.stopPrice}
                />
              ) : (
                <Input
                  type="number"
                  label="Limit Price"
                  placeholder="0.00"
                  step="0.01"
                  value={formData.price || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      price: parseFloat(e.target.value) || undefined,
                    })
                  }
                  error={errors.price}
                />
              )}
            </>
          )}
        </CardBody>

        <CardFooter className="flex gap-2">
          <Button variant="secondary" fullWidth onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant={formData.side === 'buy' ? 'success' : 'danger'}
            fullWidth
            isLoading={isSubmitting}
          >
            {formData.side === 'buy' ? 'Buy' : 'Sell'} Now
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}
