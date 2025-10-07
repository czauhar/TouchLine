'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '../../lib/auth'

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

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load database stats
      const statsResponse = await apiClient.get('/admin/database/stats')
      setStats(statsResponse.data)
      
      // Load user analytics
      const usersResponse = await apiClient.get('/admin/database/users')
      setUsers(usersResponse.data.users)
      
      // Load match analytics
      const matchesResponse = await apiClient.get('/admin/database/matches')
      setMatches(matchesResponse.data.matches)
      
      // Load alert analytics
      const alertsResponse = await apiClient.get('/admin/database/alerts')
      setAlerts(alertsResponse.data.alerts)
      
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
        <div className="text-white text-xl">Loading database analytics...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Database Admin</h1>
        
        {/* Database Stats */}
        {stats && (
          <div className="bg-slate-900 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Database Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800 rounded p-4">
                <div className="text-2xl font-bold text-blue-400">{stats.summary.total_users}</div>
                <div className="text-sm text-slate-400">Total Users</div>
              </div>
              <div className="bg-slate-800 rounded p-4">
                <div className="text-2xl font-bold text-green-400">{stats.summary.active_users}</div>
                <div className="text-sm text-slate-400">Active Users</div>
              </div>
              <div className="bg-slate-800 rounded p-4">
                <div className="text-2xl font-bold text-yellow-400">{stats.summary.total_alerts}</div>
                <div className="text-sm text-slate-400">Total Alerts</div>
              </div>
              <div className="bg-slate-800 rounded p-4">
                <div className="text-2xl font-bold text-red-400">{stats.summary.live_matches}</div>
                <div className="text-sm text-slate-400">Live Matches</div>
              </div>
            </div>
          </div>
        )}

        {/* Custom Query */}
        <div className="bg-slate-900 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Custom SQL Query</h2>
          <div className="space-y-4">
            <textarea
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="SELECT * FROM users WHERE is_active = true;"
              className="w-full h-32 bg-slate-800 text-white p-4 rounded border border-slate-700"
            />
            <button
              onClick={executeCustomQuery}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
            >
              Execute Query
            </button>
          </div>
          
          {queryResult && (
            <div className="mt-4">
              <h3 className="text-lg font-bold mb-2">Query Results:</h3>
              <pre className="bg-slate-800 p-4 rounded overflow-auto max-h-64">
                {JSON.stringify(queryResult, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* User Analytics */}
        <div className="bg-slate-900 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">User Analytics</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left p-2">Username</th>
                  <th className="text-left p-2">Email</th>
                  <th className="text-left p-2">Total Alerts</th>
                  <th className="text-left p-2">Active Alerts</th>
                  <th className="text-left p-2">Triggers</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-slate-700">
                    <td className="p-2">{user.username}</td>
                    <td className="p-2">{user.email}</td>
                    <td className="p-2">{user.total_alerts}</td>
                    <td className="p-2">{user.active_alerts}</td>
                    <td className="p-2">{user.alert_triggers}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Match Analytics */}
        <div className="bg-slate-900 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Match Analytics</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left p-2">Match</th>
                  <th className="text-left p-2">League</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Score</th>
                  <th className="text-left p-2">Alerts</th>
                </tr>
              </thead>
              <tbody>
                {matches.map((match) => (
                  <tr key={match.id} className="border-b border-slate-700">
                    <td className="p-2">{match.home_team} vs {match.away_team}</td>
                    <td className="p-2">{match.league}</td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        match.status === 'live' ? 'bg-red-600' : 
                        match.status === 'finished' ? 'bg-gray-600' : 'bg-yellow-600'
                      }`}>
                        {match.status}
                      </span>
                    </td>
                    <td className="p-2">{match.home_score} - {match.away_score}</td>
                    <td className="p-2">{match.alerts_monitoring}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Alert Analytics */}
        <div className="bg-slate-900 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Alert Analytics</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Type</th>
                  <th className="text-left p-2">Team</th>
                  <th className="text-left p-2">Condition</th>
                  <th className="text-left p-2">Triggers</th>
                  <th className="text-left p-2">Active</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id} className="border-b border-slate-700">
                    <td className="p-2">{alert.name}</td>
                    <td className="p-2">{alert.alert_type}</td>
                    <td className="p-2">{alert.team}</td>
                    <td className="p-2">{alert.condition}</td>
                    <td className="p-2">{alert.trigger_count}</td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        alert.is_active ? 'bg-green-600' : 'bg-gray-600'
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
    </div>
  )
}
