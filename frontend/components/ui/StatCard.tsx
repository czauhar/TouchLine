import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from './Card'

interface StatCardProps {
  title: string
  value: string | number
  icon?: React.ReactNode
  change?: {
    value: number
    period: string
  }
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'default'
  className?: string
}

export function StatCard({ 
  title, 
  value, 
  icon, 
  change,
  color = 'default',
  className 
}: StatCardProps) {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-500/20',
    green: 'text-green-400 bg-green-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    red: 'text-red-400 bg-red-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    default: 'text-slate-400 bg-slate-500/20'
  }

  return (
    <Card 
      variant="glass" 
      hover
      className={cn('group', className)}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-slate-300 text-sm mb-2">{title}</p>
          <p className="text-3xl font-bold text-white group-hover:text-blue-400 transition-colors">
            {value}
          </p>
          {change && (
            <p className={cn(
              'text-sm mt-2',
              change.value > 0 ? 'text-green-400' : change.value < 0 ? 'text-red-400' : 'text-slate-400'
            )}>
              {change.value > 0 ? '↑' : change.value < 0 ? '↓' : '→'} {Math.abs(change.value)}% {change.period}
            </p>
          )}
        </div>
        {icon && (
          <div className={cn(
            'p-3 rounded-lg transition-all',
            colorClasses[color],
            'group-hover:scale-110'
          )}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  )
}

