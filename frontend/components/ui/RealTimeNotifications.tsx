'use client'

import { useState, useEffect, useRef } from 'react'
import { Bell, X, AlertTriangle, CheckCircle, Info, Zap } from 'lucide-react'

interface Notification {
  id: string
  type: 'alert_triggered' | 'match_update' | 'system_status' | 'player_update'
  data: any
  timestamp: string
  user_id?: number
}

interface RealTimeNotificationsProps {
  userId?: number
  className?: string
}

export default function RealTimeNotifications({ userId, className = '' }: RealTimeNotificationsProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    connectWebSocket()
    return () => {
      disconnectWebSocket()
    }
  }, [userId])

  const connectWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = userId 
        ? `${protocol}//${window.location.host}/ws/user?token=${userId}`
        : `${protocol}//${window.location.host}/ws/broadcast`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        console.log('WebSocket connected')
        
        // Send initial ping
        ws.send(JSON.stringify({ type: 'ping' }))
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        console.log('WebSocket disconnected')
        
        // Attempt to reconnect after 5 seconds
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket()
        }, 5000)
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }

    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
      setIsConnected(false)
    }
  }

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }

  const handleWebSocketMessage = (message: any) => {
    if (message.type === 'pong') {
      // Connection health check
      return
    }

    const notification: Notification = {
      id: `${message.type}_${Date.now()}_${Math.random()}`,
      type: message.type,
      data: message.data,
      timestamp: message.timestamp,
      user_id: message.user_id
    }

    setNotifications(prev => [notification, ...prev.slice(0, 9)]) // Keep last 10 notifications

    // Auto-hide notifications after 10 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id))
    }, 10000)
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'alert_triggered':
        return <Zap className="w-5 h-5 text-yellow-500" />
      case 'match_update':
        return <Info className="w-5 h-5 text-blue-500" />
      case 'system_status':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'player_update':
        return <AlertTriangle className="w-5 h-5 text-purple-500" />
      default:
        return <Bell className="w-5 h-5 text-gray-500" />
    }
  }

  const getNotificationTitle = (type: string, data: any) => {
    switch (type) {
      case 'alert_triggered':
        return `Alert: ${data.alert_name || 'Unknown Alert'}`
      case 'match_update':
        return `Match Update: ${data.home_team || 'Unknown'} vs ${data.away_team || 'Unknown'}`
      case 'system_status':
        return `System Status: ${data.status || 'Unknown'}`
      case 'player_update':
        return `Player Update: ${data.player_name || 'Unknown Player'}`
      default:
        return 'Notification'
    }
  }

  const getNotificationMessage = (type: string, data: any) => {
    switch (type) {
      case 'alert_triggered':
        return data.trigger_message || 'Alert condition met'
      case 'match_update':
        return `${data.home_score || 0} - ${data.away_score || 0} (${data.elapsed || 0}')`
      case 'system_status':
        return data.message || 'System status updated'
      case 'player_update':
        return `${data.stat_type || 'stat'}: ${data.value || 'N/A'}`
      default:
        return 'New notification received'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSecs = Math.floor(diffMs / 1000)
    
    if (diffSecs < 60) {
      return `${diffSecs}s ago`
    } else if (diffSecs < 3600) {
      return `${Math.floor(diffSecs / 60)}m ago`
    } else {
      return date.toLocaleTimeString()
    }
  }

  return (
    <div className={`relative ${className}`}>
      {/* Notification Bell */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
      >
        <Bell className="w-5 h-5 text-white" />
        
        {/* Connection Status Indicator */}
        <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-red-500'
        }`} />
        
        {/* Notification Count */}
        {notifications.length > 0 && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {notifications.length}
          </div>
        )}
      </button>

      {/* Notifications Panel */}
      {showNotifications && (
        <div className="absolute right-0 top-12 w-80 bg-white/10 backdrop-blur-xl rounded-lg border border-white/20 shadow-xl z-50">
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center justify-between">
              <h3 className="text-white font-semibold">Real-Time Notifications</h3>
              <button
                onClick={() => setShowNotifications(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center mt-2">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-xs text-gray-300">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No notifications yet</p>
              </div>
            ) : (
              <div className="p-2">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="mb-2 p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        {getNotificationIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-white truncate">
                            {getNotificationTitle(notification.type, notification.data)}
                          </h4>
                          <p className="text-xs text-gray-300 mt-1">
                            {getNotificationMessage(notification.type, notification.data)}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatTimestamp(notification.timestamp)}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeNotification(notification.id)}
                        className="text-gray-400 hover:text-white ml-2"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {notifications.length > 0 && (
            <div className="p-3 border-t border-white/10">
              <button
                onClick={() => setNotifications([])}
                className="w-full text-xs text-gray-400 hover:text-white transition-colors"
              >
                Clear all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 