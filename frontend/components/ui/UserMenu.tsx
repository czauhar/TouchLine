'use client'

import { useSession, signOut } from 'next-auth/react'
import Link from 'next/link'
import { useState } from 'react'

export default function UserMenu() {
  const { data: session, status } = useSession()
  const user = session?.user
  const [open, setOpen] = useState(false)
  if (status !== 'authenticated') return null
  return (
    <div className="relative">
      <button onClick={() => setOpen(v => !v)} className="flex items-center space-x-2 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
        <span>{typeof user?.name === 'string' ? user.name : (user?.email || 'User')}</span>
        <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg z-50">
          <Link href="/profile" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">Profile</Link>
          <Link href="/settings" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">Settings</Link>
          <button onClick={() => signOut({ callbackUrl: '/' })} className="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100">Log Out</button>
        </div>
      )}
    </div>
  )
} 