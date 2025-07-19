'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '../lib/api'

export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [liveMatchesCount, setLiveMatchesCount] = useState(0)
  const [todaysMatchesCount, setTodaysMatchesCount] = useState(0)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const [healthResponse, liveResponse, todayResponse] = await Promise.all([
          api.health(),
          api.getLiveMatches(),
          api.getTodaysMatches()
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
    <div className="min-h-screen bg-black">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-pink-600/10"></div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20">
            <div className="text-center">
              {/* Logo */}
              <div className="flex justify-center mb-8">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-xl opacity-75 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 rounded-full shadow-2xl">
                    <span className="text-8xl">⚽</span>
                  </div>
                </div>
              </div>
              
              {/* Title */}
              <h1 className="text-8xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-6 tracking-tight">
                TouchLine
              </h1>
              
              {/* Subtitle */}
              <p className="text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed font-light">
                Real-time sports alerts and intelligent notifications powered by advanced analytics
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
          {/* System Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className={`p-4 rounded-xl ${isBackendConnected ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                    <span className={`text-3xl ${isBackendConnected ? 'text-green-400' : 'text-red-400'}`}>
                      {isBackendConnected ? '🔌' : '❌'}
                    </span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Backend</p>
                    <p className={`text-xl font-bold ${isBackendConnected ? 'text-green-400' : 'text-red-400'}`}>
                      {isBackendConnected ? 'Connected' : 'Disconnected'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-xl bg-blue-500/20">
                    <span className="text-3xl text-blue-400">🌐</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Frontend</p>
                    <p className="text-xl font-bold text-blue-400">Running</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-xl bg-green-500/20">
                    <span className="text-3xl text-green-400">💾</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Database</p>
                    <p className="text-xl font-bold text-green-400">Configured</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-6 hover:bg-gray-900/90 transition-all duration-300">
                <div className="flex items-center">
                  <div className="p-4 rounded-xl bg-purple-500/20">
                    <span className="text-3xl text-purple-400">📱</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">SMS Service</p>
                    <p className="text-xl font-bold text-purple-400">Not configured</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Live Stats */}
          <div className="relative mb-16">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-3xl blur-xl"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-12">
              <div className="text-center mb-12">
                <h2 className="text-5xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
                  Live Statistics
                </h2>
                <p className="text-xl text-gray-300">Real-time match data and analytics</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-12">
                <div className="text-center group">
                  <div className="relative mb-8">
                    <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-pink-500 rounded-3xl blur-xl opacity-50 group-hover:opacity-75 transition duration-500"></div>
                    <div className="relative bg-gradient-to-r from-red-500 to-pink-500 p-10 rounded-3xl">
                      <span className="text-7xl text-white font-black">{liveMatchesCount}</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-3">Live Matches</h3>
                  <p className="text-gray-400">Currently in progress</p>
                </div>
                
                <div className="text-center group">
                  <div className="relative mb-8">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-3xl blur-xl opacity-50 group-hover:opacity-75 transition duration-500"></div>
                    <div className="relative bg-gradient-to-r from-blue-500 to-cyan-500 p-10 rounded-3xl">
                      <span className="text-7xl text-white font-black">{todaysMatchesCount}</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-3">Today's Matches</h3>
                  <p className="text-gray-400">Scheduled for today</p>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <Link 
                  href="/matches"
                  className="group relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                  <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-12 py-6 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2">
                    🏟️ View Live Matches
                  </div>
                </Link>
                <Link 
                  href="/alerts"
                  className="group relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-500"></div>
                  <div className="relative bg-gradient-to-r from-green-600 to-emerald-600 text-white px-12 py-6 rounded-2xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-bold text-xl transform hover:-translate-y-2">
                    🔔 Manage Alerts
                  </div>
                </Link>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="text-center">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur opacity-50"></div>
                    <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-2xl inline-block">
                      <span className="text-4xl text-white">⚡</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-4">Real-time Alerts</h3>
                  <p className="text-gray-400 leading-relaxed">Get instant notifications for goals, momentum shifts, and key events</p>
                </div>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="text-center">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-50"></div>
                    <div className="relative bg-gradient-to-r from-blue-500 to-cyan-500 p-6 rounded-2xl inline-block">
                      <span className="text-4xl text-white">📊</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-4">Advanced Analytics</h3>
                  <p className="text-gray-400 leading-relaxed">xG, momentum, pressure index, and win probability calculations</p>
                </div>
              </div>
            </div>

            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-8 hover:bg-gray-900/90 transition-all duration-300">
                <div className="text-center">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur opacity-50"></div>
                    <div className="relative bg-gradient-to-r from-green-500 to-emerald-500 p-6 rounded-2xl inline-block">
                      <span className="text-4xl text-white">🤖</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-200 mb-4">Smart Logic</h3>
                  <p className="text-gray-400 leading-relaxed">Multi-condition alerts with AND/OR logic and time windows</p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 rounded-2xl blur-xl"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-800 p-12">
                <h3 className="text-4xl font-black bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-8">
                  Phase 1: Foundation & Architecture
                </h3>
                <div className="flex flex-col sm:flex-row gap-6 justify-center items-center text-gray-300">
                  <div className="flex items-center bg-gray-800/50 px-6 py-3 rounded-xl">
                    <span className="mr-3 text-xl">🐍</span>
                    <span className="font-semibold">Backend: Python FastAPI</span>
                  </div>
                  <div className="flex items-center bg-gray-800/50 px-6 py-3 rounded-xl">
                    <span className="mr-3 text-xl">⚛️</span>
                    <span className="font-semibold">Frontend: Next.js</span>
                  </div>
                  <div className="flex items-center bg-gray-800/50 px-6 py-3 rounded-xl">
                    <span className="mr-3 text-xl">📱</span>
                    <span className="font-semibold">SMS: Twilio Integration</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 