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
  Plus,
  Shield,
  Crosshair,
  Flag,
  CreditCard,
  Goal,
  Timer,
  Thermometer,
  Wind,
  Droplets,
  Sun,
  Moon,
  Star,
  TrendingDown,
  Minus,
  Equal,
  Info,
  ArrowLeft,
  RefreshCw,
  Filter,
  Search,
  Grid,
  List,
  Play,
  Pause,
  CheckCircle,
  AlertTriangle
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
    passes?: { home: number; away: number; home_accuracy: number; away_accuracy: number }
    tackles?: { home: number; away: number }
    clearances?: { home: number; away: number }
    saves?: { home: number; away: number }
    offsides?: { home: number; away: number }
    substitutions?: { home: number; away: number }
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
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [filterLeague, setFilterLeague] = useState('all')

  useEffect(() => {
    if (status === 'loading') return
    
    fetchMatches()
    const interval = setInterval(fetchMatches, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [status])

  const fetchMatches = async () => {
    try {
      setRefreshing(true)
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
      setRefreshing(false)
    }
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    })
  }

  const getMatchStatusColor = (status: string) => {
    switch (status) {
      case '1H':
      case '2H':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'HT':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'FT':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'NS':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getMatchStatusIcon = (status: string) => {
    switch (status) {
      case '1H':
      case '2H':
        return <Play className="w-4 h-4 text-green-400" />
      case 'HT':
        return <Pause className="w-4 h-4 text-yellow-400" />
      case 'FT':
        return <CheckCircle className="w-4 h-4 text-blue-400" />
      case 'NS':
        return <Clock className="w-4 h-4 text-gray-400" />
      default:
        return <Info className="w-4 h-4 text-gray-400" />
    }
  }

  const getCurrentMatches = () => {
    return activeTab === 'live' ? liveMatches : todaysMatches
  }

  const renderWeatherIcon = (weather: any) => {
    if (!weather) return null
    
    const condition = weather.condition?.toLowerCase() || ''
    
    if (condition.includes('sun') || condition.includes('clear')) return <Sun className="w-4 h-4 text-yellow-400" />
    if (condition.includes('cloud')) return <Cloud className="w-4 h-4 text-gray-400" />
    if (condition.includes('rain')) return <Droplets className="w-4 h-4 text-blue-400" />
    if (condition.includes('snow')) return <Cloud className="w-4 h-4 text-blue-200" />
    
    return <Thermometer className="w-4 h-4" />
  }

  const filteredMatches = getCurrentMatches().filter(match => {
    const matchesSearch = searchTerm === '' || 
      (typeof match.teams.home.name === 'string' && match.teams.home.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (typeof match.teams.away.name === 'string' && match.teams.away.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (typeof match.league.name === 'string' && match.league.name.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesLeague = filterLeague === 'all' || 
      (typeof match.league.name === 'string' && match.league.name === filterLeague)
    
    return matchesSearch && matchesLeague
  })

  const leagues = Array.from(new Set(getCurrentMatches().map(match => 
    typeof match.league.name === 'string' ? match.league.name : 'Unknown'
  )))

  const renderMatchCard = (match: Match) => (
    <div key={match.id} className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${getMatchStatusColor(match.fixture.status.short)}`}>
            {getMatchStatusIcon(match.fixture.status.short)}
          </div>
          <div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getMatchStatusColor(match.fixture.status.short)}`}>
              {match.fixture.status.short} {match.fixture.status.elapsed > 0 && `(${match.fixture.status.elapsed}')`}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-300 font-medium">{typeof match.league.name === 'string' ? match.league.name : 'League'}</p>
          <p className="text-xs text-gray-400">{formatDate(match.fixture.date)}</p>
        </div>
      </div>

      {/* Teams & Score */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1 text-center">
          <div className="text-lg font-bold text-white mb-2 group-hover:text-green-400 transition">
            {typeof match.teams.home.name === 'string' ? match.teams.home.name : 'Home Team'}
          </div>
          <div className="text-4xl font-bold text-white group-hover:scale-110 transition">
            {match.goals.home}
          </div>
        </div>
        <div className="mx-6 text-gray-400 font-bold text-xl">VS</div>
        <div className="flex-1 text-center">
          <div className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition">
            {typeof match.teams.away.name === 'string' ? match.teams.away.name : 'Away Team'}
          </div>
          <div className="text-4xl font-bold text-white group-hover:scale-110 transition">
            {match.goals.away}
          </div>
        </div>
      </div>

      {/* Match Details */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div className="flex items-center text-gray-300 bg-white/5 p-2 rounded-lg">
          <MapPin className="w-4 h-4 mr-2 text-blue-400" />
          <span className="truncate">{typeof match.fixture.venue.name === 'string' ? match.fixture.venue.name : 'Unknown'}</span>
        </div>
        <div className="flex items-center text-gray-300 bg-white/5 p-2 rounded-lg">
          <Users className="w-4 h-4 mr-2 text-purple-400" />
          <span className="truncate">{match.fixture.referee || 'Unknown'}</span>
        </div>
      </div>

      {/* Weather Info */}
      {match.fixture.weather && (
        <div className="flex items-center justify-center mb-4 text-sm text-gray-300 bg-white/5 p-2 rounded-lg">
          {renderWeatherIcon(match.fixture.weather)}
          <span className="ml-2">
            {match.fixture.weather.temp}°C {match.fixture.weather.condition}
          </span>
        </div>
      )}

      {/* Enhanced Stats Grid */}
      {match.alert_metrics && (
        <div className="grid grid-cols-4 gap-2 mb-6 text-xs">
          <div className="text-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition">
            <div className="text-white font-bold text-lg">{match.alert_metrics.possession?.home || 50}%</div>
            <div className="text-gray-400">Poss</div>
          </div>
          <div className="text-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition">
            <div className="text-white font-bold text-lg">{match.alert_metrics.shots?.home || 0}</div>
            <div className="text-gray-400">Shots</div>
          </div>
          <div className="text-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition">
            <div className="text-white font-bold text-lg">{match.alert_metrics.corners?.home || 0}</div>
            <div className="text-gray-400">Corners</div>
          </div>
          <div className="text-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition">
            <div className="text-white font-bold text-lg">{match.alert_metrics.cards?.home_yellow || 0}</div>
            <div className="text-gray-400">Cards</div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-3">
        <button
          onClick={() => setSelectedMatch(match)}
          className="flex-1 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center font-medium"
        >
          <Eye className="w-4 h-4 mr-2" />
          Details
        </button>
        <Link
          href={`/alerts/create?match=${match.id}`}
          className="flex-1 bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition flex items-center justify-center font-medium"
        >
          <Plus className="w-4 h-4 mr-2" />
          Alert
        </Link>
      </div>
    </div>
  )

  const renderMatchList = (match: Match) => (
    <div key={match.id} className="bg-white/10 backdrop-blur-xl rounded-lg p-4 border border-white/20 hover:bg-white/15 transition">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className={`p-2 rounded-lg ${getMatchStatusColor(match.fixture.status.short)}`}>
            {getMatchStatusIcon(match.fixture.status.short)}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{typeof match.teams.home.name === 'string' ? match.teams.home.name : 'Home Team'}</span>
              <span className="text-2xl font-bold text-white">{match.goals.home}</span>
              <span className="text-gray-400">-</span>
              <span className="text-2xl font-bold text-white">{match.goals.away}</span>
              <span className="text-white font-medium">{typeof match.teams.away.name === 'string' ? match.teams.away.name : 'Away Team'}</span>
            </div>
            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
              <span>{typeof match.league.name === 'string' ? match.league.name : 'League'}</span>
              <span>•</span>
              <span>{match.fixture.status.short} {match.fixture.status.elapsed > 0 && `(${match.fixture.status.elapsed}')`}</span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setSelectedMatch(match)}
            className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Eye className="w-4 h-4" />
          </button>
          <Link
            href={`/alerts/create?match=${match.id}`}
            className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition"
          >
            <Plus className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto"></div>
          <p className="text-white mt-4 text-lg">Loading matches...</p>
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
                <h1 className="text-3xl font-bold text-white">Matches</h1>
              </div>
              <p className="text-gray-300">Live and upcoming matches with real-time statistics</p>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchMatches}
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
        {/* Tabs and Controls */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Tabs */}
            <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('live')}
                className={`px-6 py-2 rounded-md font-medium transition ${
                  activeTab === 'live'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4" />
                  <span>Live Matches ({liveMatches.length})</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('today')}
                className={`px-6 py-2 rounded-md font-medium transition ${
                  activeTab === 'today'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Today's Matches ({todaysMatches.length})</span>
                </div>
              </button>
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search matches..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-white/10 text-white pl-10 pr-4 py-2 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* League Filter */}
              <select
                value={filterLeague}
                onChange={(e) => setFilterLeague(e.target.value)}
                className="bg-white/10 text-white px-4 py-2 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Leagues</option>
                {leagues.map((league) => (
                  <option key={league} value={league}>{league}</option>
                ))}
              </select>

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
        </div>

        {/* Matches Grid/List */}
        {filteredMatches.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No matches found</h3>
            <p className="text-gray-300">
              {searchTerm || filterLeague !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : `No ${activeTab === 'live' ? 'live' : "today's"} matches available`
              }
            </p>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }>
            {filteredMatches.map(match => 
              viewMode === 'grid' ? renderMatchCard(match) : renderMatchList(match)
            )}
          </div>
        )}
      </div>
    </div>
  )
} 