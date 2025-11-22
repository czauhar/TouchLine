import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Bell, BellOff, Trash2, Edit } from 'lucide-react'

interface AlertCardProps {
  alert: {
    id: number
    name: string
    team: string
    alert_type: string
    condition: string
    is_active: boolean
    created_at: string
  }
  onToggle: (id: number) => void
  onDelete: (id: number) => void
  onEdit?: (id: number) => void
}

export function AlertCard({ alert, onToggle, onDelete, onEdit }: AlertCardProps) {
  return (
    <Card variant="glass" hover>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>{alert.name}</CardTitle>
            <p className="text-sm text-slate-400 mt-1">{alert.team}</p>
          </div>
          <Badge variant={alert.is_active ? 'success' : 'default'}>
            {alert.is_active ? 'Active' : 'Inactive'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Alert Type */}
          <div>
            <p className="text-xs text-slate-500 uppercase mb-1">Alert Type</p>
            <p className="text-sm text-white">{alert.alert_type}</p>
          </div>

          {/* Condition */}
          <div>
            <p className="text-xs text-slate-500 uppercase mb-1">Condition</p>
            <p className="text-sm text-slate-300">{alert.condition}</p>
          </div>

          {/* Created Date */}
          <div>
            <p className="text-xs text-slate-500 uppercase mb-1">Created</p>
            <p className="text-sm text-slate-400">
              {new Date(alert.created_at).toLocaleDateString()}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t border-slate-800">
            <Button
              variant={alert.is_active ? 'ghost' : 'success'}
              size="sm"
              onClick={() => onToggle(alert.id)}
              className="flex-1"
            >
              {alert.is_active ? (
                <>
                  <BellOff className="w-4 h-4 mr-2" />
                  Deactivate
                </>
              ) : (
                <>
                  <Bell className="w-4 h-4 mr-2" />
                  Activate
                </>
              )}
            </Button>
            {onEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(alert.id)}
              >
                <Edit className="w-4 h-4" />
              </Button>
            )}
            <Button
              variant="danger"
              size="sm"
              onClick={() => onDelete(alert.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

