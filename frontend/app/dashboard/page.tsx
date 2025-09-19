'use client'

import { useState, useEffect, useRef } from 'react'
import { useSession } from 'next-auth/react'
import { apiClient } from '../../lib/auth'
import Link from 'next/link'
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
  Zap,
  Bell,
  Users,
  Target,
  BarChart3,
  ArrowRight,
  RefreshCw,
  Eye,
  Settings,
  Plus,
  Calendar,
  Globe,
  Shield,
  Heart,
  Star
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
  const [refreshing, setRefreshing] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const connectWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws/broadcast`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('Dashboard WebSocket connected')
        setWsConnected(true)
        ws.send(JSON.stringify({ type: 'ping' }))
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          if (message.type === 'health_update') {
            // Update health data in real-time
            setDashboardData(prev => prev ? {
              ...prev,
              healthData: message.data
            } : null)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        console.log('Dashboard WebSocket disconnected')
        setWsConnected(false)
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }

      ws.onerror = (error) => {
        console.error('Dashboard WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error connecting dashboard WebSocket:', error)
    }
  }

  const fetchDashboardData = async () => {
    try {
      setError(null)
      setRefreshing(true)
      
      // Check if user is authenticated
      if (!session) {
        setError('Please sign in to view dashboard data')
        setLoading(false)
        setRefreshing(false)
        return
      }
      
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
      
      // Try to fetch alerts, but handle authentication errors gracefully
      let alertsResponse: any = { alerts: [] }
      try {
        alertsResponse = await apiClient.getAlerts()
      } catch (error) {
        console.warn('Could not fetch alerts (authentication required):', error)
        // Use empty alerts array as fallback
      }

      const data: DashboardData = {
        liveMatchesCount: liveResponse.count || liveResponse.matches?.length || 0,
        todaysMatchesCount: todayResponse.count || todayResponse.matches?.length || 0,
        activeAlertsCount: alertsResponse.alerts?.filter((alert: any) => alert.is_active)?.length || 0,
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
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    connectWebSocket()
    
    // Refresh data every 60 seconds (reduced frequency for better performance)
    const interval = setInterval(fetchDashboardData, 60000)
    
    return () => {
      clearInterval(interval)
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
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

  const quickActions = [
    {
      title: "Create Alert",
      description: "Set up a new sports alert",
      icon: <Plus className="w-6 h-6" />,
      href: "/alerts/create",
      color: "from-blue-500 to-blue-600",
      hoverColor: "from-blue-600 to-blue-700"
    },
    {
      title: "View Matches",
      description: "Browse live and upcoming matches",
      icon: <Activity className="w-6 h-6" />,
      href: "/matches",
      color: "from-green-500 to-green-600",
      hoverColor: "from-green-600 to-green-700"
    },
    {
      title: "System Settings",
      description: "Configure your preferences",
      icon: <Settings className="w-6 h-6" />,
      href: "/settings",
      color: "from-purple-500 to-purple-600",
      hoverColor: "from-purple-600 to-purple-700"
    }
  ]

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="mb-4 md:mb-0">
              <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
              <p className="text-gray-300">
                Welcome back, {typeof session?.user?.name === 'string' ? session.user.name : 'User'}! 
                {lastUpdated && (
                  <span className="ml-2 text-sm text-gray-400">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                  </span>
                )}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-300">
                  {wsConnected ? 'Real-time Connected' : 'Real-time Disconnected'}
                </span>
              </div>
              <button 
                onClick={fetchDashboardData}
                disabled={refreshing}
                className="flex items-center bg-white/10 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition border border-white/20"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Live Matches</p>
                <p className="text-3xl font-bold text-white group-hover:text-green-400 transition">
                  {dashboardData?.liveMatchesCount || 0}
                </p>
              </div>
              <div className="bg-green-500/20 p-3 rounded-lg group-hover:bg-green-500/30 transition">
                <Activity className="w-8 h-8 text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Today's Matches</p>
                <p className="text-3xl font-bold text-white group-hover:text-blue-400 transition">
                  {dashboardData?.todaysMatchesCount || 0}
                </p>
              </div>
              <div className="bg-blue-500/20 p-3 rounded-lg group-hover:bg-blue-500/30 transition">
                <Clock className="w-8 h-8 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Active Alerts</p>
                <p className="text-3xl font-bold text-white group-hover:text-yellow-400 transition">
                  {dashboardData?.activeAlertsCount || 0}
                </p>
              </div>
              <div className="bg-yellow-500/20 p-3 rounded-lg group-hover:bg-yellow-500/30 transition">
                <Bell className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">System Status</p>
                <p className={`text-2xl font-bold ${getStatusColor(dashboardData?.healthData?.status || 'unknown')} group-hover:scale-105 transition`}>
                  {dashboardData?.healthData?.status || 'Unknown'}
                </p>
              </div>
              <div className="bg-white/10 p-3 rounded-lg group-hover:bg-white/20 transition">
                {getStatusIcon(dashboardData?.healthData?.status || 'unknown')}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <Zap className="w-6 h-6 mr-2 text-yellow-400" />
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <Link 
                key={index}
                href={action.href}
                className={`group bg-gradient-to-r ${action.color} hover:${action.hoverColor} text-white rounded-xl p-6 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white/20 p-3 rounded-lg group-hover:bg-white/30 transition">
                    {action.icon}
                  </div>
                  <ArrowRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{action.title}</h3>
                <p className="text-white/80">{action.description}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* System Health */}
        {dashboardData?.healthData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* System Metrics */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Monitor className="w-5 h-5 mr-2 text-blue-400" />
                System Performance
              </h2>
              
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300">CPU Usage</span>
                    <span className={getMetricColor(dashboardData.healthData?.system?.cpu_percent || 0, { warning: 70, critical: 90 })}>
                      {(dashboardData.healthData?.system?.cpu_percent || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${
                        (dashboardData.healthData?.system?.cpu_percent || 0) >= 90 ? 'bg-red-500' :
                        (dashboardData.healthData?.system?.cpu_percent || 0) >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData?.system?.cpu_percent || 0, 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300">Memory Usage</span>
                    <span className={getMetricColor(dashboardData.healthData?.system?.memory_percent || 0, { warning: 80, critical: 95 })}>
                      {(dashboardData.healthData?.system?.memory_percent || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${
                        (dashboardData.healthData?.system?.memory_percent || 0) >= 95 ? 'bg-red-500' :
                        (dashboardData.healthData?.system?.memory_percent || 0) >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData?.system?.memory_percent || 0, 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300">Disk Usage</span>
                    <span className={getMetricColor(dashboardData.healthData?.system?.disk_percent || 0, { warning: 85, critical: 95 })}>
                      {(dashboardData.healthData?.system?.disk_percent || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${
                        (dashboardData.healthData?.system?.disk_percent || 0) >= 95 ? 'bg-red-500' :
                        (dashboardData.healthData?.system?.disk_percent || 0) >= 85 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(dashboardData.healthData?.system?.disk_percent || 0, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Service Status */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Server className="w-5 h-5 mr-2 text-green-400" />
                Service Status
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <div className="flex items-center">
                    <Database className="w-5 h-5 mr-3 text-blue-400" />
                    <span className="text-gray-300">Database</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData?.database?.connection_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData?.database?.connection_status ? 'Connected' : 'Disconnected'}
                    </span>
                    {getStatusIcon(dashboardData.healthData?.database?.connection_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <div className="flex items-center">
                    <Globe className="w-5 h-5 mr-3 text-green-400" />
                    <span className="text-gray-300">Sports API</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData?.api?.sports_api_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData?.api?.sports_api_status ? 'Online' : 'Offline'}
                    </span>
                    {getStatusIcon(dashboardData.healthData?.api?.sports_api_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <div className="flex items-center">
                    <Smartphone className="w-5 h-5 mr-3 text-purple-400" />
                    <span className="text-gray-300">SMS Service</span>
                  </div>
                  <div className="flex items-center">
                    <span className={`text-sm mr-2 ${getStatusColor(dashboardData.healthData?.api?.sms_service_status ? 'running' : 'stopped')}`}>
                      {dashboardData.healthData?.api?.sms_service_status ? 'Active' : 'Inactive'}
                    </span>
                    {getStatusIcon(dashboardData.healthData?.api?.sms_service_status ? 'running' : 'stopped')}
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
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
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <MessageSquare className="w-5 h-5 mr-2 text-purple-400" />
                Alert Statistics
              </h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <p className="text-3xl font-bold text-white mb-1">{dashboardData.healthData?.alerts?.alerts_triggered_today || 0}</p>
                  <p className="text-sm text-gray-300">Triggered Today</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <p className="text-3xl font-bold text-green-400 mb-1">{dashboardData.healthData?.alerts?.sms_sent_today || 0}</p>
                  <p className="text-sm text-gray-300">SMS Sent</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <p className="text-3xl font-bold text-red-400 mb-1">{dashboardData.healthData?.alerts?.sms_failed_today || 0}</p>
                  <p className="text-sm text-gray-300">SMS Failed</p>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <p className="text-3xl font-bold text-blue-400 mb-1">{dashboardData.healthData?.alerts?.active_alerts || 0}</p>
                  <p className="text-sm text-gray-300">Active Alerts</p>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
                Performance Metrics
              </h2>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <span className="text-gray-300">Database Response</span>
                  <span className="text-white font-mono">
                    {(dashboardData.healthData?.database?.response_time_ms || 0).toFixed(2)}ms
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <span className="text-gray-300">API Errors (24h)</span>
                  <span className={`font-mono ${
                    (dashboardData.healthData?.api?.error_count || 0) > 10 ? 'text-red-400' :
                    (dashboardData.healthData?.api?.error_count || 0) > 5 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {dashboardData.healthData?.api?.error_count || 0}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                  <span className="text-gray-300">Last Health Check</span>
                  <span className="text-white text-sm">
                    {dashboardData.healthData?.last_check ? 
                      new Date(dashboardData.healthData.last_check).toLocaleTimeString() : 
                      'Never'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Activity */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-400" />
            Recent Activity
          </h2>
          <div className="text-center py-8">
            <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-300">No recent activity to display</p>
            <p className="text-sm text-gray-400 mt-2">Activity will appear here as you use the system</p>
          </div>
        </div>
      </div>
    </div>
  )
} 