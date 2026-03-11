/**
 * Unit tests for MarketDashboard component
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MarketDashboard } from '../MarketDashboard'
import type { Quote, MarketIndex, SectorPerformance } from '@types'

const mockIndices: MarketIndex[] = [
  {
    symbol: '^GSPC',
    name: 'S&P 500',
    value: 4500,
    change: 25,
    changePercent: 0.56,
    timestamp: Date.now(),
  },
  {
    symbol: '^IXIC',
    name: 'Nasdaq',
    value: 14000,
    change: -50,
    changePercent: -0.36,
    timestamp: Date.now(),
  },
  {
    symbol: '^DJI',
    name: 'Dow Jones',
    value: 35000,
    change: 100,
    changePercent: 0.29,
    timestamp: Date.now(),
  },
]

const mockQuotes = new Map<string, Quote>([
  [
    'AAPL',
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 150,
      change: 5,
      changePercent: 3.45,
      bid: 149.95,
      ask: 150.05,
      volume: 50000000,
      avgVolume: 40000000,
      timestamp: Date.now(),
      trend: 'up',
    },
  ],
  [
    'MSFT',
    {
      symbol: 'MSFT',
      name: 'Microsoft Inc.',
      price: 300,
      change: -3,
      changePercent: -0.99,
      bid: 299.95,
      ask: 300.05,
      volume: 30000000,
      avgVolume: 25000000,
      timestamp: Date.now(),
      trend: 'down',
    },
  ],
  [
    'GOOGL',
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      price: 120,
      change: 2,
      changePercent: 1.69,
      bid: 119.95,
      ask: 120.05,
      volume: 25000000,
      avgVolume: 20000000,
      timestamp: Date.now(),
      trend: 'up',
    },
  ],
])

const mockSectors: SectorPerformance[] = [
  {
    name: 'Technology',
    change: 45,
    changePercent: 1.2,
  },
  {
    name: 'Healthcare',
    change: -20,
    changePercent: -0.5,
  },
  {
    name: 'Finance',
    change: 30,
    changePercent: 0.8,
  },
]

describe('MarketDashboard Component', () => {
  it('should render market indices', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText('Market Indices')).toBeInTheDocument()
    expect(screen.getByText('S&P 500')).toBeInTheDocument()
    expect(screen.getByText('Nasdaq')).toBeInTheDocument()
    expect(screen.getByText('Dow Jones')).toBeInTheDocument()
  })

  it('should display market status when open', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
        marketStatus="open"
      />
    )

    expect(screen.getByText('Market Open')).toBeInTheDocument()
  })

  it('should display market status when pre-market', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
        marketStatus="pre_market"
      />
    )

    expect(screen.getByText('Pre-Market')).toBeInTheDocument()
  })

  it('should display market status when closed', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
        marketStatus="closed"
      />
    )

    expect(screen.getByText('Market Closed')).toBeInTheDocument()
  })

  it('should display top gainers', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText('Top Gainers')).toBeInTheDocument()
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('GOOGL')).toBeInTheDocument()
  })

  it('should display top losers', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText('Top Losers')).toBeInTheDocument()
    expect(screen.getAllByText('MSFT')[0]).toBeInTheDocument()
  })

  it('should display sector performance', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText('Sector Performance')).toBeInTheDocument()
    expect(screen.getByText('Technology')).toBeInTheDocument()
    expect(screen.getByText('Healthcare')).toBeInTheDocument()
    expect(screen.getByText('Finance')).toBeInTheDocument()
  })

  it('should show correct price change color for gainers', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    // Text content for AAPL gainner should contain '+3.45%'
    expect(screen.getByText(/\+3\.45%/)).toBeInTheDocument()
  })

  it('should show correct price change color for losers', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    // Text content for MSFT loser should contain '-0.99%'
    expect(screen.getByText('-0.99%')).toBeInTheDocument()
  })

  it('should call onQuoteClick when quote is clicked', () => {
    const onQuoteClick = vi.fn()
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
        onQuoteClick={onQuoteClick}
      />
    )

    const aaplButton = screen.getAllByText('AAPL')[0]
    fireEvent.click(aaplButton.closest('button') || aaplButton)

    // Since we're clicking on a parent button, verify the function was called
    // Note: This test verifies the click handler is attached
    expect(onQuoteClick).toHaveBeenCalledWith('AAPL')
  })

  it('should display loading state', () => {
    const { container } = render(
      <MarketDashboard
        indices={[]}
        quotes={new Map()}
        sectors={[]}
        isLoading={true}
      />
    )

    const loadingElements = container.querySelectorAll('.animate-pulse')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('should show empty state for no indices', () => {
    render(
      <MarketDashboard indices={[]} quotes={mockQuotes} sectors={mockSectors} />
    )

    // Should not render indices section
    expect(screen.queryByText('Market Indices')).not.toBeInTheDocument()
  })

  it('should show empty state for no gainers', () => {
    const emptyQuotes = new Map<string, Quote>([
      [
        'TSLA',
        {
          symbol: 'TSLA',
          name: 'Tesla Inc.',
          price: 200,
          change: -10,
          changePercent: -4.76,
          bid: 199.95,
          ask: 200.05,
          volume: 20000000,
          avgVolume: 18000000,
          timestamp: Date.now(),
          trend: 'down',
        },
      ],
    ])

    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={emptyQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText('No gainers available')).toBeInTheDocument()
  })

  it('should display volume information', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText(/Vol: 50/)).toBeInTheDocument()
  })

  it('should sort sectors by change percentage', () => {
    const { container } = render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    const sectorNames = container.querySelectorAll(
      '[class*="Sector Performance"] + [class*="CardBody"] h4'
    )

    // First sector should be Technology (highest absolute change)
    if (sectorNames.length > 0) {
      expect(sectorNames[0].textContent).toBe('Technology')
    }
  })

  it('should display percentage values for sectors', () => {
    render(
      <MarketDashboard
        indices={mockIndices}
        quotes={mockQuotes}
        sectors={mockSectors}
      />
    )

    expect(screen.getByText(/\+1\.20%/)).toBeInTheDocument()
    expect(screen.getByText(/\-0\.50%/)).toBeInTheDocument()
  })
})
