import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://64.225.56.165:8000'
    const response = await fetch(`${apiUrl}/api/matches/live?t=${Date.now()}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
      next: { revalidate: 0 }
    })

    if (!response.ok) {
      // If backend returns error, return empty matches array instead of throwing
      console.warn(`Backend returned status ${response.status} for live matches`)
      return NextResponse.json({
        matches: [],
        count: 0,
        error: response.status === 403 ? 'Sports API key is invalid or missing' : 'Failed to fetch live matches'
      })
    }

    const data = await response.json()
    return NextResponse.json({
      matches: data.matches || [],
      count: data.matches?.length || data.count || 0
    })
  } catch (error) {
    console.error('Error fetching live matches:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch live matches',
        details: error instanceof Error ? error.message : 'Unknown error',
        matches: [],
        count: 0
      },
      { status: 500 }
    )
  }
} 