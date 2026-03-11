import { useState, useEffect } from 'react'
import { useUIStore } from '@stores/ui'
import { Header } from '@components/layout/Header'
import { Sidebar } from '@components/layout/Sidebar'
import { NotificationCenter } from '@components/layout/NotificationCenter'
import { OrderPanel } from '@components/orders/OrderPanel'
import { Dashboard } from '@pages/Dashboard'
import { Market } from '@pages/Market'
import { StockExchangeBoard } from '@pages/StockExchangeBoard'
import { useMarketData } from '@hooks/useMarketData'
import { usePortfolioData } from '@hooks/usePortfolioData'

type PageType = 'dashboard' | 'market' | 'exchange' | 'portfolio' | 'orders' | 'watchlist' | 'alerts' | 'settings'

export const App: React.FC = () => {
  const { theme, showOrderPanel, setShowOrderPanel } = useUIStore()
  const [currentPage, setCurrentPage] = useState<PageType>('exchange')

  // Load data hooks
  useMarketData()
  usePortfolioData()

  // Set theme on root element
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])

  // Render current page
  const renderPage = () => {
    switch (currentPage) {
      case 'exchange':
        return <StockExchangeBoard />
      case 'dashboard':
        return <Dashboard />
      case 'market':
        return <Market />
      case 'portfolio':
        return <Dashboard /> // Placeholder
      case 'orders':
        return <Dashboard /> // Placeholder
      case 'watchlist':
        return <Dashboard /> // Placeholder
      case 'alerts':
        return <Dashboard /> // Placeholder
      case 'settings':
        return <Dashboard /> // Placeholder
      default:
        return <StockExchangeBoard />
    }
  }

  return (
    <div className="bg-neutral-50 dark:bg-neutral-900 min-h-screen">
      {/* Header */}
      <Header onSearch={(query) => {
        console.log('Search query:', query)
      }} />

      <div className="flex">
        {/* Sidebar */}
        <Sidebar
          currentPage={currentPage}
          onNavigate={(page) => setCurrentPage(page as PageType)}
        />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {renderPage()}
        </main>
      </div>

      {/* Order Panel */}
      {showOrderPanel && (
        <OrderPanel
          onClose={() => setShowOrderPanel(false)}
          onSubmit={(order) => {
            console.log('Order submitted:', order)
            setShowOrderPanel(false)
          }}
        />
      )}

      {/* Notifications */}
      <NotificationCenter />
    </div>
  )
}

export default App
