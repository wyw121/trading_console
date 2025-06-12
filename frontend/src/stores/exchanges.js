import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

export const useExchangesStore = defineStore('exchanges', () => {
  const exchangeAccounts = ref([])
  const loading = ref(false)
  const fetchExchangeAccounts = async () => {
    loading.value = true
    try {
      const response = await api.get('/exchanges/')
      exchangeAccounts.value = response.data
      return { success: true }
    } catch (error) {
      ElMessage.error('获取交易所账户失败')
      return { success: false, message: error.response?.data?.detail || '获取失败' }
    } finally {
      loading.value = false
    }
  }
  const createExchangeAccount = async (accountData) => {
    try {
      const response = await api.post('/exchanges/', accountData)
      exchangeAccounts.value.push(response.data)
      ElMessage.success('交易所账户添加成功')
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('交易所账户添加失败')
      return { success: false, message: error.response?.data?.detail || '添加失败' }
    }
  }
  const deleteExchangeAccount = async (accountId) => {
    try {
      await api.delete(`/exchanges/accounts/${accountId}`)
      exchangeAccounts.value = exchangeAccounts.value.filter(acc => acc.id !== accountId)
      ElMessage.success('交易所账户删除成功')
      return { success: true }
    } catch (error) {
      ElMessage.error('交易所账户删除失败')
      return { success: false, message: error.response?.data?.detail || '删除失败' }
    }
  }
  const getAccountBalance = async (accountId) => {
    try {
      const response = await api.get(`/exchanges/accounts/${accountId}/balance`)
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('获取账户余额失败')
      return { success: false, message: error.response?.data?.detail || '获取失败' }
    }
  }
  const getTicker = async (accountId, symbol) => {
    try {
      const response = await api.get(`/exchanges/accounts/${accountId}/ticker/${symbol}`)
      return { success: true, data: response.data }
    } catch (error) {
      ElMessage.error('获取行情数据失败')
      return { success: false, message: error.response?.data?.detail || '获取失败' }
    }
  }

  return {
    exchangeAccounts,
    loading,
    fetchExchangeAccounts,
    createExchangeAccount,
    deleteExchangeAccount,
    getAccountBalance,
    getTicker
  }
})
