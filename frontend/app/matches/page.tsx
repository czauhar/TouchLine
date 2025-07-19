'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '../../lib/api'

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
        api.getLiveMatches(),
        api.getTodaysMatches()
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
        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-gradient-to-r from-red-500 to-pink-500 text-white">
          <span className="w-3 h-3 bg-white rounded-full mr-3 animate-pulse"></span>
          LIVE {elapsed ? `(${elapsed}')` : ''}
        </span>
      )
    } else if (status === 'FT') {
      return (
        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-gray-600 text-gray-200">
          🏁 FT
        </span>
      )
    } else if (status === 'NS') {
      return (
        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
          ⏰ Upcoming
        </span>
      )
    }
    return (
      <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-yellow-600 text-yellow-100">
        {status}
      </span>
    )
  }

  const MatchCard = ({ match }: { match: Match }) => (
    <div className="group relative">
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
      <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300 transform hover:-translate-y-2">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-bold text-gray-300 bg-gray-800/50 px-4 py-2 rounded-full">
              {match.league}
            </span>
          </div>
          {getStatusBadge(match.status, match.elapsed)}
        </div>
        
        <div className="flex items-center justify-between mb-8">
          <div className="flex-1 text-right">
            <div className="font-black text-2xl text-gray-200 mb-2">{match.home_team}</div>
            <div className="text-sm text-gray-400">{match.venue}</div>
          </div>
          <div className="mx-8 flex items-center space-x-6">
            <div className="text-center">
              <div className="text-5xl font-black text-gray-200 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                {match.home_score}
              </div>
            </div>
            <div className="text-gray-500 text-3xl font-bold">-</div>
            <div className="text-center">
              <div className="text-5xl font-black text-gray-200 bg-gradient-to-r from-red-400 to-pink-400 bg-clip-text text-transparent">
                {match.away_score}
              </div>
            </div>
          </div>
          <div className="flex-1 text-left">
            <div className="font-black text-2xl text-gray-200 mb-2">{match.away_team}</div>
            <div className="text-sm text-gray-400">{formatTime(match.start_time)}</div>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm text-gray-400 border-t border-gray-600 pt-6">
          <span className="flex items-center">
            <span className="mr-2 text-lg">🏟️</span>
            {match.venue}
          </span>
          <span className="flex items-center">
            <span className="mr-2 text-lg">👨‍⚖️</span>
            {match.referee || 'TBD'}
          </span>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-black">
        <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="absolute inset-0 opacity-20" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-500 mx-auto mb-6"></div>
            <p className="text-2xl text-gray-300">Loading live matches...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>

      <div className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-xl opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 rounded-full shadow-2xl">
                  <span className="text-6xl">🏟️</span>
                </div>
              </div>
            </div>
            <h1 className="text-6xl font-black bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent mb-6">
              Live Matches
            </h1>
            <p className="text-2xl text-gray-300 mb-10">Real-time sports data and intelligent analytics</p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Link 
                href="/"
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-gray-600 to-gray-700 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                <div className="relative bg-gradient-to-r from-gray-600 to-gray-700 text-white px-8 py-4 rounded-2xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 font-bold text-lg transform hover:-translate-y-2">
                  🏠 Back to Dashboard
                </div>
              </Link>
              <Link 
                href="/alerts"
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                <div className="relative bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-2xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-bold text-lg transform hover:-translate-y-2">
                  🔔 Manage Alerts
                </div>
              </Link>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-red-500 to-pink-500">
                    <span className="text-3xl text-white">🔥</span>
                  </div>
                  <div className="ml-6">
                    <p className="text-sm font-medium text-gray-400">Live Matches</p>
                    <p className="text-4xl font-black text-gray-200">{liveMatches.length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500">
                    <span className="text-3xl text-white">📅</span>
                  </div>
                  <div className="ml-6">
                    <p className="text-sm font-medium text-gray-400">Today's Matches</p>
                    <p className="text-4xl font-black text-gray-200">{todaysMatches.length}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="relative mb-10">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-3">
              <div className="flex space-x-2">
                <button
                  onClick={() => setActiveTab('live')}
                  className={`flex-1 py-5 px-8 rounded-xl text-lg font-bold transition-all duration-300 ${
                    activeTab === 'live'
                      ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
                  }`}
                >
                  🔥 Live Matches ({liveMatches.length})
                </button>
                <button
                  onClick={() => setActiveTab('today')}
                  className={`flex-1 py-5 px-8 rounded-xl text-lg font-bold transition-all duration-300 ${
                    activeTab === 'today'
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
                  }`}
                >
                  📅 Today's Matches ({todaysMatches.length})
                </button>
              </div>
            </div>
          </div>

          {/* Matches Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {activeTab === 'live' ? (
              liveMatches.length > 0 ? (
                liveMatches.map((match) => (
                  <MatchCard key={match.external_id} match={match} />
                ))
              ) : (
                <div className="col-span-full">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl blur-xl"></div>
                    <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-16 text-center">
                      <div className="text-9xl mb-8">⚽</div>
                      <h3 className="text-3xl font-black text-gray-200 mb-6">No Live Matches</h3>
                      <p className="text-gray-400 mb-8 text-xl leading-relaxed">
                        There are currently no live matches. Check back later for exciting action!
                      </p>
                      <button
                        onClick={() => setActiveTab('today')}
                        className="group relative"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                        <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2">
                          📅 View Today's Matches
                        </div>
                      </button>
                    </div>
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
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl blur-xl"></div>
                    <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-16 text-center">
                      <div className="text-9xl mb-8">📅</div>
                      <h3 className="text-3xl font-black text-gray-200 mb-6">No Matches Today</h3>
                      <p className="text-gray-400 mb-8 text-xl leading-relaxed">
                        No matches scheduled for today. Check back tomorrow!
                      </p>
                      <button
                        onClick={() => setActiveTab('live')}
                        className="group relative"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                        <div className="relative bg-gradient-to-r from-red-600 to-pink-600 text-white px-10 py-4 rounded-2xl hover:from-red-700 hover:to-pink-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2">
                          🔥 Check Live Matches
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 