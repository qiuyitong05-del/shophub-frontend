import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: 'http://127.0.0.1:8001/api/', // Use 127.0.0.1 for better compatibility
  timeout: 10000 // Increased timeout
})

// Request interceptor
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = 'Token ' + token
    }
    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    console.log('Response received:', response.config.url, response.status)
    return response.data
  },
  error => {
    console.log('Request Error:', error)
    let message = error.message || 'Error'
    if (error.code === 'ECONNABORTED') {
        message = 'Request timed out, please try again'
    } else if (error.message === 'Network Error') {
        message = 'Network error, please try again' // X3 Requirement
    } else if (error.response && error.response.data) {
        // Try to get specific error message
        const data = error.response.data
        if (data.detail) message = data.detail
        else if (data.error) message = data.error
        else if (typeof data === 'string') message = data
        // If data is object with field errors (e.g. serializer errors)
        else if (typeof data === 'object') {
             // Take first error
             const keys = Object.keys(data)
             if (keys.length > 0) {
                 const first = data[keys[0]]
                 message = Array.isArray(first) ? first[0] : first
             }
        }
    }

    ElMessage({
        message: message,
        type: 'error',
        duration: 3000, // X3: 2-3 seconds
        showClose: true // X3: manually closed
    })
    return Promise.reject(error)
  }
)

export default service
