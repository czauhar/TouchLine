import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://68.183.59.147:8000'}/api/alerts/templates`, {
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
    console.error('Error fetching alert templates:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch alert templates',
        details: error instanceof Error ? error.message : 'Unknown error',
        templates: []
      },
      { status: 500 }
    )
  }
}
