'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [liveMatchesCount, setLiveMatchesCount] = useState(0)
  const [todaysMatchesCount, setTodaysMatchesCount] = useState(0)

  useEffect(() => {
    // Check backend connection and fetch match counts
    const checkBackend = async () => {
      try {
        const [healthResponse, liveResponse, todayResponse] = await Promise.all([
          fetch('http://localhost:8000/health'),
          fetch('http://localhost:8000/api/matches/live'),
          fetch('http://localhost:8000/api/matches/today')
        ])
        
        const healthData = await healthResponse.json()
        const liveData = await liveResponse.json()
        const todayData = await todayResponse.json()
        
        setIsBackendConnected(healthData.status === 'healthy')
        setLiveMatchesCount(liveData.count)
        setTodaysMatchesCount(todayData.count)
      } catch (error) {
        setIsBackendConnected(false)
      } finally {
        setLoading(false)
      }
    }
    
    checkBackend()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-2xl shadow-2xl">
                <span className="text-6xl">⚽</span>
              </div>
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-6">
              TouchLine
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Real-time sports alerts and intelligent notifications powered by advanced analytics
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center">
              <div className={`p-3 rounded-xl ${isBackendConnected ? 'bg-green-100' : 'bg-red-100'}`}>
                <span className={`text-2xl ${isBackendConnected ? 'text-green-600' : 'text-red-600'}`}>
                  {isBackendConnected ? '🔌' : '❌'}
                </span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Backend</p>
                <p className={`text-lg font-semibold ${isBackendConnected ? 'text-green-600' : 'text-red-600'}`}>
                  {isBackendConnected ? 'Connected' : 'Disconnected'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-blue-100">
                <span className="text-2xl text-blue-600">🌐</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Frontend</p>
                <p className="text-lg font-semibold text-blue-600">Running</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-green-100">
                <span className="text-2xl text-green-600">💾</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Database</p>
                <p className="text-lg font-semibold text-green-600">Configured</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-yellow-100">
                <span className="text-2xl text-yellow-600">📱</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">SMS Service</p>
                <p className="text-lg font-semibold text-yellow-600">Not configured</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 mb-12">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Live Statistics</h2>
            <p className="text-gray-600">Real-time match data and analytics</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="text-center">
              <div className="bg-gradient-to-r from-red-500 to-pink-500 p-6 rounded-2xl mb-4">
                <span className="text-4xl text-white font-bold">{liveMatchesCount}</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Live Matches</h3>
              <p className="text-gray-600">Currently in progress</p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 rounded-2xl mb-4">
                <span className="text-4xl text-white font-bold">{todaysMatchesCount}</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Today's Matches</h3>
              <p className="text-gray-600">Scheduled for today</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/matches"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              🏟️ View Live Matches
            </Link>
            <Link 
              href="/alerts"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              🔔 Manage Alerts
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="text-center">
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-4 rounded-xl inline-block mb-4">
                <span className="text-3xl text-white">⚡</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-time Alerts</h3>
              <p className="text-gray-600">Get instant notifications for goals, momentum shifts, and key events</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4 rounded-xl inline-block mb-4">
                <span className="text-3xl text-white">📊</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Advanced Analytics</h3>
              <p className="text-gray-600">xG, momentum, pressure index, and win probability calculations</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
            <div className="text-center">
              <div className="bg-gradient-to-r from-green-500 to-emerald-500 p-4 rounded-xl inline-block mb-4">
                <span className="text-3xl text-white">🤖</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Logic</h3>
              <p className="text-gray-600">Multi-condition alerts with AND/OR logic and time windows</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Phase 1: Foundation & Architecture</h3>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center text-gray-600">
              <div className="flex items-center">
                <span className="mr-2">🐍</span>
                <span>Backend: Python FastAPI</span>
              </div>
              <div className="flex items-center">
                <span className="mr-2">⚛️</span>
                <span>Frontend: Next.js</span>
              </div>
              <div className="flex items-center">
                <span className="mr-2">📱</span>
                <span>SMS: Twilio Integration</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 