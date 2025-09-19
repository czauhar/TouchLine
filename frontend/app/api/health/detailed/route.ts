import { NextResponse } from 'next/server'

export async function GET() {
  try {
    console.log('Frontend detailed health API: Fetching from backend...')
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health/detailed`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    console.log('Frontend detailed health API: Backend response status:', response.status)
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    console.log('Frontend detailed health API: Backend data:', JSON.stringify(data, null, 2))
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching detailed health data:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch detailed health data',
        details: error instanceof Error ? error.message : 'Unknown error',
        status: 'unknown',
        last_check: new Date().toISOString(),
        system: {
          cpu_percent: 0,
          memory_percent: 0,
          disk_percent: 0
        },
        database: {
          connection_status: false,
          response_time_ms: 0
        },
        api: {
          sports_api_status: false,
          sms_service_status: false,
          error_count: 0
        },
        alerts: {
          active_alerts: 0,
          alerts_triggered_today: 0,
          sms_sent_today: 0,
          sms_failed_today: 0
        }
      },
      { status: 500 }
    )
  }
}
