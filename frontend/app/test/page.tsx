'use client'

import { useState, useEffect } from 'react'

interface Match {
  id: string
  fixture: {
    id: number
    date: string
    status: {
      short: string
      elapsed: number
    }
    referee: string | null
    venue: {
      name: string | null
    }
  }
  teams: {
    home: { name: string }
    away: { name: string }
  }
  goals: {
    home: number
    away: number
  }
  league: { name: string }
  alert_metrics: any
}

export default function TestPage() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/test')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setMatches(data.matches || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch matches')
      } finally {
        setLoading(false)
      }
    }

    fetchMatches()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading matches...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">TouchLine Test Page</h1>
        
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Test Matches ({matches.length})
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {matches.map((match) => (
            <div key={match.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  match.fixture.status.short === '1H' ? 'bg-green-500 text-white' :
                  match.fixture.status.short === 'NS' ? 'bg-blue-500 text-white' :
                  'bg-gray-500 text-white'
                }`}>
                  {match.fixture.status.short} 
                  {match.fixture.status.elapsed > 0 && ` (${match.fixture.status.elapsed}')`}
                </span>
                <span className="text-gray-400 text-sm">{typeof match.league.name === 'string' ? match.league.name : 'League'}</span>
              </div>

              <div className="text-center mb-4">
                <div className="text-lg font-bold text-white mb-1">{typeof match.teams.home.name === 'string' ? match.teams.home.name : 'Home Team'}</div>
                <div className="text-3xl font-bold text-white">{match.goals.home}</div>
              </div>

              <div className="text-center mb-4">
                <div className="text-lg font-bold text-white mb-1">{typeof match.teams.away.name === 'string' ? match.teams.away.name : 'Away Team'}</div>
                <div className="text-3xl font-bold text-white">{match.goals.away}</div>
              </div>

              <div className="text-sm text-gray-400 space-y-1">
                <div>Venue: {typeof match.fixture.venue.name === 'string' ? match.fixture.venue.name : 'Unknown'}</div>
                <div>Referee: {match.fixture.referee || 'Unknown'}</div>
                <div>Date: {new Date(match.fixture.date).toLocaleString()}</div>
              </div>

              {match.alert_metrics && (
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <h4 className="text-sm font-semibold text-white mb-2">Advanced Metrics</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                    <div>Possession: {match.alert_metrics.possession.home}% - {match.alert_metrics.possession.away}%</div>
                    <div>Shots: {match.alert_metrics.shots.home} - {match.alert_metrics.shots.away}</div>
                    <div>xG: {match.alert_metrics.xg.home.toFixed(1)} - {match.alert_metrics.xg.away.toFixed(1)}</div>
                    <div>Pressure: {match.alert_metrics.pressure.home} - {match.alert_metrics.pressure.away}</div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {matches.length === 0 && (
          <div className="text-center text-gray-400 text-xl">
            No matches found
          </div>
        )}
      </div>
    </div>
  )
} 