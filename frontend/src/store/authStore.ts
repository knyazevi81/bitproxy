import { create } from 'zustand'
import { setAccessToken } from '../api/client'
import { User } from '../api/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  logout: () => void
}

// Zustand store for auth state (access token lives in api/client.ts memory)
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  setToken: (token) => {
    setAccessToken(token)
    set({ isAuthenticated: !!token })
  },

  logout: () => {
    setAccessToken(null)
    set({ user: null, isAuthenticated: false })
  },
}))
