'use client'

import Link from 'next/link'
import { useSession, signOut } from 'next-auth/react'
import { useState } from 'react'
import { User, Mail, Phone, Settings, LogOut, ArrowLeft } from 'lucide-react'

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const [isLoading, setIsLoading] = useState(false)
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