'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiClient } from '../../../lib/auth'
import Link from 'next/link'
import { 
  Target, 
  ArrowLeft, 
  Save, 
  Plus, 
  Trash2, 
  Settings, 
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
  Filter,
  Search,
  Target as TargetIcon,
  Shield,
  Flag,
  Timer,
  Gauge,
  Layers
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

interface AlertCondition {
  id: string
  metric: string
  team: 'home' | 'away' | 'either' | 'both'
  operator: '>=' | '>' | '<=' | '<' | '==' | '!='
  value: number | string
  timeWindow?: { start: number; end: number }
  description: string
  // Player-specific fields
  player_id?: number
  player_name?: string
}

interface AlertForm {
  name: string
  description: string
  matchId?: number
  team: string
  conditions: AlertCondition[]
  logicOperator: 'AND' | 'OR'
  notificationType: 'sms' | 'email' | 'both'
  priority: 'low' | 'medium' | 'high'
  cooldown: number
}

const METRIC_CATEGORIES = {
  'Basic Stats': [
    { value: 'goals', label: 'Goals Scored', description: 'Number of goals scored by team' },
    { value: 'score_difference', label: 'Score Difference', description: 'Goal difference between teams' },
    { value: 'total_goals', label: 'Total Goals', description: 'Combined goals from both teams' },
    { value: 'elapsed_time', label: 'Match Time', description: 'Current minute of the match' },
  ],
  'Possession & Control': [
    { value: 'possession', label: 'Ball Possession', description: 'Percentage of ball possession' },
    { value: 'final_third_possession', label: 'Final Third Possession', description: 'Time spent in attacking third' },
    { value: 'passes', label: 'Passes Completed', description: 'Number of successful passes' },
    { value: 'pass_accuracy', label: 'Pass Accuracy', description: 'Percentage of successful passes' },
  ],
  'Attacking Metrics': [
    { value: 'shots', label: 'Total Shots', description: 'Number of shots taken' },
    { value: 'shots_on_target', label: 'Shots on Target', description: 'Shots that hit the target' },
    { value: 'xg', label: 'Expected Goals (xG)', description: 'Expected goals based on shot quality' },
    { value: 'corners', label: 'Corner Kicks', description: 'Number of corner kicks won' },
  ],
  'Defensive Metrics': [
    { value: 'tackles', label: 'Tackles', description: 'Number of successful tackles' },
    { value: 'clearances', label: 'Clearances', description: 'Number of defensive clearances' },
    { value: 'saves', label: 'Saves', description: 'Number of saves by goalkeeper' },
    { value: 'interceptions', label: 'Interceptions', description: 'Number of ball interceptions' },
  ],
  'Disciplinary': [
    { value: 'yellow_cards', label: 'Yellow Cards', description: 'Number of yellow cards' },
    { value: 'red_cards', label: 'Red Cards', description: 'Number of red cards' },
    { value: 'fouls', label: 'Fouls Committed', description: 'Number of fouls committed' },
    { value: 'offsides', label: 'Offsides', description: 'Number of offside calls' },
  ],
  'Advanced Analytics': [
    { value: 'momentum', label: 'Momentum Score', description: 'Team performance momentum' },
    { value: 'pressure', label: 'Pressure Index', description: 'Attacking pressure rating' },
    { value: 'win_probability', label: 'Win Probability', description: 'Statistical win chance' },
    { value: 'form_rating', label: 'Form Rating', description: 'Recent form indicator' },
  ],
  'Player Statistics': [
    { value: 'player_goals', label: 'Player Goals', description: 'Individual player goals scored' },
    { value: 'player_assists', label: 'Player Assists', description: 'Individual player assists' },
    { value: 'player_cards', label: 'Player Cards', description: 'Individual player cards received' },
    { value: 'player_shots', label: 'Player Shots', description: 'Individual player shots taken' },
    { value: 'player_passes', label: 'Player Passes', description: 'Individual player passes completed' },
    { value: 'player_tackles', label: 'Player Tackles', description: 'Individual player tackles' },
    { value: 'player_rating', label: 'Player Rating', description: 'Individual player performance rating' },
    { value: 'player_minutes', label: 'Player Minutes', description: 'Individual player minutes played' },
    { value: 'player_goal_contributions', label: 'Player Goal Contributions', description: 'Player goals + assists combined' },
  ],
  'Match Context': [
    { value: 'referee', label: 'Referee', description: 'Specific referee officiating' },
    { value: 'venue', label: 'Venue', description: 'Stadium where match is played' },
    { value: 'weather', label: 'Weather Conditions', description: 'Weather during the match' },
    { value: 'attendance', label: 'Attendance', description: 'Number of spectators' },
  ]
}

const OPERATORS = [
  { value: '>=', label: 'Greater than or equal to (≥)', symbol: '≥' },
  { value: '>', label: 'Greater than (>)', symbol: '>' },
  { value: '<=', label: 'Less than or equal to (≤)', symbol: '≤' },
  { value: '<', label: 'Less than (<)', symbol: '<' },
  { value: '==', label: 'Equal to (=)', symbol: '=' },
  { value: '!=', label: 'Not equal to (≠)', symbol: '≠' },
]

export default function CreateAlertPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()
  const matchId = searchParams.get('match')
  
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  
  const [form, setForm] = useState<AlertForm>({
    name: '',
    description: '',
    matchId: matchId ? parseInt(matchId) : undefined,
    team: '',
    conditions: [],
    logicOperator: 'AND',
    notificationType: 'sms',
    priority: 'medium',
    cooldown: 5
  })

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.push('/auth/signin')
      return
    }
    
    fetchMatches()
  }, [session, status])

  useEffect(() => {
    if (matchId && matches.length > 0) {
      const match = matches.find(m => m.id === parseInt(matchId))
      if (match) {
        setSelectedMatch(match)
        setForm(prev => ({
          ...prev,
          name: `${match.home_team} vs ${match.away_team} Alert`,
          team: match.home_team
        }))
      }
    }
  }, [matchId, matches])

  const fetchMatches = async () => {
    try {
      const [liveData, todayData] = await Promise.all([
        apiClient.getLiveMatches(),
        apiClient.getTodaysMatches()
      ])
      setMatches([...(liveData.matches || []), ...(todayData.matches || [])])
    } catch (error) {
      console.error('Error fetching matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const addCondition = () => {
    const newCondition: AlertCondition = {
      id: Date.now().toString(),
      metric: 'goals',
      team: 'either',
      operator: '>=',
      value: 1,
      description: ''
    }
    setForm(prev => ({
      ...prev,
      conditions: [...prev.conditions, newCondition]
    }))
  }

  const updateCondition = (id: string, field: keyof AlertCondition, value: any) => {
    setForm(prev => ({
      ...prev,
      conditions: prev.conditions.map(condition =>
        condition.id === id ? { ...condition, [field]: value } : condition
      )
    }))
  }

  const removeCondition = (id: string) => {
    setForm(prev => ({
      ...prev,
      conditions: prev.conditions.filter(condition => condition.id !== id)
    }))
  }

  const getMetricDescription = (metric: string) => {
    for (const category of Object.values(METRIC_CATEGORIES)) {
      const found = category.find(m => m.value === metric)
      if (found) return found.description
    }
    return ''
  }

  const getOperatorSymbol = (operator: string) => {
    const found = OPERATORS.find(op => op.value === operator)
    return found ? found.symbol : operator
  }

  const validateForm = () => {
    if (!form.name.trim()) return 'Alert name is required'
    if (form.conditions.length === 0) return 'At least one condition is required'
    if (form.conditions.some(c => !c.description.trim())) return 'All conditions must have descriptions'
    return null
  }

  const createAlert = async () => {
    const error = validateForm()
    if (error) {
      alert(error)
      return
    }

    setSaving(true)
    try {
      const alertData = {
        name: form.name,
        description: form.description,
        match_id: form.matchId,
        team: form.team,
        conditions: JSON.stringify({
          logic_operator: form.logicOperator,
          conditions: form.conditions,
          notification_type: form.notificationType,
          priority: form.priority,
          cooldown: form.cooldown
        })
      }
      
      await apiClient.createAlert(alertData)
      router.push('/alerts')
    } catch (error) {
      console.error('Error creating alert:', error)
      alert('Failed to create alert. Please try again.')
    } finally {
      setSaving(false)
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

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/alerts" className="text-gray-400 hover:text-white transition">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-white">Create Advanced Alert</h1>
                <p className="text-gray-300">Build sophisticated alerts with detailed metrics</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowPreview(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center"
              >
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </button>
              <button
                onClick={createAlert}
                disabled={saving}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition flex items-center disabled:opacity-50"
              >
                {saving ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {saving ? 'Creating...' : 'Create Alert'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-8">
            {/* Basic Information */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Basic Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Alert Name</label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter alert name..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Team</label>
                  <input
                    type="text"
                    value={form.team}
                    onChange={(e) => setForm(prev => ({ ...prev, team: e.target.value }))}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Team name (optional)"
                  />
                </div>
              </div>
              
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe what this alert monitors..."
                />
              </div>
            </div>

            {/* Conditions */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Layers className="w-5 h-5 mr-2" />
                  Alert Conditions
                </h2>
                <div className="flex items-center space-x-4">
                  <select
                    value={form.logicOperator}
                    onChange={(e) => setForm(prev => ({ ...prev, logicOperator: e.target.value as 'AND' | 'OR' }))}
                    className="px-3 py-1 bg-white/10 border border-white/20 rounded text-white text-sm"
                  >
                    <option value="AND">ALL conditions (AND)</option>
                    <option value="OR">ANY condition (OR)</option>
                  </select>
                  <button
                    onClick={addCondition}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition flex items-center"
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    Add Condition
                  </button>
                </div>
              </div>

              {form.conditions.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-300 mb-4">No conditions added yet</p>
                  <button
                    onClick={addCondition}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                  >
                    Add Your First Condition
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {form.conditions.map((condition, index) => (
                    <div key={condition.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-white">Condition {index + 1}</h3>
                        <button
                          onClick={() => removeCondition(condition.id)}
                          className="text-red-400 hover:text-red-300 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">Metric</label>
                          <select
                            value={condition.metric}
                            onChange={(e) => updateCondition(condition.id, 'metric', e.target.value)}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            {Object.entries(METRIC_CATEGORIES).map(([category, metrics]) => (
                              <optgroup key={category} label={category}>
                                {metrics.map(metric => (
                                  <option key={metric.value} value={metric.value}>
                                    {metric.label}
                                  </option>
                                ))}
                              </optgroup>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">Team</label>
                          <select
                            value={condition.team}
                            onChange={(e) => updateCondition(condition.id, 'team', e.target.value)}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="either">Either team</option>
                            <option value="home">Home team</option>
                            <option value="away">Away team</option>
                            <option value="both">Both teams</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">Operator</label>
                          <select
                            value={condition.operator}
                            onChange={(e) => updateCondition(condition.id, 'operator', e.target.value)}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            {OPERATORS.map(op => (
                              <option key={op.value} value={op.value}>
                                {op.symbol} {op.label}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">Value</label>
                          <input
                            type="number"
                            step="0.1"
                            value={condition.value}
                            onChange={(e) => updateCondition(condition.id, 'value', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="0"
                          />
                        </div>
                      </div>

                      {/* Player Selection for Player-Specific Metrics */}
                      {condition.metric.startsWith('player_') && (
                        <div className="mt-4">
                          <label className="block text-sm font-medium text-gray-300 mb-2">Player</label>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <input
                                type="text"
                                value={condition.player_name || ''}
                                onChange={(e) => updateCondition(condition.id, 'player_name', e.target.value)}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Player name (e.g., Messi, Ronaldo)"
                              />
                            </div>
                            <div>
                              <input
                                type="number"
                                value={condition.player_id || ''}
                                onChange={(e) => updateCondition(condition.id, 'player_id', parseInt(e.target.value) || undefined)}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Player ID (optional)"
                              />
                            </div>
                          </div>
                          <p className="text-xs text-gray-400 mt-1">
                            Enter player name or ID. Player ID is more precise but name is easier to use.
                          </p>
                        </div>
                      )}

                      <div className="mt-4">
                        <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                        <input
                          type="text"
                          value={condition.description}
                          onChange={(e) => updateCondition(condition.id, 'description', e.target.value)}
                          className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`e.g., ${getMetricDescription(condition.metric)}`}
                        />
                      </div>

                      <div className="mt-4 p-3 bg-white/5 rounded text-sm text-gray-300">
                        <strong>Preview:</strong> {
                          condition.metric.startsWith('player_') && condition.player_name
                            ? `${condition.player_name} ${condition.metric.replace('player_', '')} ${getOperatorSymbol(condition.operator)} ${condition.value}`
                            : `${condition.team} team ${condition.metric} ${getOperatorSymbol(condition.operator)} ${condition.value}`
                        }
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Notification Settings */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                Notification Settings
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Notification Type</label>
                  <select
                    value={form.notificationType}
                    onChange={(e) => setForm(prev => ({ ...prev, notificationType: e.target.value as 'sms' | 'email' | 'both' }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="sms">SMS</option>
                    <option value="email">Email</option>
                    <option value="both">Both</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
                  <select
                    value={form.priority}
                    onChange={(e) => setForm(prev => ({ ...prev, priority: e.target.value as 'low' | 'medium' | 'high' }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Cooldown (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={form.cooldown}
                    onChange={(e) => setForm(prev => ({ ...prev, cooldown: parseInt(e.target.value) || 5 }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Match Selection */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-bold text-white mb-4">Match Selection</h3>
              
              {selectedMatch ? (
                <div className="bg-white/5 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-2">Selected Match</h4>
                  <div className="text-sm text-gray-300 space-y-1">
                    <p><strong>{selectedMatch.home_team}</strong> vs <strong>{selectedMatch.away_team}</strong></p>
                    <p>{selectedMatch.league}</p>
                    <p>{formatTime(selectedMatch.start_time)}</p>
                    <p className="text-blue-400">{selectedMatch.status}</p>
                  </div>
                  <button
                    onClick={() => setSelectedMatch(null)}
                    className="mt-3 text-sm text-red-400 hover:text-red-300"
                  >
                    Clear Selection
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-gray-300">Choose a specific match (optional):</p>
                  {matches.slice(0, 5).map(match => (
                    <button
                      key={match.id}
                      onClick={() => setSelectedMatch(match)}
                      className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                    >
                      <div className="font-medium text-white">{match.home_team} vs {match.away_team}</div>
                      <div className="text-gray-400">{match.league} • {formatTime(match.start_time)}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Templates */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-bold text-white mb-4">Quick Templates</h3>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      conditions: [{
                        id: Date.now().toString(),
                        metric: 'goals',
                        team: 'either',
                        operator: '>=',
                        value: 2,
                        description: 'High scoring match'
                      }]
                    }))
                  }}
                  className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                >
                  <div className="font-medium text-white">High Scoring Match</div>
                  <div className="text-gray-400">Alert when 2+ goals scored</div>
                </button>

                <button
                  onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      conditions: [{
                        id: Date.now().toString(),
                        metric: 'possession',
                        team: 'home',
                        operator: '>=',
                        value: 60,
                        description: 'Home team dominating possession'
                      }]
                    }))
                  }}
                  className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                >
                  <div className="font-medium text-white">Possession Dominance</div>
                  <div className="text-gray-400">Home team with 60%+ possession</div>
                </button>

                <button
                  onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      conditions: [{
                        id: Date.now().toString(),
                        metric: 'yellow_cards',
                        team: 'either',
                        operator: '>=',
                        value: 3,
                        description: 'Physical match with many cards'
                      }]
                    }))
                  }}
                  className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                >
                  <div className="font-medium text-white">Physical Match</div>
                  <div className="text-gray-400">3+ yellow cards in match</div>
                </button>

                <button
                  onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      conditions: [{
                        id: Date.now().toString(),
                        metric: 'player_goals',
                        team: 'either',
                        operator: '>=',
                        value: 2,
                        player_name: '',
                        description: 'Player hat-trick or brace'
                      }]
                    }))
                  }}
                  className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                >
                  <div className="font-medium text-white">Player Brace/Hat-trick</div>
                  <div className="text-gray-400">Player scores 2+ goals</div>
                </button>

                <button
                  onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      conditions: [{
                        id: Date.now().toString(),
                        metric: 'player_goal_contributions',
                        team: 'either',
                        operator: '>=',
                        value: 2,
                        player_name: '',
                        description: 'Player involved in multiple goals'
                      }]
                    }))
                  }}
                  className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                >
                  <div className="font-medium text-white">Player Goal Contributions</div>
                  <div className="text-gray-400">Player with 2+ goals/assists</div>
                </button>
              </div>
            </div>

            {/* Available Metrics */}
            <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20">
              <h3 className="text-lg font-bold text-white mb-4">Available Metrics</h3>
              <div className="space-y-2 text-sm">
                {Object.entries(METRIC_CATEGORIES).map(([category, metrics]) => (
                  <details key={category} className="group">
                    <summary className="cursor-pointer text-gray-300 hover:text-white font-medium">
                      {category} ({metrics.length})
                    </summary>
                    <div className="mt-2 ml-4 space-y-1">
                      {metrics.map(metric => (
                        <div key={metric.value} className="text-gray-400">
                          <div className="font-medium">{metric.label}</div>
                          <div className="text-xs">{metric.description}</div>
                        </div>
                      ))}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/20 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Alert Preview</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Alert Summary</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-gray-400">Name:</span> <span className="text-white">{form.name || 'Unnamed Alert'}</span></div>
                  <div><span className="text-gray-400">Team:</span> <span className="text-white">{form.team || 'Any team'}</span></div>
                  <div><span className="text-gray-400">Logic:</span> <span className="text-white">{form.logicOperator}</span></div>
                  <div><span className="text-gray-400">Notifications:</span> <span className="text-white">{form.notificationType}</span></div>
                  <div><span className="text-gray-400">Priority:</span> <span className="text-white">{form.priority}</span></div>
                </div>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <h3 className="text-lg font-bold text-white mb-3">Conditions</h3>
                {form.conditions.length === 0 ? (
                  <p className="text-gray-400">No conditions defined</p>
                ) : (
                  <div className="space-y-2">
                    {form.conditions.map((condition, index) => (
                      <div key={condition.id} className="text-sm">
                        <span className="text-gray-400">Condition {index + 1}:</span>
                        <span className="text-white ml-2">
                          {condition.team} team {condition.metric} {getOperatorSymbol(condition.operator)} {condition.value}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => setShowPreview(false)}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  Close
                </button>
                <button
                  onClick={createAlert}
                  disabled={saving}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                >
                  {saving ? 'Creating...' : 'Create Alert'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 