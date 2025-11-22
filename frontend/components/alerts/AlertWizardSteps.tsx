'use client'

import { useState, useEffect } from 'react'
import { Plus, Trash2, Target, Bell, CheckCircle, Eye, Layers } from 'lucide-react'
import { Match, AlertCondition, AlertForm, METRIC_CATEGORIES, OPERATORS } from '../types/alert'

// Export types that will be used
export interface AlertWizardData extends AlertForm {}

export interface AlertWizardStep {
  id: string
  title: string
  description: string
  component: React.ReactNode
  isValid: boolean
}

interface BasicInfoStepProps {
  form: AlertWizardData
  setForm: (updater: (prev: AlertWizardData) => AlertWizardData) => void
  matches: Match[]
  selectedMatch: Match | null
  setSelectedMatch: (match: Match | null) => void
  formatTime: (dateString: string) => string
}

function BasicInfoStep({ form, setForm, matches, selectedMatch, setSelectedMatch, formatTime }: BasicInfoStepProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white/5 rounded-lg p-6 border border-white/10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Alert Name
              <span className="text-red-400 ml-1">*</span>
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
              className={`w-full px-4 py-3 bg-white/10 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                !form.name.trim() ? 'border-red-500/50' : 'border-white/20'
              }`}
              placeholder="Enter alert name..."
            />
            {!form.name.trim() && (
              <p className="mt-1 text-sm text-red-400">Alert name is required</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Team</label>
            <input
              type="text"
              value={form.team}
              onChange={(e) => setForm(prev => ({ ...prev, team: e.target.value }))}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Team name (optional)"
            />
          </div>
        </div>
        
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            value={form.description}
            onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
            rows={4}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Describe what this alert monitors..."
          />
        </div>
      </div>

      {/* Match Selection */}
      <div className="bg-white/5 rounded-lg p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">Match Selection (Optional)</h3>
        
        {selectedMatch ? (
          <div className="bg-white/10 rounded-lg p-4">
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
  )
}

interface ConditionsStepProps {
  form: AlertWizardData
  setForm: (updater: (prev: AlertWizardData) => AlertWizardData) => void
  getMetricDescription: (metric: string) => string
  getOperatorSymbol: (operator: string) => string
}

function ConditionsStep({ form, setForm, getMetricDescription, getOperatorSymbol }: ConditionsStepProps) {
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">Alert Conditions</h3>
          <p className="text-sm text-gray-400">
            Define when this alert should trigger. You can use {form.logicOperator === 'AND' ? 'ALL' : 'ANY'} conditions.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={form.logicOperator}
            onChange={(e) => setForm(prev => ({ ...prev, logicOperator: e.target.value as 'AND' | 'OR' }))}
            className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="AND">ALL conditions (AND)</option>
            <option value="OR">ANY condition (OR)</option>
          </select>
          <button
            onClick={addCondition}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Condition
          </button>
        </div>
      </div>

      {form.conditions.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-600 rounded-lg bg-white/5">
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
            <div key={condition.id} className="bg-white/5 rounded-lg p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">Condition {index + 1}</h3>
                <button
                  onClick={() => removeCondition(condition.id)}
                  className="text-red-400 hover:text-red-300 transition"
                >
                  <Trash2 className="w-5 h-5" />
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
  )
}

interface NotificationsStepProps {
  form: AlertWizardData
  setForm: (updater: (prev: AlertWizardData) => AlertWizardData) => void
}

function NotificationsStep({ form, setForm }: NotificationsStepProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white/5 rounded-lg p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
          <Bell className="w-5 h-5 mr-2" />
          Notification Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Notification Type</label>
            <select
              value={form.notificationType}
              onChange={(e) => setForm(prev => ({ ...prev, notificationType: e.target.value as 'sms' | 'email' | 'both' }))}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="sms">SMS</option>
              <option value="email">Email</option>
              <option value="both">Both</option>
            </select>
            <p className="mt-1 text-xs text-gray-400">How you want to be notified</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
            <select
              value={form.priority}
              onChange={(e) => setForm(prev => ({ ...prev, priority: e.target.value as 'low' | 'medium' | 'high' }))}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <p className="mt-1 text-xs text-gray-400">Alert importance level</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Cooldown (minutes)</label>
            <input
              type="number"
              min="1"
              max="60"
              value={form.cooldown}
              onChange={(e) => setForm(prev => ({ ...prev, cooldown: parseInt(e.target.value) || 5 }))}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-400">Time between notifications</p>
          </div>
        </div>
      </div>

      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start">
          <Eye className="w-5 h-5 text-blue-400 mr-3 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-400 mb-1">Notification Tips</h4>
            <ul className="text-xs text-gray-300 space-y-1 list-disc list-inside">
              <li>Higher priority alerts are processed first</li>
              <li>Cooldown prevents notification spam for similar events</li>
              <li>SMS notifications require a valid phone number in your profile</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

interface ReviewStepProps {
  form: AlertWizardData
  selectedMatch: Match | null
  getMetricDescription: (metric: string) => string
  getOperatorSymbol: (operator: string) => string
  formatTime: (dateString: string) => string
}

function ReviewStep({ form, selectedMatch, getMetricDescription, getOperatorSymbol, formatTime }: ReviewStepProps) {
  return (
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
  )
}

export { BasicInfoStep, ConditionsStep, NotificationsStep, ReviewStep }

