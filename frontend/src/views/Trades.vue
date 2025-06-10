<template>
          <div class="trades">
                    <div class="page-header">
                              <h1 class="page-title">交易记录</h1>
                              <p class="page-description">查看您的交易历史和详细信息</p>
                    </div>

                    <el-card class="card-container">
                              <template #header>
                                        <div class="flex-between">
                                                  <span>交易列表</span>
                                                  <div class="header-actions">
                                                            <el-select v-model="selectedStrategy" placeholder="筛选策略"
                                                                      clearable style="width: 200px; margin-right: 10px"
                                                                      @change="loadTrades">
                                                                      <el-option v-for="strategy in strategies"
                                                                                :key="strategy.id"
                                                                                :label="strategy.name"
                                                                                :value="strategy.id" />
                                                            </el-select>
                                                            <el-button @click="loadTrades">
                                                                      <el-icon>
                                                                                <Refresh />
                                                                      </el-icon>
                                                                      刷新
                                                            </el-button>
                                                  </div>
                                        </div>
                              </template>

                              <el-table :data="trades" style="width: 100%" v-loading="loading">
                                        <el-table-column prop="id" label="交易ID" width="80" />
                                        <el-table-column prop="symbol" label="交易对" width="120" />
                                        <el-table-column prop="side" label="方向" width="80">
                                                  <template #default="scope">
                                                            <el-tag
                                                                      :type="scope.row.side === 'buy' ? 'success' : 'danger'">
                                                                      {{ scope.row.side === 'buy' ? '买入' : '卖出' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="order_type" label="订单类型" width="100">
                                                  <template #default="scope">
                                                            <el-tag type="info">
                                                                      {{ scope.row.order_type === 'market' ? '市价' : '限价'
                                                                      }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="amount" label="数量" width="120">
                                                  <template #default="scope">
                                                            {{ formatNumber(scope.row.amount, 6) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="price" label="价格" width="120">
                                                  <template #default="scope">
                                                            {{ scope.row.price ? formatNumber(scope.row.price, 2) : '-'
                                                            }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="filled_amount" label="成交数量" width="120">
                                                  <template #default="scope">
                                                            {{ formatNumber(scope.row.filled_amount, 6) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="filled_price" label="成交价格" width="120">
                                                  <template #default="scope">
                                                            {{ scope.row.filled_price ?
                                                            formatNumber(scope.row.filled_price, 2) : '-' }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="status" label="状态" width="100">
                                                  <template #default="scope">
                                                            <el-tag :type="getTradeStatusType(scope.row.status)">
                                                                      {{ getTradeStatusText(scope.row.status) }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="fee" label="手续费" width="100">
                                                  <template #default="scope">
                                                            {{ formatNumber(scope.row.fee, 4) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="profit_loss" label="盈亏" width="100">
                                                  <template #default="scope">
                                                            <span :class="getProfitClass(scope.row.profit_loss)">
                                                                      {{ formatProfitLoss(scope.row.profit_loss) }}
                                                            </span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="created_at" label="创建时间" width="180">
                                                  <template #default="scope">
                                                            {{ formatDateTime(scope.row.created_at) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="filled_at" label="成交时间" width="180">
                                                  <template #default="scope">
                                                            {{ scope.row.filled_at ? formatDateTime(scope.row.filled_at)
                                                            : '-' }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column label="操作" width="100" fixed="right">
                                                  <template #default="scope">
                                                            <el-button v-if="scope.row.status === 'pending'"
                                                                      size="small" type="warning"
                                                                      @click="cancelTrade(scope.row)">
                                                                      取消
                                                            </el-button>
                                                            <span v-else>-</span>
                                                  </template>
                                        </el-table-column>
                              </el-table>
                    </el-card>
          </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const trades = ref([])
const strategies = ref([])
const loading = ref(false)
const selectedStrategy = ref(null)

const formatNumber = (value, decimals = 2) => {
          return Number(value).toFixed(decimals)
}

const formatDateTime = (dateStr) => {
          return new Date(dateStr).toLocaleString('zh-CN')
}

const formatProfitLoss = (value) => {
          const num = Number(value)
          const prefix = num > 0 ? '+' : ''
          return `${prefix}${num.toFixed(2)}`
}

const getProfitClass = (value) => {
          const num = Number(value)
          if (num > 0) return 'text-success'
          if (num < 0) return 'text-danger'
          return 'text-info'
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

const loadTrades = async () => {
          loading.value = true
          try {
                    const params = selectedStrategy.value ? { strategy_id: selectedStrategy.value } : {}
                    const response = await api.get('/trades', { params })
                    trades.value = response.data
          } catch (error) {
                    ElMessage.error('加载交易记录失败')
          } finally {
                    loading.value = false
          }
}

const loadStrategies = async () => {
          try {
                    const response = await api.get('/strategies')
                    strategies.value = response.data
          } catch (error) {
                    console.error('加载策略列表失败:', error)
          }
}

const cancelTrade = async (trade) => {
          try {
                    await ElMessageBox.confirm(
                              `确定要取消交易 #${trade.id} 吗？`,
                              '取消确认',
                              {
                                        confirmButtonText: '确定',
                                        cancelButtonText: '取消',
                                        type: 'warning',
                              }
                    )

                    await api.post(`/trades/${trade.id}/cancel`)
                    ElMessage.success('交易已取消')
                    await loadTrades()
          } catch (error) {
                    if (error !== 'cancel') {
                              ElMessage.error('取消失败')
                    }
          }
}

onMounted(() => {
          loadTrades()
          loadStrategies()
})
</script>

<style scoped>
.trades {
          max-width: 1400px;
          margin: 0 auto;
}

.header-actions {
          display: flex;
          align-items: center;
}

.text-success {
          color: #67c23a;
          font-weight: 500;
}

.text-danger {
          color: #f56c6c;
          font-weight: 500;
}

.text-info {
          color: #909399;
}
</style>
