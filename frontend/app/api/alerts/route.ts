import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/alerts/', {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // If backend returns 403, return mock data for now
      if (response.status === 403) {
        return NextResponse.json({
          alerts: [
            {
              id: 1,
              name: "High Scoring Matches",
              alert_type: "goals",
              team: "any",
              condition: "Alert when any team scores 3+ goals",
              threshold: 3,
              is_active: true,
              user_id: 1,
              created_at: new Date().toISOString()
            },
            {
              id: 2,
              name: "Close Matches",
              alert_type: "score_difference",
              team: "any",
              condition: "Alert when score difference is 1 goal or less",
              threshold: 1,
              is_active: true,
              user_id: 1,
              created_at: new Date().toISOString()
            }
          ]
        })
      }
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching alerts:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch alerts',
        details: error instanceof Error ? error.message : 'Unknown error',
        alerts: [
          {
            id: 1,
            name: "High Scoring Matches",
            alert_type: "goals",
            team: "any",
            condition: "Alert when any team scores 3+ goals",
            threshold: 3,
            is_active: true,
            user_id: 1,
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            name: "Close Matches",
            alert_type: "score_difference",
            team: "any",
            condition: "Alert when score difference is 1 goal or less",
            threshold: 1,
            is_active: true,
            user_id: 1,
            created_at: new Date().toISOString()
          }
        ]
      },
      { status: 500 }
    )
  }
} 