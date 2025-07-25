'use client'

import Link from 'next/link'
import { useSession, signOut } from 'next-auth/react'

export default function ProfilePage() {
  const { data: session } = useSession()
  const user = session?.user || {}
  return (
    <div className="max-w-xl mx-auto py-16 px-4">
      <h1 className="text-3xl font-bold mb-4">Your Profile</h1>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <p className="mb-2"><span className="font-semibold">Email:</span> {user.email || 'N/A'}</p>
        <p className="mb-2"><span className="font-semibold">Username:</span> {user.name || 'N/A'}</p>
        {typeof (user as any)?.phone_number === 'string' && (user as any)?.phone_number && (
          <p className="mb-2"><span className="font-semibold">Phone:</span> {(user as any).phone_number}</p>
        )}
      </div>
      <div className="flex space-x-4 mb-6">
        <Link href="/settings" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">Edit Profile</Link>
        <button onClick={() => signOut({ callbackUrl: '/' })} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition">Log Out</button>
      </div>
    </div>
  )
} 