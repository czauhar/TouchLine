'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Match {
  external_id: string
  home_team: string
  away_team: string
  league: string
  start_time: string
  status: string
  home_score: number
  away_score: number
  venue: string
  referee: string
  elapsed: number
}

interface MatchesResponse {
  matches: Match[]
  count: number
}

export default function MatchesPage() {
  const [liveMatches, setLiveMatches] = useState<Match[]>([])
  const [todaysMatches, setTodaysMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'live' | 'today'>('live')

  useEffect(() => {
    fetchMatches()
  }, [])

  const fetchMatches = async () => {
    try {
      const [liveResponse, todayResponse] = await Promise.all([
        fetch('http://localhost:8000/api/matches/live'),
        fetch('http://localhost:8000/api/matches/today')
      ])
      
      const liveData: MatchesResponse = await liveResponse.json()
      const todayData: MatchesResponse = await todayResponse.json()
      
      setLiveMatches(liveData.matches)
      setTodaysMatches(todayData.matches)
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

  const getStatusBadge = (status: string, elapsed?: number) => {
    if (status === 'LIVE') {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg">
          <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
          LIVE {elapsed ? `(${elapsed}')` : ''}
        </span>
      )
    } else if (status === 'FT') {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-gray-100 text-gray-800">
          🏁 FT
        </span>
      )
    } else if (status === 'NS') {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
          ⏰ Upcoming
        </span>
      )
    }
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800">
        {status}
      </span>
    )
  }

  const MatchCard = ({ match }: { match: Match }) => (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-semibold text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
            {match.league}
          </span>
        </div>
        {getStatusBadge(match.status, match.elapsed)}
      </div>
      
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1 text-right">
          <div className="font-bold text-lg text-gray-900 mb-1">{match.home_team}</div>
          <div className="text-sm text-gray-500">{match.venue}</div>
        </div>
        <div className="mx-6 flex items-center space-x-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              {match.home_score}
            </div>
          </div>
          <div className="text-gray-400 text-2xl font-bold">-</div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent">
              {match.away_score}
            </div>
          </div>
        </div>
        <div className="flex-1 text-left">
          <div className="font-bold text-lg text-gray-900 mb-1">{match.away_team}</div>
          <div className="text-sm text-gray-500">{formatTime(match.start_time)}</div>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-4">
        <span className="flex items-center">
          <span className="mr-1">🏟️</span>
          {match.venue}
        </span>
        <span className="flex items-center">
          <span className="mr-1">👨‍⚖️</span>
          {match.referee || 'TBD'}
        </span>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-xl text-gray-600">Loading live matches...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-2xl shadow-2xl">
              <span className="text-4xl">🏟️</span>
            </div>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-4">
            Live Matches
          </h1>
          <p className="text-xl text-gray-600 mb-8">Real-time sports data and intelligent analytics</p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/"
              className="bg-gradient-to-r from-gray-600 to-gray-700 text-white px-6 py-3 rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              🏠 Back to Dashboard
            </Link>
            <Link 
              href="/alerts"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              🔔 Manage Alerts
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-gradient-to-r from-red-500 to-pink-500">
                <span className="text-2xl text-white">🔥</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Live Matches</p>
                <p className="text-3xl font-bold text-gray-900">{liveMatches.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500">
                <span className="text-2xl text-white">📅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Today's Matches</p>
                <p className="text-3xl font-bold text-gray-900">{todaysMatches.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-2 mb-8">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('live')}
              className={`flex-1 py-4 px-6 rounded-xl text-sm font-semibold transition-all duration-300 ${
                activeTab === 'live'
                  ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              🔥 Live Matches ({liveMatches.length})
            </button>
            <button
              onClick={() => setActiveTab('today')}
              className={`flex-1 py-4 px-6 rounded-xl text-sm font-semibold transition-all duration-300 ${
                activeTab === 'today'
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              📅 Today's Matches ({todaysMatches.length})
            </button>
          </div>
        </div>

        {/* Matches Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeTab === 'live' ? (
            liveMatches.length > 0 ? (
              liveMatches.map((match) => (
                <MatchCard key={match.external_id} match={match} />
              ))
            ) : (
              <div className="col-span-full">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
                  <div className="text-8xl mb-6">⚽</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">No Live Matches</h3>
                  <p className="text-gray-600 mb-6 text-lg">
                    There are currently no live matches. Check back later for exciting action!
                  </p>
                  <button
                    onClick={() => setActiveTab('today')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                  >
                    📅 View Today's Matches
                  </button>
                </div>
              </div>
            )
          ) : (
            todaysMatches.length > 0 ? (
              todaysMatches.map((match) => (
                <MatchCard key={match.external_id} match={match} />
              ))
            ) : (
              <div className="col-span-full">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
                  <div className="text-8xl mb-6">📅</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">No Matches Today</h3>
                  <p className="text-gray-600 mb-6 text-lg">
                    No matches scheduled for today. Check back tomorrow!
                  </p>
                  <button
                    onClick={() => setActiveTab('live')}
                    className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-8 py-3 rounded-xl hover:from-red-700 hover:to-pink-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                  >
                    🔥 Check Live Matches
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  )
} 