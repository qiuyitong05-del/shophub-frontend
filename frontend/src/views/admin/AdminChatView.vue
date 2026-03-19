<template>
  <div class="admin-chat-container">
    <div class="conversations-list">
        <h3>Conversations</h3>
        <div v-if="loadingConversations" class="loading">Loading...</div>
        <div v-else>
            <div 
                v-for="conv in conversations" 
                :key="conv.user_id" 
                class="conversation-item" 
                :class="{ active: currentUserId === conv.user_id }"
                @click="selectConversation(conv.user_id)"
            >
                <div class="user-info">
                    <div class="name-badge-wrapper">
                        <span class="username">{{ conv.username }}</span>
                        <el-badge v-if="conv.unread_count > 0" :value="conv.unread_count" class="unread-badge" />
                    </div>
                    <span class="time">{{ conv.last_time ? new Date(conv.last_time).toLocaleDateString() : '' }}</span>
                </div>
                <p class="last-msg">{{ conv.last_message }}</p>
            </div>
        </div>
    </div>
    
    <div class="chat-area">
        <div v-if="currentUserId" class="chat-window">
            <div class="chat-header">
                Chat with {{ currentUsername }}
            </div>
            <div class="messages" ref="messagesRef">
                <div v-for="msg in messages" :key="msg.id" 
                     class="message-bubble" 
                     :class="{ 'sent': msg.is_sender_me, 'received': !msg.is_sender_me }">
                    <div class="message-content">
                        <p>{{ msg.content }}</p>
                        <span class="time">{{ new Date(msg.created_at).toLocaleTimeString() }}</span>
                    </div>
                </div>
            </div>
            <div class="input-area">
                <el-input 
                    v-model="newMessage" 
                    placeholder="Type your message..." 
                    @keyup.enter="sendMessage"
                    :disabled="sending"
                >
                    <template #append>
                        <el-button @click="sendMessage" :loading="sending">Send</el-button>
                    </template>
                </el-input>
            </div>
        </div>
        <div v-else class="empty-state">
            Select a conversation to start chatting
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const conversations = ref([])
const messages = ref([])
const currentUserId = ref(null)
const newMessage = ref('')
const loadingConversations = ref(false)
const sending = ref(false)
const messagesRef = ref(null)
let pollInterval = null

const currentUsername = computed(() => {
    const c = conversations.value.find(c => c.user_id === currentUserId.value)
    return c ? c.username : 'User'
})

const fetchConversations = async () => {
    try {
        const res = await request.get('/admin/chat/conversations/')
        if (Array.isArray(res)) {
            // If we are currently chatting with someone, their unread count should be 0 visually
            // regardless of what server says (in case of race conditions)
            if (currentUserId.value) {
                const currentConv = res.find(c => c.user_id === currentUserId.value)
                if (currentConv) {
                    currentConv.unread_count = 0
                }
            }
            conversations.value = res
        }
    } catch (e) {
        console.error(e)
        // If unauthorized, stop polling to prevent spamming errors
        if (e.response && (e.response.status === 401 || e.response.status === 403)) {
            if (pollInterval) {
                clearInterval(pollInterval)
                pollInterval = null
            }
        }
    }
}

const selectConversation = (userId) => {
    // Optimistic update when user clicks a conversation
    const conv = conversations.value.find(c => c.user_id === userId)
    if (conv && conv.unread_count > 0) {
        chatStore.unreadCount = Math.max(0, chatStore.unreadCount - conv.unread_count)
        conv.unread_count = 0
    }
    
    currentUserId.value = userId
    fetchMessages()
}

const fetchMessages = async () => {
    if (!currentUserId.value) return
    try {
        const res = await request.get('/chat/messages/', { params: { target_user_id: currentUserId.value } })
        
        // Ensure local consistency
        const conv = conversations.value.find(c => c.user_id === currentUserId.value)
        if (conv && conv.unread_count > 0) {
             // Decrease global count locally
             chatStore.unreadCount = Math.max(0, chatStore.unreadCount - conv.unread_count)
             conv.unread_count = 0
        }
        
        if (res.length !== messages.value.length || (res.length > 0 && res[res.length-1].id !== (messages.value.length > 0 ? messages.value[messages.value.length-1].id : 0))) {
            messages.value = res
            scrollToBottom()
        }
    } catch (e) {
        console.error(e)
    }
}

const sendMessage = async () => {
    if (!newMessage.value.trim() || !currentUserId.value) return
    
    sending.value = true
    try {
        const res = await request.post('/chat/send/', { 
            content: newMessage.value,
            receiver_id: currentUserId.value 
        })
        messages.value.push(res)
        newMessage.value = ''
        scrollToBottom()
        // Update conversation list last message
        fetchConversations()
    } catch (e) {
        ElMessage.error(e.response?.data?.error || 'Failed to send message')
    } finally {
        sending.value = false
    }
}

const scrollToBottom = () => {
    nextTick(() => {
        if (messagesRef.value) {
            messagesRef.value.scrollTop = messagesRef.value.scrollHeight
        }
    })
}

onMounted(() => {
    loadingConversations.value = true
    fetchConversations().finally(() => loadingConversations.value = false)
    pollInterval = setInterval(() => {
        fetchConversations()
        if (currentUserId.value) fetchMessages()
    }, 5000)
})

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.admin-chat-container {
    display: flex;
    height: calc(100vh - 100px); /* Adjust based on header/footer */
    border: 1px solid #eee;
    background: white;
}

.conversations-list {
    width: 300px;
    border-right: 1px solid #eee;
    overflow-y: auto;
    background: #fcfcfc;
}

.conversations-list h3 {
    padding: 20px;
    margin: 0;
    border-bottom: 1px solid #eee;
    color: #333;
}

.conversation-item {
    padding: 15px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background 0.2s;
}

.conversation-item:hover {
    background: #f5f5f5;
}

.conversation-item.active {
    background: #e6f7ff;
    border-right: 3px solid #1890ff;
}

.name-badge-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
}

.unread-badge :deep(.el-badge__content) {
    border: none;
    height: 16px;
    line-height: 16px;
    padding: 0 4px;
}

.user-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    align-items: center;
}

.username {
    font-weight: bold;
    color: #333;
}

.time {
    font-size: 0.8em;
    color: #999;
}

.last-msg {
    margin: 0;
    font-size: 0.9em;
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
}

.chat-window {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    font-weight: bold;
    background: #fff;
}

.messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 15px;
    background-color: #FAFAFA;
}

.message-bubble {
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 18px;
    font-size: 0.95rem;
    position: relative;
}

.message-bubble.sent {
    align-self: flex-end;
    background-color: #1890ff;
    color: white;
    border-bottom-right-radius: 4px;
}

.message-bubble.received {
    align-self: flex-start;
    background-color: #EFEBE9;
    color: #3E2723;
    border-bottom-left-radius: 4px;
}

.input-area {
    padding: 15px;
    border-top: 1px solid #EFEBE9;
    background: white;
}
</style>
