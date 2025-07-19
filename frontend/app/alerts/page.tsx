'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '../../lib/api'

interface Alert {
  id: number
  name: string
  is_active: boolean
  conditions: string
  created_at: string
}

interface Match {
  external_id: string
  home_team: string
  away_team: string
  league: string
  home_score: number
  away_score: number
  status: string
  elapsed: number | null
  venue: string | null
}

interface Team {
  name: string
  league: string
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [leagues, setLeagues] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  
  // Alert form state
  const [newAlert, setNewAlert] = useState({
    name: '',
    team: '',
    league: '',
    condition_type: 'goals',
    operator: '>=',
    value: '',
    time_window: '',
    description: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [alertsResponse, matchesResponse] = await Promise.all([
        api.getAlerts(),
        api.getLiveMatches()
      ])
      
      const alertsData = await alertsResponse.json()
      const matchesData = await matchesResponse.json()
      
      setAlerts(alertsData.alerts || [])
      setMatches(matchesData.matches || [])
      
      // Extract unique teams and leagues
      const allTeams: Team[] = []
      const allLeagues: Set<string> = new Set()
      
      matchesData.matches?.forEach((match: Match) => {
        allLeagues.add(match.league)
        allTeams.push({ name: match.home_team, league: match.league })
        allTeams.push({ name: match.away_team, league: match.league })
      })
      
      setTeams(allTeams)
      setLeagues(Array.from(allLeagues))
      
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const alertData = {
        name: newAlert.name,
        conditions: JSON.stringify({
          team: newAlert.team,
          league: newAlert.league,
          condition_type: newAlert.condition_type,
          operator: newAlert.operator,
          value: parseFloat(newAlert.value) || newAlert.value,
          time_window: newAlert.time_window,
          description: newAlert.description
        })
      }
      
      const response = await api.createAlert(alertData)
      
      if (response.ok) {
        setNewAlert({
          name: '',
          team: '',
          league: '',
          condition_type: 'goals',
          operator: '>=',
          value: '',
          time_window: '',
          description: ''
        })
        setShowCreateForm(false)
        setSelectedMatch(null)
        fetchData()
      }
    } catch (error) {
      console.error('Error creating alert:', error)
    }
  }

  const createQuickAlert = (match: Match, condition: string) => {
    setSelectedMatch(match)
    setNewAlert({
      name: `${match.home_team} vs ${match.away_team} - ${condition}`,
      team: match.home_team,
      league: match.league,
      condition_type: 'goals',
      operator: '>=',
      value: '1',
      time_window: '',
      description: `Quick alert for ${condition}`
    })
    setShowCreateForm(true)
  }

  const toggleAlert = async (id: number) => {
    try {
      const response = await api.toggleAlert(id)
      if (response.ok) {
        fetchData()
      }
    } catch (error) {
      console.error('Error toggling alert:', error)
    }
  }

  const deleteAlert = async (id: number) => {
    try {
      const response = await api.deleteAlert(id)
      if (response.ok) {
        fetchData()
      }
    } catch (error) {
      console.error('Error deleting alert:', error)
    }
  }

  const getMatchStatusColor = (status: string) => {
    switch (status) {
      case '1H': return 'text-green-400'
      case '2H': return 'text-yellow-400'
      case 'HT': return 'text-blue-400'
      case 'FT': return 'text-gray-400'
      case 'P': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getMatchStatusIcon = (status: string) => {
    switch (status) {
      case '1H': return '⚽'
      case '2H': return '⚽'
      case 'HT': return '⏸️'
      case 'FT': return '🏁'
      case 'P': return '⏰'
      default: return '⏰'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading alerts and live matches...</p>
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
                <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-pink-500 to-purple-500 rounded-full blur-xl opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-r from-red-600 via-pink-600 to-purple-600 p-6 rounded-full shadow-2xl">
                  <span className="text-6xl">🚨</span>
                </div>
              </div>
            </div>
            <h1 className="text-6xl font-black bg-gradient-to-r from-red-400 via-pink-400 to-purple-400 bg-clip-text text-transparent mb-6">
              Intelligent Alerts
            </h1>
            <p className="text-2xl text-gray-300 mb-10">Create smart alerts based on live match data and advanced analytics</p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button
                onClick={() => setShowCreateForm(true)}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-5 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2 flex items-center justify-center">
                  <span className="mr-3">➕</span>
                  Create Smart Alert
                </div>
              </button>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-10">
            <Link href="/" className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-gray-600 to-gray-700 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
              <div className="relative bg-gradient-to-r from-gray-600 to-gray-700 text-white px-8 py-4 rounded-2xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 font-bold text-lg transform hover:-translate-y-2">
                🏠 Dashboard
              </div>
            </Link>
            <Link href="/matches" className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
              <div className="relative bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-2xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-300 font-bold text-lg transform hover:-translate-y-2">
                🏟️ Live Matches
              </div>
            </Link>
            <span className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl blur opacity-50"></div>
              <div className="relative bg-gradient-to-r from-red-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold text-lg">
                🚨 Alerts
              </div>
            </span>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500">
                    <span className="text-2xl text-white">🔔</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Total Alerts</p>
                    <p className="text-3xl font-black text-gray-200">{alerts.length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500">
                    <span className="text-2xl text-white">🟢</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Active Alerts</p>
                    <p className="text-3xl font-black text-gray-200">{alerts.filter(a => a.is_active).length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500">
                    <span className="text-2xl text-white">⚽</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Live Matches</p>
                    <p className="text-3xl font-black text-gray-200">{matches.length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-yellow-500 to-orange-500">
                    <span className="text-2xl text-white">🏆</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Leagues</p>
                    <p className="text-3xl font-black text-gray-200">{leagues.length}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Live Matches for Quick Alerts */}
          <div className="relative mb-12">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
              <h2 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-6">
                Live Matches - Quick Alerts
              </h2>
              
              {matches.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {matches.slice(0, 9).map((match) => (
                    <div key={match.external_id} className="group relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                      <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                        {/* Match Header */}
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center">
                            <span className={`text-2xl mr-2 ${getMatchStatusColor(match.status)}`}>
                              {getMatchStatusIcon(match.status)}
                            </span>
                            <span className={`text-sm font-bold ${getMatchStatusColor(match.status)}`}>
                              {match.status} {match.elapsed && `(${match.elapsed}')`}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                            {match.league}
                          </span>
                        </div>
                        
                        {/* Teams and Score */}
                        <div className="text-center mb-4">
                          <div className="text-lg font-bold text-gray-200 mb-1">{match.home_team}</div>
                          <div className="text-3xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                            {match.home_score} - {match.away_score}
                          </div>
                          <div className="text-lg font-bold text-gray-200 mt-1">{match.away_team}</div>
                        </div>
                        
                        {/* Quick Alert Buttons */}
                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={() => createQuickAlert(match, 'Goal')}
                            className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-3 py-2 rounded-lg text-sm font-bold hover:from-green-700 hover:to-emerald-700 transition-all duration-300"
                          >
                            🥅 Goal Alert
                          </button>
                          <button
                            onClick={() => createQuickAlert(match, 'Comeback')}
                            className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-3 py-2 rounded-lg text-sm font-bold hover:from-red-700 hover:to-pink-700 transition-all duration-300"
                          >
                            🔄 Comeback
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">⚽</div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-2">No Live Matches</h3>
                  <p className="text-gray-400">Check back later for live matches to create alerts!</p>
                </div>
              )}
            </div>
          </div>

          {/* Your Alerts */}
          <div className="relative mb-12">
            <div className="absolute inset-0 bg-gradient-to-r from-red-600/20 to-pink-600/20 rounded-3xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
              <h2 className="text-3xl font-black bg-gradient-to-r from-red-400 to-pink-400 bg-clip-text text-transparent mb-6">
                Your Alerts
              </h2>
              
              {alerts.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="group relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                      <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-xl font-bold text-gray-200">{alert.name}</h3>
                          <button
                            onClick={() => toggleAlert(alert.id)}
                            className={`px-3 py-1 rounded-full text-sm font-bold ${
                              alert.is_active
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-gray-500/20 text-gray-400'
                            }`}
                          >
                            {alert.is_active ? 'Active' : 'Inactive'}
                          </button>
                        </div>
                        <p className="text-gray-400 text-sm mb-4">{alert.conditions}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-500">
                            {new Date(alert.created_at).toLocaleDateString()}
                          </span>
                          <button
                            onClick={() => deleteAlert(alert.id)}
                            className="text-red-400 hover:text-red-300 text-sm font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔔</div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-2">No Alerts Yet</h3>
                  <p className="text-gray-400">Create your first alert to get started!</p>
                </div>
              )}
            </div>
          </div>

          {/* Create Alert Modal */}
          {showCreateForm && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="relative max-w-2xl w-full mx-4">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-xl"></div>
                <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
                  <h3 className="text-3xl font-bold text-gray-200 mb-6">Create Smart Alert</h3>
                  
                  {selectedMatch && (
                    <div className="mb-6 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
                      <h4 className="text-lg font-bold text-gray-200 mb-2">Selected Match:</h4>
                      <div className="text-center">
                        <div className="text-xl font-bold text-gray-200">{selectedMatch.home_team}</div>
                        <div className="text-2xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                          {selectedMatch.home_score} - {selectedMatch.away_score}
                        </div>
                        <div className="text-xl font-bold text-gray-200">{selectedMatch.away_team}</div>
                        <div className="text-sm text-gray-400 mt-1">{selectedMatch.league}</div>
                      </div>
                    </div>
                  )}
                  
                  <form onSubmit={createAlert} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Alert Name
                        </label>
                        <input
                          type="text"
                          value={newAlert.name}
                          onChange={(e) => setNewAlert({ ...newAlert, name: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          League
                        </label>
                        <select
                          value={newAlert.league}
                          onChange={(e) => setNewAlert({ ...newAlert, league: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                        >
                          <option value="">Select League</option>
                          {leagues.map((league) => (
                            <option key={league} value={league}>{league}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Team
                        </label>
                        <select
                          value={newAlert.team}
                          onChange={(e) => setNewAlert({ ...newAlert, team: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                          required
                        >
                          <option value="">Select Team</option>
                          {teams
                            .filter(team => !newAlert.league || team.league === newAlert.league)
                            .map((team) => (
                              <option key={team.name} value={team.name}>{team.name}</option>
                            ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Condition Type
                        </label>
                        <select
                          value={newAlert.condition_type}
                          onChange={(e) => setNewAlert({ ...newAlert, condition_type: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                        >
                          <option value="goals">Goals</option>
                          <option value="score_difference">Score Difference</option>
                          <option value="time_based">Time Based</option>
                          <option value="momentum">Momentum</option>
                          <option value="pressure">Pressure</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Operator
                        </label>
                        <select
                          value={newAlert.operator}
                          onChange={(e) => setNewAlert({ ...newAlert, operator: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                        >
                          <option value=">=">Greater than or equal (≥)</option>
                          <option value="&gt;">Greater than (&gt;)</option>
                          <option value="==">Equals (=)</option>
                          <option value="&lt;">Less than (&lt;)</option>
                          <option value="<=">Less than or equal (≤)</option>
                        </select>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Value
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={newAlert.value}
                          onChange={(e) => setNewAlert({ ...newAlert, value: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          Time Window (minutes, optional)
                        </label>
                        <input
                          type="number"
                          value={newAlert.time_window}
                          onChange={(e) => setNewAlert({ ...newAlert, time_window: e.target.value })}
                          className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500"
                          placeholder="e.g., 10"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Description
                      </label>
                      <textarea
                        value={newAlert.description}
                        onChange={(e) => setNewAlert({ ...newAlert, description: e.target.value })}
                        className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500 h-20"
                        placeholder="Optional description of this alert..."
                      />
                    </div>
                    
                    <div className="flex gap-4">
                      <button
                        type="submit"
                        className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-4 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-lg"
                      >
                        Create Alert
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowCreateForm(false)
                          setSelectedMatch(null)
                        }}
                        className="flex-1 bg-gray-700 text-gray-300 px-6 py-4 rounded-xl hover:bg-gray-600 transition-all duration-300 font-bold text-lg"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 