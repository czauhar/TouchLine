'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { apiClient } from '../../lib/auth'
import Link from 'next/link'
import { 
  Activity, 
  Clock, 
  Trophy, 
  Calendar, 
  Target, 
  BarChart3,
  Users,
  MapPin,
  Cloud,
  TrendingUp,
  Zap,
  Eye,
  Plus
} from 'lucide-react'

interface Match {
  id: string
  fixture: {
    id: number
    date: string
    status: {
      short: string
      elapsed: number
    }
    referee: string | null
    venue: {
      name: string | null
    }
    weather: any
  }
  teams: {
    home: { name: string }
    away: { name: string }
  }
  goals: {
    home: number
    away: number
  }
  league: { name: string }
  alert_metrics: {
    basic: {
      home_score: number
      away_score: number
      score_difference: number
      total_goals: number
      match_status: string
      elapsed_time: number
      referee: string | null
      venue: string | null
      weather: any
    }
    possession: { home: number; away: number }
    shots: { home: number; away: number; home_on_target: number; away_on_target: number }
    corners: { home: number; away: number }
    fouls: { home: number; away: number }
    cards: { home_yellow: number; away_yellow: number; home_red: number; away_red: number }
    xg: { home: number; away: number }
    pressure: { home: number; away: number }
    momentum: { home: number; away: number }
  }
  detailed_stats: any[]
  events: any[]
  lineups: any[]
}

export default function MatchesPage() {
  const { data: session, status } = useSession()
  const [liveMatches, setLiveMatches] = useState<Match[]>([])
  const [todaysMatches, setTodaysMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'live' | 'today'>('live')
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [viewMode, setViewMode] = useState<'cards' | 'list' | 'stats'>('cards')

  useEffect(() => {
    if (status === 'loading') return
    if (!session) return
    
    fetchMatches()
    const interval = setInterval(fetchMatches, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [session, status])

  const fetchMatches = async () => {
    try {
      const [liveData, todayData] = await Promise.all([
        apiClient.getLiveMatches(),
        apiClient.getTodaysMatches()
      ])
      setLiveMatches(liveData.matches || [])
      setTodaysMatches(todayData.matches || [])
    } catch (error) {
      console.error('Error fetching matches:', error)
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    })
  }

  const getMatchStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'live': return 'text-red-500 bg-red-500/10'
      case 'finished': return 'text-gray-500 bg-gray-500/10'
      case 'scheduled': return 'text-blue-500 bg-blue-500/10'
      default: return 'text-gray-400 bg-gray-400/10'
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

  const getCurrentMatches = () => {
    return activeTab === 'live' ? liveMatches : todaysMatches
  }

  const renderMatchCard = (match: Match) => (
    <div key={match.id} className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getMatchStatusIcon(match.fixture.status.short)}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchStatusColor(match.fixture.status.short)}`}>
            {match.fixture.status.short} {match.fixture.status.elapsed > 0 && `(${match.fixture.status.elapsed}')`}
          </span>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-300">{match.league.name}</p>
          <p className="text-xs text-gray-400">{formatDate(match.fixture.date)}</p>
        </div>
      </div>

      {/* Teams & Score */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1 text-center">
          <div className="text-lg font-bold text-white mb-1">{match.teams.home.name}</div>
          <div className="text-3xl font-bold text-white">{match.goals.home}</div>
        </div>
        <div className="mx-4 text-gray-400 font-bold">VS</div>
        <div className="flex-1 text-center">
          <div className="text-lg font-bold text-white mb-1">{match.teams.away.name}</div>
          <div className="text-3xl font-bold text-white">{match.goals.away}</div>
        </div>
      </div>

      {/* Match Details */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div className="flex items-center text-gray-300">
          <MapPin className="w-4 h-4 mr-2" />
          <span className="truncate">{match.fixture.venue.name || 'Unknown'}</span>
        </div>
        <div className="flex items-center text-gray-300">
          <Users className="w-4 h-4 mr-2" />
          <span className="truncate">{match.fixture.referee || 'Unknown'}</span>
        </div>
      </div>

      {/* Quick Stats */}
      {match.alert_metrics && (
        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
          <div className="text-center p-2 bg-white/5 rounded">
            <div className="text-white font-bold">{match.alert_metrics.possession?.home || 50}%</div>
            <div className="text-gray-400">Home Poss</div>
          </div>
          <div className="text-center p-2 bg-white/5 rounded">
            <div className="text-white font-bold">{match.alert_metrics.shots?.home || 0}</div>
            <div className="text-gray-400">Home Shots</div>
          </div>
          <div className="text-center p-2 bg-white/5 rounded">
            <div className="text-white font-bold">{match.alert_metrics.cards?.home_yellow || 0}</div>
            <div className="text-gray-400">Home Cards</div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => setSelectedMatch(match)}
          className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center"
        >
          <Eye className="w-4 h-4 mr-1" />
          Details
        </button>
        <Link
          href={`/alerts/create?match=${match.id}`}
          className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition flex items-center justify-center"
        >
          <Plus className="w-4 h-4 mr-1" />
          Alert
        </Link>
      </div>
    </div>
  )

  const renderMatchList = (match: Match) => (
    <div key={match.id} className="bg-white/10 backdrop-blur-xl rounded-lg p-4 border border-white/20 hover:bg-white/15 transition">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-sm text-gray-300">{formatTime(match.fixture.date)}</div>
            <div className="text-xs text-gray-400">{formatDate(match.fixture.date)}</div>
          </div>
          <div className="flex items-center space-x-2">
            {getMatchStatusIcon(match.fixture.status.short)}
            <span className={`px-2 py-1 rounded text-xs font-medium ${getMatchStatusColor(match.fixture.status.short)}`}>
              {match.fixture.status.short}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="text-center">
            <div className="text-sm text-gray-300">{match.teams.home.name}</div>
            <div className="text-lg font-bold text-white">{match.goals.home}</div>
          </div>
          <div className="text-gray-400 font-bold">-</div>
          <div className="text-center">
            <div className="text-sm text-gray-300">{match.teams.away.name}</div>
            <div className="text-lg font-bold text-white">{match.goals.away}</div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-400">{match.league.name}</span>
          <button
            onClick={() => setSelectedMatch(match)}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition"
          >
            View
          </button>
        </div>
      </div>
    </div>
  )

  const renderStatsView = () => {
    const matches = getCurrentMatches()
    const totalGoals = matches.reduce((sum, m) => sum + m.goals.home + m.goals.away, 0)
    const totalCards = matches.reduce((sum, m) => {
      const metrics = m.alert_metrics || {}
      return sum + (metrics.cards?.home_yellow || 0) + (metrics.cards?.away_yellow || 0) + 
             (metrics.cards?.home_red || 0) + (metrics.cards?.away_red || 0)
    }, 0)
    const totalShots = matches.reduce((sum, m) => {
      const metrics = m.alert_metrics || {}
      return sum + (metrics.shots?.home || 0) + (metrics.shots?.away || 0)
    }, 0)

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
          <div className="flex items-center">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <Target className="w-6 h-6 text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-gray-300 text-sm">Total Goals</p>
              <p className="text-2xl font-bold text-white">{totalGoals}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <BarChart3 className="w-6 h-6 text-yellow-400" />
            </div>
            <div className="ml-4">
              <p className="text-gray-300 text-sm">Total Shots</p>
              <p className="text-2xl font-bold text-white">{totalShots}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
          <div className="flex items-center">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Users className="w-6 h-6 text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-gray-300 text-sm">Total Cards</p>
              <p className="text-2xl font-bold text-white">{totalCards}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
          <div className="flex items-center">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-gray-300 text-sm">Active Matches</p>
              <p className="text-2xl font-bold text-white">{matches.length}</p>
            </div>
          </div>
        </div>
      </div>
    )
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
          <p className="text-gray-300 mb-8">Please sign in to view matches</p>
          <Link href="/auth/signin" className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition">
            Sign In
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
              <h1 className="text-3xl font-bold text-white">Match Center</h1>
              <p className="text-gray-300">Live matches and detailed statistics</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('live')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'live' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <Activity className="w-4 h-4 inline mr-2" />
              Live ({liveMatches.length})
            </button>
            <button
              onClick={() => setActiveTab('today')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'today' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <Calendar className="w-4 h-4 inline mr-2" />
              Today ({todaysMatches.length})
            </button>
          </div>

          <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
            <button
              onClick={() => setViewMode('cards')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                viewMode === 'cards' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Cards
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
            <button
              onClick={() => setViewMode('stats')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                viewMode === 'stats' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Stats
            </button>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="animate-pulse bg-white/10 rounded-xl h-64"></div>
            ))}
          </div>
        ) : viewMode === 'stats' ? (
          renderStatsView()
        ) : viewMode === 'list' ? (
          <div className="space-y-4">
            {getCurrentMatches().map(renderMatchList)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {getCurrentMatches().map(renderMatchCard)}
          </div>
        )}

        {getCurrentMatches().length === 0 && !loading && (
          <div className="text-center py-16">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No matches found</h3>
            <p className="text-gray-300">There are no {activeTab} matches at the moment.</p>
          </div>
        )}
      </div>

      {/* Match Detail Modal */}
      {selectedMatch && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Match Details</h2>
              <button
                onClick={() => setSelectedMatch(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Match Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">League:</span>
                    <span className="text-white ml-2">{selectedMatch.league.name}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Venue:</span>
                    <span className="text-white ml-2">{selectedMatch.fixture.venue.name || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Referee:</span>
                    <span className="text-white ml-2">{selectedMatch.fixture.referee || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className="text-white ml-2">{selectedMatch.fixture.status.short}</span>
                  </div>
                </div>
              </div>

              {/* Detailed Stats */}
              {selectedMatch.alert_metrics && (
                <div className="bg-white/5 rounded-lg p-4">
                  <h3 className="text-lg font-bold text-white mb-3">Statistics</h3>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">{selectedMatch.alert_metrics.possession?.home || 50}%</div>
                      <div className="text-gray-400">Home Possession</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">{selectedMatch.alert_metrics.shots?.home || 0}</div>
                      <div className="text-gray-400">Home Shots</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">{selectedMatch.alert_metrics.cards?.home_yellow || 0}</div>
                      <div className="text-gray-400">Home Cards</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-4">
                <Link
                  href={`/alerts/create?match=${selectedMatch.id}`}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-center"
                >
                  Create Alert for This Match
                </Link>
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 