import { create } from 'zustand'

interface Alert {
  id: number
  name: string
  team: string
  alert_type: string
  threshold: number
  description: string
  is_active: boolean
  created_at: string
}

interface Match {
  id: number
  external_id: string
  home_team: string
  away_team: string
  league: string
  start_time: string
  status: string
  home_score: number
  away_score: number
}

interface AppState {
  // User state
  user: any | null
  
  // Alerts state
  alerts: Alert[]
  alertsLoading: boolean
  alertsError: string | null
  
  // Matches state
  liveMatches: Match[]
  todaysMatches: Match[]
  matchesLoading: boolean
  matchesError: string | null
  
  // UI state
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  
  // Actions
  setUser: (user: any) => void
  setAlerts: (alerts: Alert[]) => void
  setAlertsLoading: (loading: boolean) => void
  setAlertsError: (error: string | null) => void
  addAlert: (alert: Alert) => void
  updateAlert: (id: number, updates: Partial<Alert>) => void
  deleteAlert: (id: number) => void
  setLiveMatches: (matches: Match[]) => void
  setTodaysMatches: (matches: Match[]) => void
  setMatchesLoading: (loading: boolean) => void
  setMatchesError: (error: string | null) => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  logout: () => void
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  user: null,
  alerts: [],
  alertsLoading: false,
  alertsError: null,
  liveMatches: [],
  todaysMatches: [],
  matchesLoading: false,
  matchesError: null,
  sidebarOpen: false,
  theme: 'dark',
  
  // Actions
  setUser: (user) => set({ user }),
  setAlerts: (alerts) => set({ alerts }),
  setAlertsLoading: (loading) => set({ alertsLoading: loading }),
  setAlertsError: (error) => set({ alertsError: error }),
  
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts]
  })),
  
  updateAlert: (id, updates) => set((state) => ({
    alerts: state.alerts.map(alert =>
      alert.id === id ? { ...alert, ...updates } : alert
    )
  })),
  
  deleteAlert: (id) => set((state) => ({
    alerts: state.alerts.filter(alert => alert.id !== id)
  })),
  
  setLiveMatches: (matches) => set({ liveMatches: matches }),
  setTodaysMatches: (matches) => set({ todaysMatches: matches }),
  setMatchesLoading: (loading) => set({ matchesLoading: loading }),
  setMatchesError: (error) => set({ matchesError: error }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
  
  logout: () => set({
    user: null,
    alerts: [],
    liveMatches: [],
    todaysMatches: [],
    sidebarOpen: false
  }),
}))

// Selectors for better performance
export const useAlerts = () => useAppStore((state) => state.alerts)
export const useLiveMatches = () => useAppStore((state) => state.liveMatches)
export const useTodaysMatches = () => useAppStore((state) => state.todaysMatches)
export const useUser = () => useAppStore((state) => state.user)
export const useTheme = () => useAppStore((state) => state.theme) 