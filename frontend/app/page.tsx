'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { apiClient } from '../lib/auth'
import { useSession } from 'next-auth/react'

export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [liveMatchesCount, setLiveMatchesCount] = useState(0)
  const [todaysMatchesCount, setTodaysMatchesCount] = useState(0)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log('🔍 Checking backend status...')
        const [healthResponse, liveResponse, todayResponse] = await Promise.all([
          fetch(process.env.NEXT_PUBLIC_API_URL + '/health'),
          apiClient.getLiveMatches(),
          apiClient.getTodaysMatches()
        ])
        
        console.log('📡 Backend responses received')
        const healthData = await healthResponse.json()
        const liveData = liveResponse
        const todayData = todayResponse
        
        console.log('📊 Health data:', healthData)
        console.log('⚽ Live matches:', liveData.matches?.length || 0)
        console.log('📅 Today matches:', todayData.matches?.length || 0)
        
        setIsBackendConnected(healthData.status === 'healthy')
        setLiveMatchesCount(liveData.matches?.length || 0)
        setTodaysMatchesCount(todayData.matches?.length || 0)
      } catch (error) {
        console.error('❌ Backend connection failed:', error)
        setIsBackendConnected(false)
      } finally {
        setLoading(false)
      }
    }
    
    checkBackend()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col justify-center items-center">
      <div className="max-w-2xl w-full mx-auto text-center py-20 px-4">
        <div className="mb-8">
          <span className="inline-block bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full p-6 shadow-2xl animate-pulse">
            <span className="text-7xl">⚽</span>
          </span>
        </div>
        <h1 className="text-5xl md:text-6xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-6 tracking-tight">
          Welcome to TouchLine
        </h1>
        <p className="text-xl text-gray-200 mb-10 max-w-xl mx-auto leading-relaxed font-light">
          Real-time sports alerts, intelligent notifications, and advanced analytics for fans and power users alike.
        </p>
        <Link href="/dashboard" className="inline-block bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:bg-blue-700 transition mb-12">
          Go to Dashboard
        </Link>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <Link href="/alerts" className="block bg-blue-600 text-white rounded-lg p-6 text-center hover:bg-blue-700 transition">Alerts</Link>
          <Link href="/matches" className="block bg-green-600 text-white rounded-lg p-6 text-center hover:bg-green-700 transition">Matches</Link>
          <Link href="/profile" className="block bg-purple-600 text-white rounded-lg p-6 text-center hover:bg-purple-700 transition">Profile</Link>
          <Link href="/settings" className="block bg-gray-700 text-white rounded-lg p-6 text-center hover:bg-gray-800 transition md:col-span-3">Settings</Link>
        </div>
      </div>
    </div>
  )
} 