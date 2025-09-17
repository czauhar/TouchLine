'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { apiClient } from '../lib/auth'
import { useSession } from 'next-auth/react'
import { 
  Activity, 
  Bell, 
  TrendingUp, 
  Zap, 
  Shield, 
  Clock, 
  Target, 
  BarChart3,
  ArrowRight,
  Play,
  Users,
  Globe,
  Smartphone,
  CheckCircle
} from 'lucide-react'

export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [liveMatchesCount, setLiveMatchesCount] = useState(0)
  const [todaysMatchesCount, setTodaysMatchesCount] = useState(0)
  const [activeAlertsCount, setActiveAlertsCount] = useState(0)
  const { data: session } = useSession()

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
        
        // Try to get alerts count if user is authenticated
        if (session) {
          try {
            const alertsResponse = await apiClient.getAlerts()
            setActiveAlertsCount(alertsResponse.alerts?.filter((alert: any) => alert.is_active)?.length || 0)
          } catch (error) {
            console.warn('Could not fetch alerts:', error)
          }
        }
      } catch (error) {
        console.error('❌ Backend connection failed:', error)
        setIsBackendConnected(false)
      } finally {
        setLoading(false)
      }
    }
    
    checkBackend()
  }, [session])

  const features = [
    {
      icon: <Bell className="w-6 h-6" />,
      title: "Real-time Alerts",
      description: "Get instant notifications when your conditions are met during live matches",
      color: "from-blue-500 to-blue-600"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "Live Match Monitoring",
      description: "Track live matches with advanced analytics and real-time statistics",
      color: "from-green-500 to-green-600"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Advanced Analytics",
      description: "xG, pressure index, momentum scoring, and predictive insights",
      color: "from-purple-500 to-purple-600"
    },
    {
      icon: <Smartphone className="w-6 h-6" />,
      title: "SMS Notifications",
      description: "Receive alerts via SMS for critical match events and conditions",
      color: "from-pink-500 to-pink-600"
    }
  ]

  const stats = [
    {
      label: "Live Matches",
      value: liveMatchesCount,
      icon: <Activity className="w-5 h-5" />,
      color: "text-green-400"
    },
    {
      label: "Today's Matches",
      value: todaysMatchesCount,
      icon: <Clock className="w-5 h-5" />,
      color: "text-blue-400"
    },
    {
      label: "Active Alerts",
      value: activeAlertsCount,
      icon: <Bell className="w-5 h-5" />,
      color: "text-yellow-400"
    },
    {
      label: "System Status",
      value: isBackendConnected ? "Healthy" : "Offline",
      icon: isBackendConnected ? <CheckCircle className="w-5 h-5" /> : <Shield className="w-5 h-5" />,
      color: isBackendConnected ? "text-green-400" : "text-red-400"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation Bar */}
      <nav className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">⚽</span>
                <span className="text-xl font-bold text-white">TouchLine</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {session ? (
                <>
                  <Link href="/dashboard" className="text-gray-300 hover:text-white transition">
                    Dashboard
                  </Link>
                  <Link href="/alerts" className="text-gray-300 hover:text-white transition">
                    Alerts
                  </Link>
                  <Link href="/matches" className="text-gray-300 hover:text-white transition">
                    Matches
                  </Link>
                  <Link href="/profile" className="text-gray-300 hover:text-white transition">
                    Profile
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/auth/signin" className="text-gray-300 hover:text-white transition">
                    Sign In
                  </Link>
                  <Link href="/auth/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="mb-8">
              <span className="inline-block bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full p-8 shadow-2xl animate-pulse">
                <span className="text-8xl">⚽</span>
              </span>
            </div>
            
            <h1 className="text-6xl md:text-7xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-6 tracking-tight">
              Welcome to TouchLine
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto leading-relaxed font-light">
              Real-time sports alerts, intelligent notifications, and advanced analytics for fans and power users alike.
            </p>

            {session ? (
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
                <Link href="/dashboard" className="inline-flex items-center bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:bg-blue-700 transition">
                  <Play className="w-5 h-5 mr-2" />
                  Go to Dashboard
                </Link>
                <Link href="/alerts" className="inline-flex items-center bg-green-600 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:bg-green-700 transition">
                  <Bell className="w-5 h-5 mr-2" />
                  Manage Alerts
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
                <Link href="/auth/signup" className="inline-flex items-center bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:bg-blue-700 transition">
                  <Users className="w-5 h-5 mr-2" />
                  Get Started
                </Link>
                <Link href="/auth/signin" className="inline-flex items-center bg-white/10 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:bg-white/20 transition border border-white/20">
                  <ArrowRight className="w-5 h-5 mr-2" />
                  Sign In
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Live Stats Section */}
      {!loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 text-center">
                <div className={`${stat.color} mb-2 flex justify-center`}>
                  {stat.icon}
                </div>
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-300">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Everything you need to stay on top of your favorite sports with intelligent alerts and real-time insights.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20 hover:bg-white/15 transition">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-r ${feature.color} mb-6`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">{feature.title}</h3>
              <p className="text-gray-300 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions Section */}
      {session && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Quick Actions</h2>
            <p className="text-xl text-gray-300">Get started with TouchLine's core features</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/alerts" className="group bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl p-8 text-center hover:from-blue-700 hover:to-blue-800 transition shadow-lg">
              <Bell className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition" />
              <h3 className="text-xl font-semibold mb-2">Manage Alerts</h3>
              <p className="text-blue-100">Create and configure your sports alerts</p>
            </Link>
            
            <Link href="/matches" className="group bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl p-8 text-center hover:from-green-700 hover:to-green-800 transition shadow-lg">
              <Activity className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition" />
              <h3 className="text-xl font-semibold mb-2">View Matches</h3>
              <p className="text-green-100">Browse live and upcoming matches</p>
            </Link>
            
            <Link href="/profile" className="group bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl p-8 text-center hover:from-purple-700 hover:to-purple-800 transition shadow-lg">
              <Users className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition" />
              <h3 className="text-xl font-semibold mb-2">Profile</h3>
              <p className="text-purple-100">Manage your account and preferences</p>
            </Link>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-black/20 border-t border-white/10 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <span className="text-2xl">⚽</span>
              <span className="text-xl font-bold text-white">TouchLine</span>
            </div>
            <p className="text-gray-400 mb-4">
              Real-time sports alerts and advanced analytics
            </p>
            <div className="flex justify-center space-x-6 text-sm text-gray-400">
              <span>© 2025 TouchLine</span>
              <span>•</span>
              <span>Privacy Policy</span>
              <span>•</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
} 