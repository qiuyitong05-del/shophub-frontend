import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    pollingInterval: null
  }),
  
  getters: {
    unreadCount: (state) => state.notifications.filter(n => !n.is_read).length,
    allNotifications: (state) => state.notifications
  },
  
  actions: {
    async fetchNotifications(userId) {
      if (!userId) return
      try {
        const res = await request({
          url: '/notifications/',
          method: 'get',
          params: { user_id: userId }
        })
        this.notifications = res
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
      }
    },
    
    async markAsRead(notificationId) {
      const notification = this.notifications.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        try {
          await request({
            url: `/notifications/${notificationId}/read/`,
            method: 'post'
          })
          notification.is_read = true
        } catch (error) {
          console.error('Failed to mark notification as read:', error)
        }
      }
    },
    
    startPolling(userId) {
      this.fetchNotifications(userId) // Initial fetch
      if (this.pollingInterval) clearInterval(this.pollingInterval)
      
      this.pollingInterval = setInterval(() => {
        this.fetchNotifications(userId)
      }, 30000) // Poll every 30 seconds
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    }
  }
})
