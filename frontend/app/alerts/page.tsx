'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Alert {
  id: number
  name: string
  is_active: boolean
  conditions: string
  created_at: string
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showAdvancedForm, setShowAdvancedForm] = useState(false)
  const [newAlert, setNewAlert] = useState({
    name: '',
    conditions: ''
  })

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts')
      const data = await response.json()
      setAlerts(data.alerts || [])
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/api/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAlert),
      })
      
      if (response.ok) {
        setNewAlert({ name: '', conditions: '' })
        setShowCreateForm(false)
        fetchAlerts()
      }
    } catch (error) {
      console.error('Error creating alert:', error)
    }
  }

  const toggleAlert = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${id}/toggle`, {
        method: 'PUT',
      })
      
      if (response.ok) {
        fetchAlerts()
      }
    } catch (error) {
      console.error('Error toggling alert:', error)
    }
  }

  const deleteAlert = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${id}`, {
        method: 'DELETE',
      })
      
      if (response.ok) {
        fetchAlerts()
      }
    } catch (error) {
      console.error('Error deleting alert:', error)
    }
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
              Alert Management
            </h1>
            <p className="text-2xl text-gray-300 mb-10">Create and manage your intelligent soccer alerts</p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button
                onClick={() => setShowCreateForm(true)}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-5 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2 flex items-center justify-center">
                  <span className="mr-3">➕</span>
                  Create Alert
                </div>
              </button>
              <button
                onClick={() => setShowAdvancedForm(true)}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-5 rounded-2xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2 flex items-center justify-center">
                  <span className="mr-3">⚡</span>
                  Advanced Alerts
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500">
                    <span className="text-3xl text-white">🔔</span>
                  </div>
                  <div className="ml-6">
                    <p className="text-sm font-medium text-gray-400">Total Alerts</p>
                    <p className="text-4xl font-black text-gray-200">{alerts.length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500">
                    <span className="text-3xl text-white">🟢</span>
                  </div>
                  <div className="ml-6">
                    <p className="text-sm font-medium text-gray-400">Active Alerts</p>
                    <p className="text-4xl font-black text-gray-200">{alerts.filter(a => a.is_active).length}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500">
                    <span className="text-3xl text-white">⚡</span>
                  </div>
                  <div className="ml-6">
                    <p className="text-sm font-medium text-gray-400">Advanced Alerts</p>
                    <p className="text-4xl font-black text-gray-200">0</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Simple Alerts Section */}
          <div className="relative mb-12">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
              <h2 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-6">
                Simple Alerts
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

          {/* Advanced Alerts Section */}
          <div className="relative mb-12">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-3xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
              <h2 className="text-3xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-6">
                Advanced Alerts
              </h2>
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚡</div>
                <h3 className="text-2xl font-bold text-gray-200 mb-2">Coming Soon</h3>
                <p className="text-gray-400">Advanced multi-condition alerts with AND/OR logic</p>
              </div>
            </div>
          </div>

          {/* Create Alert Modal */}
          {showCreateForm && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-xl"></div>
                <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8 max-w-md w-full mx-4">
                  <h3 className="text-2xl font-bold text-gray-200 mb-6">Create New Alert</h3>
                  <form onSubmit={createAlert} className="space-y-4">
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
                        Conditions
                      </label>
                      <textarea
                        value={newAlert.conditions}
                        onChange={(e) => setNewAlert({ ...newAlert, conditions: e.target.value })}
                        className="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:border-blue-500 h-24"
                        required
                      />
                    </div>
                    <div className="flex gap-4">
                      <button
                        type="submit"
                        className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold"
                      >
                        Create Alert
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowCreateForm(false)}
                        className="flex-1 bg-gray-700 text-gray-300 px-6 py-3 rounded-xl hover:bg-gray-600 transition-all duration-300 font-bold"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}

          {/* Advanced Alert Modal */}
          {showAdvancedForm && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-3xl blur-xl"></div>
                <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8 max-w-md w-full mx-4">
                  <h3 className="text-2xl font-bold text-gray-200 mb-6">Advanced Alerts</h3>
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">⚡</div>
                    <p className="text-gray-400 mb-6">Advanced multi-condition alerts coming soon!</p>
                    <button
                      onClick={() => setShowAdvancedForm(false)}
                      className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-bold"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 