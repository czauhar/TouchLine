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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-cyan-600/20 animate-gradient"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 rounded-3xl glow-cyan hover-glow-cyan transition-all duration-500">
                <span className="text-8xl">⚽</span>
              </div>
            </div>
            <h1 className="text-7xl font-black bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent text-glow-cyan mb-8">
              TouchLine
            </h1>
            <p className="text-2xl text-gray-300 mb-16 max-w-3xl mx-auto leading-relaxed">
              Real-time sports alerts and intelligent notifications powered by advanced analytics
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-6 hover:bg-gray-800/70 transition-all duration-300 hover-glow-green">
            <div className="flex items-center">
              <div className={`p-4 rounded-2xl ${isBackendConnected ? 'bg-green-500/20 glow-green' : 'bg-red-500/20 glow-red'}`}>
                <span className={`text-3xl ${isBackendConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {isBackendConnected ? '🔌' : '❌'}
                </span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Backend</p>
                <p className={`text-xl font-bold ${isBackendConnected ? 'text-green-400 text-glow-green' : 'text-red-400 text-glow-red'}`}>
                  {isBackendConnected ? 'Connected' : 'Disconnected'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-6 hover:bg-gray-800/70 transition-all duration-300 hover-glow-blue">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-blue-500/20 glow-blue">
                <span className="text-3xl text-blue-400">🌐</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Frontend</p>
                <p className="text-xl font-bold text-blue-400 text-glow-blue">Running</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-6 hover:bg-gray-800/70 transition-all duration-300 hover-glow-green">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-green-500/20 glow-green">
                <span className="text-3xl text-green-400">💾</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Database</p>
                <p className="text-xl font-bold text-green-400 text-glow-green">Configured</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-6 hover:bg-gray-800/70 transition-all duration-300 hover-glow-cyan">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-cyan-500/20 glow-cyan">
                <span className="text-3xl text-cyan-400">📱</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">SMS Service</p>
                <p className="text-xl font-bold text-cyan-400 text-glow-cyan">Not configured</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-3xl border border-gray-700 p-10 mb-12 glow-purple">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent text-glow-purple mb-4">
              Live Statistics
            </h2>
            <p className="text-xl text-gray-300">Real-time match data and analytics</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-10">
            <div className="text-center">
              <div className="bg-gradient-to-r from-red-500 to-pink-500 p-8 rounded-3xl mb-6 glow-red hover-glow-red transition-all duration-500">
                <span className="text-6xl text-white font-black">{liveMatchesCount}</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-200 mb-3">Live Matches</h3>
              <p className="text-gray-400">Currently in progress</p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-8 rounded-3xl mb-6 glow-cyan hover-glow-cyan transition-all duration-500">
                <span className="text-6xl text-white font-black">{todaysMatchesCount}</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-200 mb-3">Today's Matches</h3>
              <p className="text-gray-400">Scheduled for today</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link 
              href="/matches"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-5 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl glow-blue hover-glow-blue transform hover:-translate-y-2"
            >
              🏟️ View Live Matches
            </Link>
            <Link 
              href="/alerts"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-10 py-5 rounded-2xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-bold text-xl glow-green hover-glow-green transform hover:-translate-y-2"
            >
              🔔 Manage Alerts
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-purple">
            <div className="text-center">
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-2xl inline-block mb-6 glow-purple">
                <span className="text-4xl text-white">⚡</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-200 mb-4">Real-time Alerts</h3>
              <p className="text-gray-400 leading-relaxed">Get instant notifications for goals, momentum shifts, and key events</p>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-cyan">
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 rounded-2xl inline-block mb-6 glow-cyan">
                <span className="text-4xl text-white">📊</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-200 mb-4">Advanced Analytics</h3>
              <p className="text-gray-400 leading-relaxed">xG, momentum, pressure index, and win probability calculations</p>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-green">
            <div className="text-center">
              <div className="bg-gradient-to-r from-green-500 to-emerald-500 p-6 rounded-2xl inline-block mb-6 glow-green">
                <span className="text-4xl text-white">🤖</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-200 mb-4">Smart Logic</h3>
              <p className="text-gray-400 leading-relaxed">Multi-condition alerts with AND/OR logic and time windows</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-10 glow-blue">
            <h3 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent text-glow-blue mb-6">
              Phase 1: Foundation & Architecture
            </h3>
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center text-gray-300">
              <div className="flex items-center bg-gray-700/50 px-4 py-2 rounded-xl">
                <span className="mr-3 text-xl">🐍</span>
                <span className="font-semibold">Backend: Python FastAPI</span>
              </div>
              <div className="flex items-center bg-gray-700/50 px-4 py-2 rounded-xl">
                <span className="mr-3 text-xl">⚛️</span>
                <span className="font-semibold">Frontend: Next.js</span>
              </div>
              <div className="flex items-center bg-gray-700/50 px-4 py-2 rounded-xl">
                <span className="mr-3 text-xl">📱</span>
                <span className="font-semibold">SMS: Twilio Integration</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 