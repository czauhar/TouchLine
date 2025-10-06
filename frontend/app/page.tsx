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
    <div className="min-h-screen bg-slate-950">
      {/* Clean Navigation Bar */}
      <nav className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">⚽</span>
              </div>
              <span className="text-xl font-bold text-white">TouchLine</span>
            </div>
            <div className="flex items-center space-x-6">
              {session ? (
                <>
                  <Link href="/dashboard" className="text-slate-300 hover:text-white transition-colors font-medium">
                    Dashboard
                  </Link>
                  <Link href="/alerts" className="text-slate-300 hover:text-white transition-colors font-medium">
                    Alerts
                  </Link>
                  <Link href="/matches" className="text-slate-300 hover:text-white transition-colors font-medium">
                    Matches
                  </Link>
                  <Link href="/profile" className="text-slate-300 hover:text-white transition-colors font-medium">
                    Profile
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/auth/signin" className="text-slate-300 hover:text-white transition-colors font-medium">
                    Sign In
                  </Link>
                  <Link href="/auth/signup" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Clean Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="mb-8">
            <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">⚽</span>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            TouchLine
          </h1>
          
          <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
            Real-time sports alerts and intelligent notifications powered by advanced analytics.
          </p>

          {session ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors">
                Go to Dashboard
              </Link>
              <Link href="/alerts" className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-3 rounded-lg font-medium transition-colors">
                Manage Alerts
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/signup" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors">
                Get Started
              </Link>
              <Link href="/auth/signin" className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-3 rounded-lg font-medium transition-colors">
                Sign In
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Clean Stats Section */}
      {!loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 text-center">
                <div className={`${stat.color} mb-4 flex justify-center`}>
                  {stat.icon}
                </div>
                <div className="text-2xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clean Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Features</h2>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Everything you need to stay on top of your favorite sports with intelligent alerts and real-time insights.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-slate-900/50 border border-slate-800 rounded-lg p-8">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-600 mb-6`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-4">{feature.title}</h3>
              <p className="text-slate-300 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Clean Quick Actions Section */}
      {session && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Quick Actions</h2>
            <p className="text-lg text-slate-300">Get started with TouchLine's core features</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/alerts" className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-8 text-center transition-colors">
              <Bell className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">Manage Alerts</h3>
              <p className="text-blue-100">Create and configure your sports alerts</p>
            </Link>
            
            <Link href="/matches" className="bg-slate-800 hover:bg-slate-700 text-white rounded-lg p-8 text-center transition-colors">
              <Activity className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">View Matches</h3>
              <p className="text-slate-300">Browse live and upcoming matches</p>
            </Link>
            
            <Link href="/profile" className="bg-slate-800 hover:bg-slate-700 text-white rounded-lg p-8 text-center transition-colors">
              <Users className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">Profile</h3>
              <p className="text-slate-300">Manage your account and preferences</p>
            </Link>
          </div>
        </div>
      )}

      {/* Clean Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">⚽</span>
              </div>
              <span className="text-xl font-bold text-white">TouchLine</span>
            </div>
            <p className="text-slate-400 mb-6">
              Real-time sports alerts and advanced analytics
            </p>
            <div className="flex justify-center space-x-6 text-sm text-slate-500">
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