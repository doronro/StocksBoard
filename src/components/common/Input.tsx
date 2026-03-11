import React from 'react'
import classNames from 'classnames'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
  helpText?: string
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  icon,
  helpText,
  className,
  id,
  ...props
}) => {
  const inputId = id || Math.random().toString(36).substr(2, 9)

  return (
    <div className="space-y-1">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {icon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500">{icon}</div>}
        <input
          id={inputId}
          className={classNames(
            'w-full px-3 py-2 border rounded-lg',
            'bg-white dark:bg-neutral-700',
            'text-neutral-900 dark:text-neutral-100',
            'placeholder-neutral-500 dark:placeholder-neutral-400',
            'border-neutral-300 dark:border-neutral-600',
            'focus:outline-none focus:ring-2 focus:ring-accent-500 dark:focus:ring-accent-400',
            'transition-colors duration-200',
            icon && 'pl-10',
            error && 'border-red-500 focus:ring-red-500',
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
      {helpText && !error && <p className="text-sm text-neutral-500">{helpText}</p>}
    </div>
  )
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: Array<{ value: string | number; label: string }>
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  options,
  className,
  id,
  ...props
}) => {
  const selectId = id || Math.random().toString(36).substr(2, 9)

  return (
    <div className="space-y-1">
      {label && (
        <label
          htmlFor={selectId}
          className="block text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={classNames(
          'w-full px-3 py-2 border rounded-lg',
          'bg-white dark:bg-neutral-700',
          'text-neutral-900 dark:text-neutral-100',
          'border-neutral-300 dark:border-neutral-600',
          'focus:outline-none focus:ring-2 focus:ring-accent-500 dark:focus:ring-accent-400',
          'transition-colors duration-200',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  )
}
