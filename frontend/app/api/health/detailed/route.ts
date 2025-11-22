import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://64.225.56.165:8000'
    // Force fresh fetch every time - no caching at any level
    const response = await fetch(`${apiUrl}/health/detailed`, {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
      },
      cache: 'no-store',
      next: { revalidate: 0 }
    })

    console.log('Frontend detailed health API: Backend response status:', response.status)
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    console.log('Frontend detailed health API: Backend data:', JSON.stringify(data, null, 2))
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })
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
