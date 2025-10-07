'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '../../lib/auth'
import Link from 'next/link'
import { 
  Database, 
  Users, 
  Bell, 
  Activity, 
  Terminal,
  ArrowLeft,
  RefreshCw,
  TrendingUp
} from 'lucide-react'

interface DatabaseStats {
  timestamp: string
  database_type: string
  tables: Record<string, number>
  summary: {
    active_users: number
    active_alerts: number
    live_matches: number
    total_users: number
    total_matches: number
    total_alerts: number
    total_alert_triggers: number
  }
}

interface UserAnalytics {
  id: number
  username: string
  email: string
  full_name: string
  created_at: string | null
  total_alerts: number
  active_alerts: number
  alert_triggers: number
}

interface MatchAnalytics {
  id: number
  home_team: string
  away_team: string
  league: string
  status: string
  home_score: number
  away_score: number
  start_time: string
  alerts_monitoring: number
}

interface AlertAnalytics {
  id: number
  name: string
  alert_type: string
  team: string
  condition: string
  threshold: number
  is_active: boolean
  created_at: string | null
  trigger_count: number
  last_triggered: string | null
}

export default function AdminPage() {
  const [stats, setStats] = useState<DatabaseStats | null>(null)
  const [users, setUsers] = useState<UserAnalytics[]>([])
  const [matches, setMatches] = useState<MatchAnalytics[]>([])
  const [alerts, setAlerts] = useState<AlertAnalytics[]>([])
  const [loading, setLoading] = useState(true)
  const [customQuery, setCustomQuery] = useState('')
  const [queryResult, setQueryResult] = useState<any>(null)
  const [activeView, setActiveView] = useState<'stats' | 'users' | 'matches' | 'alerts' | 'query'>('stats')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      const [statsResponse, usersResponse, matchesResponse, alertsResponse] = await Promise.all([
        apiClient.get('/admin/database/stats'),
        apiClient.get('/admin/database/users'),
        apiClient.get('/admin/database/matches'),
        apiClient.get('/admin/database/alerts')
      ])
      
      setStats(statsResponse)
      setUsers(usersResponse.users)
      setMatches(matchesResponse.matches)
      setAlerts(alertsResponse.alerts)
      
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const executeCustomQuery = async () => {
    if (!customQuery.trim()) return
    
    try {
      const response = await apiClient.post('/admin/database/query', {
        query: customQuery
      })
      setQueryResult(response.data)
    } catch (error) {
      console.error('Query error:', error)
      setQueryResult({ error: 'Query failed' })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <div className="text-white text-xl">Loading database analytics...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="bg-slate-900/50 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/" className="inline-flex items-center text-slate-400 hover:text-white transition-colors mb-4 group">
            <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to home
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Database Admin</h1>
              <p className="text-slate-400">Monitor and manage your TouchLine database</p>
            </div>
            <button
              onClick={loadData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all flex items-center gap-2 hover:shadow-lg hover:shadow-blue-500/50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-slate-900/30 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'stats', label: 'Overview', icon: <TrendingUp className="w-4 h-4" /> },
              { id: 'users', label: 'Users', icon: <Users className="w-4 h-4" /> },
              { id: 'matches', label: 'Matches', icon: <Activity className="w-4 h-4" /> },
              { id: 'alerts', label: 'Alerts', icon: <Bell className="w-4 h-4" /> },
              { id: 'query', label: 'SQL Query', icon: <Terminal className="w-4 h-4" /> }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 transition-colors ${
                  activeView === tab.id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-white'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeView === 'stats' && stats && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Database Overview</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="bg-slate-900/50 border border-blue-500/20 rounded-xl p-6 hover:bg-slate-900/70 transition-all hover:-translate-y-1">
                  <div className="text-3xl font-bold text-blue-400 mb-2">{stats.summary.total_users}</div>
                  <div className="text-sm text-slate-400">Total Users</div>
                </div>
                <div className="bg-slate-900/50 border border-green-500/20 rounded-xl p-6 hover:bg-slate-900/70 transition-all hover:-translate-y-1">
                  <div className="text-3xl font-bold text-green-400 mb-2">{stats.summary.active_users}</div>
                  <div className="text-sm text-slate-400">Active Users</div>
                </div>
                <div className="bg-slate-900/50 border border-yellow-500/20 rounded-xl p-6 hover:bg-slate-900/70 transition-all hover:-translate-y-1">
                  <div className="text-3xl font-bold text-yellow-400 mb-2">{stats.summary.total_alerts}</div>
                  <div className="text-sm text-slate-400">Total Alerts</div>
                </div>
                <div className="bg-slate-900/50 border border-red-500/20 rounded-xl p-6 hover:bg-slate-900/70 transition-all hover:-translate-y-1">
                  <div className="text-3xl font-bold text-red-400 mb-2">{stats.summary.live_matches}</div>
                  <div className="text-sm text-slate-400">Live Matches</div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Database Info</h2>
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <span className="text-slate-300">Database Type</span>
                    <span className="text-white font-semibold">{stats.database_type}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <span className="text-slate-300">Last Updated</span>
                    <span className="text-white font-semibold">{new Date(stats.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Table Statistics</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(stats.tables).map(([tableName, count]) => (
                  <div key={tableName} className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 hover:bg-slate-900/70 transition-all">
                    <div className="text-lg font-bold text-white mb-1">{count.toLocaleString()}</div>
                    <div className="text-sm text-slate-400 capitalize">{tableName.replace(/_/g, ' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeView === 'users' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">User Analytics</h2>
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Username</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Email</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Total Alerts</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Active Alerts</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Triggers</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user, idx) => (
                      <tr key={user.id} className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="py-4 px-6 text-white font-medium">{user.username}</td>
                        <td className="py-4 px-6 text-slate-300">{user.email}</td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm font-medium">
                            {user.total_alerts}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm font-medium">
                            {user.active_alerts}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-slate-300">{user.alert_triggers}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Matches Tab */}
        {activeView === 'matches' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Match Analytics</h2>
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Match</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">League</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Status</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Score</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Alerts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {matches.map((match) => (
                      <tr key={match.id} className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="py-4 px-6">
                          <div className="text-white font-medium">{match.home_team} vs {match.away_team}</div>
                        </td>
                        <td className="py-4 px-6 text-slate-300">{match.league}</td>
                        <td className="py-4 px-6">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            match.status === 'live' 
                              ? 'bg-green-500/10 text-green-400' 
                              : 'bg-slate-500/10 text-slate-400'
                          }`}>
                            {match.status}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-white font-semibold">{match.home_score} - {match.away_score}</td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm font-medium">
                            {match.alerts_monitoring}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeView === 'alerts' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Alert Analytics</h2>
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Name</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Type</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Team</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Condition</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Triggers</th>
                      <th className="py-3 px-6 text-left text-sm font-semibold text-slate-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.map((alert) => (
                      <tr key={alert.id} className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="py-4 px-6 text-white font-medium">{alert.name}</td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-sm font-medium">
                            {alert.alert_type}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-slate-300">{alert.team}</td>
                        <td className="py-4 px-6 text-slate-400 text-sm">{alert.condition}</td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 text-sm font-medium">
                            {alert.trigger_count}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            alert.is_active 
                              ? 'bg-green-500/10 text-green-400' 
                              : 'bg-slate-500/10 text-slate-400'
                          }`}>
                            {alert.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* SQL Query Tab */}
        {activeView === 'query' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Custom SQL Query</h2>
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                <textarea
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  placeholder="SELECT * FROM users WHERE is_active = true;"
                  className="w-full h-48 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all p-4 font-mono text-sm"
                />
                <button
                  onClick={executeCustomQuery}
                  className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 hover:shadow-lg hover:shadow-blue-500/50"
                >
                  <Terminal className="w-4 h-4" />
                  Execute Query
                </button>
              </div>
            </div>

            {queryResult && (
              <div>
                <h3 className="text-xl font-bold text-white mb-4">Query Results</h3>
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 overflow-auto">
                  <pre className="text-sm text-slate-300 font-mono">
                    {JSON.stringify(queryResult, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
