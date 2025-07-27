'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { apiClient } from '../../lib/auth'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database, 
  MessageSquare, 
  Monitor, 
  Server, 
  Smartphone, 
  TrendingUp,
  Wifi,
  Zap
} from 'lucide-react'

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

interface SystemStatus {
  backend: string
  database: string
  sms_service: string
  sports_api: string
  alert_engine: string
}

interface DashboardData {
  liveMatchesCount: number
  todaysMatchesCount: number
  activeAlertsCount: number
  systemStatus: SystemStatus
  healthData: HealthData
}

export default function Dashboard() {
  const { data: session } = useSession()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchDashboardData = async () => {
    try {
      setError(null)
      
      // Fetch all dashboard data in parallel
      const [liveResponse, todayResponse, alertsResponse, statusResponse, healthResponse] = await Promise.all([
        apiClient.getLiveMatches(),
        apiClient.getTodaysMatches(),
        apiClient.getAlerts(),
        fetch('/api/status').then(res => res.json()),
        fetch('/health/detailed').then(res => res.json())
      ])

      const data: DashboardData = {
        liveMatchesCount: liveResponse.matches?.length || 0,
        todaysMatchesCount: todayResponse.matches?.length || 0,
        activeAlertsCount: alertsResponse.alerts?.filter((alert: any) => alert.is_active)?.length || 0,
        systemStatus: statusResponse,
        healthData: healthResponse
      }

      setDashboardData(data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'running':
      case 'configured':
        return 'text-green-500'
      case 'degraded':
        return 'text-yellow-500'
      case 'unhealthy':
      case 'stopped':
      case 'not_configured':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'running':
      case 'configured':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'unhealthy':
      case 'stopped':
      case 'not_configured':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getMetricColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'text-red-500'
    if (value >= thresholds.warning) return 'text-yellow-500'
    return 'text-green-500'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto"></div>
          <p className="text-white mt-4 text-lg">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-white text-xl mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-gray-300">
            Welcome back, {session?.user?.name || 'User'}! 
            {lastUpdated && (
              <span className="ml-2 text-sm text-gray-400">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Live Matches</p>
                <p className="text-3xl font-bold text-white">{dashboardData?.liveMatchesCount || 0}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Today's Matches</p>
                <p className="text-3xl font-bold text-white">{dashboardData?.todaysMatchesCount || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Active Alerts</p>
                <p className="text-3xl font-bold text-white">{dashboardData?.activeAlertsCount || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">System Status</p>
                <p className={`text-2xl font-bold ${getStatusColor(dashboardData?.healthData?.status || 'unknown')}`}>
                  {dashboardData?.healthData?.status || 'Unknown'}
                </p>
              </div>
              {getStatusIcon(dashboardData?.healthData?.status || 'unknown')}
            </div>
          </div>
        </div>

        {/* System Health */}
        {dashboardData?.healthData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* System Metrics */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <Monitor className="w-5 h-5 mr-2" />
                System Performance
              </h2>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">CPU Usage</span>
                    <span className={getMetricColor(dashboardData.healthData.system.cpu_percent, { warning: 70, critical: 90 })}>
                      {dashboardData.healthData.system.cpu_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        dashboardData.healthData.system.cpu_percent >= 90 ? 'bg-red-500' :
                        dashboardData.healthData.system.cpu_percent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData.system.cpu_percent, 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">Memory Usage</span>
                    <span className={getMetricColor(dashboardData.healthData.system.memory_percent, { warning: 80, critical: 95 })}>
                      {dashboardData.healthData.system.memory_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        dashboardData.healthData.system.memory_percent >= 95 ? 'bg-red-500' :
                        dashboardData.healthData.system.memory_percent >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData.system.memory_percent, 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">Disk Usage</span>
                    <span className={getMetricColor(dashboardData.healthData.system.disk_percent, { warning: 85, critical: 95 })}>
                      {dashboardData.healthData.system.disk_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        dashboardData.healthData.system.disk_percent >= 95 ? 'bg-red-500' :
                        dashboardData.healthData.system.disk_percent >= 85 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData.system.disk_percent, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Service Status */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <Server className="w-5 h-5 mr-2" />
                Service Status
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center">
                    <Database className="w-5 h-5 mr-3 text-blue-400" />
                    <span className="text-gray-300">Database</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData.database.connection_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData.database.connection_status ? 'Connected' : 'Disconnected'}
                    </span>
                    {getStatusIcon(dashboardData.healthData.database.connection_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center">
                    <Wifi className="w-5 h-5 mr-3 text-green-400" />
                    <span className="text-gray-300">Sports API</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData.api.sports_api_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData.api.sports_api_status ? 'Online' : 'Offline'}
                    </span>
                    {getStatusIcon(dashboardData.healthData.api.sports_api_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center">
                    <Smartphone className="w-5 h-5 mr-3 text-purple-400" />
                    <span className="text-gray-300">SMS Service</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData.api.sms_service_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData.api.sms_service_status ? 'Active' : 'Inactive'}
                    </span>
                    {getStatusIcon(dashboardData.healthData.api.sms_service_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center">
                    <Zap className="w-5 h-5 mr-3 text-yellow-400" />
                    <span className="text-gray-300">Alert Engine</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.systemStatus?.alert_engine || 'unknown')}`}>
                      {dashboardData.systemStatus?.alert_engine || 'Unknown'}
                    </span>
                    {getStatusIcon(dashboardData.systemStatus?.alert_engine || 'unknown')}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Alert Statistics */}
        {dashboardData?.healthData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                Alert Statistics
              </h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-white/5 rounded-lg">
                  <p className="text-2xl font-bold text-white">{dashboardData.healthData.alerts.alerts_triggered_today}</p>
                  <p className="text-sm text-gray-300">Triggered Today</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg">
                  <p className="text-2xl font-bold text-green-400">{dashboardData.healthData.alerts.sms_sent_today}</p>
                  <p className="text-sm text-gray-300">SMS Sent</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg">
                  <p className="text-2xl font-bold text-red-400">{dashboardData.healthData.alerts.sms_failed_today}</p>
                  <p className="text-sm text-gray-300">SMS Failed</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg">
                  <p className="text-2xl font-bold text-blue-400">{dashboardData.healthData.alerts.active_alerts}</p>
                  <p className="text-sm text-gray-300">Active Alerts</p>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Performance Metrics
              </h2>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Database Response</span>
                  <span className="text-white font-mono">
                    {dashboardData.healthData.database.response_time_ms.toFixed(2)}ms
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">API Errors (24h)</span>
                  <span className={`font-mono ${
                    dashboardData.healthData.api.error_count > 10 ? 'text-red-400' :
                    dashboardData.healthData.api.error_count > 5 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {dashboardData.healthData.api.error_count}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Last Health Check</span>
                  <span className="text-white text-sm">
                    {dashboardData.healthData.last_check ? 
                      new Date(dashboardData.healthData.last_check).toLocaleTimeString() : 
                      'Never'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => window.location.href = '/alerts'}
              className="p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition flex items-center justify-center"
            >
              <AlertTriangle className="w-5 h-5 mr-2" />
              Manage Alerts
            </button>
            <button 
              onClick={() => window.location.href = '/matches'}
              className="p-4 bg-green-600 hover:bg-green-700 text-white rounded-lg transition flex items-center justify-center"
            >
              <Activity className="w-5 h-5 mr-2" />
              View Matches
            </button>
            <button 
              onClick={() => window.location.href = '/settings'}
              className="p-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition flex items-center justify-center"
            >
              <Monitor className="w-5 h-5 mr-2" />
              Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
} 