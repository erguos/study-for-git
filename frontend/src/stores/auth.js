import { defineStore } from 'pinia'
import { api } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('da_token') || '',
    username: localStorage.getItem('da_username') || '',
    role: localStorage.getItem('da_role') || '',
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isAdmin: (s) => s.role === 'admin',
  },
  actions: {
    setSession({ token, username, role }) {
      this.token = token
      this.username = username
      this.role = role
      localStorage.setItem('da_token', token)
      localStorage.setItem('da_username', username)
      localStorage.setItem('da_role', role)
    },
    logout() {
      this.token = ''
      this.username = ''
      this.role = ''
      localStorage.removeItem('da_token')
      localStorage.removeItem('da_username')
      localStorage.removeItem('da_role')
    },
    async login(username, password) {
      const { data } = await api.post('/auth/login', { username, password })
      this.setSession(data)
      return data
    },
    async register(username, password) {
      const { data } = await api.post('/auth/register', { username, password })
      this.setSession(data)
      return data
    },
  },
})
