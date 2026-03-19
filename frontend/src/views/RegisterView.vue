<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <span>Register</span>
      </template>
      <el-form :model="form" label-width="140px" :rules="rules" ref="formRef">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="Confirm Password" prop="password_confirm">
          <el-input v-model="form.password_confirm" type="password" />
        </el-form-item>
        <el-form-item label="Province" prop="province">
            <el-input v-model="form.province" />
        </el-form-item>
        <el-form-item label="City" prop="city">
            <el-input v-model="form.city" />
        </el-form-item>
        <el-form-item label="Address" prop="detail_address">
            <el-input v-model="form.detail_address" type="textarea" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="loading" style="width: 100%;">Register</el-button>
        </el-form-item>
        <div style="text-align: center;">
            <el-button link @click="$router.push({ path: '/login', query: { redirect: route.query.redirect } })">Already have an account? Login</el-button>
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
const formRef = ref(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  province: '',
  city: '',
  detail_address: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('Please input the password again'))
  } else if (value !== form.value.password) {
    callback(new Error("Two inputs don't match!"))
  } else {
    callback()
  }
}

const rules = {
    username: [{ required: true, message: 'Required', trigger: 'blur' }],
    email: [{ required: true, message: 'Required', trigger: 'blur' }, { type: 'email', message: 'Invalid email', trigger: 'blur' }],
    password: [{ required: true, message: 'Required', trigger: 'blur' }],
    password_confirm: [{ required: true, validator: validatePass2, trigger: 'blur' }],
    province: [{ required: true, message: 'Required', trigger: 'blur' }],
    city: [{ required: true, message: 'Required', trigger: 'blur' }],
    detail_address: [{ required: true, message: 'Required', trigger: 'blur' }]
}

const onSubmit = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            loading.value = true
            try {
                await authStore.register(form.value)
                ElMessage.success('Registration successful. Please login.')
                router.push({ 
                    path: '/login',
                    query: { redirect: route.query.redirect }
                })
            } catch (e) {
                console.error(e)
                const errorMsg = e.response?.data ? JSON.stringify(e.response.data) : 'Registration failed'
                ElMessage.error(errorMsg)
            } finally {
                loading.value = false
            }
        }
    })
}
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    margin-top: 50px;
}
.register-card {
    width: 500px;
}
</style>
