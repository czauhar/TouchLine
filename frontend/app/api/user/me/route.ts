import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '../../../../lib/auth'

export async function GET() {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session || !(session as any).accessToken) {
      return NextResponse.json(
        { 
          error: 'Not authenticated',
          detail: 'Please sign in to view your profile'
        },
        { status: 401 }
      )
    }
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://64.225.56.165:8000'
    const response = await fetch(`${apiUrl}/api/user/me`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${(session as any).accessToken}`
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to fetch user profile',
          detail: errorData.detail || `Backend responded with status: ${response.status}`
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching user profile:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch user profile',
        detail: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

