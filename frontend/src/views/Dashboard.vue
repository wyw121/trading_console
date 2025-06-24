<template>
          <div class="dashboard">
                    <div class="page-header">
                              <h1 class="page-title">控制台概览</h1>
                              <p class="page-description">查看您的交易策略概况和账户信息</p>
                    </div>

                    <!-- 统计卡片 -->
                    <el-row :gutter="20" class="stats-row">
                              <el-col :span="6">
                                        <el-card class="stats-card">
                                                  <div class="stats-content">
                                                            <div class="stats-icon stats-icon-primary">
                                                                      <el-icon>
                                                                                <Setting />
                                                                      </el-icon>
                                                            </div>
                                                            <div class="stats-info">
                                                                      <div class="stats-number">{{
                                                                                dashboardStats.total_strategies }}</div>
                                                                      <div class="stats-label">策略总数</div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>

                              <el-col :span="6">
                                        <el-card class="stats-card">
                                                  <div class="stats-content">
                                                            <div class="stats-icon stats-icon-success">
                                                                      <el-icon>
                                                                                <VideoPlay />
                                                                      </el-icon>
                                                            </div>
                                                            <div class="stats-info">
                                                                      <div class="stats-number">{{
                                                                                dashboardStats.active_strategies }}
                                                                      </div>
                                                                      <div class="stats-label">运行中策略</div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>

                              <el-col :span="6">
                                        <el-card class="stats-card">
                                                  <div class="stats-content">
                                                            <div class="stats-icon stats-icon-warning">
                                                                      <el-icon>
                                                                                <List />
                                                                      </el-icon>
                                                            </div>
                                                            <div class="stats-info">
                                                                      <div class="stats-number">{{
                                                                                dashboardStats.total_trades }}</div>
                                                                      <div class="stats-label">交易次数</div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>

                              <el-col :span="6">
                                        <el-card class="stats-card">
                                                  <div class="stats-content">
                                                            <div class="stats-icon" :class="profitClass">
                                                                      <el-icon>
                                                                                <TrendCharts />
                                                                      </el-icon>
                                                            </div>
                                                            <div class="stats-info">
                                                                      <div class="stats-number" :class="profitClass">
                                                                                {{
                                                                                formatCurrency(dashboardStats.total_profit_loss)
                                                                                }}
                                                                      </div>
                                                                      <div class="stats-label">总盈亏</div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>
                    </el-row>

                    <!-- 账户余额 -->
                    <el-row :gutter="20" class="content-row">
                              <el-col :span="12">
                                        <el-card class="card-container">
                                                  <template #header>
                                                            <div class="flex-between">
                                                                      <span>账户余额</span>
                                                                      <el-button size="small" @click="refreshBalances">
                                                                                <el-icon>
                                                                                          <Refresh />
                                                                                </el-icon>
                                                                                刷新
                                                                      </el-button>
                                                            </div>
                                                  </template>

                                                  <div v-if="balanceLoading" class="loading-container">
                                                            <el-skeleton :rows="3" animated />
                                                  </div>

                                                  <div v-else-if="dashboardStats.account_balances.length === 0"
                                                            class="empty-container">
                                                            <el-empty description="暂无账户信息">
                                                                      <el-button type="primary"
                                                                                @click="$router.push('/exchanges')">
                                                                                添加交易所账户
                                                                      </el-button>
                                                            </el-empty>
                                                  </div>

                                                  <div v-else>
                                                            <div v-for="balance in dashboardStats.account_balances"
                                                                      :key="`${balance.exchange}_${balance.currency}`"
                                                                      class="balance-item">
                                                                      <div class="balance-info">
                                                                                <div class="balance-header">
                                                                                          <span class="exchange-name">{{
                                                                                                    balance.exchange.toUpperCase()
                                                                                                    }}</span>
                                                                                          <span class="currency-name">{{
                                                                                                    balance.currency
                                                                                                    }}</span>
                                                                                </div>
                                                                                <div class="balance-details">
                                                                                          <div class="balance-detail">
                                                                                                    <span
                                                                                                              class="label">可用:</span>
                                                                                                    <span class="value">{{
                                                                                                              formatNumber(balance.free)
                                                                                                              }}</span>
                                                                                          </div>
                                                                                          <div class="balance-detail">
                                                                                                    <span
                                                                                                              class="label">冻结:</span>
                                                                                                    <span class="value">{{
                                                                                                              formatNumber(balance.used)
                                                                                                              }}</span>
                                                                                          </div>
                                                                                          <div class="balance-detail">
                                                                                                    <span
                                                                                                              class="label">总计:</span>
                                                                                                    <span
                                                                                                              class="value total">{{
                                                                                                              formatNumber(balance.total)
                                                                                                              }}</span>
                                                                                          </div>
                                                                                </div>
                                                                      </div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>

                              <el-col :span="12">
                                        <el-card class="card-container">
                                                  <template #header>
                                                            <span>最近交易</span>
                                                  </template>

                                                  <div v-if="recentTrades.length === 0" class="empty-container">
                                                            <el-empty description="暂无交易记录" />
                                                  </div>

                                                  <div v-else>
                                                            <div v-for="trade in recentTrades" :key="trade.id"
                                                                      class="trade-item">
                                                                      <div class="trade-info">
                                                                                <div class="trade-header">
                                                                                          <span class="trade-symbol">{{
                                                                                                    trade.symbol
                                                                                                    }}</span>
                                                                                          <span class="trade-side"
                                                                                                    :class="trade.side === 'buy' ? 'text-success' : 'text-danger'">
                                                                                                    {{ trade.side ===
                                                                                                    'buy' ? '买入' : '卖出'
                                                                                                    }}
                                                                                          </span>
                                                                                </div>
                                                                                <div class="trade-details">
                                                                                          <div>数量: {{
                                                                                                    formatNumber(trade.amount)
                                                                                                    }}</div>
                                                                                          <div>状态: <el-tag :type="getTradeStatusType(trade.status)"
                                                                                                              size="small">{{
                                                                                                              getTradeStatusText(trade.status)
                                                                                                              }}</el-tag>
                                                                                          </div>
                                                                                          <div>时间: {{
                                                                                                    formatDateTime(trade.created_at)
                                                                                                    }}</div>
                                                                                </div>
                                                                      </div>
                                                            </div>
                                                  </div>
                                        </el-card>
                              </el-col>
                    </el-row>
          </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, VideoPlay, List, TrendCharts, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const dashboardStats = ref({
          total_strategies: 0,
          active_strategies: 0,
          total_trades: 0,
          total_profit_loss: 0,
          account_balances: []
})

const recentTrades = ref([])
const balanceLoading = ref(false)

const profitClass = computed(() => {
          const profit = dashboardStats.value.total_profit_loss
          if (profit > 0) return 'stats-icon-success'
          if (profit < 0) return 'stats-icon-danger'
          return 'stats-icon-info'
})

const formatCurrency = (value) => {
          const num = Number(value)
          const prefix = num >= 0 ? '+' : ''
          return `${prefix}${num.toFixed(2)} USDT`
}

const formatNumber = (value) => {
          return Number(value).toFixed(8)
}

const formatDateTime = (dateStr) => {
          return new Date(dateStr).toLocaleString('zh-CN')
}

const getTradeStatusType = (status) => {
          const statusMap = {
                    'pending': 'warning',
                    'filled': 'success',
                    'cancelled': 'info',
                    'failed': 'danger'
          }
          return statusMap[status] || 'info'
}

const getTradeStatusText = (status) => {
          const statusMap = {
                    'pending': '待成交',
                    'filled': '已成交',
                    'cancelled': '已取消',
                    'failed': '失败'
          }
          return statusMap[status] || status
}

const loadDashboardData = async () => {
          try {
                    console.log('开始加载控制台数据...')
                    const response = await api.get('/dashboard/stats')
                    dashboardStats.value = response.data
                    console.log('Dashboard数据加载成功:', response.data)
                    ElMessage.success('控制台数据加载成功')
          } catch (error) {
                    console.error('加载控制台数据失败:', error)
                    console.error('错误详情:', error.response?.data)
                    
                    // Check if it's a timeout error
                    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
                              ElMessage.warning('加载超时，但不影响基本功能')
                              // Set default stats on timeout
                              dashboardStats.value = {
                                        total_strategies: 0,
                                        active_strategies: 0,
                                        total_trades: 0,
                                        total_profit_loss: 0.0,
                                        today_trades: 0,
                                        today_profit_loss: 0.0,
                                        account_balances: []
                              }
                    } else {
                              const errorMessage = error.response?.data?.detail || error.message || '加载控制台数据失败'
                              ElMessage.error(`加载控制台数据失败: ${errorMessage}`)
                    }
          }
}

const loadRecentTrades = async () => {
          try {
                    const response = await api.get('/trades')
                    recentTrades.value = response.data.slice(0, 5) // Show only 5 recent trades
                    console.log('交易记录加载成功:', response.data)
          } catch (error) {
                    console.error('加载交易记录失败:', error)
                    console.error('错误详情:', error.response?.data)
                    // 不显示错误消息，因为交易记录为空是正常的
          }
}

const refreshBalances = async () => {
          balanceLoading.value = true
          try {
                    console.log('开始刷新余额...')
                    const response = await api.get('/dashboard/refresh-balances')
                    dashboardStats.value = response.data
                    console.log('余额刷新成功:', response.data)
                    ElMessage.success('余额刷新成功')
          } catch (error) {
                    console.error('刷新余额失败:', error)
                    ElMessage.error('刷新失败')
          } finally {
                    balanceLoading.value = false
          }
}

onMounted(() => {
          loadDashboardData()
          loadRecentTrades()
})
</script>

<style scoped>
.dashboard {
          max-width: 1200px;
          margin: 0 auto;
}

.stats-row {
          margin-bottom: 20px;
}

.content-row {
          margin-bottom: 20px;
}

.stats-card {
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
}

.stats-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stats-content {
          display: flex;
          align-items: center;
          padding: 10px 0;
}

.stats-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          font-size: 20px;
          color: white;
}

.stats-icon-primary {
          background: linear-gradient(135deg, #409eff, #6c5ce7);
}

.stats-icon-success {
          background: linear-gradient(135deg, #67c23a, #00b894);
}

.stats-icon-warning {
          background: linear-gradient(135deg, #e6a23c, #fdcb6e);
}

.stats-icon-danger {
          background: linear-gradient(135deg, #f56c6c, #e17055);
}

.stats-icon-info {
          background: linear-gradient(135deg, #909399, #b2bec3);
}

.stats-info {
          flex: 1;
}

.stats-number {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
}

.stats-label {
          font-size: 14px;
          color: #909399;
}

.loading-container,
.empty-container {
          padding: 20px;
          text-align: center;
}

.balance-item {
          padding: 16px;
          border-bottom: 1px solid #f0f0f0;
}

.balance-item:last-child {
          border-bottom: none;
}

.balance-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
}

.exchange-name {
          font-weight: 600;
          color: #303133;
}

.currency-name {
          color: #409eff;
          font-weight: 500;
}

.balance-details {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 12px;
}

.balance-detail {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 14px;
}

.balance-detail .label {
          color: #909399;
}

.balance-detail .value {
          color: #303133;
          font-weight: 500;
}

.balance-detail .value.total {
          color: #409eff;
          font-weight: 600;
}

.trade-item {
          padding: 16px;
          border-bottom: 1px solid #f0f0f0;
}

.trade-item:last-child {
          border-bottom: none;
}

.trade-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
}

.trade-symbol {
          font-weight: 600;
          color: #303133;
}

.trade-side {
          font-weight: 500;
}

.trade-details {
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
}
</style>
