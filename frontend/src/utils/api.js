import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
          baseURL: '/api',
          timeout: 15000  // Increase timeout to 15 seconds for dashboard
})

// Request interceptor
api.interceptors.request.use(
          (config) => {
                    const authStore = useAuthStore()
                    if (authStore.token) {
                              config.headers.Authorization = `Bearer ${authStore.token}`
                    }
                    return config
          },
          (error) => {
                    return Promise.reject(error)
          }
)

// Response interceptor
api.interceptors.response.use(
          (response) => {
                    return response
          },
          (error) => {
                    if (error.response?.status === 401) {
                              const authStore = useAuthStore()
                              authStore.logout()
                              window.location.href = '/login'
                    } else if (error.response?.status >= 500) {
                              ElMessage.error('服务器错误，请稍后再试')
                    }
                    return Promise.reject(error)
          }
)

export default api
