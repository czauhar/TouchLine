import NextAuth, { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

interface AuthUser {
  id: string
  email: string
  name: string
  accessToken: string
  phone_number?: string
}

interface User {
  id: string
  email: string
  name: string
  phone_number?: string
}

interface CustomSession {
  user: User
  accessToken: string
}

declare module 'next-auth' {
  interface User extends AuthUser {}
  interface Session extends CustomSession {}
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken?: string
    phone_number?: string
  }
}

export const authOptions: AuthOptions = {
  secret: process.env.NEXTAUTH_SECRET || 'fallback-secret-for-development-only',
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          console.log('Missing credentials')
          return null
        }

        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
          const response = await fetch(`${apiUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!response.ok) {
            console.log('Login failed:', response.status, response.statusText)
            return null
          }

          const data = await response.json()
          console.log('Login successful for:', data.user.email)
          return {
            id: data.user.id,
            email: data.user.email,
            name: data.user.username, // Backend returns 'username', not 'name'
            accessToken: data.access_token,
            phone_number: data.user.phone_number,
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (account && user) {
        token.accessToken = user.accessToken
        token.id = user.id
        token.phone_number = user.phone_number
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        (session.user as any).id = token.id as string
        (session as any).accessToken = token.accessToken as string
        (session.user as any).phone_number = token.phone_number as string
        
        // Store access token in session storage for API client
        if (typeof window !== 'undefined' && token.accessToken) {
          sessionStorage.setItem('accessToken', token.accessToken as string)
        }
      }
      return session
    },
  },
  pages: {
    signIn: '/auth/signin',
  },
  session: {
    strategy: 'jwt',
  },
}

class ApiClient {
  private baseUrl: string
  private accessToken: string | null = null

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl
  }

  setAccessToken(token: string) {
    this.accessToken = token
  }

  // Get access token from session
  private getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      // Try to get from session storage or other sources
      return this.accessToken || sessionStorage.getItem('accessToken')
    }
    return this.accessToken
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    }

    const accessToken = this.getAccessToken()
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`)
    }

    return response.json()
  }

  // Auth endpoints
  async register(userData: { email: string; password: string; username: string; phone_number?: string }) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async login(credentials: { email: string; password: string }) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  async getCurrentUser() {
    return this.request('/api/user/me')
  }

  async updateProfile(userData: { name?: string; phone_number?: string; password?: string }) {
    return this.request('/api/user/me', {
      method: 'PATCH',
      body: JSON.stringify(userData),
    })
  }

  // Match endpoints
  async getLiveMatches() {
    return this.request<{ matches: any[] }>('/api/matches/live')
  }

  async getTodaysMatches() {
    return this.request<{ matches: any[] }>('/api/matches/today')
  }

  async getMatchDetails(matchId: number) {
    return this.request(`/api/matches/${matchId}`)
  }

  // Alert endpoints
  async getAlerts() {
    return this.request<{ alerts: any[] }>('/api/alerts')
  }

  async createAlert(alertData: any) {
    return this.request('/api/alerts', {
      method: 'POST',
      body: JSON.stringify(alertData),
    })
  }

  async toggleAlert(alertId: number) {
    return this.request(`/api/alerts/${alertId}/toggle`, {
      method: 'PUT',
    })
  }

  async deleteAlert(alertId: number) {
    return this.request(`/api/alerts/${alertId}`, {
      method: 'DELETE',
    })
  }

  async updateAlert(alertId: number, alertData: any) {
    return this.request(`/api/alerts/${alertId}`, {
      method: 'PUT',
      body: JSON.stringify(alertData),
    })
  }

  // Template endpoints
  async getAlertTemplates() {
    return this.request<{ templates: any[] }>('/api/alerts/templates')
  }

  // System endpoints
  async getSystemStatus() {
    return this.request('/api/status')
  }

  async getHealth() {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://68.183.59.147:8000') 