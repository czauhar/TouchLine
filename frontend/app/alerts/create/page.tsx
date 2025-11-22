'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiClient } from '../../../lib/auth'
import Link from 'next/link'
import toast from 'react-hot-toast'
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
  Layers,
  ChevronLeft,
  ChevronRight,
  Check
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
  const [currentStep, setCurrentStep] = useState(1) // Wizard steps: 1=Basic, 2=Conditions, 3=Notifications, 4=Review
  
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
    // Validate condition values
    for (const condition of form.conditions) {
      if (typeof condition.value === 'number' && isNaN(condition.value)) {
        return `Condition "${condition.metric}" has an invalid value`
      }
      if (condition.metric.startsWith('player_') && !condition.player_name && !condition.player_id) {
        return `Player-specific metric "${condition.metric}" requires a player name or ID`
      }
    }
    return null
  }

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1: // Basic Info
        return form.name.trim().length > 0
      case 2: // Conditions
        return form.conditions.length > 0 && form.conditions.every(c => c.description.trim().length > 0)
      case 3: // Notifications
        return true // No required fields in notifications step
      case 4: // Review
        return validateForm() === null
      default:
        return false
    }
  }

  const nextStep = () => {
    if (currentStep < 4 && validateStep(currentStep)) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const createAlert = async () => {
    const error = validateForm()
    if (error) {
      toast.error(error)
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
      toast.success('Alert created successfully!')
      router.push('/alerts')
    } catch (error) {
      console.error('Error creating alert:', error)
      toast.error('Failed to create alert. Please try again.')
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Progress Bar */}
      <div className="relative bg-white/10 backdrop-blur-xl border-b border-white/20 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <Link href="/alerts" className="text-gray-400 hover:text-white transition-all duration-300 hover:scale-110">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <div className="flex-1 max-w-4xl mx-8">
              <h1 className="text-3xl font-black text-gradient mb-2 text-center">Create Alert</h1>
              <p className="text-gray-300 text-center">Step {currentStep} of 4</p>
            </div>
            <button
              onClick={() => setShowPreview(true)}
              className="btn-secondary flex items-center"
            >
              <Eye className="w-5 h-5 mr-2" />
              Preview
            </button>
          </div>
          
          {/* Step Indicators */}
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            {[
              { step: 1, title: 'Basic Info', icon: Target },
              { step: 2, title: 'Conditions', icon: Layers },
              { step: 3, title: 'Notifications', icon: Bell },
              { step: 4, title: 'Review', icon: Check }
            ].map(({ step, title, icon: Icon }, index) => (
              <div key={step} className="flex items-center flex-1">
                <div
                  className={`flex flex-col items-center justify-center w-full ${
                    step < currentStep ? 'text-green-500' :
                    step === currentStep ? 'text-blue-500' :
                    'text-gray-500'
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-full border-2 flex items-center justify-center mb-2 transition-all ${
                      step < currentStep
                        ? 'bg-green-500 border-green-500 text-white'
                        : step === currentStep
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : 'bg-transparent border-gray-600 text-gray-400'
                    }`}
                  >
                    {step < currentStep ? (
                      <Check className="w-6 h-6" />
                    ) : (
                      <Icon className="w-6 h-6" />
                    )}
                  </div>
                  <span className="text-xs font-medium hidden md:block">{title}</span>
                </div>
                {index < 3 && (
                  <div
                    className={`hidden md:block h-1 flex-1 mx-2 rounded ${
                      step < currentStep ? 'bg-green-500' : 'bg-gray-700'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step 1: Basic Information */}
        {currentStep === 1 && (
          <div className="card-elevated p-8 animate-slide-in-up">
              <h2 className="text-2xl font-bold text-white mb-8 flex items-center">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mr-4">
                  <Target className="w-5 h-5 text-white" />
                </div>
                Basic Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-lg font-semibold text-gray-300 mb-3">
                    Alert Name
                    <span className="text-red-400 ml-1">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                    className={`input-primary text-lg ${!form.name.trim() ? 'border-red-500/50' : ''}`}
                    placeholder="Enter alert name..."
                  />
                  {!form.name.trim() && (
                    <p className="mt-1 text-sm text-red-400">Alert name is required</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-lg font-semibold text-gray-300 mb-3">Team</label>
                  <input
                    type="text"
                    value={form.team}
                    onChange={(e) => setForm(prev => ({ ...prev, team: e.target.value }))}
                    className="input-primary text-lg"
                    placeholder="Team name (optional)"
                  />
                </div>
              </div>
              
              <div className="mt-8">
                <label className="block text-lg font-semibold text-gray-300 mb-3">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                  rows={4}
                  className="input-primary text-lg resize-none"
                  placeholder="Describe what this alert monitors..."
                />
              </div>

              {/* Match Selection in Step 1 */}
              <div className="mt-8">
                <label className="block text-lg font-semibold text-gray-300 mb-3">Match Selection (Optional)</label>
                {selectedMatch ? (
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <h4 className="font-medium text-white mb-2">Selected Match</h4>
                    <div className="text-sm text-gray-300 space-y-1">
                      <p><strong>{selectedMatch.home_team}</strong> vs <strong>{selectedMatch.away_team}</strong></p>
                      <p>{selectedMatch.league}</p>
                      <p>{formatTime(selectedMatch.start_time)}</p>
                      <p className="text-blue-400">{selectedMatch.status}</p>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedMatch(null)
                        setForm(prev => ({ ...prev, matchId: undefined }))
                      }}
                      className="mt-3 text-sm text-red-400 hover:text-red-300"
                    >
                      Clear Selection
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    <p className="text-sm text-gray-300 mb-3">Choose a specific match (optional):</p>
                    {matches.slice(0, 10).map(match => (
                      <button
                        key={match.id}
                        onClick={() => {
                          setSelectedMatch(match)
                          setForm(prev => ({
                            ...prev,
                            matchId: match.id,
                            name: `${match.home_team} vs ${match.away_team} Alert`,
                            team: match.home_team
                          }))
                        }}
                        className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition text-sm"
                      >
                        <div className="font-medium text-white">{match.home_team} vs {match.away_team}</div>
                        <div className="text-gray-400">{match.league} • {formatTime(match.start_time)}</div>
                      </button>
                    ))}
                    {matches.length === 0 && (
                      <p className="text-sm text-gray-400 text-center py-4">No matches available</p>
                    )}
                  </div>
                )}
              </div>
          </div>
        )}

        {/* Step 2: Conditions */}
        {currentStep === 2 && (
          <div className="card-elevated p-8 animate-slide-in-up" style={{animationDelay: '0.1s'}}>
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-white flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center mr-4">
                    <Layers className="w-5 h-5 text-white" />
                  </div>
                  Alert Conditions
                </h2>
                <div className="flex items-center space-x-4">
                  <select
                    value={form.logicOperator}
                    onChange={(e) => setForm(prev => ({ ...prev, logicOperator: e.target.value as 'AND' | 'OR' }))}
                    className="input-secondary text-sm"
                  >
                    <option value="AND">ALL conditions (AND)</option>
                    <option value="OR">ANY condition (OR)</option>
                  </select>
                  <button
                    onClick={addCondition}
                    className="btn-primary text-sm px-4 py-2 flex items-center"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Condition
                  </button>
                </div>
              </div>

              {form.conditions.length === 0 ? (
                <div className="text-center py-8 border-2 border-dashed border-gray-600 rounded-lg">
                  <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-300 mb-2">No conditions added yet</p>
                  <p className="text-gray-400 text-sm mb-4">Add at least one condition to create your alert</p>
                  <button
                    onClick={addCondition}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium"
                  >
                    <Plus className="w-4 h-4 inline mr-2" />
                    Add Your First Condition
                  </button>
                  <p className="text-red-400 text-sm mt-2">⚠️ At least one condition is required</p>
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
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Metric
                            {condition.metric && (
                              <span className="ml-2 text-xs text-gray-400 font-normal" title={getMetricDescription(condition.metric)}>
                                (ℹ️ {getMetricDescription(condition.metric)})
                              </span>
                            )}
                          </label>
                          <select
                            value={condition.metric}
                            onChange={(e) => updateCondition(condition.id, 'metric', e.target.value)}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            title={getMetricDescription(condition.metric)}
                          >
                            {Object.entries(METRIC_CATEGORIES).map(([category, metrics]) => (
                              <optgroup key={category} label={category}>
                                {metrics.map(metric => (
                                  <option key={metric.value} value={metric.value} title={metric.description}>
                                    {metric.label}
                                  </option>
                                ))}
                              </optgroup>
                            ))}
                          </select>
                          {condition.metric && (
                            <p className="mt-1 text-xs text-gray-400">{getMetricDescription(condition.metric)}</p>
                          )}
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
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Description
                          <span className="text-red-400 ml-1">*</span>
                        </label>
                        <input
                          type="text"
                          value={condition.description}
                          onChange={(e) => updateCondition(condition.id, 'description', e.target.value)}
                          className={`w-full px-3 py-2 bg-white/10 border rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                            !condition.description.trim() ? 'border-red-500/50' : 'border-white/20'
                          }`}
                          placeholder={`e.g., ${getMetricDescription(condition.metric)}`}
                        />
                        {!condition.description.trim() && (
                          <p className="mt-1 text-xs text-red-400">Description is required</p>
                        )}
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
        )}

        {/* Step 3: Notifications */}
        {currentStep === 3 && (
          <div className="card-elevated p-8 animate-slide-in-up">
            <h2 className="text-2xl font-bold text-white mb-8 flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center mr-4">
                <Bell className="w-5 h-5 text-white" />
              </div>
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
        )}

        {/* Step 4: Review */}
        {currentStep === 4 && (
          <div className="card-elevated p-8 animate-slide-in-up">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
                <Check className="w-5 h-5 text-white" />
              </div>
              Review Alert
            </h2>
            
            <div className="space-y-6">
              <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-4">Alert Summary</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Name:</span>
                    <span className="text-white font-medium">{form.name || 'Unnamed Alert'}</span>
                  </div>
                  {form.description && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Description:</span>
                      <span className="text-white">{form.description}</span>
                    </div>
                  )}
                  {form.team && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Team:</span>
                      <span className="text-white">{form.team}</span>
                    </div>
                  )}
                  {selectedMatch && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Match:</span>
                      <span className="text-white">{selectedMatch.home_team} vs {selectedMatch.away_team}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-400">Logic:</span>
                    <span className="text-white">{form.logicOperator === 'AND' ? 'ALL conditions' : 'ANY condition'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Notifications:</span>
                    <span className="text-white">{form.notificationType.toUpperCase()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Priority:</span>
                    <span className="text-white capitalize">{form.priority}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cooldown:</span>
                    <span className="text-white">{form.cooldown} minutes</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-4">Conditions ({form.conditions.length})</h3>
                {form.conditions.length === 0 ? (
                  <p className="text-gray-400">No conditions defined</p>
                ) : (
                  <div className="space-y-3">
                    {form.conditions.map((condition, index) => (
                      <div key={condition.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-white">Condition {index + 1}</span>
                          {condition.description && (
                            <span className="text-xs text-gray-400">{condition.description}</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-300">
                          {condition.metric.startsWith('player_') && condition.player_name
                            ? `${condition.player_name} ${condition.metric.replace('player_', '')} ${getOperatorSymbol(condition.operator)} ${condition.value}`
                            : `${condition.team} team ${condition.metric} ${getOperatorSymbol(condition.operator)} ${condition.value}`
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/20">
          <button
            onClick={currentStep === 1 ? () => router.push('/alerts') : prevStep}
            className="flex items-center px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 mr-2" />
            {currentStep === 1 ? 'Cancel' : 'Back'}
          </button>

          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>Step {currentStep} of 4</span>
          </div>

          {currentStep === 4 ? (
            <button
              onClick={createAlert}
              disabled={!validateStep(4) || saving}
              className="flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5 mr-2" />
                  Create Alert
                </>
              )}
            </button>
          ) : (
            <button
              onClick={nextStep}
              disabled={!validateStep(currentStep)}
              className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight className="w-5 h-5 ml-2" />
            </button>
          )}
        </div>

        {/* Validation Message */}
        {!validateStep(currentStep) && (
          <div className="mt-4 flex items-center text-yellow-400 text-sm bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
            <AlertTriangle className="w-4 h-4 mr-2" />
            Please complete all required fields to continue
          </div>
        )}

        {/* Sidebar - Only show in relevant steps */}
        {currentStep === 2 && (
          <div className="fixed right-8 top-1/2 transform -translate-y-1/2 space-y-6 max-w-xs">
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