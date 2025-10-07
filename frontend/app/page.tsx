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
  CheckCircle,
  AlertCircle
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
      color: "bg-blue-500/10",
      iconColor: "text-blue-400",
      borderColor: "border-blue-500/20"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "Live Match Monitoring",
      description: "Track live matches with advanced analytics and real-time statistics",
      color: "bg-green-500/10",
      iconColor: "text-green-400",
      borderColor: "border-green-500/20"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Advanced Analytics",
      description: "xG, pressure index, momentum scoring, and predictive insights",
      color: "bg-purple-500/10",
      iconColor: "text-purple-400",
      borderColor: "border-purple-500/20"
    },
    {
      icon: <Smartphone className="w-6 h-6" />,
      title: "SMS Notifications",
      description: "Receive alerts via SMS for critical match events and conditions",
      color: "bg-pink-500/10",
      iconColor: "text-pink-400",
      borderColor: "border-pink-500/20"
    }
  ]

  const stats = [
    {
      label: "Live Matches",
      value: liveMatchesCount,
      icon: <Activity className="w-5 h-5" />,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20"
    },
    {
      label: "Today's Matches",
      value: todaysMatchesCount,
      icon: <Clock className="w-5 h-5" />,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20"
    },
    {
      label: "Active Alerts",
      value: activeAlertsCount,
      icon: <Bell className="w-5 h-5" />,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/20"
    },
    {
      label: "System Status",
      value: isBackendConnected ? "Healthy" : "Offline",
      icon: isBackendConnected ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />,
      color: isBackendConnected ? "text-green-400" : "text-red-400",
      bgColor: isBackendConnected ? "bg-green-500/10" : "bg-red-500/10",
      borderColor: isBackendConnected ? "border-green-500/20" : "border-red-500/20"
    }
  ]

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Navigation Bar */}
      <nav className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center group-hover:bg-blue-500 transition-colors">
                <span className="text-white font-bold">⚽</span>
              </div>
              <span className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">TouchLine</span>
            </Link>
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
                  <Link href="/auth/signup" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all font-medium hover:shadow-lg hover:shadow-blue-500/50">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/50">
              <span className="text-4xl">⚽</span>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            TouchLine
          </h1>
          
          <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            Real-time sports alerts and intelligent notifications powered by advanced analytics.
          </p>

          {session ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard" className="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-all hover:shadow-lg hover:shadow-blue-500/50 hover:-translate-y-0.5 inline-flex items-center justify-center">
                Go to Dashboard
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link href="/alerts" className="group bg-slate-800 hover:bg-slate-700 text-white px-8 py-3 rounded-lg font-medium transition-all hover:shadow-lg hover:-translate-y-0.5 inline-flex items-center justify-center">
                Manage Alerts
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/signup" className="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-all hover:shadow-lg hover:shadow-blue-500/50 hover:-translate-y-0.5 inline-flex items-center justify-center">
                Get Started
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link href="/auth/signin" className="group bg-slate-800 hover:bg-slate-700 text-white px-8 py-3 rounded-lg font-medium transition-all hover:shadow-lg hover:-translate-y-0.5 inline-flex items-center justify-center">
                Sign In
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Stats Section */}
      {!loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div 
                key={index} 
                className={`bg-slate-900/50 border ${stat.borderColor} rounded-xl p-6 text-center hover:bg-slate-900/70 transition-all hover:shadow-lg hover:-translate-y-1`}
              >
                <div className={`${stat.bgColor} ${stat.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4 mx-auto`}>
                  {stat.icon}
                </div>
                <div className="text-2xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Features</h2>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Everything you need to stay on top of your favorite sports with intelligent alerts and real-time insights.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className={`group bg-slate-900/50 border ${feature.borderColor} rounded-xl p-8 hover:bg-slate-900/70 transition-all hover:shadow-xl hover:-translate-y-1`}
            >
              <div className={`${feature.color} ${feature.iconColor} inline-flex items-center justify-center w-12 h-12 rounded-lg mb-6 group-hover:scale-110 transition-transform`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-4">{feature.title}</h3>
              <p className="text-slate-300 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions Section */}
      {session && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Quick Actions</h2>
            <p className="text-lg text-slate-300">Get started with TouchLine's core features</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/alerts" className="group bg-blue-600 hover:bg-blue-700 text-white rounded-xl p-8 text-center transition-all hover:shadow-xl hover:shadow-blue-500/50 hover:-translate-y-1">
              <Bell className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-xl font-bold mb-2">Manage Alerts</h3>
              <p className="text-blue-100">Create and configure your sports alerts</p>
            </Link>
            
            <Link href="/matches" className="group bg-slate-800 hover:bg-slate-700 text-white rounded-xl p-8 text-center transition-all hover:shadow-xl hover:-translate-y-1">
              <Activity className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-xl font-bold mb-2">View Matches</h3>
              <p className="text-slate-300">Browse live and upcoming matches</p>
            </Link>
            
            <Link href="/profile" className="group bg-slate-800 hover:bg-slate-700 text-white rounded-xl p-8 text-center transition-all hover:shadow-xl hover:-translate-y-1">
              <Users className="w-12 h-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-xl font-bold mb-2">Profile</h3>
              <p className="text-slate-300">Manage your account and preferences</p>
            </Link>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-slate-900/50 border-t border-slate-800 mt-20">
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
              <Link href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</Link>
              <span>•</span>
              <Link href="#" className="hover:text-slate-300 transition-colors">Terms of Service</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
