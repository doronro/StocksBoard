import React, { ReactNode } from 'react'
import classNames from 'classnames'

interface TabProps {
  children: ReactNode
  isActive?: boolean
  onClick?: () => void
}

export const Tab: React.FC<TabProps> = ({ children, isActive, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={classNames(
        'px-3 py-2 text-sm font-medium border-b-2 transition-colors',
        isActive
          ? 'border-accent-600 text-accent-600'
          : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200'
      )}
    >
      {children}
    </button>
  )
}
