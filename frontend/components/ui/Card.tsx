import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  variant?: 'default' | 'glass' | 'bordered'
  hover?: boolean
}

export function Card({ 
  children, 
  className, 
  variant = 'default',
  hover = false,
  ...props 
}: CardProps) {
  const variants = {
    default: 'bg-slate-900/50 border border-slate-800',
    glass: 'bg-white/10 backdrop-blur-lg border border-white/20',
    bordered: 'bg-slate-900 border-2 border-slate-700'
  }

  return (
    <div
      className={cn(
        'rounded-xl p-6 transition-all',
        variants[variant],
        hover && 'hover:bg-slate-900/70 hover:-translate-y-1 hover:shadow-lg',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  )
}

interface CardTitleProps {
  children: React.ReactNode
  className?: string
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-xl font-semibold text-white', className)}>
      {children}
    </h3>
  )
}

interface CardDescriptionProps {
  children: React.ReactNode
  className?: string
}

export function CardDescription({ children, className }: CardDescriptionProps) {
  return (
    <p className={cn('text-sm text-slate-400', className)}>
      {children}
    </p>
  )
}

interface CardContentProps {
  children: React.ReactNode
  className?: string
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn(className)}>
      {children}
    </div>
  )
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn('mt-4 pt-4 border-t border-slate-800', className)}>
      {children}
    </div>
  )
}

