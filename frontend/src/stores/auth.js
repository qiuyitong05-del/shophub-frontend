import { defineStore } from 'pinia'
import { login, loginAdmin, register } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null
  }),
  actions: {
    async login(userInfo) {
      const res = await login(userInfo)
      this.token = res.token
      this.user = {
          id: res.user_id,
          username: res.username,
          email: res.email,
          is_staff: res.is_staff
      }
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    async loginAdmin(userInfo) {
      const res = await loginAdmin(userInfo)
      this.token = res.token
      this.user = {
          id: res.user_id,
          username: res.username,
          email: res.email,
          is_staff: res.is_staff
      }
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    async register(userInfo) {
        await register(userInfo)
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
