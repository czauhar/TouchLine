import React from 'react'
import { Card, CardContent } from '../ui/Card'
import { Badge, StatusBadge } from '../ui/Badge'
import { Clock } from 'lucide-react'

interface MatchCardProps {
  match: {
    id: string
    fixture: {
      date: string
      status: {
        short: string
        elapsed?: number
      }
    }
    teams: {
      home: { name: string }
      away: { name: string }
    }
    goals: {
      home: number | null
      away: number | null
    }
    league: {
      name: string
    }
  }
  onClick?: () => void
}

export function MatchCard({ match, onClick }: MatchCardProps) {
  const isLive = ['1H', '2H', 'HT', 'ET', 'P', 'BT'].includes(match.fixture.status.short)
  const matchDate = new Date(match.fixture.date)
  
  return (
    <Card 
      variant="glass" 
      hover
      className="cursor-pointer"
      onClick={onClick}
    >
      <CardContent>
        {/* League & Status */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-slate-400">{match.league.name}</span>
          <StatusBadge status={match.fixture.status.short} />
        </div>

        {/* Teams & Score */}
        <div className="space-y-3">
          {/* Home Team */}
          <div className="flex items-center justify-between">
            <span className="text-white font-medium flex-1">{match.teams.home.name}</span>
            <span className={`text-2xl font-bold ${isLive ? 'text-green-400' : 'text-white'} ml-4`}>
              {match.goals.home ?? '-'}
            </span>
          </div>

          {/* Away Team */}
          <div className="flex items-center justify-between">
            <span className="text-white font-medium flex-1">{match.teams.away.name}</span>
            <span className={`text-2xl font-bold ${isLive ? 'text-green-400' : 'text-white'} ml-4`}>
              {match.goals.away ?? '-'}
            </span>
          </div>
        </div>

        {/* Time/Elapsed */}
        <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-sm text-slate-400">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            {isLive && match.fixture.status.elapsed ? (
              <span>{match.fixture.status.elapsed}&apos;</span>
            ) : (
              <span>{matchDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            )}
          </div>
          {isLive && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-red-400 font-medium">LIVE</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

