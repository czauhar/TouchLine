import { useState, useEffect, useCallback, useMemo } from 'react'

interface Match {
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

interface UseMatchesOptions {
  type?: 'live' | 'today' | 'all'
  autoRefresh?: boolean
  refreshInterval?: number
}

export function useMatches(options: UseMatchesOptions = {}) {
  const { 
    type = 'today', 
    autoRefresh = true,
    refreshInterval = 30000 // 30 seconds for live matches
  } = options

  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [leagueFilter, setLeagueFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const fetchMatches = useCallback(async () => {
    try {
      setError(null)
      const endpoint = type === 'live' ? '/api/matches/live' : '/api/matches/today'
      const response = await fetch(endpoint)
      const data = await response.json()
      
      if (data.matches) {
        setMatches(data.matches)
      }
    } catch (err) {
      console.error('Error fetching matches:', err)
      setError('Failed to load matches')
      setMatches([])
    } finally {
      setLoading(false)
    }
  }, [type])

  useEffect(() => {
    fetchMatches()
    
    if (autoRefresh) {
      const interval = setInterval(fetchMatches, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchMatches, autoRefresh, refreshInterval])

  // Get unique leagues from matches
  const leagues = useMemo(() => {
    const uniqueLeagues = new Set(matches.map(m => m.league.name))
    return Array.from(uniqueLeagues).sort()
  }, [matches])

  // Filter matches based on search and filters
  const filteredMatches = useMemo(() => {
    return matches.filter(match => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const homeTeam = match.teams.home.name.toLowerCase()
        const awayTeam = match.teams.away.name.toLowerCase()
        const league = match.league.name.toLowerCase()
        
        if (!homeTeam.includes(query) && !awayTeam.includes(query) && !league.includes(query)) {
          return false
        }
      }

      // League filter
      if (leagueFilter !== 'all' && match.league.name !== leagueFilter) {
        return false
      }

      // Status filter
      if (statusFilter !== 'all') {
        const isLive = ['1H', '2H', 'HT', 'ET', 'P', 'BT'].includes(match.fixture.status.short)
        if (statusFilter === 'live' && !isLive) return false
        if (statusFilter === 'finished' && match.fixture.status.short !== 'FT') return false
        if (statusFilter === 'upcoming' && match.fixture.status.short !== 'NS') return false
      }

      return true
    })
  }, [matches, searchQuery, leagueFilter, statusFilter])

  const refresh = useCallback(() => {
    setLoading(true)
    fetchMatches()
  }, [fetchMatches])

  return {
    matches: filteredMatches,
    allMatches: matches,
    loading,
    error,
    refresh,
    // Filters
    searchQuery,
    setSearchQuery,
    leagueFilter,
    setLeagueFilter,
    statusFilter,
    setStatusFilter,
    leagues,
    // Stats
    stats: {
      total: matches.length,
      live: matches.filter(m => ['1H', '2H', 'HT', 'ET', 'P', 'BT'].includes(m.fixture.status.short)).length,
      finished: matches.filter(m => m.fixture.status.short === 'FT').length,
      upcoming: matches.filter(m => m.fixture.status.short === 'NS').length
    }
  }
}

