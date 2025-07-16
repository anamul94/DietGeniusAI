'use client'

import React from 'react'
import { cn } from '@/lib/utils'

interface PageWrapperProps {
  children: React.ReactNode
  className?: string
  container?: 'default' | 'small' | 'extraSmall' | 'full'
  background?: 'default' | 'gradient' | 'medical' | 'glass'
  showPattern?: boolean
}

export function PageWrapper({
  children,
  className,
  container = 'default',
  background = 'default',
  showPattern = false,
}: PageWrapperProps) {
  const containerClasses = {
    default: 'container',
    small: 'container-sm',
    extraSmall: 'container-xs',
    full: 'w-full',
  }

  const backgroundClasses = {
    default: 'bg-background',
    gradient: 'gradient-bg',
    medical: 'medical-pattern',
    glass: 'glass-effect',
  }

  return (
    <div
      className={cn(
        'min-h-screen transition-colors duration-300',
        backgroundClasses[background],
        showPattern && 'medical-pattern',
        className
      )}
    >
      <div className={cn(containerClasses[container], 'py-8 md:py-12')}>
        {children}
      </div>
    </div>
  )
}

// Header component for consistent page headers
interface PageHeaderProps {
  title: string
  subtitle?: string
  description?: string
  actions?: React.ReactNode
  className?: string
}

export function PageHeader({
  title,
  subtitle,
  description,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <header className={cn('mb-8 md:mb-12', className)}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          {subtitle && (
            <p className="text-sm font-medium text-emerald-primary mb-2">
              {subtitle}
            </p>
          )}
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-50">
            {title}
          </h1>
          {description && (
            <p className="mt-3 text-lg text-slate-600 dark:text-slate-400 max-w-2xl">
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex-shrink-0">{actions}</div>}
      </div>
    </header>
  )
}

// Section wrapper for consistent content sections
interface SectionProps {
  children: React.ReactNode
  title?: string
  description?: string
  className?: string
  spacing?: 'default' | 'tight' | 'loose'
}

export function Section({
  children,
  title,
  description,
  className,
  spacing = 'default',
}: SectionProps) {
  const spacingClasses = {
    default: 'mb-8 md:mb-12',
    tight: 'mb-6',
    loose: 'mb-16',
  }

  return (
    <section className={cn(spacingClasses[spacing], className)}>
      {(title || description) && (
        <div className="mb-6">
          {title && (
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              {title}
            </h2>
          )}
          {description && (
            <p className="mt-2 text-slate-600 dark:text-slate-400">
              {description}
            </p>
          )}
        </div>
      )}
      {children}
    </section>
  )
}

// Card component for consistent card styling
interface CardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'outline'
  padding?: 'default' | 'tight' | 'loose'
}

export function Card({
  children,
  className,
  variant = 'default',
  padding = 'default',
}: CardProps) {
  const variantClasses = {
    default: 'card',
    elevated: 'card shadow-lg hover:shadow-xl',
    outline: 'card border-2 border-slate-200',
  }

  const paddingClasses = {
    default: 'p-6',
    tight: 'p-4',
    loose: 'p-8',
  }

  return (
    <div className={cn(variantClasses[variant], className)}>
      <div className={paddingClasses[padding]}>{children}</div>
    </div>
  )
}

// Loading state component
export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <div className="w-12 h-12 border-4 border-emerald-primary border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-slate-600 dark:text-slate-400">{message}</p>
    </div>
  )
}

// Empty state component
interface EmptyStateProps {
  title: string
  description?: string
  action?: React.ReactNode
  icon?: React.ReactNode
}

export function EmptyState({
  title,
  description,
  action,
  icon,
}: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      {icon && <div className="mx-auto mb-4 text-slate-400">{icon}</div>}
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-50 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-slate-600 dark:text-slate-400 mb-4">{description}</p>
      )}
      {action && <div>{action}</div>}
    </div>
  )
}