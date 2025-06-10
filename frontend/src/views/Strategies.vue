<template>
          <div class="strategies">
                    <div class="page-header">
                              <h1 class="page-title">策略配置</h1>
                              <p class="page-description">管理和配置您的交易策略</p>
                    </div>

                    <el-card class="card-container">
                              <template #header>
                                        <div class="flex-between">
                                                  <span>策略列表</span>
                                                  <el-button type="primary" @click="showCreateDialog = true">
                                                            <el-icon>
                                                                      <Plus />
                                                            </el-icon>
                                                            创建策略
                                                  </el-button>
                                        </div>
                              </template>

                              <el-table :data="strategies" style="width: 100%" v-loading="loading">
                                        <el-table-column prop="name" label="策略名称" />
                                        <el-table-column prop="strategy_type" label="策略类型" />
                                        <el-table-column prop="symbol" label="交易对" />
                                        <el-table-column prop="timeframe" label="时间周期" />
                                        <el-table-column prop="entry_amount" label="交易金额">
                                                  <template #default="scope">
                                                            {{ formatNumber(scope.row.entry_amount) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="leverage" label="杠杆">
                                                  <template #default="scope">
                                                            {{ scope.row.leverage }}x
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="is_active" label="状态">
                                                  <template #default="scope">
                                                            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                                                                      {{ scope.row.is_active ? '运行中' : '已停止' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column label="操作" width="200">
                                                  <template #default="scope">
                                                            <el-button size="small"
                                                                      :type="scope.row.is_active ? 'warning' : 'success'"
                                                                      @click="toggleStrategy(scope.row)">
                                                                      {{ scope.row.is_active ? '停止' : '启动' }}
                                                            </el-button>
                                                            <el-button size="small" @click="editStrategy(scope.row)">
                                                                      编辑
                                                            </el-button>
                                                            <el-button size="small" type="danger"
                                                                      @click="deleteStrategy(scope.row)">
                                                                      删除
                                                            </el-button>
                                                  </template>
                                        </el-table-column>
                              </el-table>
                    </el-card>

                    <!-- 创建/编辑策略对话框 -->
                    <el-dialog :title="editingStrategy ? '编辑策略' : '创建策略'" v-model="showCreateDialog" width="600px"
                              @close="resetForm">
                              <el-form ref="strategyFormRef" :model="strategyForm" :rules="strategyRules"
                                        label-width="120px">
                                        <el-form-item label="策略名称" prop="name">
                                                  <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
                                        </el-form-item>

                                        <el-form-item label="交易所账户" prop="exchange_account_id">
                                                  <el-select v-model="strategyForm.exchange_account_id"
                                                            placeholder="请选择交易所账户" style="width: 100%">
                                                            <el-option v-for="account in exchangeAccounts"
                                                                      :key="account.id"
                                                                      :label="`${account.exchange_name.toUpperCase()} (${account.api_key})`"
                                                                      :value="account.id" />
                                                  </el-select>
                                        </el-form-item>

                                        <el-form-item label="策略类型" prop="strategy_type">
                                                  <el-select v-model="strategyForm.strategy_type" placeholder="请选择策略类型"
                                                            style="width: 100%">
                                                            <el-option label="5分钟布林带+MA60策略" value="5m_boll_ma60" />
                                                            <!-- 可以添加更多策略类型 -->
                                                  </el-select>
                                        </el-form-item>

                                        <el-form-item label="交易对" prop="symbol">
                                                  <el-input v-model="strategyForm.symbol" placeholder="例如: BTC/USDT" />
                                        </el-form-item>

                                        <el-form-item label="时间周期" prop="timeframe">
                                                  <el-select v-model="strategyForm.timeframe" style="width: 100%">
                                                            <el-option label="1分钟" value="1m" />
                                                            <el-option label="5分钟" value="5m" />
                                                            <el-option label="15分钟" value="15m" />
                                                            <el-option label="1小时" value="1h" />
                                                            <el-option label="4小时" value="4h" />
                                                            <el-option label="1天" value="1d" />
                                                  </el-select>
                                        </el-form-item>

                                        <el-form-item label="交易金额" prop="entry_amount">
                                                  <el-input-number v-model="strategyForm.entry_amount" :min="0.01"
                                                            :precision="2" style="width: 100%" />
                                        </el-form-item>

                                        <el-form-item label="杠杆倍数" prop="leverage">
                                                  <el-input-number v-model="strategyForm.leverage" :min="1" :max="100"
                                                            style="width: 100%" />
                                        </el-form-item>

                                        <el-form-item label="止损比例 (%)" prop="stop_loss_percent">
                                                  <el-input-number v-model="strategyForm.stop_loss_percent" :min="0"
                                                            :max="50" :precision="2" style="width: 100%" />
                                        </el-form-item>

                                        <el-form-item label="止盈比例 (%)" prop="take_profit_percent">
                                                  <el-input-number v-model="strategyForm.take_profit_percent" :min="0"
                                                            :max="100" :precision="2" style="width: 100%" />
                                        </el-form-item>

                                        <el-divider>布林带参数</el-divider>

                                        <el-form-item label="周期" prop="bb_period">
                                                  <el-input-number v-model="strategyForm.bb_period" :min="5" :max="100"
                                                            style="width: 100%" />
                                        </el-form-item>

                                        <el-form-item label="标准差倍数" prop="bb_deviation">
                                                  <el-input-number v-model="strategyForm.bb_deviation" :min="1" :max="5"
                                                            :precision="1" style="width: 100%" />
                                        </el-form-item>

                                        <el-divider>移动平均线参数</el-divider>

                                        <el-form-item label="MA周期" prop="ma_period">
                                                  <el-input-number v-model="strategyForm.ma_period" :min="5" :max="200"
                                                            style="width: 100%" />
                                        </el-form-item>
                              </el-form>

                              <template #footer>
                                        <span class="dialog-footer">
                                                  <el-button @click="showCreateDialog = false">取消</el-button>
                                                  <el-button type="primary" @click="saveStrategy" :loading="saving">
                                                            {{ editingStrategy ? '保存' : '创建' }}
                                                  </el-button>
                                        </span>
                              </template>
                    </el-dialog>
          </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const strategies = ref([])
const exchangeAccounts = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingStrategy = ref(null)
const strategyFormRef = ref()

const strategyForm = reactive({
          name: '',
          exchange_account_id: null,
          strategy_type: '5m_boll_ma60',
          symbol: 'BTC/USDT',
          timeframe: '5m',
          entry_amount: 100,
          leverage: 1,
          stop_loss_percent: 2,
          take_profit_percent: 5,
          bb_period: 20,
          bb_deviation: 2.0,
          ma_period: 60
})

const strategyRules = {
          name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
          exchange_account_id: [{ required: true, message: '请选择交易所账户', trigger: 'change' }],
          strategy_type: [{ required: true, message: '请选择策略类型', trigger: 'change' }],
          symbol: [{ required: true, message: '请输入交易对', trigger: 'blur' }],
          timeframe: [{ required: true, message: '请选择时间周期', trigger: 'change' }],
          entry_amount: [{ required: true, message: '请输入交易金额', trigger: 'change' }]
}

const formatNumber = (value) => {
          return Number(value).toFixed(2)
}

const loadStrategies = async () => {
          loading.value = true
          try {
                    const response = await api.get('/strategies')
                    strategies.value = response.data
          } catch (error) {
                    ElMessage.error('加载策略列表失败')
          } finally {
                    loading.value = false
          }
}

const loadExchangeAccounts = async () => {
          try {
                    const response = await api.get('/exchange/accounts')
                    exchangeAccounts.value = response.data
          } catch (error) {
                    ElMessage.error('加载交易所账户失败')
          }
}

const resetForm = () => {
          editingStrategy.value = null
          Object.assign(strategyForm, {
                    name: '',
                    exchange_account_id: null,
                    strategy_type: '5m_boll_ma60',
                    symbol: 'BTC/USDT',
                    timeframe: '5m',
                    entry_amount: 100,
                    leverage: 1,
                    stop_loss_percent: 2,
                    take_profit_percent: 5,
                    bb_period: 20,
                    bb_deviation: 2.0,
                    ma_period: 60
          })
          if (strategyFormRef.value) {
                    strategyFormRef.value.clearValidate()
          }
}

const editStrategy = (strategy) => {
          editingStrategy.value = strategy
          Object.assign(strategyForm, {
                    name: strategy.name,
                    exchange_account_id: strategy.exchange_account_id,
                    strategy_type: strategy.strategy_type,
                    symbol: strategy.symbol,
                    timeframe: strategy.timeframe,
                    entry_amount: strategy.entry_amount,
                    leverage: strategy.leverage,
                    stop_loss_percent: strategy.stop_loss_percent,
                    take_profit_percent: strategy.take_profit_percent,
                    bb_period: strategy.bb_period,
                    bb_deviation: strategy.bb_deviation,
                    ma_period: strategy.ma_period
          })
          showCreateDialog.value = true
}

const saveStrategy = async () => {
          if (!strategyFormRef.value) return

          await strategyFormRef.value.validate(async (valid) => {
                    if (valid) {
                              saving.value = true

                              try {
                                        if (editingStrategy.value) {
                                                  // 更新策略
                                                  await api.put(`/strategies/${editingStrategy.value.id}`, strategyForm)
                                                  ElMessage.success('策略更新成功')
                                        } else {
                                                  // 创建策略
                                                  await api.post('/strategies', strategyForm)
                                                  ElMessage.success('策略创建成功')
                                        }

                                        showCreateDialog.value = false
                                        await loadStrategies()
                              } catch (error) {
                                        ElMessage.error(error.response?.data?.detail || '保存失败')
                              } finally {
                                        saving.value = false
                              }
                    }
          })
}

const toggleStrategy = async (strategy) => {
          try {
                    await api.post(`/strategies/${strategy.id}/toggle`)
                    ElMessage.success(`策略已${strategy.is_active ? '停止' : '启动'}`)
                    await loadStrategies()
          } catch (error) {
                    ElMessage.error('操作失败')
          }
}

const deleteStrategy = async (strategy) => {
          try {
                    await ElMessageBox.confirm(
                              `确定要删除策略 "${strategy.name}" 吗？`,
                              '删除确认',
                              {
                                        confirmButtonText: '确定',
                                        cancelButtonText: '取消',
                                        type: 'warning',
                              }
                    )

                    await api.delete(`/strategies/${strategy.id}`)
                    ElMessage.success('策略删除成功')
                    await loadStrategies()
          } catch (error) {
                    if (error !== 'cancel') {
                              ElMessage.error('删除失败')
                    }
          }
}

onMounted(() => {
          loadStrategies()
          loadExchangeAccounts()
})
</script>

<style scoped>
.strategies {
          max-width: 1200px;
          margin: 0 auto;
}

.dialog-footer {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
}

.el-divider {
          margin: 20px 0;
}
</style>
