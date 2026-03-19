<template>
  <div class="notification-settings-container container">
    <h1 class="page-title">Notification Settings</h1>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="settings-card">
        <div class="setting-item master-switch">
            <div class="setting-info">
                <h3>Allow Notifications</h3>
                <p>Master switch for all notifications.</p>
            </div>
            <el-switch v-model="settings.master_switch" @change="updateSettings" />
        </div>
        
        <el-divider />
        
        <div class="individual-settings" :class="{ disabled: !settings.master_switch }">
            <div v-if="!isStaff" class="setting-item">
                <div class="setting-info">
                    <h3>Coupons</h3>
                    <p>Coupons, sales, and special offers.</p>
                </div>
                <el-switch v-model="settings.promotion_on" :disabled="!settings.master_switch" @change="updateSettings" />
            </div>
            
            <div class="setting-item">
                <div class="setting-info">
                    <h3>Invitations</h3>
                    <p>Review invitations and Q&A requests.</p>
                </div>
                <el-switch v-model="settings.invitation_on" :disabled="!settings.master_switch" @change="updateSettings" />
            </div>

            <div v-if="!isStaff" class="setting-item">
                <div class="setting-info">
                    <h3>Price Drops</h3>
                    <p>Get notified when prices drop for items in your wishlist.</p>
                </div>
                <el-switch v-model="settings.price_drop_on" :disabled="!settings.master_switch" @change="updateSettings" />
            </div>
            
            <div class="setting-item">
                <div class="setting-info">
                    <h3>Restock Alerts</h3>
                    <p>Get notified when items are back in stock.</p>
                </div>
                <el-switch v-model="settings.restock_on" :disabled="!settings.master_switch" @change="updateSettings" />
            </div>
            
            <div class="setting-item">
                <div class="setting-info">
                    <h3>Order Updates</h3>
                    <p>Track your order status (Shipped, Hold, Cancelled).</p>
                </div>
                <el-switch v-model="settings.order_update_on" :disabled="!settings.master_switch" @change="updateSettings" />
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const loading = ref(true)
const authStore = useAuthStore()
const isStaff = computed(() => !!authStore.user?.is_staff)
const settings = ref({
    master_switch: false,
    promotion_on: false,
    invitation_on: false,
    price_drop_on: false,
    restock_on: false,
    order_update_on: false
})

const fetchSettings = async () => {
    try {
        const res = await request.get('/settings/notifications/')
        settings.value = res
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const updateSettings = async () => {
    try {
        await request.post('/settings/notifications/update/', settings.value)
        ElMessage.success('Settings updated successfully')
    } catch (e) {
        ElMessage.error('Failed to update settings')
    }
}

onMounted(() => {
    fetchSettings()
})
</script>

<style scoped>
.page-title {
    margin-bottom: 30px;
    text-align: center;
    color: #3E2723;
}

.settings-card {
    background: #fff;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    max-width: 600px;
    margin: 0 auto;
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.setting-info h3 {
    margin: 0 0 5px 0;
    font-size: 1.1rem;
    color: #333;
}

.setting-info p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
}

.individual-settings.disabled {
    opacity: 0.5;
    pointer-events: none;
}
</style>
