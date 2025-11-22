import React from 'react'
import Link from 'next/link'
import { Card } from '../ui/Card'
import { ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface QuickActionProps {
  title: string
  description: string
  icon: React.ReactNode
  href: string
  color: string
  hoverColor: string
}

export function QuickAction({ title, description, icon, href, color, hoverColor }: QuickActionProps) {
  return (
    <Link href={href}>
      <Card
        className={cn(
          'group cursor-pointer bg-gradient-to-r transition-all duration-300',
          'hover:shadow-xl hover:-translate-y-1',
          color
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="bg-white/20 p-3 rounded-lg group-hover:bg-white/30 transition">
            {icon}
          </div>
          <ArrowRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition text-white" />
        </div>
        <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
        <p className="text-white/80">{description}</p>
      </Card>
    </Link>
  )
}

interface QuickActionsProps {
  actions: QuickActionProps[]
}

export function QuickActions({ actions }: QuickActionsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {actions.map((action, index) => (
        <QuickAction key={index} {...action} />
      ))}
    </div>
  )
}

