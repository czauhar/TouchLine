'use client'

import Link from 'next/link'
import { useSession, signOut } from 'next-auth/react'
import { useState } from 'react'
import { User, Mail, Phone, Settings, LogOut, ArrowLeft, MessageSquare, CheckCircle, AlertTriangle } from 'lucide-react'

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const [isLoading, setIsLoading] = useState(false)
  const [smsTestStatus, setSmsTestStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle')
  const [smsTestMessage, setSmsTestMessage] = useState('')
  const user = session?.user || {}

  const handleSignOut = async () => {
    setIsLoading(true)
    try {
      await signOut({ callbackUrl: '/' })
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSmsTest = async () => {
    if (!(user as any)?.phone_number) {
      setSmsTestStatus('error')
      setSmsTestMessage('No phone number registered. Please update your profile.')
      return
    }

    setSmsTestStatus('sending')
    setSmsTestMessage('')

    try {
      const response = await fetch('/api/sms/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to_number: (user as any).phone_number,
          message: 'TouchLine Test: Your SMS notifications are working! 🎉'
        })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setSmsTestStatus('success')
        setSmsTestMessage('Test SMS sent successfully! Check your phone.')
      } else {
        setSmsTestStatus('error')
        setSmsTestMessage(result.error || 'Failed to send test SMS')
      }
    } catch (error) {
      setSmsTestStatus('error')
      setSmsTestMessage('Network error. Please try again.')
    }
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading profile...</div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">Please sign in to view your profile</div>
          <Link href="/auth/signin" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
            Sign In
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-2xl mx-auto py-16 px-4">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Link href="/dashboard" className="mr-4 p-2 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition">
            <ArrowLeft className="w-5 h-5 text-white" />
          </Link>
          <h1 className="text-4xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
            Your Profile
          </h1>
        </div>

        {/* Profile Card */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-xl"></div>
          <div className="relative bg-gray-900/80 backdrop-blur-xl rounded-3xl border border-gray-800 p-8">
            {/* Avatar Section */}
            <div className="text-center mb-8">
              <div className="relative inline-block">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-xl opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 rounded-full shadow-2xl">
                  <User className="w-12 h-12 text-white" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-white mt-4">{typeof user.name === 'string' ? user.name : 'User'}</h2>
              <p className="text-gray-400">TouchLine Member</p>
            </div>

            {/* User Info */}
            <div className="space-y-4 mb-8">
              <div className="flex items-center p-4 bg-gray-800/50 rounded-xl">
                <Mail className="w-5 h-5 text-blue-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-400">Email Address</p>
                  <p className="text-white font-medium">{user.email || 'N/A'}</p>
                </div>
              </div>

              <div className="flex items-center p-4 bg-gray-800/50 rounded-xl">
                <User className="w-5 h-5 text-purple-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-400">Username</p>
                  <p className="text-white font-medium">{typeof user.name === 'string' ? user.name : 'N/A'}</p>
                </div>
              </div>

              {typeof (user as any)?.phone_number === 'string' && (user as any)?.phone_number && (
                <div className="flex items-center p-4 bg-gray-800/50 rounded-xl">
                  <Phone className="w-5 h-5 text-green-400 mr-3" />
                  <div>
                    <p className="text-sm text-gray-400">Phone Number</p>
                    <p className="text-white font-medium">{(user as any).phone_number}</p>
                  </div>
                </div>
              )}
            </div>

            {/* SMS Test Section */}
            {typeof (user as any)?.phone_number === 'string' && (user as any)?.phone_number ? (
              <div className="mb-8">
                <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 rounded-xl p-6 border border-green-500/30">
                  <div className="flex items-center mb-4">
                    <MessageSquare className="w-6 h-6 text-green-400 mr-3" />
                    <h3 className="text-xl font-semibold text-white">SMS Notifications</h3>
                  </div>
                  <p className="text-gray-300 mb-4">
                    Test your SMS notifications to make sure you'll receive alerts on your phone.
                  </p>
                  
                  <button
                    onClick={handleSmsTest}
                    disabled={smsTestStatus === 'sending'}
                    className="w-full flex items-center justify-center gap-2 bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {smsTestStatus === 'sending' ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Sending Test SMS...
                      </>
                    ) : (
                      <>
                        <MessageSquare className="w-5 h-5" />
                        Send Test SMS
                      </>
                    )}
                  </button>

                  {/* Status Message */}
                  {smsTestMessage && (
                    <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
                      smsTestStatus === 'success' 
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                        : 'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                      {smsTestStatus === 'success' ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <AlertTriangle className="w-5 h-5" />
                      )}
                      <span>{smsTestMessage}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="mb-8">
                <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 rounded-xl p-6 border border-yellow-500/30">
                  <div className="flex items-center mb-4">
                    <MessageSquare className="w-6 h-6 text-yellow-400 mr-3" />
                    <h3 className="text-xl font-semibold text-white">SMS Notifications</h3>
                  </div>
                  <p className="text-gray-300 mb-4">
                    Add a phone number to your profile to receive SMS alerts for your sports notifications.
                  </p>
                  <Link 
                    href="/settings" 
                    className="inline-flex items-center gap-2 bg-yellow-600 text-white px-6 py-3 rounded-xl hover:bg-yellow-700 transition-all duration-300 font-medium"
                  >
                    <Settings className="w-5 h-5" />
                    Add Phone Number
                  </Link>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                href="/settings" 
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all duration-300 font-medium"
              >
                <Settings className="w-5 h-5" />
                Edit Profile
              </Link>
              <button 
                onClick={handleSignOut}
                disabled={isLoading}
                className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white px-6 py-3 rounded-xl hover:bg-red-700 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <LogOut className="w-5 h-5" />
                {isLoading ? 'Signing Out...' : 'Sign Out'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 