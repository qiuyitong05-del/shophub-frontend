<template>
  <div class="chat-container container">
    <h1 class="page-title">Customer Service</h1>
    
    <div class="chat-window">
        <div class="messages" ref="messagesRef">
            <div v-for="msg in messages" :key="msg.id" 
                 class="message-bubble" 
                 :class="{ 'sent': msg.is_sender_me, 'received': !msg.is_sender_me }">
                <div class="message-content">
                    <p>{{ msg.content }}</p>
                    <span class="time">{{ new Date(msg.created_at).toLocaleTimeString() }}</span>
                </div>
            </div>
            <div v-if="messages.length === 0" class="empty-state">
                <p>Start a conversation with us!</p>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const messages = ref([])
const newMessage = ref('')
const sending = ref(false)
const messagesRef = ref(null)
let pollInterval = null

const fetchMessages = async () => {
    try {
        const res = await request.get('/chat/messages/')
        
        // Optimistically clear global unread count
        chatStore.unreadCount = 0
        
        // Only update if changed or first load?
        // For simplicity, just replace. Vue handles diffing.
        if (res.length !== messages.value.length) {
            messages.value = res
            scrollToBottom()
        }
    } catch (e) {
        console.error(e)
    }
}

const sendMessage = async () => {
    if (!newMessage.value.trim()) return
    
    sending.value = true
    try {
        const res = await request.post('/chat/send/', { content: newMessage.value })
        messages.value.push(res)
        newMessage.value = ''
        scrollToBottom()
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
    fetchMessages()
    pollInterval = setInterval(fetchMessages, 5000)
})

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.chat-container {
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
    height: calc(100vh - 160px);
    display: flex;
    flex-direction: column;
}

.page-title {
    text-align: center;
    color: var(--color-secondary);
    margin-bottom: 30px;
    font-family: var(--font-serif);
    font-size: 2.5rem;
}

.chat-window {
    flex: 1;
    display: flex;
    flex-direction: column;
    border: none;
    border-radius: 20px;
    background: var(--color-white);
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

.messages {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
    background-color: #FAFAFA;
}

.message-bubble {
    max-width: 75%;
    padding: 15px 20px;
    border-radius: 18px;
    font-size: 1rem;
    position: relative;
    line-height: 1.5;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.message-bubble.sent {
    align-self: flex-end;
    background-color: var(--color-primary);
    color: var(--color-white);
    border-bottom-right-radius: 4px;
}

.message-bubble.received {
    align-self: flex-start;
    background-color: #F0F2F5;
    color: var(--color-text-main);
    border-bottom-left-radius: 4px;
}

.time {
    display: block;
    font-size: 0.75rem;
    margin-top: 8px;
    opacity: 0.8;
    text-align: right;
}

.input-area {
    padding: 20px;
    border-top: 1px solid rgba(0,0,0,0.05);
    background: var(--color-white);
}

:deep(.el-input__wrapper) {
    box-shadow: none !important;
    background-color: #F5F7F9;
    border-radius: 24px;
    padding: 10px 20px;
}

:deep(.el-input-group__append) {
    background-color: transparent;
    box-shadow: none;
    border: none;
    padding: 0 0 0 10px;
}

:deep(.el-button) {
    border-radius: 20px;
    padding: 10px 24px;
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    color: white;
    font-weight: 600;
}

:deep(.el-button:hover) {
    background-color: var(--color-accent);
    border-color: var(--color-accent);
}

.empty-state {
    text-align: center;
    color: var(--color-text-light);
    margin-top: 100px;
    font-style: italic;
}
</style>
