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
    <main className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          TouchLine 🏈
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Real-time sports alerts and notifications
        </p>
        
        <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
          <h2 className="text-2xl font-semibold mb-4">System Status</h2>
          
          {loading ? (
            <div className="text-blue-600">Checking backend connection...</div>
          ) : (
            <div className={`text-lg ${isBackendConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isBackendConnected ? '✅ Backend Connected' : '❌ Backend Disconnected'}
            </div>
          )}
          
          <div className="mt-6 space-y-2 text-sm text-gray-600">
            <div>Frontend: ✅ Running</div>
            <div>Database: ✅ Configured</div>
            <div>SMS Service: ⏳ Not configured</div>
            <div>Sports API: ✅ Configured</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto mt-6">
          <h2 className="text-2xl font-semibold mb-4">Quick Stats</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{liveMatchesCount}</div>
              <div className="text-sm text-gray-600">Live Matches</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{todaysMatchesCount}</div>
              <div className="text-sm text-gray-600">Today's Matches</div>
            </div>
          </div>
          <div className="mt-4 flex space-x-3 justify-center">
            <Link 
              href="/matches"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Matches
            </Link>
            <Link 
              href="/alerts"
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Manage Alerts
            </Link>
          </div>
        </div>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>Phase 1: Foundation & Architecture</p>
          <p>Backend: Python FastAPI | Frontend: Next.js</p>
        </div>
      </div>
    </main>
  )
} 