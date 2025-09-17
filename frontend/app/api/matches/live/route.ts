import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/matches/live', {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
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