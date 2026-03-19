import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useChatStore = defineStore('chat', () => {
    const unreadCount = ref(0)
    let pollInterval = null

    const fetchUnreadCount = async () => {
        try {
            const res = await request.get('/chat/unread/')
            unreadCount.value = res?.count ?? 0
        } catch (error) {
            console.error('Failed to fetch unread chat count:', error)
            unreadCount.value = 0
        }
    }

    const startPolling = () => {
        fetchUnreadCount()
        if (pollInterval) clearInterval(pollInterval)
        pollInterval = setInterval(fetchUnreadCount, 10000) // Poll every 10 seconds
    }

    const stopPolling = () => {
        if (pollInterval) {
            clearInterval(pollInterval)
            pollInterval = null
        }
    }
    
    // Optimistic update or manual decrement
    const markRead = () => {
        // Since we mark as read when fetching messages, we can just fetch count again
        // or manually reset to 0 if we are sure we read everything.
        // For simplicity, we'll re-fetch count shortly after.
        setTimeout(fetchUnreadCount, 1000)
    }

    return {
        unreadCount,
        fetchUnreadCount,
        startPolling,
        stopPolling,
        markRead
    }
})
