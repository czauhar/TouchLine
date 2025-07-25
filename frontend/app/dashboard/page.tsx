'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { apiClient } from '../../lib/auth'
import Link from 'next/link'
import { 
  TrendingUp, 
  Zap, 
  Target, 
  Clock, 
  Users, 
  Activity,
  AlertTriangle,
  Trophy,
  Calendar,
  BarChart3
} from 'lucide-react'

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

interface Alert {
  id: number
  name: string
  is_active: boolean
  condition: string
  created_at: string
  team: string
  alert_type: string
  threshold: number
}

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const [liveMatches, setLiveMatches] = useState<Match[]>([])
  const [todaysMatches, setTodaysMatches] = useState<Match[]>([])
  const [userAlerts, setUserAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalMatches: 0,
    liveMatches: 0,
    activeAlerts: 0,
    totalGoals: 0
  })

  useEffect(() => {
    if (status === 'loading') return
    if (!session) return
    
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [session, status])

  const fetchDashboardData = async () => {
    try {
      const [liveData, todayData, alertsData] = await Promise.all([
        apiClient.getLiveMatches(),
        apiClient.getTodaysMatches(),
        apiClient.getAlerts()
      ])

      setLiveMatches(liveData.matches || [])
      setTodaysMatches(todayData.matches || [])
      setUserAlerts(alertsData.alerts || [])

      // Calculate stats
      const totalMatches = (liveData.matches || []).length + (todayData.matches || []).length
      const liveMatches = (liveData.matches || []).length
      const activeAlerts = (alertsData.alerts || []).filter((a: Alert) => a.is_active).length
      const totalGoals = [...(liveData.matches || []), ...(todayData.matches || [])]
        .reduce((sum, match) => sum + match.home_score + match.away_score, 0)

      setStats({ totalMatches, liveMatches, activeAlerts, totalGoals })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    })
  }

  const getMatchStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'live': return 'text-red-500'
      case 'finished': return 'text-gray-500'
      case 'scheduled': return 'text-blue-500'
      default: return 'text-gray-400'
    }
  }

  const getMatchStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'live': return <Activity className="w-4 h-4 animate-pulse" />
      case 'finished': return <Trophy className="w-4 h-4" />
      case 'scheduled': return <Clock className="w-4 h-4" />
      default: return <Calendar className="w-4 h-4" />
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
          <h1 className="text-4xl font-bold text-white mb-4">Welcome to TouchLine</h1>
          <p className="text-gray-300 mb-8">Your ultimate sports alert platform</p>
          <Link href="/auth/signin" className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition">
            Sign In to Continue
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">TouchLine Dashboard</h1>
              <p className="text-gray-300">Real-time sports monitoring & alerts</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/alerts" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Manage Alerts
              </Link>
              <Link href="/matches" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center">
                <BarChart3 className="w-4 h-4 mr-2" />
                View Matches
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
              <div className="p-2 bg-red-500/20 rounded-lg">
                <Activity className="w-6 h-6 text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Live Matches</p>
                <p className="text-2xl font-bold text-white">{stats.liveMatches}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Total Matches</p>
                <p className="text-2xl font-bold text-white">{stats.totalMatches}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-500/20 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Active Alerts</p>
                <p className="text-2xl font-bold text-white">{stats.activeAlerts}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
            <div className="flex items-center">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Target className="w-6 h-6 text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-gray-300 text-sm">Total Goals</p>
                <p className="text-2xl font-bold text-white">{stats.totalGoals}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Live Matches */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-yellow-400" />
                  Live Matches
                </h2>
                <span className="text-sm text-gray-300">{liveMatches.length} active</span>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse bg-white/5 rounded-lg h-24"></div>
                  ))}
                </div>
              ) : liveMatches.length > 0 ? (
                <div className="space-y-4">
                  {liveMatches.map((match) => (
                    <div key={match.id} className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          {getMatchStatusIcon(match.status)}
                          <span className={`text-sm font-medium ${getMatchStatusColor(match.status)}`}>
                            {match.status} {match.elapsed > 0 && `(${match.elapsed}')`}
                          </span>
                        </div>
                        <span className="text-xs text-gray-400">{match.league}</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-white font-medium">{match.home_team}</span>
                            <span className="text-2xl font-bold text-white">{match.home_score}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-white font-medium">{match.away_team}</span>
                            <span className="text-2xl font-bold text-white">{match.away_score}</span>
                          </div>
                        </div>
                        
                        <div className="ml-6 flex flex-col items-center space-y-2">
                          <Link 
                            href={`/matches/${match.id}`}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition"
                          >
                            View Details
                          </Link>
                          <Link 
                            href={`/alerts/create?match=${match.id}`}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition"
                          >
                            Create Alert
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-300">No live matches at the moment</p>
                  <p className="text-gray-400 text-sm">Check back later for live action</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions & Alerts */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-bold text-white mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link 
                  href="/alerts/create"
                  className="flex items-center p-3 bg-blue-600/20 rounded-lg hover:bg-blue-600/30 transition"
                >
                  <Target className="w-5 h-5 text-blue-400 mr-3" />
                  <span className="text-white">Create New Alert</span>
                </Link>
                <Link 
                  href="/matches"
                  className="flex items-center p-3 bg-green-600/20 rounded-lg hover:bg-green-600/30 transition"
                >
                  <BarChart3 className="w-5 h-5 text-green-400 mr-3" />
                  <span className="text-white">Browse Matches</span>
                </Link>
                <Link 
                  href="/settings"
                  className="flex items-center p-3 bg-purple-600/20 rounded-lg hover:bg-purple-600/30 transition"
                >
                  <Users className="w-5 h-5 text-purple-400 mr-3" />
                  <span className="text-white">Account Settings</span>
                </Link>
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-bold text-white mb-4">Your Alerts</h3>
              {userAlerts.length > 0 ? (
                <div className="space-y-3">
                  {userAlerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white font-medium text-sm">{alert.name}</p>
                        <p className="text-gray-400 text-xs">{alert.condition}</p>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${alert.is_active ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                    </div>
                  ))}
                  {userAlerts.length > 5 && (
                    <Link href="/alerts" className="text-blue-400 text-sm hover:underline">
                      View all {userAlerts.length} alerts
                    </Link>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <Target className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-300 text-sm">No alerts yet</p>
                  <Link href="/alerts/create" className="text-blue-400 text-sm hover:underline">
                    Create your first alert
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 