import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
          const token = ref(localStorage.getItem('token') || null)
          const user = ref(null)

          const isAuthenticated = computed(() => !!token.value)

          const login = async (username, password) => {
                    try {
                              const formData = new FormData()
                              formData.append('username', username)
                              formData.append('password', password)

                              const response = await api.post('/auth/login', formData)

                              token.value = response.data.access_token
                              localStorage.setItem('token', token.value)

                              // Get user info
                              await getCurrentUser()

                              return { success: true }
                    } catch (error) {
                              return {
                                        success: false,
                                        message: error.response?.data?.detail || '登录失败'
                              }
                    }
          }

          const register = async (username, email, password) => {
                    try {
                              await api.post('/auth/register', {
                                        username,
                                        email,
                                        password
                              })

                              return { success: true }
                    } catch (error) {
                              return {
                                        success: false,
                                        message: error.response?.data?.detail || '注册失败'
                              }
                    }
          }

          const getCurrentUser = async () => {
                    try {
                              const response = await api.get('/auth/me')
                              user.value = response.data
                    } catch (error) {
                              logout()
                    }
          }

          const logout = () => {
                    token.value = null
                    user.value = null
                    localStorage.removeItem('token')
          }

          // Initialize on store creation
          if (token.value) {
                    getCurrentUser()
          }

          return {
                    token,
                    user,
                    isAuthenticated,
                    login,
                    register,
                    getCurrentUser,
                    logout
          }
})
