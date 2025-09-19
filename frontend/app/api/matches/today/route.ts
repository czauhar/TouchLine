import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://68.183.59.147:8000'}/api/matches/today`, {
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
    console.error('Error fetching today\'s matches:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch today\'s matches',
        details: error instanceof Error ? error.message : 'Unknown error',
        matches: [],
        count: 0
      },
      { status: 500 }
    )
  }
} 