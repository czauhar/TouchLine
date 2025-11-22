import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { toast } from 'react-hot-toast'

interface Alert {
  id: number
  name: string
  team: string
  alert_type: string
  threshold: number
  condition: string
  user_phone: string
  is_active: boolean
  created_at: string
}

export function useAlerts() {
  const { data: session } = useSession()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAlerts = useCallback(async () => {
    if (!session) {
      setLoading(false)
      return
    }

    try {
      setError(null)
      const { apiClient } = await import('../lib/auth')
      const response = await apiClient.getAlerts()
      
      if (response.alerts) {
        setAlerts(response.alerts)
      }
    } catch (err) {
      console.error('Error fetching alerts:', err)
      setError('Failed to load alerts')
      setAlerts([])
    } finally {
      setLoading(false)
    }
  }, [session])

  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  const toggleAlert = useCallback(async (alertId: number) => {
    try {
      const response = await fetch(`/api/alerts/${alertId}/toggle`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to toggle alert')
      }

      const data = await response.json()
      
      // Update local state
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId 
            ? { ...alert, is_active: data.is_active }
            : alert
        )
      )

      toast.success(data.message || `Alert ${data.is_active ? 'activated' : 'deactivated'}`)
    } catch (err) {
      console.error('Error toggling alert:', err)
      toast.error('Failed to toggle alert')
    }
  }, [])

  const deleteAlert = useCallback(async (alertId: number) => {
    try {
      const response = await fetch(`/api/alerts/${alertId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete alert')
      }

      // Update local state
      setAlerts(prev => prev.filter(alert => alert.id !== alertId))
      
      toast.success('Alert deleted successfully')
    } catch (err) {
      console.error('Error deleting alert:', err)
      toast.error('Failed to delete alert')
    }
  }, [])

  const createAlert = useCallback(async (alertData: any) => {
    try {
      const response = await fetch('/api/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(alertData),
      })

      if (!response.ok) {
        throw new Error('Failed to create alert')
      }

      const newAlert = await response.json()
      
      // Update local state
      setAlerts(prev => [...prev, newAlert])
      
      toast.success('Alert created successfully!')
      return newAlert
    } catch (err) {
      console.error('Error creating alert:', err)
      toast.error('Failed to create alert')
      throw err
    }
  }, [])

  const refresh = useCallback(() => {
    setLoading(true)
    fetchAlerts()
  }, [fetchAlerts])

  // Calculate stats
  const stats = {
    total_alerts: alerts.length,
    active_alerts: alerts.filter(a => a.is_active).length,
    inactive_alerts: alerts.filter(a => !a.is_active).length,
  }

  return {
    alerts,
    loading,
    error,
    refresh,
    toggleAlert,
    deleteAlert,
    createAlert,
    stats,
  }
}

