<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span style="color: #f56c6c; font-weight: bold;">Admin Login</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="Username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="danger" @click="onSubmit" :loading="loading" style="width: 100%;">Login to Admin</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

const onSubmit = async () => {
    if(!form.value.username || !form.value.password) {
        ElMessage.warning('Please enter username and password')
        return
    }
    loading.value = true
    try {
        await authStore.loginAdmin(form.value)
        ElMessage.success('Admin login successful')
        router.push('/admin/products')
    } catch (e) {
        console.error(e)
        ElMessage.error(e.response?.data?.error || e.message || 'Login failed')
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    margin-top: 50px;
}
.login-card {
    width: 400px;
}
</style>
