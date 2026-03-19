
<template>
  <div class="notifications-container container">
    <div class="header">
        <h2 class="page-title">Notifications</h2>
        <el-button type="primary" link @click="$router.push('/settings/notifications')">
            <el-icon><Setting /></el-icon> Settings
        </el-button>
    </div>

    <el-tabs v-model="activeCategory" class="notification-tabs">
        <el-tab-pane label="All" name="all" />
        <el-tab-pane v-if="!authStore.user.is_staff" label="Coupons" name="promotion" />
        <el-tab-pane label="Invitations" name="invitation" />
        <el-tab-pane v-if="!authStore.user.is_staff" label="Price Drops" name="price_drop" />
        <el-tab-pane label="Restock" name="restock" />
        <el-tab-pane label="Order Updates" name="order_update" />
    </el-tabs>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="filteredNotifications.length > 0" class="notifications-list">
        <el-card v-for="n in filteredNotifications" :key="n.id" class="notification-item" :class="{ 'unread': !n.is_read }" @click="handleNotificationClick(n)">
            <div class="notification-content">
                <div class="message-body">
                    <p class="message-text">
                        <span v-if="!n.product_name">{{ n.message }}</span>
                        <span v-else>
                            <span v-for="(part, index) in n.message.split(n.product_name)" :key="index">
                                {{ part }}
                                <router-link 
                                    v-if="index < n.message.split(n.product_name).length - 1" 
                                    :to="`/product/${n.product_id}`" 
                                    class="product-link"
                                    @click.stop
                                >
                                    {{ n.product_name }}
                                </router-link>
                            </span>
                        </span>
                    </p>
                    <span class="timestamp">{{ new Date(n.created_at).toLocaleString() }}</span>
                </div>
                <div class="actions">
                    <el-button v-if="!n.is_read" size="small" type="primary" link @click.stop="markRead(n)">Mark as Read</el-button>
                </div>
            </div>
        </el-card>
    </div>
    <el-empty v-else description="No notifications" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { Setting } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const loading = ref(false) // Store handles loading, but we can keep local for initial fetch if needed
const activeCategory = ref('all')

const filteredNotifications = computed(() => {
    const all = notificationStore.allNotifications
    if (activeCategory.value === 'all') {
        return all
    }
    return all.filter(n => n.category === activeCategory.value)
})

const markRead = async (n) => {
    await notificationStore.markAsRead(n.id)
}

const handleNotificationClick = (n) => {
    markRead(n)
    if (n.category === 'long_term_review' && n.product_id) {
        goToWriteLongTermReview(n)
    } else if (n.order_id) {
        if (authStore.user.is_staff) {
            router.push({ path: '/admin/orders', query: { order_id: n.order_id } })
        } else {
            router.push({ path: '/orders', query: { order_id: n.order_id } })
        }
    } else if (n.product_id) { 
        router.push({ path: `/product/${n.product_id}` })
    }
}

const goToWriteLongTermReview = (n) => {
    router.push({ 
        path: `/product/${n.product_id}`, 
        query: { action: 'review', type: 'long_term' } 
    })
}

onMounted(() => {
    // Refresh to ensure up to date
    notificationStore.fetchNotifications(authStore.user.id)
})
</script>

<style scoped>
.notifications-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-title {
    color: #3E2723;
    margin: 0;
}

.notification-item {
    margin-bottom: 15px;
    cursor: pointer;
    transition: all 0.3s;
}

.notification-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.unread {
    border-left: 5px solid #8D6E63;
    background-color: #FFF8E1;
}

.notification-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.message-text {
    margin: 0 0 5px 0;
    font-size: 1rem;
    color: #333;
}

.timestamp {
    font-size: 0.8rem;
    color: #999;
}

.product-link {
    color: #8D6E63;
    font-weight: bold;
    text-decoration: underline;
    margin: 0 4px;
}
.product-link:hover {
    color: #5D4037;
}
</style>
