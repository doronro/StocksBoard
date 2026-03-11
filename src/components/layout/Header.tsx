import { useState } from 'react'
import type { FC } from 'react'
import { useUIStore } from '@stores/ui'
import { Button } from '@components/common/Button'
import { Input } from '@components/common/Input'
import { Menu, Moon, Sun, Bell, Search, Settings } from 'lucide-react'

interface HeaderProps {
  onSearch?: (query: string) => void
}

export const Header: FC<HeaderProps> = ({ onSearch }) => {
  const { theme, toggleTheme, toggleSidebar } = useUIStore()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    onSearch?.(searchQuery)
  }

  return (
    <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 sticky top-0 z-40">
      <div className="flex items-center justify-between px-4 py-3 gap-4">
        {/* Left - Logo and Menu */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="lg:hidden"
            icon={<Menu className="w-5 h-5" />}
          />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-600 flex items-center justify-center text-white font-bold">
              SX
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                Stock Exchange
              </h1>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">
                Real-time trading platform
              </p>
            </div>
          </div>
        </div>

        {/* Center - Search */}
        <form
          onSubmit={handleSearch}
          className="flex-1 max-w-sm hidden sm:block"
        >
          <div className="relative">
            <Input
              type="search"
              placeholder="Search stocks (e.g., AAPL)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon={<Search className="w-4 h-4" />}
              className="pr-4"
            />
          </div>
        </form>

        {/* Right - Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            icon={
              theme === 'dark' ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )
            }
            title="Toggle theme"
          />

          <Button
            variant="ghost"
            size="sm"
            icon={<Bell className="w-5 h-5" />}
            title="Notifications"
          />

          <Button
            variant="ghost"
            size="sm"
            icon={<Settings className="w-5 h-5" />}
            title="Settings"
          />
        </div>
      </div>

      {/* Mobile Search */}
      <div className="px-4 py-2 sm:hidden border-t border-neutral-200 dark:border-neutral-700">
        <form onSubmit={handleSearch}>
          <Input
            type="search"
            placeholder="Search stocks"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search className="w-4 h-4" />}
          />
        </form>
      </div>
    </header>
  )
}
