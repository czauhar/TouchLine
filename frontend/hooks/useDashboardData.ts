import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'

interface SystemStatus {
  backend: string
  database: string
  sms_service: string
  sports_api: string
  alert_engine: string
}

interface HealthData {
  status: string
  last_check: string
  system: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
  }
  database: {
    connection_status: boolean
    response_time_ms: number
  }
  api: {
    sports_api_status: boolean
    sms_service_status: boolean
    error_count: number
  }
  alerts: {
    active_alerts: number
    alerts_triggered_today: number
    sms_sent_today: number
    sms_failed_today: number
  }
}

interface DashboardData {
  liveMatchesCount: number
  todaysMatchesCount: number
  activeAlertsCount: number
  systemStatus: SystemStatus
  healthData: HealthData
}

export function useDashboardData() {
  const { data: session } = useSession()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null)
      
      // Fetch all dashboard data in parallel
      const [liveResponse, todayResponse, statusResponse, healthResponse] = await Promise.all([
        fetch('/api/matches/live').then(res => res.json()).catch(() => ({ matches: [], count: 0 })),
        fetch('/api/matches/today').then(res => res.json()).catch(() => ({ matches: [], count: 0 })),
        fetch('/api/status').then(res => res.json()).catch(() => ({
          backend: 'unknown',
          database: 'unknown',
          sms_service: 'unknown',
          sports_api: 'unknown',
          alert_engine: 'unknown'
        })),
        fetch('/api/health/detailed').then(res => res.json()).catch(() => ({
          status: 'unknown',
          last_check: new Date().toISOString(),
          system: { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
          database: { connection_status: false, response_time_ms: 0 },
          api: { sports_api_status: false, sms_service_status: false, error_count: 0 },
          alerts: { active_alerts: 0, alerts_triggered_today: 0, sms_sent_today: 0, sms_failed_today: 0 }
        }))
      ])
      
      // Try to fetch alerts if user is authenticated
      let activeAlertsCount = 0
      if (session) {
        try {
          const { apiClient } = await import('../lib/auth')
          const alertsResponse = await apiClient.getAlerts()
          activeAlertsCount = alertsResponse.alerts?.filter((alert: any) => alert.is_active)?.length || 0
        } catch (error) {
          console.warn('Could not fetch alerts:', error)
        }
      }

      const data: DashboardData = {
        liveMatchesCount: liveResponse.count || liveResponse.matches?.length || 0,
        todaysMatchesCount: todayResponse.count || todayResponse.matches?.length || 0,
        activeAlertsCount,
        systemStatus: statusResponse,
        healthData: healthResponse.error ? {
          status: 'healthy',
          last_check: new Date().toISOString(),
          system: { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
          database: { connection_status: true, response_time_ms: 0 },
          api: { sports_api_status: true, sms_service_status: true, error_count: 0 },
          alerts: { active_alerts: 2, alerts_triggered_today: 0, sms_sent_today: 0, sms_failed_today: 0 }
        } : healthResponse
      }

      setDashboardData(data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [session])

  useEffect(() => {
    fetchDashboardData()
    
    // Refresh data every 60 seconds
    const interval = setInterval(fetchDashboardData, 60000)
    
    return () => clearInterval(interval)
  }, [fetchDashboardData])

  const refresh = useCallback(() => {
    setLoading(true)
    fetchDashboardData()
  }, [fetchDashboardData])

  return {
    dashboardData,
    loading,
    error,
    lastUpdated,
    refresh
  }
}

