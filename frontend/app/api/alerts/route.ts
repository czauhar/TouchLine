import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '../../../lib/auth'

export async function GET(request: Request) {
  try {
    // Get session from NextAuth in App Router
    const session = await getServerSession(authOptions)
    
    if (!session || !(session as any).accessToken) {
      // Return empty alerts array instead of error - frontend will handle gracefully
      return NextResponse.json({
        alerts: [],
        count: 0
      })
    }
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://64.225.56.165:8000'
    const response = await fetch(`${apiUrl}/api/alerts`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${(session as any).accessToken}`
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      // If unauthorized or forbidden, return empty alerts array
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json({
          alerts: [],
          count: 0,
          error: 'Authentication required'
        })
      }
      
      // Get error details from backend
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching alerts:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch alerts',
        details: error instanceof Error ? error.message : 'Unknown error',
        alerts: [],
        count: 0
      },
      { status: 500 }
    )
  }
} 