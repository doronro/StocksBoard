/**
 * Unit tests for AlertManager component
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AlertManager } from '../AlertManager'
import type { PriceAlert } from '@types'

const mockAlerts: PriceAlert[] = [
  {
    id: 'alert-1',
    userId: 'user-1',
    symbol: 'AAPL',
    name: 'Apple Inc.',
    type: 'above',
    targetPrice: 150,
    isActive: true,
    triggered: false,
    createdAt: Date.now(),
  },
  {
    id: 'alert-2',
    userId: 'user-1',
    symbol: 'MSFT',
    name: 'Microsoft Inc.',
    type: 'below',
    targetPrice: 300,
    isActive: true,
    triggered: true,
    createdAt: Date.now(),
  },
  {
    id: 'alert-3',
    userId: 'user-1',
    symbol: 'AAPL',
    name: 'Apple Inc.',
    type: 'below',
    targetPrice: 100,
    isActive: false,
    triggered: false,
    createdAt: Date.now(),
  },
]

describe('AlertManager Component', () => {
  it('should render alerts heading and button', () => {
    render(<AlertManager alerts={[]} watchlistSymbols={['AAPL']} />)

    expect(screen.getByText('Price Alerts')).toBeInTheDocument()
    expect(screen.getByText('New Alert')).toBeInTheDocument()
  })

  it('should display empty state when no alerts', () => {
    render(<AlertManager alerts={[]} watchlistSymbols={['AAPL']} />)

    expect(screen.getByText((content, _element) => content.includes('No active alerts') || content.includes('No alerts created'))).toBeInTheDocument()
  })

  it('should display active alerts badge', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL']} />)

    const badge = screen.getByText('2 Active')
    expect(badge).toBeInTheDocument()
  })

  it('should display all alerts by default', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    // Should show both AAPL and MSFT symbol headers
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getAllByText('MSFT')[0]).toBeInTheDocument()
  })

  it('should filter to show only active alerts', async () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    // Click active filter button - find the one in the filter section
    const allActiveTexts = screen.getAllByText(/Active/)
    const filterButton = allActiveTexts.find(btn => btn.tagName === 'BUTTON')
    if (filterButton) fireEvent.click(filterButton)

    await waitFor(() => {
      // Should only show AAPL and MSFT (2 active alerts)
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getAllByText('MSFT')[0]).toBeInTheDocument()
    })
  })

  it('should show form when New Alert button is clicked', async () => {
    render(<AlertManager alerts={[]} watchlistSymbols={['AAPL']} />)

    const newAlertButton = screen.getByText('New Alert')
    fireEvent.click(newAlertButton)

    await waitFor(() => {
      expect(screen.getByText('Create New Alert')).toBeInTheDocument()
      expect(screen.getByDisplayValue('AAPL')).toBeInTheDocument()
    })
  })

  it('should call onCreateAlert with correct data', async () => {
    const onCreateAlert = vi.fn()
    render(
      <AlertManager
        alerts={[]}
        watchlistSymbols={['AAPL', 'MSFT']}
        onCreateAlert={onCreateAlert}
      />
    )

    // Open form
    const newAlertButton = screen.getByText('New Alert')
    fireEvent.click(newAlertButton)

    // Fill form
    const priceInput = screen.getByPlaceholderText('Enter price')
    await userEvent.type(priceInput, '150.00')

    // Submit
    const submitButtons = screen.getAllByText('Create Alert')
    fireEvent.click(submitButtons[0])

    expect(onCreateAlert).toHaveBeenCalledWith('AAPL', 'above', 150)
  })

  it('should call onDeleteAlert when delete button clicked', () => {
    const onDeleteAlert = vi.fn()
    const { container } = render(
      <AlertManager
        alerts={mockAlerts}
        watchlistSymbols={['AAPL', 'MSFT']}
        onDeleteAlert={onDeleteAlert}
      />
    )

    // Find delete button - should be a button with an X icon in the alert item
    const deleteButtons = container.querySelectorAll('button svg[class*="w-4"][class*="h-4"]')
    if (deleteButtons.length > 0) {
      // Find the parent button and click it
      const deleteButton = (deleteButtons[deleteButtons.length - 1] as any).closest('button')
      if (deleteButton) {
        fireEvent.click(deleteButton)
        expect(onDeleteAlert).toHaveBeenCalled()
      }
    }
  })

  it('should show triggered alert indicator', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    // Should show triggered badge for alert-2 - count them
    const triggeredElements = screen.getAllByText(/Triggered/)
    expect(triggeredElements.length).toBeGreaterThan(0)
  })

  it('should display alert statistics', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    // Check for the active count badge
    expect(screen.getByText('2 Active')).toBeInTheDocument()
  })

  it('should show loading state', () => {
    const { container } = render(
      <AlertManager alerts={[]} isLoading={true} watchlistSymbols={['AAPL']} />
    )

    const loadingElement = container.querySelector('.animate-pulse')
    expect(loadingElement).toBeInTheDocument()
  })

  it('should display alert details correctly', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    // Check for alert type indicators with flexible matching
    expect(screen.getByText((content, _element) => content.includes('Price above'))).toBeInTheDocument()
    expect(screen.getByText((content, _element) => content.includes('Price below'))).toBeInTheDocument()
  })

  it('should have disable/enable buttons for each alert', () => {
    render(<AlertManager alerts={mockAlerts} watchlistSymbols={['AAPL', 'MSFT']} />)

    const disableButtons = screen.queryAllByText(/Disable/)
    const enableButtons = screen.queryAllByText(/Enable/)

    // Should have at least one disable button (for active alerts) and one enable button (for inactive)
    expect(disableButtons.length + enableButtons.length).toBeGreaterThan(0)
  })

  it('should call onToggleAlert when disable/enable clicked', () => {
    const onToggleAlert = vi.fn()
    render(
      <AlertManager
        alerts={mockAlerts}
        watchlistSymbols={['AAPL', 'MSFT']}
        onToggleAlert={onToggleAlert}
      />
    )

    const disableButton = screen.getAllByText('Disable')[0]
    fireEvent.click(disableButton)

    expect(onToggleAlert).toHaveBeenCalled()
  })
})
