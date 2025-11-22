import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { CheckCircle, AlertTriangle, XCircle, Server, Database, Globe, Smartphone } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ServiceStatus {
  name: string
  status: 'healthy' | 'degraded' | 'unhealthy'
  icon: React.ReactNode
  details?: string
}

interface SystemHealthProps {
  services: ServiceStatus[]
  className?: string
}

export function SystemHealth({ services, className }: SystemHealthProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-400'
      case 'degraded':
        return 'text-yellow-400'
      case 'unhealthy':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <Card variant="glass" className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="w-5 h-5 text-green-400" />
          System Health
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {services.map((service, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition"
            >
              <div className="flex items-center gap-3">
                <div className="text-slate-400">
                  {service.icon}
                </div>
                <div>
                  <p className="text-white font-medium">{service.name}</p>
                  {service.details && (
                    <p className="text-sm text-slate-400">{service.details}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={cn('text-sm font-medium capitalize', getStatusColor(service.status))}>
                  {service.status}
                </span>
                {getStatusIcon(service.status)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface SystemMetricsProps {
  metrics: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
  }
}

export function SystemMetrics({ metrics }: SystemMetricsProps) {
  const getMetricColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'bg-red-500'
    if (value >= thresholds.warning) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const metricData = [
    { label: 'CPU Usage', value: metrics.cpu_percent, thresholds: { warning: 70, critical: 90 } },
    { label: 'Memory Usage', value: metrics.memory_percent, thresholds: { warning: 80, critical: 95 } },
    { label: 'Disk Usage', value: metrics.disk_percent, thresholds: { warning: 85, critical: 95 } }
  ]

  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle>System Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {metricData.map((metric, index) => (
            <div key={index}>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-300">{metric.label}</span>
                <span className={cn(
                  'font-mono',
                  metric.value >= metric.thresholds.critical ? 'text-red-400' :
                  metric.value >= metric.thresholds.warning ? 'text-yellow-400' : 'text-green-400'
                )}>
                  {metric.value.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3">
                <div
                  className={cn(
                    'h-3 rounded-full transition-all duration-500',
                    getMetricColor(metric.value, metric.thresholds)
                  )}
                  style={{ width: `${Math.min(metric.value, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

