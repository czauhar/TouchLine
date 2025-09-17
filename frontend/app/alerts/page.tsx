'use client'

import { useState, useEffect } from 'react'
import { useSession, signIn } from 'next-auth/react'
import { apiClient } from '../../lib/auth'
import Link from 'next/link'
import { 
  Target, 
  Plus, 
  Settings, 
  Trash2, 
  ToggleLeft, 
  ToggleRight,
  BarChart3,
  Clock,
  Bell,
  AlertTriangle,
  Zap,
  TrendingUp,
  Activity,
  Users,
  MapPin,
  Calendar,
  Eye,
  Edit,
  Filter,
  Search,
  ArrowLeft,
  RefreshCw,
  Grid,
  List,
  CheckCircle,
  X,
  Info,
  Shield,
  Smartphone,
  Mail
} from 'lucide-react'

interface Alert {
  id: number
  name: string
  is_active: boolean
  condition: string
  created_at: string
  team: string
  alert_type: string
  threshold: number
  trigger_count: number
  last_triggered_at: string | null
}

interface Match {
  id: number
  external_id: string
  home_team: string
  away_team: string
  league: string
  start_time: string
  status: string
  elapsed: number
  home_score: number
  away_score: number
  venue: string
  referee: string
  alert_metrics: any
}

export default function AlertsPage() {
  const { data: session, status } = useSession()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      signIn()
      return
    }
    
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [session, status])

  const fetchData = async () => {
    try {
      setRefreshing(true)
      const [alertsData, matchesData] = await Promise.all([
        apiClient.getAlerts(),
        apiClient.getLiveMatches()
      ])
      setAlerts(alertsData.alerts || [])
      setMatches(matchesData.matches || [])
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const toggleAlert = async (alertId: number) => {
    try {
      await apiClient.toggleAlert(alertId)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error toggling alert:', error)
    }
  }

  const deleteAlert = async (alertId: number) => {
    if (!confirm('Are you sure you want to delete this alert?')) return
    
    try {
      await apiClient.deleteAlert(alertId)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error deleting alert:', error)
    }
  }

  const getAlertStats = () => {
    const total = alerts.length
    const active = alerts.filter(alert => alert.is_active).length
    const triggered = alerts.filter(alert => alert.trigger_count > 0).length
    return { total, active, triggered }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getAlertTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goal': return <Target className="w-5 h-5 text-red-400" />
      case 'score': return <BarChart3 className="w-5 h-5 text-blue-400" />
      case 'xg': return <TrendingUp className="w-5 h-5 text-green-400" />
      case 'pressure': return <Zap className="w-5 h-5 text-yellow-400" />
      case 'momentum': return <Activity className="w-5 h-5 text-purple-400" />
      default: return <Bell className="w-5 h-5 text-gray-400" />
    }
  }

  const getAlertTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goal': return 'from-red-500 to-red-600'
      case 'score': return 'from-blue-500 to-blue-600'
      case 'xg': return 'from-green-500 to-green-600'
      case 'pressure': return 'from-yellow-500 to-yellow-600'
      case 'momentum': return 'from-purple-500 to-purple-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = searchTerm === '' || 
      alert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.team.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.alert_type.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filter === 'all' || 
      (filter === 'active' && alert.is_active) ||
      (filter === 'inactive' && !alert.is_active)
    
    return matchesSearch && matchesFilter
  })

  const stats = getAlertStats()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto"></div>
          <p className="text-white mt-4 text-lg">Loading alerts...</p>
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
              <div className="flex items-center space-x-4 mb-2">
                <Link href="/dashboard" className="text-gray-300 hover:text-white transition">
                  <ArrowLeft className="w-5 h-5" />
                </Link>
                <h1 className="text-3xl font-bold text-white">Alerts</h1>
              </div>
              <p className="text-gray-300">Manage your sports alerts and notifications</p>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchData}
                disabled={refreshing}
                className="flex items-center bg-white/10 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition border border-white/20"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <Link
                href="/alerts/create"
                className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Alert
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Alerts</p>
                <p className="text-3xl font-bold text-white group-hover:text-blue-400 transition">
                  {stats.total}
                </p>
              </div>
              <div className="bg-blue-500/20 p-3 rounded-lg group-hover:bg-blue-500/30 transition">
                <Bell className="w-8 h-8 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Active Alerts</p>
                <p className="text-3xl font-bold text-white group-hover:text-green-400 transition">
                  {stats.active}
                </p>
              </div>
              <div className="bg-green-500/20 p-3 rounded-lg group-hover:bg-green-500/30 transition">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Triggered Today</p>
                <p className="text-3xl font-bold text-white group-hover:text-yellow-400 transition">
                  {stats.triggered}
                </p>
              </div>
              <div className="bg-yellow-500/20 p-3 rounded-lg group-hover:bg-yellow-500/30 transition">
                <AlertTriangle className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search and Filter */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search alerts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-white/10 text-white pl-10 pr-4 py-2 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'inactive')}
                className="bg-white/10 text-white px-4 py-2 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Alerts</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>

            {/* View Mode */}
            <div className="flex bg-white/10 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Alerts Grid/List */}
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No alerts found</h3>
            <p className="text-gray-300 mb-6">
              {searchTerm || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : "You haven't created any alerts yet"
              }
            </p>
            {!searchTerm && filter === 'all' && (
              <Link
                href="/alerts/create"
                className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Alert
              </Link>
            )}
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }>
            {filteredAlerts.map(alert => 
              viewMode === 'grid' ? renderAlertCard(alert) : renderAlertList(alert)
            )}
          </div>
        )}
      </div>
    </div>
  )

  function renderAlertCard(alert: Alert) {
    return (
      <div key={alert.id} className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 group">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className={`p-2 rounded-lg bg-gradient-to-r ${getAlertTypeColor(alert.alert_type)}`}>
            {getAlertTypeIcon(alert.alert_type)}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => toggleAlert(alert.id)}
              className={`p-2 rounded-lg transition ${
                alert.is_active 
                  ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                  : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
              }`}
            >
              {alert.is_active ? <CheckCircle className="w-4 h-4" /> : <X className="w-4 h-4" />}
            </button>
            <button
              onClick={() => deleteAlert(alert.id)}
              className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-400 transition">
            {alert.name}
          </h3>
          <p className="text-gray-300 text-sm mb-3">{alert.condition}</p>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center text-gray-300">
              <Target className="w-4 h-4 mr-2 text-blue-400" />
              <span>{alert.team}</span>
            </div>
            <div className="flex items-center text-gray-300">
              <BarChart3 className="w-4 h-4 mr-2 text-green-400" />
              <span>{alert.alert_type}</span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
          <div className="bg-white/5 p-3 rounded-lg text-center">
            <div className="text-white font-bold">{alert.trigger_count}</div>
            <div className="text-gray-400">Triggers</div>
          </div>
          <div className="bg-white/5 p-3 rounded-lg text-center">
            <div className="text-white font-bold">{alert.threshold}</div>
            <div className="text-gray-400">Threshold</div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Created: {formatDate(alert.created_at)}</span>
          {alert.last_triggered_at && (
            <span>Last: {formatDate(alert.last_triggered_at)}</span>
          )}
        </div>
      </div>
    )
  }

  function renderAlertList(alert: Alert) {
    return (
      <div key={alert.id} className="bg-white/10 backdrop-blur-xl rounded-lg p-4 border border-white/20 hover:bg-white/15 transition">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`p-2 rounded-lg bg-gradient-to-r ${getAlertTypeColor(alert.alert_type)}`}>
              {getAlertTypeIcon(alert.alert_type)}
            </div>
            <div>
              <h3 className="text-white font-semibold">{alert.name}</h3>
              <div className="flex items-center space-x-4 mt-1 text-sm text-gray-300">
                <span>{alert.team}</span>
                <span>•</span>
                <span>{alert.alert_type}</span>
                <span>•</span>
                <span>{alert.trigger_count} triggers</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => toggleAlert(alert.id)}
              className={`p-2 rounded-lg transition ${
                alert.is_active 
                  ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                  : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
              }`}
            >
              {alert.is_active ? <CheckCircle className="w-4 h-4" /> : <X className="w-4 h-4" />}
            </button>
            <button
              onClick={() => deleteAlert(alert.id)}
              className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    )
  }
} 