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
  Search
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

  const filteredAlerts = alerts.filter(alert => {
    const matchesFilter = filter === 'all' || 
      (filter === 'active' && alert.is_active) || 
      (filter === 'inactive' && !alert.is_active)
    
    const matchesSearch = alert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.condition.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesFilter && matchesSearch
  })

  const getAlertStats = () => {
    const total = alerts.length
    const active = alerts.filter(a => a.is_active).length
    const triggered = alerts.filter(a => a.trigger_count > 0).length
    const totalTriggers = alerts.reduce((sum, a) => sum + a.trigger_count, 0)
    
    return { total, active, triggered, totalTriggers }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getAlertTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goals': return <Target className="w-4 h-4" />
      case 'cards': return <AlertTriangle className="w-4 h-4" />
      case 'possession': return <Activity className="w-4 h-4" />
      case 'shots': return <BarChart3 className="w-4 h-4" />
      case 'momentum': return <TrendingUp className="w-4 h-4" />
      default: return <Bell className="w-4 h-4" />
    }
  }

  const getAlertTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goals': return 'text-green-400 bg-green-400/10'
      case 'cards': return 'text-yellow-400 bg-yellow-400/10'
      case 'possession': return 'text-blue-400 bg-blue-400/10'
      case 'shots': return 'text-purple-400 bg-purple-400/10'
      case 'momentum': return 'text-orange-400 bg-orange-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Access Required</h1>
          <p className="text-gray-300 mb-8">Please sign in to manage alerts</p>
          <button onClick={() => signIn()} className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition">
            Sign In
          </button>
        </div>
      </div>
    )
  }

  const stats = getAlertStats()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Alert Center</h1>
              <p className="text-gray-300">Manage your sports alerts and notifications</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Alert
              </button>
              <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Target className="w-6 h-6 text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Total Alerts</p>
                <p className="text-2xl font-bold text-white">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <ToggleRight className="w-6 h-6 text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Active Alerts</p>
                <p className="text-2xl font-bold text-white">{stats.active}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-500/20 rounded-lg">
                <Bell className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Triggered Alerts</p>
                <p className="text-2xl font-bold text-white">{stats.triggered}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <Zap className="w-6 h-6 text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Total Triggers</p>
                <p className="text-2xl font-bold text-white">{stats.totalTriggers}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row items-center justify-between mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  filter === 'all' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                All ({alerts.length})
              </button>
              <button
                onClick={() => setFilter('active')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  filter === 'active' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Active ({alerts.filter(a => a.is_active).length})
              </button>
              <button
                onClick={() => setFilter('inactive')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  filter === 'inactive' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Inactive ({alerts.filter(a => !a.is_active).length})
              </button>
            </div>

            <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                List
              </button>
            </div>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Alerts Grid/List */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="animate-pulse bg-white/10 rounded-xl h-48"></div>
            ))}
          </div>
        ) : viewMode === 'list' ? (
          <div className="space-y-4">
            {filteredAlerts.map((alert) => (
              <div key={alert.id} className="bg-white/10 backdrop-blur-xl rounded-lg p-6 border border-white/20 hover:bg-white/15 transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${getAlertTypeColor(alert.alert_type)}`}>
                      {getAlertTypeIcon(alert.alert_type)}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">{alert.name}</h3>
                      <p className="text-gray-300 text-sm">{alert.condition}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                        <span>Team: {alert.team || 'Any'}</span>
                        <span>Type: {alert.alert_type}</span>
                        <span>Threshold: {alert.threshold}</span>
                        <span>Triggers: {alert.trigger_count}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm text-gray-300">Created</p>
                      <p className="text-xs text-gray-400">{formatDate(alert.created_at)}</p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleAlert(alert.id)}
                        className={`p-2 rounded-lg transition ${
                          alert.is_active 
                            ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30' 
                            : 'bg-gray-600/20 text-gray-400 hover:bg-gray-600/30'
                        }`}
                      >
                        {alert.is_active ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                      </button>
                      
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="p-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => deleteAlert(alert.id)}
                        className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAlerts.map((alert) => (
              <div key={alert.id} className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-2 rounded-lg ${getAlertTypeColor(alert.alert_type)}`}>
                    {getAlertTypeIcon(alert.alert_type)}
                  </div>
                  <div className={`w-2 h-2 rounded-full ${alert.is_active ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                </div>

                {/* Content */}
                <div className="mb-4">
                  <h3 className="text-lg font-bold text-white mb-2">{alert.name}</h3>
                  <p className="text-gray-300 text-sm mb-3">{alert.condition}</p>
                  
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-400">Team:</span>
                      <span className="text-white ml-1">{alert.team || 'Any'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white ml-1">{alert.alert_type}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Threshold:</span>
                      <span className="text-white ml-1">{alert.threshold}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Triggers:</span>
                      <span className="text-white ml-1">{alert.trigger_count}</span>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-400">
                    {formatDate(alert.created_at)}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleAlert(alert.id)}
                      className={`p-1 rounded transition ${
                        alert.is_active 
                          ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30' 
                          : 'bg-gray-600/20 text-gray-400 hover:bg-gray-600/30'
                      }`}
                    >
                      {alert.is_active ? <ToggleRight className="w-3 h-3" /> : <ToggleLeft className="w-3 h-3" />}
                    </button>
                    
                    <button
                      onClick={() => setSelectedAlert(alert)}
                      className="p-1 bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600/30 transition"
                    >
                      <Eye className="w-3 h-3" />
                    </button>
                    
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="p-1 bg-red-600/20 text-red-400 rounded hover:bg-red-600/30 transition"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredAlerts.length === 0 && !loading && (
          <div className="text-center py-16">
            <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No alerts found</h3>
            <p className="text-gray-300 mb-6">
              {searchTerm ? 'No alerts match your search criteria.' : 'You haven\'t created any alerts yet.'}
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition flex items-center mx-auto"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Alert
            </button>
          </div>
        )}
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Alert Details</h2>
              <button
                onClick={() => setSelectedAlert(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Alert Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Name:</span>
                    <span className="text-white ml-2">{selectedAlert.name}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="text-white ml-2">{selectedAlert.alert_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Team:</span>
                    <span className="text-white ml-2">{selectedAlert.team || 'Any'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Threshold:</span>
                    <span className="text-white ml-2">{selectedAlert.threshold}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className={`ml-2 ${selectedAlert.is_active ? 'text-green-400' : 'text-gray-400'}`}>
                      {selectedAlert.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Triggers:</span>
                    <span className="text-white ml-2">{selectedAlert.trigger_count}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Condition</h3>
                <p className="text-gray-300">{selectedAlert.condition}</p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Timeline</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Created:</span>
                    <span className="text-white">{formatDate(selectedAlert.created_at)}</span>
                  </div>
                  {selectedAlert.last_triggered_at && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Last Triggered:</span>
                      <span className="text-white">{formatDate(selectedAlert.last_triggered_at)}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => toggleAlert(selectedAlert.id)}
                  className={`flex-1 px-4 py-2 rounded-lg transition ${
                    selectedAlert.is_active 
                      ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  {selectedAlert.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  onClick={() => deleteAlert(selectedAlert.id)}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
                >
                  Delete Alert
                </button>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Create New Alert</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="text-center py-8">
              <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Advanced Alert Creation</h3>
              <p className="text-gray-300 mb-6">
                Create sophisticated alerts with detailed statistics, referee conditions, and advanced metrics.
              </p>
              <Link
                href="/alerts/create"
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition inline-flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Start Creating Alert
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 