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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      {/* Enhanced Navigation Bar */}
      <nav className="relative bg-white/10 backdrop-blur-xl border-b border-white/20 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-75 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-full shadow-xl">
                    <span className="text-2xl">⚽</span>
                  </div>
                </div>
                <span className="text-2xl font-black text-gradient">TouchLine</span>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              {session ? (
                <>
                  <Link href="/dashboard" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 font-medium">
                    Dashboard
                  </Link>
                  <Link href="/alerts" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 font-medium">
                    Alerts
                  </Link>
                  <Link href="/matches" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 font-medium">
                    Matches
                  </Link>
                  <Link href="/profile" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 font-medium">
                    Profile
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/auth/signin" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 font-medium">
                    Sign In
                  </Link>
                  <Link href="/auth/signup" className="btn-primary">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center animate-fade-in">
            <div className="mb-12 animate-scale-in">
              <div className="relative inline-block">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-2xl opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full p-12 shadow-2xl animate-float">
                  <span className="text-8xl">⚽</span>
                </div>
              </div>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-black text-gradient mb-8 tracking-tight animate-slide-in-up">
              Welcome to TouchLine
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-200 mb-12 max-w-4xl mx-auto leading-relaxed font-light animate-slide-in-up" style={{animationDelay: '0.2s'}}>
              Real-time sports alerts, intelligent notifications, and advanced analytics for fans and power users alike.
            </p>

            {session ? (
              <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16 animate-slide-in-up" style={{animationDelay: '0.4s'}}>
                <Link href="/dashboard" className="btn-primary text-lg px-8 py-4 flex items-center justify-center">
                  <Play className="w-6 h-6 mr-3" />
                  Go to Dashboard
                </Link>
                <Link href="/alerts" className="btn-success text-lg px-8 py-4 flex items-center justify-center">
                  <Bell className="w-6 h-6 mr-3" />
                  Manage Alerts
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16 animate-slide-in-up" style={{animationDelay: '0.4s'}}>
                <Link href="/auth/signup" className="btn-primary text-lg px-8 py-4 flex items-center justify-center">
                  <Users className="w-6 h-6 mr-3" />
                  Get Started
                </Link>
                <Link href="/auth/signin" className="btn-secondary text-lg px-8 py-4 flex items-center justify-center">
                  <ArrowRight className="w-6 h-6 mr-3" />
                  Sign In
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Live Stats Section */}
      {!loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="card-elevated p-6 text-center animate-scale-in group" style={{animationDelay: `${index * 0.1}s`}}>
                <div className={`${stat.color} mb-4 flex justify-center group-hover:scale-110 transition-transform duration-300`}>
                  {stat.icon}
                </div>
                <div className="text-3xl font-bold text-white mb-2 group-hover:text-gradient-primary transition-all duration-300">{stat.value}</div>
                <div className="text-sm text-gray-300 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-20 animate-fade-in">
          <h2 className="text-5xl font-bold text-gradient mb-6">Powerful Features</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Everything you need to stay on top of your favorite sports with intelligent alerts and real-time insights.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card-interactive p-8 animate-slide-in-up group" style={{animationDelay: `${index * 0.1}s`}}>
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.color} mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg`}>
                {feature.icon}
              </div>
              <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-gradient-primary transition-all duration-300">{feature.title}</h3>
              <p className="text-gray-300 leading-relaxed text-lg">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Enhanced Quick Actions Section */}
      {session && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-5xl font-bold text-gradient mb-6">Quick Actions</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">Get started with TouchLine's core features</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Link href="/alerts" className="group bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl p-8 text-center hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-2xl hover:shadow-3xl hover:scale-105 animate-slide-in-up">
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-lg group-hover:blur-xl transition-all duration-300"></div>
                <Bell className="w-16 h-16 mx-auto relative group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Manage Alerts</h3>
              <p className="text-blue-100 text-lg">Create and configure your sports alerts</p>
            </Link>
            
            <Link href="/matches" className="group bg-gradient-to-r from-green-600 to-green-700 text-white rounded-2xl p-8 text-center hover:from-green-700 hover:to-green-800 transition-all duration-300 shadow-2xl hover:shadow-3xl hover:scale-105 animate-slide-in-up" style={{animationDelay: '0.1s'}}>
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-lg group-hover:blur-xl transition-all duration-300"></div>
                <Activity className="w-16 h-16 mx-auto relative group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-2xl font-bold mb-3">View Matches</h3>
              <p className="text-green-100 text-lg">Browse live and upcoming matches</p>
            </Link>
            
            <Link href="/profile" className="group bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-2xl p-8 text-center hover:from-purple-700 hover:to-purple-800 transition-all duration-300 shadow-2xl hover:shadow-3xl hover:scale-105 animate-slide-in-up" style={{animationDelay: '0.2s'}}>
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-lg group-hover:blur-xl transition-all duration-300"></div>
                <Users className="w-16 h-16 mx-auto relative group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Profile</h3>
              <p className="text-purple-100 text-lg">Manage your account and preferences</p>
            </Link>
          </div>
        </div>
      )}

      {/* Enhanced Footer */}
      <footer className="relative bg-black/30 backdrop-blur-xl border-t border-white/20 mt-24">
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-75"></div>
                <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-full">
                  <span className="text-2xl">⚽</span>
                </div>
              </div>
              <span className="text-3xl font-black text-gradient">TouchLine</span>
            </div>
            <p className="text-gray-300 mb-8 text-lg">
              Real-time sports alerts and advanced analytics
            </p>
            <div className="flex justify-center space-x-8 text-sm text-gray-400">
              <span className="hover:text-white transition-colors duration-300 cursor-pointer">© 2025 TouchLine</span>
              <span>•</span>
              <span className="hover:text-white transition-colors duration-300 cursor-pointer">Privacy Policy</span>
              <span>•</span>
              <span className="hover:text-white transition-colors duration-300 cursor-pointer">Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
} 