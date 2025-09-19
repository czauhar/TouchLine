'use client'

import Link from 'next/link'
import { useSession, signIn } from 'next-auth/react'
import type { Session } from 'next-auth'
import { useState } from 'react'
import { apiClient } from '../../lib/auth'

export default function SettingsPage() {
  const { data: session } = useSession()
  const user = session?.user || {}
  const [phone, setPhone] = useState(typeof (user as any)?.phone_number === 'string' ? (user as any).phone_number : '')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setIsLoading(true)
    
    try {
      // Set access token for authenticated request
      const s = session as Session | undefined
      if (s && 'accessToken' in s && typeof s.accessToken === 'string') {
        apiClient.setAccessToken(s.accessToken)
      }
      
      const updateData: any = {}
      if (phone.trim()) updateData.phone_number = phone.trim()
      if (password.trim()) updateData.password = password.trim()
      
      if (Object.keys(updateData).length === 0) {
        setMessage('Please enter at least one field to update')
        setIsLoading(false)
        return
      }
      
      console.log('Updating profile with:', updateData)
      const result = await apiClient.updateProfile(updateData)
      console.log('Profile update result:', result)
      
      // Update the phone number in the local state immediately
      if (updateData.phone_number) {
        setPhone(updateData.phone_number)
      }
      
      setMessage('Settings saved successfully!')
      setPassword('') // Clear password field after successful update
      
      // Refresh the session to get updated user data
      window.location.reload()
    } catch (error: any) {
      console.error('Profile update error:', error)
      setMessage(`Error: ${error.message || 'Failed to save settings'}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto py-16 px-4">
      <h1 className="text-3xl font-bold mb-4">Settings</h1>
      <form onSubmit={handleSave} className="bg-white rounded-lg shadow p-6 mb-6 space-y-4">
        <div>
          <label className="block font-semibold mb-1">Phone Number</label>
          <input type="text" value={phone} onChange={e => setPhone(e.target.value)} className="w-full border rounded px-3 py-2" />
        </div>
        <div>
          <label className="block font-semibold mb-1">New Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border rounded px-3 py-2" />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed" disabled={(!phone.trim() && !password.trim()) || isLoading}>
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
        {message && (
          <div className={`mt-2 p-3 rounded ${
            message.includes('Error') || message.includes('Failed') 
              ? 'bg-red-100 text-red-700 border border-red-300' 
              : 'bg-green-100 text-green-700 border border-green-300'
          }`}>
            {message}
          </div>
        )}
      </form>
      <Link href="/profile" className="text-blue-600 hover:underline">Back to Profile</Link>
    </div>
  )
} 