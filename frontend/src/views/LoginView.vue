<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>Login</span>
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
          <el-button type="primary" @click="onSubmit" :loading="loading" style="width: 100%;">Login</el-button>
        </el-form-item>
        <div style="text-align: center;">
            <el-button link @click="$router.push({ path: '/register', query: { redirect: route.query.redirect } })">No account? Register</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
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
        await authStore.login(form.value)
        ElMessage.success('Login successful')
        
        // Handle redirection
        let redirect = route.query.redirect
        if (Array.isArray(redirect)) {
            redirect = redirect[0]
        }
        
        // If redirect is just a path string, push it
        if (redirect) {
            router.push(redirect)
        } else {
            router.push('/')
        }
    } catch (e) {
        // Error handled in interceptor
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
