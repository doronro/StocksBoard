import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../Button'

describe('Button Component', () => {
  it('Should render button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('Should handle click event', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('Should render with different variants', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    expect(screen.getByText('Primary')).toHaveClass('bg-accent-600')

    rerender(<Button variant="danger">Danger</Button>)
    expect(screen.getByText('Danger')).toHaveClass('bg-red-500')

    rerender(<Button variant="success">Success</Button>)
    expect(screen.getByText('Success')).toHaveClass('bg-green-500')
  })

  it('Should render with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    expect(screen.getByText('Small')).toHaveClass('px-3')

    rerender(<Button size="lg">Large</Button>)
    expect(screen.getByText('Large')).toHaveClass('px-6')
  })

  it('Should disable button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByText('Disabled') as HTMLButtonElement
    expect(button.disabled).toBe(true)
  })

  it('Should show loading state', () => {
    render(<Button isLoading>Loading</Button>)
    const button = screen.getByText('Loading') as HTMLButtonElement
    expect(button).toBeInTheDocument()
    expect(button.disabled).toBe(true)
  })

  it('Should render full width when fullWidth prop is true', () => {
    render(<Button fullWidth>Full Width</Button>)
    expect(screen.getByText('Full Width')).toHaveClass('w-full')
  })

  it('Should render icon when provided', () => {
    render(<Button icon={<span data-testid="test-icon">Icon</span>}>With Icon</Button>)
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
  })

  it('Should not show icon when loading', () => {
    render(
      <Button isLoading icon={<span data-testid="test-icon">Icon</span>}>
        Loading
      </Button>
    )
    expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument()
  })
})
