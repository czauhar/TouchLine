import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/status', {
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
    console.error('Error fetching system status:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch system status',
        details: error instanceof Error ? error.message : 'Unknown error',
        backend: 'unknown',
        database: 'unknown',
        sms_service: 'unknown',
        sports_api: 'unknown',
        alert_engine: 'unknown'
      },
      { status: 500 }
    )
  }
} 