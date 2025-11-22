'use client'

import React, { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [mounted, setMounted] = useState(false)

  // Only run on client side
  useEffect(() => {
    setMounted(true)
    // Check localStorage or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const initialTheme = savedTheme || systemTheme
    setTheme(initialTheme)
    document.documentElement.setAttribute('data-theme', initialTheme)
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  // Prevent flash of wrong theme
  if (!mounted) {
    return <div className="w-10 h-10" />
  }

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        'relative w-14 h-7 rounded-full transition-colors duration-300',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900',
        theme === 'dark' ? 'bg-slate-700' : 'bg-blue-500'
      )}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {/* Toggle Background */}
      <div className="relative w-full h-full rounded-full">
        {/* Sun Icon (Light Mode) */}
        <div
          className={cn(
            'absolute left-1 top-1 transition-opacity duration-300',
            theme === 'light' ? 'opacity-100' : 'opacity-0'
          )}
        >
          <Sun className="w-5 h-5 text-white" />
        </div>
        
        {/* Moon Icon (Dark Mode) */}
        <div
          className={cn(
            'absolute right-1 top-1 transition-opacity duration-300',
            theme === 'dark' ? 'opacity-100' : 'opacity-0'
          )}
        >
          <Moon className="w-5 h-5 text-blue-200" />
        </div>
      </div>
      
      {/* Toggle Circle */}
      <div
        className={cn(
          'absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-lg',
          'transition-transform duration-300 ease-in-out',
          theme === 'dark' ? 'translate-x-0.5' : 'translate-x-7'
        )}
      />
    </button>
  )
}

// Compact version for mobile/tight spaces
export function ThemeToggleCompact() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const initialTheme = savedTheme || systemTheme
    setTheme(initialTheme)
    document.documentElement.setAttribute('data-theme', initialTheme)
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  if (!mounted) {
    return <div className="w-10 h-10" />
  }

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        'p-2 rounded-lg transition-all',
        'hover:bg-slate-800 active:scale-95',
        'focus:outline-none focus:ring-2 focus:ring-blue-500'
      )}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <Sun className="w-5 h-5 text-slate-300" />
      ) : (
        <Moon className="w-5 h-5 text-slate-700" />
      )}
    </button>
  )
}

