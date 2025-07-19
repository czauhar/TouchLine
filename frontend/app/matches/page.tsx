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
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <span className="w-2 h-2 bg-red-400 rounded-full mr-1 animate-pulse"></span>
          LIVE {elapsed ? `(${elapsed}')` : ''}
        </span>
      )
    } else if (status === 'FT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          FT
        </span>
      )
    } else if (status === 'NS') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          Upcoming
        </span>
      )
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        {status}
      </span>
    )
  }

  const MatchCard = ({ match }: { match: Match }) => (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500 font-medium">{match.league}</span>
        {getStatusBadge(match.status, match.elapsed)}
      </div>
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex-1 text-right">
          <div className="font-semibold text-gray-900">{match.home_team}</div>
        </div>
        <div className="mx-4 flex items-center space-x-2">
          <span className="text-2xl font-bold text-gray-900">{match.home_score}</span>
          <span className="text-gray-400">-</span>
          <span className="text-2xl font-bold text-gray-900">{match.away_score}</span>
        </div>
        <div className="flex-1 text-left">
          <div className="font-semibold text-gray-900">{match.away_team}</div>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{match.venue}</span>
        <span>{formatTime(match.start_time)}</span>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading matches...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Live Matches</h1>
            <p className="text-gray-600 mt-2">Real-time sports data and statistics</p>
          </div>
          <div className="flex space-x-3">
            <Link 
              href="/alerts"
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Manage Alerts
            </Link>
            <Link 
              href="/"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white p-1 rounded-lg shadow-sm mb-6">
          <button
            onClick={() => setActiveTab('live')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'live'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Live Matches ({liveMatches.length})
          </button>
          <button
            onClick={() => setActiveTab('today')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'today'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Today's Matches ({todaysMatches.length})
          </button>
        </div>

        {/* Matches Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeTab === 'live' ? (
            liveMatches.length > 0 ? (
              liveMatches.map((match) => (
                <MatchCard key={match.external_id} match={match} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">⚽</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Live Matches</h3>
                <p className="text-gray-600">There are currently no live matches. Check back later!</p>
              </div>
            )
          ) : (
            todaysMatches.length > 0 ? (
              todaysMatches.map((match) => (
                <MatchCard key={match.external_id} match={match} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">📅</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Matches Today</h3>
                <p className="text-gray-600">No matches scheduled for today.</p>
              </div>
            )
          )}
        </div>

        {/* Refresh Button */}
        <div className="text-center mt-8">
          <button
            onClick={fetchMatches}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Refresh Matches
          </button>
        </div>
      </div>
    </div>
  )
} 