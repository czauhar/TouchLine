import React from 'react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  text?: string
}

export function LoadingSpinner({ size = 'md', className, text }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-16 w-16',
    xl: 'h-32 w-32'
  }

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div
        className={cn(
          'animate-spin rounded-full border-b-2 border-white',
          sizes[size],
          className
        )}
      ></div>
      {text && <p className="text-white text-lg">{text}</p>}
    </div>
  )
}

interface FullPageLoadingProps {
  text?: string
}

export function FullPageLoading({ text = 'Loading...' }: FullPageLoadingProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <LoadingSpinner size="xl" text={text} />
    </div>
  )
}

// Skeleton loader for content
interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
}

export function Skeleton({ className, variant = 'rectangular' }: SkeletonProps) {
  const variants = {
    text: 'h-4 w-full',
    circular: 'h-12 w-12 rounded-full',
    rectangular: 'h-24 w-full'
  }

  return (
    <div
      className={cn(
        'animate-pulse bg-slate-700/50 rounded',
        variants[variant],
        className
      )}
    ></div>
  )
}

