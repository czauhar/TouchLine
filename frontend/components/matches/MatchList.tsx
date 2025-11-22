import React from 'react'
import { MatchCard } from './MatchCard'
import { EmptyState } from '../ui/EmptyState'
import { Activity } from 'lucide-react'

interface MatchListProps {
  matches: any[]
  onMatchClick?: (match: any) => void
  emptyMessage?: string
}

export function MatchList({ matches, onMatchClick, emptyMessage = 'No matches available' }: MatchListProps) {
  if (matches.length === 0) {
    return (
      <EmptyState
        icon={<Activity className="w-16 h-16" />}
        title="No Matches"
        description={emptyMessage}
      />
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {matches.map((match) => (
        <MatchCard
          key={match.id}
          match={match}
          onClick={() => onMatchClick?.(match)}
        />
      ))}
    </div>
  )
}

