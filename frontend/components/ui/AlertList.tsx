import React from 'react'

export interface Alert {
  id: number
  name: string
  is_active: boolean
  conditions: string
  created_at: string
  team: string
  alert_type: string
  threshold: number
  user_phone: string
}

interface AlertListProps {
  alerts: Alert[]
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export default function AlertList({ alerts, onToggle, onDelete }: AlertListProps) {
  if (!alerts.length) {
    return <div className="text-center py-8 text-gray-500">No alerts yet.</div>
  }
  return (
    <div className="space-y-4">
      {alerts.map(alert => (
        <div key={alert.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="font-medium text-gray-900">{alert.name}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-2">{alert.conditions}</p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>Team: {alert.team}</span>
                <span>Type: {alert.alert_type}</span>
                <span>Threshold: {alert.threshold}</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onToggle(alert.id)}
                className={`px-3 py-1 text-xs rounded ${
                  alert.is_active 
                    ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {alert.is_active ? 'Disable' : 'Enable'}
              </button>
              <button
                onClick={() => onDelete(alert.id)}
                className="px-3 py-1 text-xs rounded bg-red-100 text-red-700 hover:bg-red-200"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 