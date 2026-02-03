<template>
  <div class="register-container">
    <h2>Customer Registration</h2>
    <form @submit.prevent="handleRegister">
      <input v-model="formData.username" placeholder="Full Name (e.g. John Doe)" required />
      <input v-model="formData.email" type="email" placeholder="Email Address" required />
      <input v-model="formData.password" type="password" placeholder="Password" required />
      <input v-model="formData.province" placeholder="Province" required />
      <input v-model="formData.city" placeholder="City" required />
      <input v-model="formData.detail_address" placeholder="Detailed Street Address" required />
      
      <button type="submit">Register Now</button>
    </form>
    <p v-if="statusMessage" :style="{ color: isError ? 'red' : 'green' }">
      {{ statusMessage }}
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const formData = ref({
  username: '', email: '', password: '',
  province: '', city: '', detail_address: ''
});
const statusMessage = ref('');
const isError = ref(false);

const handleRegister = async () => {
  try {
    // 提示：把 127.0.0.1 换成你电脑的局域网 IP
    const response = await axios.post('http://127.0.0.1:8000/api/register/', formData.value);
    statusMessage.value = response.data.message; // 应该显示 Registration successful!
    isError.value = false;
  } catch (error) {
    statusMessage.value = "Registration Failed: " + JSON.stringify(error.response?.data || "Network Error");
    isError.value = true;
  }
};
</script>

<style scoped>
.register-container { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
input { display: block; width: 100%; margin-bottom: 10px; padding: 8px; }
button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>