import React, { useEffect } from 'react'
import { Check, AlertCircle, Info, AlertTriangle, X } from 'lucide-react'
import classNames from 'classnames'
import { Notification } from '@stores/ui'

interface ToastProps extends Notification {
  onClose: (id: string) => void
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  duration = 3000,
  onClose,
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onClose(id), duration)
      return () => clearTimeout(timer)
    }
  }, [id, duration, onClose])

  const iconMap = {
    success: <Check className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
  }

  const bgColorMap = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
  }

  return (
    <div
      className={classNames(
        'animate-slideUp flex items-center gap-3 px-4 py-3 rounded-lg',
        'text-white shadow-lg',
        bgColorMap[type]
      )}
      role="alert"
    >
      {iconMap[type]}
      <span className="flex-1 text-sm">{message}</span>
      <button
        onClick={() => onClose(id)}
        className="text-white hover:opacity-80 transition-opacity"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
