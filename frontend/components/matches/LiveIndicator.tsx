import React from 'react'
import { cn } from '@/lib/utils'

interface LiveIndicatorProps {
  isLive: boolean
  className?: string
  showText?: boolean
}

export function LiveIndicator({ isLive, className, showText = true }: LiveIndicatorProps) {
  if (!isLive) return null

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping" />
      </div>
      {showText && (
        <span className="text-red-400 font-semibold text-sm">LIVE</span>
      )}
    </div>
  )
}

