import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { WatchlistCard } from '../WatchlistCard'
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
  marketCap: 2_400_000_000_000,
  pe: 28.5,
  eps: 5.27,
  high52w: 199.62,
  low52w: 124.17,
  timestamp: Date.now(),
  trend: 'up',
}

describe('WatchlistCard', () => {
  it('displays symbol and name correctly', () => {
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
      />
    )

    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
  })

  it('displays price and change information', () => {
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
      />
    )

    expect(screen.getByText('150.25')).toBeInTheDocument()
    expect(screen.getByText(/\+1\.69%/)).toBeInTheDocument()
  })

  it('shows trending up icon when trend is up', () => {
    const { container } = render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
      />
    )

    // Look for the SVG with green color (trending up icon)
    const icons = container.querySelectorAll('svg[class*="text-green"]')
    expect(icons.length).toBeGreaterThan(0)
  })

  it('calls onBuy when buy button is clicked', async () => {
    const onBuy = vi.fn()
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
        onBuy={onBuy}
      />
    )

    // Click to expand
    const card = screen.getByText('AAPL').closest('div')
    fireEvent.click(card!)

    // Click buy button
    const buyButton = screen.getByText('Buy')
    fireEvent.click(buyButton)

    expect(onBuy).toHaveBeenCalledWith('AAPL')
  })

  it('calls onRemove when remove button is clicked', () => {
    const onRemove = vi.fn()
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
        onRemove={onRemove}
      />
    )

    const removeButton = screen.getByLabelText('Remove AAPL from watchlist')
    fireEvent.click(removeButton)

    expect(onRemove).toHaveBeenCalledWith('AAPL')
  })

  it('expands to show detailed information when clicked', () => {
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
        showTechnicalDetails={true}
      />
    )

    // Click to expand
    const card = screen.getByText('AAPL').closest('div')
    fireEvent.click(card!)

    // Check if technical details are now visible
    expect(screen.getByText('P/E Ratio')).toBeInTheDocument()
    expect(screen.getByText((content, _element) => content.includes('28.5'))).toBeInTheDocument()
  })

  it('shows loading state when quote is not provided', () => {
    const { container } = render(
      <WatchlistCard
        symbol="AAPL"
        isLoading={true}
      />
    )

    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('displays positive change with green styling', () => {
    const { container } = render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
      />
    )

    const percentBadge = container.querySelector('.text-green-600')
    expect(percentBadge).toBeInTheDocument()
  })

  it('displays negative change with red styling', () => {
    const negativeQuote: Quote = {
      ...mockQuote,
      change: -2.5,
      changePercent: -1.69,
      trend: 'down',
    }

    const { container } = render(
      <WatchlistCard
        symbol="AAPL"
        quote={negativeQuote}
      />
    )

    const percentBadge = container.querySelector('.text-red-600')
    expect(percentBadge).toBeInTheDocument()
  })

  it('calls onSelect when card is clicked', () => {
    const onSelect = vi.fn()
    render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
        onSelect={onSelect}
      />
    )

    const card = screen.getByText('AAPL').closest('div')
    fireEvent.click(card!)

    expect(onSelect).toHaveBeenCalledWith('AAPL')
  })

  it('shows selected state styling when isSelected is true', () => {
    const { container } = render(
      <WatchlistCard
        symbol="AAPL"
        quote={mockQuote}
        isSelected={true}
      />
    )

    const card = container.querySelector('.border-l-accent-600')
    expect(card).toBeInTheDocument()
  })
})
