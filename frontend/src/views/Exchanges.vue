<template>
          <div class="exchanges">
                    <div class="page-header">
                              <h1 class="page-title">交易所配置</h1>
                              <p class="page-description">管理您的交易所API账户</p>
                    </div>

                    <el-card class="card-container">
                              <template #header>
                                        <div class="flex-between">
                                                  <span>交易所账户</span>
                                                  <el-button type="primary" @click="showCreateDialog = true">
                                                            <el-icon>
                                                                      <Plus />
                                                            </el-icon>
                                                            添加账户
                                                  </el-button>
                                        </div>
                              </template>

                              <el-table :data="exchangeAccounts" style="width: 100%" v-loading="loading">
                                        <el-table-column prop="exchange_name" label="交易所">
                                                  <template #default="scope">
                                                            <span style="font-weight: 600; text-transform: uppercase;">
                                                                      {{ scope.row.exchange_name }}
                                                            </span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="api_key" label="API Key">
                                                  <template #default="scope">
                                                            <span class="api-key">{{ scope.row.api_key }}</span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="is_testnet" label="环境">
                                                  <template #default="scope">
                                                            <el-tag
                                                                      :type="scope.row.is_testnet ? 'warning' : 'success'">
                                                                      {{ scope.row.is_testnet ? '测试网' : '正式网' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="is_active" label="状态">
                                                  <template #default="scope">
                                                            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                                                                      {{ scope.row.is_active ? '正常' : '禁用' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="created_at" label="创建时间">
                                                  <template #default="scope">
                                                            {{ formatDateTime(scope.row.created_at) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column label="操作" width="200">
                                                  <template #default="scope">
                                                            <el-button size="small" @click="testConnection(scope.row)">
                                                                      测试连接
                                                            </el-button>
                                                            <el-button size="small" type="primary"
                                                                      @click="viewBalance(scope.row)">
                                                                      查看余额
                                                            </el-button>
                                                            <el-button size="small" type="danger"
                                                                      @click="deleteAccount(scope.row)">
                                                                      删除
                                                            </el-button>
                                                  </template>
                                        </el-table-column>
                              </el-table>
                    </el-card>                    <!-- 添加账户对话框 -->
                    <el-dialog title="添加交易所账户" v-model="showCreateDialog" width="500px" @close="resetForm">
                              <el-alert title="测试环境" type="info" :closable="false" style="margin-bottom: 15px">
                                        <p>当前已自动填充OKX测试API密钥，您可以直接点击保存进行测试。</p>
                                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                                                  <el-button size="small" type="success" @click="fillTestCredentials">
                                                            快速填充测试密钥
                                                  </el-button>
                                                  <el-button size="small" @click="clearForm">
                                                            清空表单
                                                  </el-button>
                                        </div>
                              </el-alert>
                              
                              <el-alert title="安全提示" type="warning" :closable="false" style="margin-bottom: 20px">
                                        <p>请确保您的API密钥具有交易权限，但建议禁用提币权限以保证资金安全。</p>
                                        <p>API密钥将被加密存储在数据库中。</p>
                              </el-alert>

                              <el-form ref="accountFormRef" :model="accountForm" :rules="accountRules"
                                        label-width="120px">
                                        <el-form-item label="交易所" prop="exchange_name">
                                                  <el-select v-model="accountForm.exchange_name" placeholder="请选择交易所"
                                                            style="width: 100%">
                                                            <el-option label="Binance" value="binance" />
                                                            <el-option label="OKX" value="okex" />
                                                            <!-- 可以添加更多交易所 -->
                                                  </el-select>
                                        </el-form-item>

                                        <el-form-item label="API Key" prop="api_key">
                                                  <el-input v-model="accountForm.api_key" placeholder="请输入API Key"
                                                            type="password" show-password />
                                        </el-form-item>

                                        <el-form-item label="Secret Key" prop="api_secret">
                                                  <el-input v-model="accountForm.api_secret" placeholder="请输入Secret Key"
                                                            type="password" show-password />
                                        </el-form-item>

                                        <el-form-item v-if="accountForm.exchange_name === 'okex'" label="Passphrase"
                                                  prop="api_passphrase">
                                                  <el-input v-model="accountForm.api_passphrase"
                                                            placeholder="请输入Passphrase (OKX专用)" type="password"
                                                            show-password />
                                        </el-form-item>

                                        <el-form-item label="环境">
                                                  <el-switch v-model="accountForm.is_testnet" active-text="测试网"
                                                            inactive-text="正式网" />
                                        </el-form-item>
                              </el-form>

                              <template #footer>
                                        <span class="dialog-footer">
                                                  <el-button @click="showCreateDialog = false">取消</el-button>
                                                  <el-button type="primary" @click="saveAccount" :loading="saving">
                                                            保存
                                                  </el-button>
                                        </span>
                              </template>
                    </el-dialog>

                    <!-- 余额查看对话框 -->
                    <el-dialog title="账户余额" v-model="showBalanceDialog" width="600px">
                              <div v-if="balanceLoading" class="loading-container">
                                        <el-skeleton :rows="5" animated />
                              </div>

                              <div v-else-if="balanceData">
                                        <el-table :data="balanceTableData" style="width: 100%">
                                                  <el-table-column prop="currency" label="币种" />
                                                  <el-table-column prop="free" label="可用">
                                                            <template #default="scope">
                                                                      {{ formatNumber(scope.row.free) }}
                                                            </template>
                                                  </el-table-column>
                                                  <el-table-column prop="used" label="冻结">
                                                            <template #default="scope">
                                                                      {{ formatNumber(scope.row.used) }}
                                                            </template>
                                                  </el-table-column>
                                                  <el-table-column prop="total" label="总计">
                                                            <template #default="scope">
                                                                      {{ formatNumber(scope.row.total) }}
                                                            </template>
                                                  </el-table-column>
                                        </el-table>
                              </div>

                              <div v-else class="error-container">
                                        <el-result icon="error" title="获取余额失败" />
                              </div>
                    </el-dialog>
          </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const exchangeAccounts = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showBalanceDialog = ref(false)
const balanceLoading = ref(false)
const balanceData = ref(null)
const accountFormRef = ref()

const accountForm = reactive({
          exchange_name: 'okex',  // 默认选择OKX
          api_key: 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',  // 默认测试API Key
          api_secret: 'CD6A497EEB00AA2DC60B2B0974DD2485',  // 默认测试Secret
          api_passphrase: 'vf5Y3UeUFiz6xfF!',  // 默认测试Passphrase
          is_testnet: true  // 默认使用测试网
})

const accountRules = {
          exchange_name: [{ required: true, message: '请选择交易所', trigger: 'change' }],
          api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }],
          api_secret: [{ required: true, message: '请输入Secret Key', trigger: 'blur' }]
}

const balanceTableData = computed(() => {
          if (!balanceData.value || !balanceData.value.total) return []

          return Object.entries(balanceData.value.total)
                    .filter(([currency, amount]) => amount > 0)
                    .map(([currency, total]) => ({
                              currency,
                              free: balanceData.value.free?.[currency] || 0,
                              used: balanceData.value.used?.[currency] || 0,
                              total
                    }))
})

const formatDateTime = (dateStr) => {
          return new Date(dateStr).toLocaleString('zh-CN')
}

const formatNumber = (value) => {
          return Number(value).toFixed(8)
}

const loadExchangeAccounts = async () => {
          loading.value = true
          try {
                    const response = await api.get('/exchanges/')
                    exchangeAccounts.value = response.data
          } catch (error) {
                    ElMessage.error('加载交易所账户失败')
          } finally {
                    loading.value = false
          }
}

const resetForm = () => {
          Object.assign(accountForm, {
                    exchange_name: 'okex',  // 默认选择OKX
                    api_key: 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',  // 默认测试API Key
                    api_secret: 'CD6A497EEB00AA2DC60B2B0974DD2485',  // 默认测试Secret
                    api_passphrase: 'vf5Y3UeUFiz6xfF!',  // 默认测试Passphrase
                    is_testnet: true  // 默认使用测试网
          })
          if (accountFormRef.value) {
                    accountFormRef.value.clearValidate()
          }
}

const fillTestCredentials = () => {
          Object.assign(accountForm, {
                    exchange_name: 'okex',
                    api_key: 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
                    api_secret: 'CD6A497EEB00AA2DC60B2B0974DD2485',
                    api_passphrase: 'vf5Y3UeUFiz6xfF!',
                    is_testnet: true
          })
          ElMessage.success('已填充OKX测试API密钥')
}

const clearForm = () => {
          Object.assign(accountForm, {
                    exchange_name: '',
                    api_key: '',
                    api_secret: '',
                    api_passphrase: '',
                    is_testnet: true
          })
          if (accountFormRef.value) {
                    accountFormRef.value.clearValidate()
          }
          ElMessage.info('表单已清空')
}

const saveAccount = async () => {
          if (!accountFormRef.value) return

          await accountFormRef.value.validate(async (valid) => {                    if (valid) {
                              saving.value = true

                              try {
                                        await api.post('/exchanges/', accountForm)
                                        ElMessage.success('交易所账户添加成功')
                                        showCreateDialog.value = false
                                        await loadExchangeAccounts()
                              } catch (error) {
                                        ElMessage.error(error.response?.data?.detail || '添加失败')
                              } finally {
                                        saving.value = false
                              }
                    }
          })
}

const testConnection = async (account) => {
          try {
                    ElMessage.info('测试连接中...')
                    await api.get(`/exchanges/accounts/${account.id}/ticker/BTCUSDT`)
                    ElMessage.success('连接测试成功')
          } catch (error) {
                    ElMessage.error('连接测试失败: ' + (error.response?.data?.detail || error.message))
          }
}

const viewBalance = async (account) => {
          showBalanceDialog.value = true
          balanceLoading.value = true
          balanceData.value = null

          try {
                    const response = await api.get(`/exchanges/accounts/${account.id}/balance`)
                    balanceData.value = response.data
          } catch (error) {
                    ElMessage.error('获取余额失败: ' + (error.response?.data?.detail || error.message))
          } finally {
                    balanceLoading.value = false
          }
}

const deleteAccount = async (account) => {
          try {
                    await ElMessageBox.confirm(
                              `确定要删除 ${account.exchange_name.toUpperCase()} 账户吗？`,
                              '删除确认',
                              {
                                        confirmButtonText: '确定',
                                        cancelButtonText: '取消',
                                        type: 'warning',
                              }                    )

                    await api.delete(`/exchanges/accounts/${account.id}`)
                    ElMessage.success('账户删除成功')
                    await loadExchangeAccounts()
          } catch (error) {
                    if (error !== 'cancel') {
                              ElMessage.error('删除失败')
                    }
          }
}

onMounted(() => {
          loadExchangeAccounts()
})
</script>

<style scoped>
.exchanges {
          max-width: 1200px;
          margin: 0 auto;
}

.api-key {
          font-family: monospace;
          color: #606266;
}

.loading-container,
.error-container {
          padding: 20px;
          text-align: center;
}

.dialog-footer {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
}
</style>
