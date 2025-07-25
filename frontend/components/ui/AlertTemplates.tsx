'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '../../lib/auth'

interface AlertTemplate {
  id: string
  name: string
  description: string
  conditions: {
    logic_operator: string
    conditions: Array<{
      type: string
      team: string
      operator: string
      value: number
      description: string
    }>
    time_windows?: Array<{
      start_minute: number
      end_minute: number
    }>
  }
}

interface AlertTemplatesProps {
  onTemplateSelect: (template: AlertTemplate) => void
  onClose: () => void
}

export default function AlertTemplates({ onTemplateSelect, onClose }: AlertTemplatesProps) {
  const [templates, setTemplates] = useState<AlertTemplate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const data = await apiClient.getAlertTemplates()
      setTemplates(data.templates || [])
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const getConditionTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'goals': 'Goals',
      'score_difference': 'Score Difference',
      'possession': 'Possession',
      'xg': 'Expected Goals (xG)',
      'momentum': 'Momentum',
      'pressure': 'Pressure Index',
      'win_probability': 'Win Probability',
      'shots': 'Shots',
      'shots_on_target': 'Shots on Target',
      'corners': 'Corners',
      'cards': 'Cards'
    }
    return labels[type] || type
  }

  const getOperatorLabel = (operator: string) => {
    const labels: { [key: string]: string } = {
      '>=': '≥',
      '>': '>',
      '<=': '≤',
      '<': '<',
      '==': '=',
      '!=': '≠'
    }
    return labels[operator] || operator
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading templates...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900">Alert Templates</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          Choose from these pre-built alert templates to get started quickly. You can customize them after selection.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map((template) => (
            <div key={template.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
                  <p className="text-gray-600 text-sm">{template.description}</p>
                </div>
                <button
                  onClick={() => onTemplateSelect(template)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                >
                  Use Template
                </button>
              </div>

              <div className="space-y-3">
                <div className="text-sm text-gray-500">
                  Logic: <span className="font-medium">{template.conditions.logic_operator}</span>
                </div>
                
                <div className="space-y-2">
                  {template.conditions.conditions.map((condition, index) => (
                    <div key={index} className="bg-gray-50 rounded p-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700">
                          {getConditionTypeLabel(condition.type)}
                        </span>
                        <span className="text-gray-600">
                          {condition.team || 'Any team'} {getOperatorLabel(condition.operator)} {condition.value}
                        </span>
                      </div>
                      {condition.description && (
                        <p className="text-xs text-gray-500 mt-1">{condition.description}</p>
                      )}
                    </div>
                  ))}
                </div>

                {template.conditions.time_windows && template.conditions.time_windows.length > 0 && (
                  <div className="bg-blue-50 rounded p-3">
                    <div className="text-sm font-medium text-blue-700 mb-1">Time Windows:</div>
                    {template.conditions.time_windows.map((window, index) => (
                      <div key={index} className="text-xs text-blue-600">
                        Minutes {window.start_minute}-{window.end_minute}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
} 