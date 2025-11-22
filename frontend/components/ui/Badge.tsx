import React from 'react'
import { cn } from '@/lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'primary'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Badge({ 
  children, 
  variant = 'default',
  size = 'md',
  className 
}: BadgeProps) {
  const variants = {
    default: 'bg-slate-700 text-slate-200',
    success: 'bg-green-500/20 text-green-400 border border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    danger: 'bg-red-500/20 text-red-400 border border-red-500/30',
    info: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    primary: 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base'
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  )
}

// Status-specific badge variants
export function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { variant: BadgeProps['variant'], label: string }> = {
    'live': { variant: 'success', label: '🔴 LIVE' },
    '1H': { variant: 'success', label: '1st Half' },
    '2H': { variant: 'success', label: '2nd Half' },
    'HT': { variant: 'warning', label: 'Half Time' },
    'FT': { variant: 'default', label: 'Full Time' },
    'NS': { variant: 'info', label: 'Not Started' },
    'PST': { variant: 'warning', label: 'Postponed' },
    'CANC': { variant: 'danger', label: 'Cancelled' },
    'TBD': { variant: 'default', label: 'TBD' }
  }

  const config = statusConfig[status] || { variant: 'default', label: status }

  return <Badge variant={config.variant}>{config.label}</Badge>
}

