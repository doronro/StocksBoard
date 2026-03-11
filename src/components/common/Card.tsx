import React from 'react'
import classNames from 'classnames'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  hoverable?: boolean
  interactive?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  hoverable = false,
  interactive = false,
  className,
  ...props
}) => {
  return (
    <div
      className={classNames(
        'rounded-lg border border-neutral-200 dark:border-neutral-700',
        'bg-white dark:bg-neutral-800',
        'p-4 transition-all duration-200',
        hoverable && 'hover:shadow-lg dark:hover:shadow-neutral-900/50',
        interactive &&
          'cursor-pointer hover:border-accent-500 dark:hover:border-accent-400',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  action?: React.ReactNode
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  action,
  className,
  ...props
}) => {
  return (
    <div
      className={classNames('flex items-center justify-between mb-4', className)}
      {...props}
    >
      <div>{children}</div>
      {action && <div>{action}</div>}
    </div>
  )
}

export const CardBody: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  return <div className={classNames('space-y-4', className)}>{children}</div>
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className,
  ...props
}) => {
  return (
    <div
      className={classNames(
        'border-t border-neutral-200 dark:border-neutral-700 pt-4 mt-4 flex gap-2',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
