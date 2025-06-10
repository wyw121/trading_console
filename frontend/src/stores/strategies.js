import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

export const useStrategiesStore = defineStore('strategies', () => {
  const strategies = ref([])
  const loading = ref(false)

  const fetchStrategies = async () => {
    loading.value = true
    try {
      const response = await api.get('/strategies')
      strategies.value = response.data
      return { success: true }
    } catch (error) {
      ElMessage.error('获取策略列表失败')
      return { success: false, message: error.response?.data?.detail || '获取失败' }
    } finally {
      loading.value = false
    }
  }

  const createStrategy = async (strategyData) => {
    try {
      const response = await api.post('/strategies', strategyData)
      strategies.value.push(response.data)
      ElMessage.success('策略创建成功')
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('策略创建失败')
      return { success: false, message: error.response?.data?.detail || '创建失败' }
    }
  }

  const updateStrategy = async (strategyId, strategyData) => {
    try {
      const response = await api.put(`/strategies/${strategyId}`, strategyData)
      const index = strategies.value.findIndex(s => s.id === strategyId)
      if (index !== -1) {
        strategies.value[index] = response.data
      }
      ElMessage.success('策略更新成功')
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('策略更新失败')
      return { success: false, message: error.response?.data?.detail || '更新失败' }
    }
  }

  const deleteStrategy = async (strategyId) => {
    try {
      await api.delete(`/strategies/${strategyId}`)
      strategies.value = strategies.value.filter(s => s.id !== strategyId)
      ElMessage.success('策略删除成功')
      return { success: true }
    } catch (error) {
      ElMessage.error('策略删除失败')
      return { success: false, message: error.response?.data?.detail || '删除失败' }
    }
  }

  const toggleStrategy = async (strategyId) => {
    try {
      const response = await api.post(`/strategies/${strategyId}/toggle`)
      const index = strategies.value.findIndex(s => s.id === strategyId)
      if (index !== -1) {
        strategies.value[index].is_active = response.data.is_active
      }
      ElMessage.success(response.data.message)
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('策略状态切换失败')
      return { success: false, message: error.response?.data?.detail || '切换失败' }
    }
  }

  return {
    strategies,
    loading,
    fetchStrategies,
    createStrategy,
    updateStrategy,
    deleteStrategy,
    toggleStrategy
  }
})
