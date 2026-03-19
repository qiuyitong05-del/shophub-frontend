<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>My Profile</h1>
      <p>Manage your account and view your rewards</p>
    </div>

    <div class="profile-content">
      <!-- Left Column: Personal Info -->
      <div class="info-card">
        <div class="card-header">
          <h2>Personal Information</h2>
          <button @click="isEditing = !isEditing" class="edit-btn">
            <el-icon v-if="!isEditing" style="margin-right: 5px;"><Edit /></el-icon>
            {{ isEditing ? 'Cancel' : 'Edit' }}
          </button>
        </div>
        
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else>
          <form @submit.prevent="updateProfile" class="profile-form">
            <div class="form-group">
              <label>Username</label>
              <input :value="user.username" disabled class="disabled-input">
            </div>
            
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" :disabled="!isEditing" type="email">
            </div>
            
            <div class="form-group">
              <label>Member Since</label>
              <input :value="new Date(user.date_joined).toLocaleDateString()" disabled class="disabled-input">
            </div>

            <div class="form-group">
               <label>Default Address (Province / City / Detail)</label>
               <div style="display: flex; gap: 10px; margin-bottom: 5px;">
                   <input v-model="form.province" :disabled="!isEditing" placeholder="Province" style="flex: 1;">
                   <input v-model="form.city" :disabled="!isEditing" placeholder="City" style="flex: 1;">
               </div>
               <input v-model="form.detail_address" :disabled="!isEditing" placeholder="Detailed Address">
            </div>

            <div v-if="isEditing" class="form-group">
               <label>New Password (Optional)</label>
               <input v-model="form.password" type="password" placeholder="Leave blank to keep current">
            </div>

            <div v-if="isEditing" class="form-actions">
              <button type="submit" class="save-btn" :disabled="updating">
                {{ updating ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Right Column: Coupons & Address -->
      <div class="side-column">
         <!-- Address Card -->
         <div class="info-card small-card">
            <h2>Default Address</h2>
            <div v-if="user.address">
                <p><strong>Province:</strong> {{ user.address.province }}</p>
                <p><strong>City:</strong> {{ user.address.city }}</p>
                <p><strong>Detail:</strong> {{ user.address.detail_address }}</p>
            </div>
            <div v-else>
                <p>No default address set.</p>
            </div>
         </div>

         <!-- Coupons Card -->
         <div class="info-card small-card">
            <h2>My Coupons</h2>
            <div v-if="user.coupons && user.coupons.length > 0" class="coupon-list">
                <div v-for="(coupon, index) in user.coupons" :key="index" class="coupon-item">
                    <div class="coupon-icon">🎟️</div>
                    <div class="coupon-details">
                        <p class="coupon-msg">{{ coupon.message }}</p>
                        <span class="coupon-date">
                            {{ formatDate(coupon.date) }}
                            <span v-if="coupon.valid_until"> · Valid until {{ formatDate(coupon.valid_until) }}</span>
                            <span v-if="typeof coupon.days_left === 'number'"> ({{ coupon.days_left }} day{{ coupon.days_left === 1 ? '' : 's' }} left)</span>
                        </span>
                    </div>
                </div>
            </div>
            <div v-else class="empty-state">
                <p>No coupons yet.</p>
                <router-link to="/wishlist" class="link">Add items to wishlist to get offers!</router-link>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUserProfile, updateUserProfile } from '@/api/user'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'

const user = ref({})
const form = ref({
    email: '',
    password: '',
    province: '',
    city: '',
    detail_address: ''
})
const loading = ref(true)
const isEditing = ref(false)
const updating = ref(false)

const formatDate = (dt) => {
    const d = new Date(dt)
    if (Number.isNaN(d.getTime())) return String(dt)
    return d.toLocaleDateString()
}

const fetchProfile = async () => {
    loading.value = true
    try {
        const res = await getUserProfile()
        user.value = res
        form.value.email = res.email
        if (res.address) {
            form.value.province = res.address.province
            form.value.city = res.address.city
            form.value.detail_address = res.address.detail_address
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const updateProfile = async () => {
    updating.value = true
    try {
        await updateUserProfile(form.value)
        ElMessage.success('Profile updated successfully')
        isEditing.value = false
        fetchProfile() // Refresh
    } catch (e) {
        console.error(e)
    } finally {
        updating.value = false
    }
}

onMounted(() => {
    fetchProfile()
})
</script>

<style scoped>
.profile-container {
    max-width: 1000px;
    margin: 40px auto;
    padding: 0 20px;
}

.profile-header {
    text-align: center;
    margin-bottom: 40px;
}

.profile-header h1 {
    font-size: 2.5rem;
    color: var(--color-secondary);
    margin-bottom: 10px;
    font-family: var(--font-serif);
}

.profile-content {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}

@media (min-width: 768px) {
    .profile-content {
        grid-template-columns: 2fr 1fr;
    }
}

.info-card {
    background: var(--color-white);
    padding: 30px;
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    border: none;
    transition: all 0.3s ease;
}

.info-card:hover {
    box-shadow: var(--shadow-hover);
}

.small-card {
    margin-bottom: 30px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding-bottom: 15px;
}

.card-header h2 {
    font-size: 1.5rem;
    color: var(--color-secondary);
    margin: 0;
    font-family: var(--font-serif);
}

.edit-btn {
    background: transparent;
    border: none;
    color: var(--color-primary);
    padding: 5px 10px;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    font-weight: 600;
}

.edit-btn:hover {
    color: var(--color-accent);
}

.form-group {
    margin-bottom: 24px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: var(--color-secondary);
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 10px 0;
    border: none;
    border-bottom: 1px solid #E0E0E0;
    border-radius: 0;
    font-size: 1rem;
    transition: border-color 0.3s;
    background: transparent;
}

.form-group input:focus {
    border-bottom-color: var(--color-primary);
    outline: none;
}

.disabled-input {
    color: var(--color-text-light);
    border-bottom-style: dashed;
}

.save-btn {
    background-color: var(--color-primary);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 24px;
    font-size: 1rem;
    cursor: pointer;
    width: 100%;
    font-weight: 600;
    transition: all 0.3s;
}

.save-btn:hover:not(:disabled) {
    background-color: var(--color-accent);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.side-column h2 {
    font-size: 1.2rem;
    color: var(--color-secondary);
    margin-bottom: 15px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding-bottom: 10px;
    font-family: var(--font-serif);
}

.coupon-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.coupon-item {
    display: flex;
    align-items: center;
    gap: 15px;
    background: var(--color-bg);
    padding: 15px;
    border-radius: 8px;
    border: 1px dashed var(--color-primary);
}

.coupon-icon {
    font-size: 1.5rem;
}

.coupon-msg {
    margin: 0;
    font-weight: 600;
    color: var(--color-primary);
    font-size: 0.9rem;
}

.coupon-date {
    font-size: 0.8rem;
    color: var(--color-text-light);
}

.empty-state {
    text-align: center;
    color: var(--color-text-light);
    padding: 20px 0;
}

.link {
    color: var(--color-primary);
    text-decoration: underline;
}
</style>
