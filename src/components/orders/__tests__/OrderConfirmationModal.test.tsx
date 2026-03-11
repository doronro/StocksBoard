import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { OrderConfirmationModal } from '../OrderConfirmationModal'
import type { Quote } from '@types'

const mockQuote: Quote = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 150.25,
  change: 2.5,
  changePercent: 1.69,
  bid: 150.20,
  ask: 150.30,
  volume: 50_000_000,
  avgVolume: 48_000_000,
  timestamp: Date.now(),
  trend: 'up',
}

const mockOrder = {
  symbol: 'AAPL',
  side: 'buy' as const,
  type: 'market' as const,
  quantity: 10,
}

describe('OrderConfirmationModal', () => {
  it('displays order confirmation form', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText('Confirm Order')).toBeInTheDocument()
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('BUY')).toBeInTheDocument()
  })

  it('displays quantity and price information', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText('10 shares')).toBeInTheDocument()
    expect(screen.getByText('Market')).toBeInTheDocument()
  })

  it('displays estimated cost', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText('Estimated Cost')).toBeInTheDocument()
  })

  it('shows sufficient buying power message when funds available', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText('Sufficient Buying Power')).toBeInTheDocument()
  })

  it('shows insufficient buying power message when funds unavailable', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={100}
      />
    )

    expect(screen.getByText('Insufficient Buying Power')).toBeInTheDocument()
  })

  it('disables confirm button when countdown is active', async () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    const confirmButton = screen.getByRole('button', { name: /Confirm Buy/i })
    expect(confirmButton).toBeDisabled()

    // Wait for countdown to finish
    await waitFor(
      () => {
        expect(confirmButton).not.toBeDisabled()
      },
      { timeout: 3000 }
    )
  })

  it('calls onConfirm when confirm button is clicked', async () => {
    const onConfirm = vi.fn()
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
        onConfirm={onConfirm}
      />
    )

    // Wait for countdown to complete
    await waitFor(
      () => {
        const confirmButton = screen.getByRole('button', { name: /Confirm Buy/i })
        expect(confirmButton).not.toBeDisabled()
      },
      { timeout: 3000 }
    )

    const confirmButton = screen.getByRole('button', { name: /Confirm Buy/i })
    fireEvent.click(confirmButton)

    expect(onConfirm).toHaveBeenCalled()
  })

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn()
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
        onCancel={onCancel}
      />
    )

    const cancelButton = screen.getByRole('button', { name: 'Cancel Order' })
    fireEvent.click(cancelButton)

    expect(onCancel).toHaveBeenCalled()
  })

  it('displays limit price for limit orders', () => {
    const limitOrder = {
      ...mockOrder,
      type: 'limit' as const,
      price: 145,
    }

    render(
      <OrderConfirmationModal
        order={limitOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText(/Limit @/)).toBeInTheDocument()
  })

  it('displays stop price for stop loss orders', () => {
    const stopOrder = {
      ...mockOrder,
      type: 'stop_loss' as const,
      stopPrice: 140,
    }

    render(
      <OrderConfirmationModal
        order={stopOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText(/Stop Loss @/)).toBeInTheDocument()
  })

  it('shows sell warning for sell orders', () => {
    const sellOrder = {
      ...mockOrder,
      side: 'sell' as const,
    }

    render(
      <OrderConfirmationModal
        order={sellOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText(/close your position/)).toBeInTheDocument()
  })

  it('disables confirm button when insufficient funds for buy orders', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={100}
      />
    )

    // Wait for countdown
    setTimeout(() => {
      const confirmButton = screen.getByRole('button', { name: /Confirm Buy/i })
      expect(confirmButton).toBeDisabled()
    }, 2500)
  })

  it('does not require sufficient funds for sell orders', async () => {
    const sellOrder = {
      ...mockOrder,
      side: 'sell' as const,
    }

    render(
      <OrderConfirmationModal
        order={sellOrder}
        quote={mockQuote}
        availableBuyingPower={0}
        onConfirm={vi.fn()}
      />
    )

    // Wait for countdown to complete
    await waitFor(
      () => {
        const confirmButton = screen.getByRole('button', { name: /Confirm Sell/i })
        expect(confirmButton).not.toBeDisabled()
      },
      { timeout: 3000 }
    )
  })

  it('displays countdown timer', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
      />
    )

    expect(screen.getByText(/Confirming in/)).toBeInTheDocument()
  })

  it('displays loading state when submitting', () => {
    render(
      <OrderConfirmationModal
        order={mockOrder}
        quote={mockQuote}
        availableBuyingPower={50000}
        isSubmitting={true}
      />
    )

    const cancelButton = screen.getByRole('button', { name: 'Cancel Order' })
    expect(cancelButton).toBeDisabled()
  })
})
