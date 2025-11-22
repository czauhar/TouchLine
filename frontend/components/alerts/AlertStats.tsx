import React from 'react'
import { StatCard } from '../ui/StatCard'
import { Bell, BellOff, Zap, TrendingUp } from 'lucide-react'

interface AlertStatsProps {
  stats: {
    total_alerts: number
    active_alerts: number
    inactive_alerts: number
  }
}

export function AlertStats({ stats }: AlertStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <StatCard
        title="Total Alerts"
        value={stats.total_alerts}
        icon={<Zap className="w-6 h-6" />}
        color="blue"
      />
      <StatCard
        title="Active Alerts"
        value={stats.active_alerts}
        icon={<Bell className="w-6 h-6" />}
        color="green"
      />
      <StatCard
        title="Inactive Alerts"
        value={stats.inactive_alerts}
        icon={<BellOff className="w-6 h-6" />}
        color="default"
      />
    </div>
  )
}

