import { create } from 'zustand'
import { Theme } from '@types'

interface UIState {
  theme: Theme
  sidebarOpen: boolean
  selectedPanel: string | null
  showOrderPanel: boolean
  showSearchModal: boolean
  notifications: Notification[]

  // Actions
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setSelectedPanel: (panel: string | null) => void
  setShowOrderPanel: (show: boolean) => void
  setShowSearchModal: (show: boolean) => void
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
  timestamp: number
}

export const useUIStore = create<UIState>((set, get) => ({
  theme: 'dark',
  sidebarOpen: true,
  selectedPanel: null,
  showOrderPanel: false,
  showSearchModal: false,
  notifications: [],

  toggleTheme: () => {
    set((state) => ({
      theme: state.theme === 'dark' ? 'light' : 'dark',
    }))
  },

  setTheme: (theme) => {
    set({ theme })
  },

  toggleSidebar: () => {
    set((state) => ({
      sidebarOpen: !state.sidebarOpen,
    }))
  },

  setSidebarOpen: (open) => {
    set({ sidebarOpen: open })
  },

  setSelectedPanel: (panel) => {
    set({ selectedPanel: panel })
  },

  setShowOrderPanel: (show) => {
    set({ showOrderPanel: show })
  },

  setShowSearchModal: (show) => {
    set({ showSearchModal: show })
  },

  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9)
    const fullNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
    }

    set((state) => ({
      notifications: [fullNotification, ...state.notifications],
    }))

    const duration = notification.duration || 3000
    if (duration > 0) {
      setTimeout(() => {
        get().removeNotification(id)
      }, duration)
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }))
  },
}))
