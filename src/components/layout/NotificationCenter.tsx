import React from 'react'
import { useUIStore } from '@stores/ui'
import { Toast } from '@components/common/Toast'

export const NotificationCenter: React.FC = () => {
  const { notifications, removeNotification } = useUIStore()

  return (
    <div className="fixed top-20 right-4 space-y-2 z-50 max-w-sm pointer-events-none">
      {notifications.map((notification) => (
        <div key={notification.id} className="pointer-events-auto">
          <Toast
            {...notification}
            onClose={removeNotification}
          />
        </div>
      ))}
    </div>
  )
}
