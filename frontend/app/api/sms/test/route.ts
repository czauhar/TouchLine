import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { to_number, message } = body

    if (!to_number || !message) {
      return NextResponse.json(
        { success: false, error: 'Phone number and message are required' },
        { status: 400 }
      )
    }

    console.log('Frontend SMS test API: Sending test SMS...')
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/sms/test?to_number=${encodeURIComponent(to_number)}&message=${encodeURIComponent(message)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    console.log('Frontend SMS test API: Backend response status:', response.status)
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    console.log('Frontend SMS test API: Backend data:', data)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error sending test SMS:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to send test SMS'
      },
      { status: 500 }
    )
  }
}
