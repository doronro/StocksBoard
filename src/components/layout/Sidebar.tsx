import React from 'react'
import { useUIStore } from '@stores/ui'
import { Button } from '@components/common/Button'
import {
  BarChart3,
  TrendingUp,
  Briefcase,
  ShoppingCart,
  Eye,
  Bell,
  Settings,
  LogOut,
  LayoutGrid,
} from 'lucide-react'
import classNames from 'classnames'

interface SidebarProps {
  onNavigate?: (page: string) => void
  currentPage?: string
}

interface NavItem {
  id: string
  label: string
  icon: React.ReactNode
  section?: string
}

const NAV_ITEMS: NavItem[] = [
  {
    id: 'exchange',
    label: 'Exchange Board',
    icon: <LayoutGrid className="w-5 h-5" />,
  },
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <BarChart3 className="w-5 h-5" />,
  },
  {
    id: 'market',
    label: 'Market Data',
    icon: <TrendingUp className="w-5 h-5" />,
  },
  {
    id: 'portfolio',
    label: 'Portfolio',
    icon: <Briefcase className="w-5 h-5" />,
  },
  {
    id: 'orders',
    label: 'Orders',
    icon: <ShoppingCart className="w-5 h-5" />,
  },
  {
    id: 'watchlist',
    label: 'Watchlist',
    icon: <Eye className="w-5 h-5" />,
  },
  {
    id: 'alerts',
    label: 'Price Alerts',
    icon: <Bell className="w-5 h-5" />,
    section: 'advanced',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings className="w-5 h-5" />,
    section: 'advanced',
  },
]

export const Sidebar: React.FC<SidebarProps> = ({ onNavigate, currentPage = 'dashboard' }) => {
  const { sidebarOpen, setSidebarOpen } = useUIStore()

  const handleNavClick = (pageId: string) => {
    onNavigate?.(pageId)
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 1024) {
      setSidebarOpen(false)
    }
  }

  return (
    <>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={classNames(
          'fixed left-0 top-0 h-screen w-64 bg-white dark:bg-neutral-800',
          'border-r border-neutral-200 dark:border-neutral-700',
          'transform transition-transform duration-300 z-40',
          'lg:static lg:translate-x-0',
          'overflow-y-auto',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Top Spacing */}
        <div className="h-16" />

        {/* Navigation */}
        <nav className="px-4 py-4 space-y-1">
          {NAV_ITEMS.filter((item) => !item.section).map((item) => (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              className={classNames(
                'w-full flex items-center gap-3 px-4 py-2.5 rounded-lg',
                'transition-colors duration-200 text-left',
                currentPage === item.id
                  ? 'bg-accent-600 text-white'
                  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
              )}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Advanced Section */}
        <div className="px-4 py-4 border-t border-neutral-200 dark:border-neutral-700">
          <p className="text-xs font-semibold text-neutral-500 uppercase px-4 mb-2">
            Advanced
          </p>
          <nav className="space-y-1">
            {NAV_ITEMS.filter((item) => item.section === 'advanced').map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={classNames(
                  'w-full flex items-center gap-3 px-4 py-2.5 rounded-lg',
                  'transition-colors duration-200 text-left',
                  currentPage === item.id
                    ? 'bg-accent-600 text-white'
                    : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
                )}
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-200 dark:border-neutral-700">
          <Button
            variant="ghost"
            fullWidth
            size="sm"
            icon={<LogOut className="w-4 h-4" />}
            className="justify-center"
          >
            Logout
          </Button>
        </div>
      </aside>
    </>
  )
}
