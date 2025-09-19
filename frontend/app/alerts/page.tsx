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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Enhanced Header */}
      <div className="relative bg-white/10 backdrop-blur-xl border-b border-white/20 shadow-2xl">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="mb-6 md:mb-0">
              <div className="flex items-center space-x-6 mb-4">
                <Link href="/dashboard" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-110">
                  <ArrowLeft className="w-6 h-6" />
                </Link>
                <h1 className="text-4xl font-black text-gradient">Alerts</h1>
              </div>
              <p className="text-gray-300 text-lg">Manage your sports alerts and notifications</p>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchData}
                disabled={refreshing}
                className="btn-secondary flex items-center"
              >
                <RefreshCw className={`w-5 h-5 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <Link
                href="/alerts/create"
                className="btn-primary flex items-center"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create Alert
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Enhanced Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="card-elevated p-8 animate-scale-in group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-lg font-medium mb-2">Total Alerts</p>
                <p className="text-4xl font-black text-white group-hover:text-gradient-primary transition-all duration-300">
                  {stats.total}
                </p>
              </div>
              <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-4 rounded-2xl group-hover:from-blue-500/30 group-hover:to-blue-600/30 transition-all duration-300">
                <Bell className="w-10 h-10 text-blue-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
          </div>

          <div className="card-elevated p-8 animate-scale-in group" style={{animationDelay: '0.1s'}}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-lg font-medium mb-2">Active Alerts</p>
                <p className="text-4xl font-black text-white group-hover:text-gradient-secondary transition-all duration-300">
                  {stats.active}
                </p>
              </div>
              <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 p-4 rounded-2xl group-hover:from-green-500/30 group-hover:to-emerald-500/30 transition-all duration-300">
                <CheckCircle className="w-10 h-10 text-green-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
          </div>

          <div className="card-elevated p-8 animate-scale-in group" style={{animationDelay: '0.2s'}}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-lg font-medium mb-2">Triggered Today</p>
                <p className="text-4xl font-black text-white group-hover:text-gradient-accent transition-all duration-300">
                  {stats.triggered}
                </p>
              </div>
              <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 p-4 rounded-2xl group-hover:from-yellow-500/30 group-hover:to-orange-500/30 transition-all duration-300">
                <AlertTriangle className="w-10 h-10 text-yellow-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Controls */}
        <div className="mb-12">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            {/* Search and Filter */}
            <div className="flex items-center space-x-6">
              <div className="relative">
                <Search className="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search alerts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input-primary pl-12 pr-4 py-3 text-lg"
                />
              </div>

              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'inactive')}
                className="input-primary text-lg px-4 py-3"
              >
                <option value="all">All Alerts</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>

            {/* Enhanced View Mode */}
            <div className="flex bg-white/10 rounded-2xl p-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-3 rounded-xl transition-all duration-300 flex items-center space-x-2 ${
                  viewMode === 'grid'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <Grid className="w-5 h-5" />
                <span className="font-medium">Grid</span>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-3 rounded-xl transition-all duration-300 flex items-center space-x-2 ${
                  viewMode === 'list'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <List className="w-5 h-5" />
                <span className="font-medium">List</span>
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Alerts Grid/List */}
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-20 animate-fade-in">
            <div className="relative inline-block mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-full blur-2xl"></div>
              <div className="relative bg-white/10 backdrop-blur-xl rounded-full p-8 border border-white/20">
                <Bell className="w-20 h-20 text-gray-400" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-white mb-4">No alerts found</h3>
            <p className="text-gray-300 mb-8 text-lg max-w-md mx-auto">
              {searchTerm || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : "You haven't created any alerts yet"
              }
            </p>
            {!searchTerm && filter === 'all' && (
              <Link
                href="/alerts/create"
                className="btn-primary text-lg px-8 py-4 inline-flex items-center"
              >
                <Plus className="w-6 h-6 mr-3" />
                Create Your First Alert
              </Link>
            )}
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'
            : 'space-y-6'
          }>
            {filteredAlerts.map((alert, index) => 
              viewMode === 'grid' ? renderAlertCard(alert, index) : renderAlertList(alert, index)
            )}
          </div>
        )}
      </div>
    </div>
  )

  function renderAlertCard(alert: Alert, index: number) {
    return (
      <div key={alert.id} className="card-interactive p-8 animate-slide-in-up group" style={{animationDelay: `${index * 0.1}s`}}>
        {/* Enhanced Header */}
        <div className="flex items-center justify-between mb-6">
          <div className={`p-3 rounded-2xl bg-gradient-to-r ${getAlertTypeColor(alert.alert_type)} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
            {getAlertTypeIcon(alert.alert_type)}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => toggleAlert(alert.id)}
              className={`p-3 rounded-xl transition-all duration-300 ${
                alert.is_active 
                  ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30 hover:scale-110' 
                  : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 hover:scale-110'
              }`}
            >
              {alert.is_active ? <CheckCircle className="w-5 h-5" /> : <X className="w-5 h-5" />}
            </button>
            <button
              onClick={() => deleteAlert(alert.id)}
              className="p-3 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all duration-300 hover:scale-110"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Enhanced Content */}
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-gradient-primary transition-all duration-300">
            {alert.name}
          </h3>
          <p className="text-gray-300 text-lg mb-4">{alert.condition}</p>
          
          <div className="grid grid-cols-2 gap-4 text-lg">
            <div className="flex items-center text-gray-300 bg-white/5 p-3 rounded-xl">
              <Target className="w-5 h-5 mr-3 text-blue-400" />
              <span className="font-medium">{alert.team}</span>
            </div>
            <div className="flex items-center text-gray-300 bg-white/5 p-3 rounded-xl">
              <BarChart3 className="w-5 h-5 mr-3 text-green-400" />
              <span className="font-medium">{alert.alert_type}</span>
            </div>
          </div>
        </div>

        {/* Enhanced Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white/10 p-4 rounded-xl text-center group-hover:bg-white/15 transition-all duration-300">
            <div className="text-2xl font-bold text-white mb-1">{alert.trigger_count}</div>
            <div className="text-gray-400 font-medium">Triggers</div>
          </div>
          <div className="bg-white/10 p-4 rounded-xl text-center group-hover:bg-white/15 transition-all duration-300">
            <div className="text-2xl font-bold text-white mb-1">{alert.threshold}</div>
            <div className="text-gray-400 font-medium">Threshold</div>
          </div>
        </div>

        {/* Enhanced Footer */}
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span className="font-medium">Created: {formatDate(alert.created_at)}</span>
          {alert.last_triggered_at && (
            <span className="font-medium">Last: {formatDate(alert.last_triggered_at)}</span>
          )}
        </div>
      </div>
    )
  }

  function renderAlertList(alert: Alert, index: number) {
    return (
      <div key={alert.id} className="card p-6 animate-slide-in-up group" style={{animationDelay: `${index * 0.1}s`}}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className={`p-4 rounded-2xl bg-gradient-to-r ${getAlertTypeColor(alert.alert_type)} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
              {getAlertTypeIcon(alert.alert_type)}
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-gradient-primary transition-all duration-300">{alert.name}</h3>
              <div className="flex items-center space-x-6 text-lg text-gray-300">
                <div className="flex items-center">
                  <Target className="w-5 h-5 mr-2 text-blue-400" />
                  <span className="font-medium">{alert.team}</span>
                </div>
                <div className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-green-400" />
                  <span className="font-medium">{alert.alert_type}</span>
                </div>
                <div className="flex items-center">
                  <Bell className="w-5 h-5 mr-2 text-yellow-400" />
                  <span className="font-medium">{alert.trigger_count} triggers</span>
                </div>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => toggleAlert(alert.id)}
              className={`p-3 rounded-xl transition-all duration-300 ${
                alert.is_active 
                  ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30 hover:scale-110' 
                  : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 hover:scale-110'
              }`}
            >
              {alert.is_active ? <CheckCircle className="w-5 h-5" /> : <X className="w-5 h-5" />}
            </button>
            <button
              onClick={() => deleteAlert(alert.id)}
              className="p-3 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all duration-300 hover:scale-110"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    )
  }
} 