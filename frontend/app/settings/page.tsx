'use client'

import Link from 'next/link'
import { useSession } from 'next-auth/react'
import type { Session } from 'next-auth'
import { useState } from 'react'
import { apiClient } from '../../lib/auth'

export default function SettingsPage() {
  const { data: session } = useSession()
  const user = session?.user || {}
  const [phone, setPhone] = useState(typeof (user as any)?.phone_number === 'string' ? (user as any).phone_number : '')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    try {
      // Set access token for authenticated request
      const s = session as Session | undefined
      if (s && 'accessToken' in s && typeof s.accessToken === 'string') {
        apiClient.setAccessToken(s.accessToken)
      }
      const updateData: any = {}
      if (phone) updateData.phone_number = phone
      if (password) updateData.password = password
      await apiClient.updateProfile(updateData)
      setMessage('Settings saved!')
    } catch (error: any) {
      setMessage(error.message || 'Failed to save settings')
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
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">Save Changes</button>
        {message && <p className="text-green-600 mt-2">{message}</p>}
      </form>
      <Link href="/profile" className="text-blue-600 hover:underline">Back to Profile</Link>
    </div>
  )
} 