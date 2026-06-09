import { create } from 'zustand'

interface User {
  id: number
  email: string
  full_name: string
  avatar: string | null
}

interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  login: (access: string, refresh: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),

  login(access, refresh) {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    set({ isAuthenticated: true })
  },

  setUser(user) {
    set({ user })
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },
}))
