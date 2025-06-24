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
                              </template>                              <el-table :data="exchangeAccounts" style="width: 100%" v-loading="loading">
                                        <el-table-column prop="exchange_name" label="交易所" width="100">
                                                  <template #default="scope">
                                                            <span style="font-weight: 600; text-transform: uppercase;">
                                                                      {{ scope.row.exchange_name }}
                                                            </span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="api_key" label="API Key" width="180">
                                                  <template #default="scope">
                                                            <span class="api-key">{{ scope.row.api_key }}</span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="is_testnet" label="环境" width="80">
                                                  <template #default="scope">
                                                            <el-tag
                                                                      :type="scope.row.is_testnet ? 'warning' : 'success'"
                                                                      size="small">
                                                                      {{ scope.row.is_testnet ? '测试网' : '正式网' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="permissions" label="权限" width="120">
                                                  <template #default="scope">
                                                            <div v-if="scope.row.permissions && scope.row.permissions.length > 0" 
                                                                      class="permissions-tags">
                                                                      <el-tag v-for="permission in scope.row.permissions" 
                                                                                :key="permission"
                                                                                :type="getPermissionTagType(permission)"
                                                                                size="small"
                                                                                style="margin-right: 4px; margin-bottom: 2px;">
                                                                                {{ getPermissionLabel(permission) }}
                                                                      </el-tag>
                                                            </div>
                                                            <span v-else class="text-muted">未设置</span>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="validation_status" label="验证状态" width="100">
                                                  <template #default="scope">
                                                            <el-tag :type="getValidationStatusType(scope.row.validation_status)"
                                                                      size="small">
                                                                      {{ getValidationStatusLabel(scope.row.validation_status) }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="is_active" label="状态" width="80">
                                                  <template #default="scope">
                                                            <el-tag :type="scope.row.is_active ? 'success' : 'danger'"
                                                                      size="small">
                                                                      {{ scope.row.is_active ? '正常' : '禁用' }}
                                                            </el-tag>
                                                  </template>
                                        </el-table-column>
                                        <el-table-column prop="created_at" label="创建时间" width="150">
                                                  <template #default="scope">
                                                            {{ formatDateTime(scope.row.created_at) }}
                                                  </template>
                                        </el-table-column>
                                        <el-table-column label="操作" width="280">
                                                  <template #default="scope">
                                                            <el-button size="small" @click="testConnection(scope.row)">
                                                                      测试连接
                                                            </el-button>
                                                            <el-button size="small" type="info"
                                                                      @click="validatePermissions(scope.row)">
                                                                      验证权限
                                                            </el-button>
                                                            <el-button size="small" type="primary"
                                                                      @click="viewBalance(scope.row)">
                                                                      查看余额
                                                            </el-button>
                                                            <el-dropdown @command="handleAccountAction">
                                                                      <el-button size="small" type="warning">
                                                                                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                                                                      </el-button>
                                                                      <template #dropdown>
                                                                                <el-dropdown-menu>
                                                                                          <el-dropdown-item :command="`edit:${scope.row.id}`">
                                                                                                    编辑配置
                                                                                          </el-dropdown-item>
                                                                                          <el-dropdown-item :command="`permissions:${scope.row.id}`">
                                                                                                    权限管理
                                                                                          </el-dropdown-item>
                                                                                          <el-dropdown-item :command="`ip:${scope.row.id}`">
                                                                                                    IP白名单
                                                                                          </el-dropdown-item>
                                                                                          <el-dropdown-item :command="`delete:${scope.row.id}`" divided>
                                                                                                    删除账户
                                                                                          </el-dropdown-item>
                                                                                </el-dropdown-menu>
                                                                      </template>
                                                            </el-dropdown>
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
                                        </el-form-item>                                        <el-form-item v-if="accountForm.exchange_name === 'okex'" label="Passphrase"
                                                  prop="api_passphrase">
                                                  <el-input v-model="accountForm.api_passphrase"
                                                            placeholder="请输入Passphrase (OKX专用)" type="password"
                                                            show-password />
                                        </el-form-item>

                                        <!-- OKX权限配置 -->
                                        <el-form-item v-if="accountForm.exchange_name === 'okex'" label="API权限">
                                                  <el-checkbox-group v-model="accountForm.permissions">
                                                            <el-checkbox label="read">只读权限</el-checkbox>
                                                            <el-checkbox label="trade">交易权限</el-checkbox>
                                                            <el-checkbox label="withdraw">提币权限</el-checkbox>
                                                  </el-checkbox-group>
                                                  <div class="form-tip">
                                                            <el-text type="info" size="small">
                                                                      建议：选择"只读"和"交易"权限，不建议开启"提币"权限以保证资金安全
                                                            </el-text>
                                                  </div>
                                        </el-form-item>

                                        <!-- IP白名单配置 -->
                                        <el-form-item v-if="accountForm.exchange_name === 'okex'" label="IP白名单">
                                                  <div class="ip-whitelist-container">
                                                            <el-input 
                                                                      v-model="newIpAddress" 
                                                                      placeholder="请输入IP地址 (如: 192.168.1.1)"
                                                                      style="margin-bottom: 10px;"
                                                                      @keyup.enter="addIpAddress">
                                                                      <template #append>
                                                                                <el-button @click="addIpAddress">添加</el-button>
                                                                      </template>
                                                            </el-input>
                                                            <div v-if="accountForm.ip_whitelist && accountForm.ip_whitelist.length > 0">
                                                                      <el-tag 
                                                                                v-for="(ip, index) in accountForm.ip_whitelist" 
                                                                                :key="index"
                                                                                closable
                                                                                @close="removeIpAddress(index)"
                                                                                style="margin-right: 8px; margin-bottom: 4px;">
                                                                                {{ ip }}
                                                                      </el-tag>
                                                            </div>
                                                            <div v-else class="no-ip-placeholder">
                                                                      <el-text type="info" size="small">未设置IP白名单 (不推荐)</el-text>
                                                            </div>
                                                  </div>
                                                  <div class="form-tip">
                                                            <el-text type="warning" size="small">
                                                                      建议设置IP白名单以提高安全性。留空表示允许所有IP访问。
                                                            </el-text>
                                                  </div>
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
                              </div>                              <div v-else class="error-container">
                                        <el-result icon="error" title="获取余额失败" />
                              </div>
                    </el-dialog>

                    <!-- 权限管理对话框 -->
                    <el-dialog title="权限管理" v-model="showPermissionsDialog" width="500px">
                              <div v-if="currentAccount">
                                        <el-alert title="当前权限状态" type="info" :closable="false" style="margin-bottom: 20px">
                                                  <div class="permission-status">
                                                            <p><strong>账户:</strong> {{ currentAccount.exchange_name.toUpperCase() }}</p>
                                                            <p><strong>验证状态:</strong> 
                                                                      <el-tag :type="getValidationStatusType(currentAccount.validation_status)">
                                                                                {{ getValidationStatusLabel(currentAccount.validation_status) }}
                                                                      </el-tag>
                                                            </p>
                                                            <p v-if="currentAccount.validation_error"><strong>错误信息:</strong> {{ currentAccount.validation_error }}</p>
                                                            <p v-if="currentAccount.last_validation"><strong>上次验证:</strong> {{ formatDateTime(currentAccount.last_validation) }}</p>
                                                  </div>
                                        </el-alert>

                                        <el-form label-width="100px">
                                                  <el-form-item label="API权限">
                                                            <el-checkbox-group v-model="permissionForm.permissions">
                                                                      <el-checkbox label="read">只读权限</el-checkbox>
                                                                      <el-checkbox label="trade">交易权限</el-checkbox>
                                                                      <el-checkbox label="withdraw">提币权限</el-checkbox>
                                                            </el-checkbox-group>
                                                  </el-form-item>
                                        </el-form>

                                        <div class="permission-actions">
                                                  <el-button type="primary" @click="updatePermissions" :loading="permissionSaving">
                                                            保存权限配置
                                                  </el-button>
                                                  <el-button @click="validateAccountPermissions" :loading="permissionValidating">
                                                            验证权限
                                                  </el-button>
                                        </div>
                              </div>
                    </el-dialog>

                    <!-- IP白名单管理对话框 -->
                    <el-dialog title="IP白名单管理" v-model="showIpWhitelistDialog" width="600px">
                              <div v-if="currentAccount">
                                        <el-alert title="当前IP状态" type="info" :closable="false" style="margin-bottom: 20px">
                                                  <div class="ip-status">
                                                            <p><strong>当前IP:</strong> {{ currentIpAddress || '获取中...' }}</p>
                                                            <p><strong>白名单状态:</strong> 
                                                                      <el-tag :type="isCurrentIpInWhitelist ? 'success' : 'warning'">
                                                                                {{ isCurrentIpInWhitelist ? '已在白名单' : '不在白名单' }}
                                                                      </el-tag>
                                                            </p>
                                                  </div>
                                        </el-alert>

                                        <div class="ip-whitelist-manager">
                                                  <el-form label-width="100px">
                                                            <el-form-item label="添加IP">
                                                                      <el-input 
                                                                                v-model="newIpForWhitelist" 
                                                                                placeholder="请输入IP地址"
                                                                                @keyup.enter="addIpToWhitelist">
                                                                                <template #append>
                                                                                          <el-button @click="addIpToWhitelist">添加</el-button>
                                                                                </template>
                                                                      </el-input>
                                                            </el-form-item>
                                                  </el-form>

                                                  <div class="ip-list">
                                                            <h4>当前白名单IP:</h4>
                                                            <div v-if="ipWhitelistForm.ip_whitelist && ipWhitelistForm.ip_whitelist.length > 0">
                                                                      <el-tag 
                                                                                v-for="(ip, index) in ipWhitelistForm.ip_whitelist" 
                                                                                :key="index"
                                                                                closable
                                                                                @close="removeIpFromWhitelist(index)"
                                                                                style="margin-right: 8px; margin-bottom: 8px;">
                                                                                {{ ip }}
                                                                      </el-tag>
                                                            </div>
                                                            <div v-else class="no-ip-notice">
                                                                      <el-empty description="未设置IP白名单" :image-size="60" />
                                                                      <el-text type="warning">注意: 未设置IP白名单可能存在安全风险</el-text>
                                                            </div>
                                                  </div>

                                                  <div class="ip-actions">
                                                            <el-button type="primary" @click="updateIpWhitelist" :loading="ipWhitelistSaving">
                                                                      保存白名单
                                                            </el-button>
                                                            <el-button @click="getCurrentIp">
                                                                      获取当前IP
                                                            </el-button>
                                                            <el-button type="success" @click="addCurrentIpToWhitelist">
                                                                      添加当前IP到白名单
                                                            </el-button>
                                                  </div>
                                        </div>
                              </div>
                    </el-dialog>
          </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import api from '@/utils/api'

const exchangeAccounts = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showBalanceDialog = ref(false)
const showPermissionsDialog = ref(false)
const showIpWhitelistDialog = ref(false)
const balanceLoading = ref(false)
const balanceData = ref(null)
const accountFormRef = ref()
const currentAccount = ref(null)
const permissionSaving = ref(false)
const permissionValidating = ref(false)
const ipWhitelistSaving = ref(false)
const newIpAddress = ref('')
const newIpForWhitelist = ref('')
const currentIpAddress = ref('')

const accountForm = reactive({
          exchange_name: 'okex',  // 默认选择OKX
          api_key: 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',  // 默认测试API Key
          api_secret: 'CD6A497EEB00AA2DC60B2B0974DD2485',  // 默认测试Secret
          api_passphrase: 'vf5Y3UeUFiz6xfF!',  // 默认测试Passphrase
          is_testnet: true,  // 默认使用测试网
          permissions: ['read', 'trade'],  // 默认权限
          ip_whitelist: []  // IP白名单
})

const permissionForm = reactive({
          permissions: []
})

const ipWhitelistForm = reactive({
          ip_whitelist: []
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

const isCurrentIpInWhitelist = computed(() => {
          if (!currentIpAddress.value || !ipWhitelistForm.ip_whitelist) return false
          return ipWhitelistForm.ip_whitelist.includes(currentIpAddress.value)
})

const formatDateTime = (dateStr) => {
          return new Date(dateStr).toLocaleString('zh-CN')
}

const formatNumber = (value) => {
          return Number(value).toFixed(8)
}

// 权限相关辅助方法
const getPermissionLabel = (permission) => {
          const labels = {
                    'read': '只读',
                    'trade': '交易',
                    'withdraw': '提币'
          }
          return labels[permission] || permission
}

const getPermissionTagType = (permission) => {
          const types = {
                    'read': 'info',
                    'trade': 'success',
                    'withdraw': 'danger'
          }
          return types[permission] || 'info'
}

const getValidationStatusLabel = (status) => {
          const labels = {
                    'pending': '待验证',
                    'valid': '有效',
                    'invalid': '无效',
                    'error': '错误'
          }
          return labels[status] || '未知'
}

const getValidationStatusType = (status) => {
          const types = {
                    'pending': 'warning',
                    'valid': 'success',
                    'invalid': 'danger',
                    'error': 'danger'
          }
          return types[status] || 'info'
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
                    is_testnet: true,  // 默认使用测试网
                    permissions: ['read', 'trade'],  // 默认权限
                    ip_whitelist: []  // IP白名单
          })
          if (accountFormRef.value) {
                    accountFormRef.value.clearValidate()
          }
}

// IP地址管理方法
const addIpAddress = () => {
          if (!newIpAddress.value.trim()) {
                    ElMessage.warning('请输入有效的IP地址')
                    return
          }
          
          if (!validateIpAddress(newIpAddress.value.trim())) {
                    ElMessage.error('IP地址格式不正确')
                    return
          }
          
          if (!accountForm.ip_whitelist) {
                    accountForm.ip_whitelist = []
          }
          
          if (accountForm.ip_whitelist.includes(newIpAddress.value.trim())) {
                    ElMessage.warning('IP地址已存在')
                    return
          }
          
          accountForm.ip_whitelist.push(newIpAddress.value.trim())
          newIpAddress.value = ''
          ElMessage.success('IP地址添加成功')
}

const removeIpAddress = (index) => {
          accountForm.ip_whitelist.splice(index, 1)
          ElMessage.success('IP地址删除成功')
}

const validateIpAddress = (ip) => {
          const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
          return ipRegex.test(ip)
}

const fillTestCredentials = () => {
          Object.assign(accountForm, {
                    exchange_name: 'okex',
                    api_key: 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
                    api_secret: 'CD6A497EEB00AA2DC60B2B0974DD2485',
                    api_passphrase: 'vf5Y3UeUFiz6xfF!',
                    is_testnet: true,
                    permissions: ['read', 'trade'],
                    ip_whitelist: []
          })
          ElMessage.success('已填充OKX测试API密钥')
}

const clearForm = () => {
          Object.assign(accountForm, {
                    exchange_name: '',
                    api_key: '',
                    api_secret: '',
                    api_passphrase: '',
                    is_testnet: true,
                    permissions: [],
                    ip_whitelist: []
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

// 权限验证方法
const validatePermissions = async (account) => {
          try {
                    ElMessage.info('验证权限中...')
                    const response = await api.post('/exchanges/validate-permissions', {
                              account_id: account.id
                    })
                    
                    if (response.data.valid) {
                              ElMessage.success('权限验证成功')
                    } else {
                              ElMessage.warning(`权限验证失败: ${response.data.message}`)
                    }
                    
                    // 刷新账户列表以获取最新状态
                    await loadExchangeAccounts()
          } catch (error) {
                    ElMessage.error('权限验证失败: ' + (error.response?.data?.detail || error.message))
          }
}

// 处理账户操作下拉菜单
const handleAccountAction = async (command) => {
          const [action, accountId] = command.split(':')
          const account = exchangeAccounts.value.find(acc => acc.id === parseInt(accountId))
          
          if (!account) return
          
          switch (action) {
                    case 'edit':
                              // TODO: 实现编辑功能
                              ElMessage.info('编辑功能开发中...')
                              break
                    case 'permissions':
                              openPermissionsDialog(account)
                              break
                    case 'ip':
                              openIpWhitelistDialog(account)
                              break
                    case 'delete':
                              await deleteAccount(account)
                              break
          }
}

// 打开权限管理对话框
const openPermissionsDialog = (account) => {
          currentAccount.value = account
          permissionForm.permissions = [...(account.permissions || [])]
          showPermissionsDialog.value = true
}

// 打开IP白名单管理对话框
const openIpWhitelistDialog = async (account) => {
          currentAccount.value = account
          ipWhitelistForm.ip_whitelist = [...(account.ip_whitelist || [])]
          showIpWhitelistDialog.value = true
          
          // 获取当前IP
          await getCurrentIp()
}

// 更新权限
const updatePermissions = async () => {
          if (!currentAccount.value) return
          
          permissionSaving.value = true
          try {
                    await api.put(`/api/exchanges/accounts/${currentAccount.value.id}/permissions`, {
                              permissions: permissionForm.permissions
                    })
                    ElMessage.success('权限更新成功')
                    showPermissionsDialog.value = false
                    await loadExchangeAccounts()
          } catch (error) {
                    ElMessage.error('权限更新失败: ' + (error.response?.data?.detail || error.message))
          } finally {
                    permissionSaving.value = false
          }
}

// 验证账户权限
const validateAccountPermissions = async () => {
          if (!currentAccount.value) return
          
          permissionValidating.value = true
          try {
                    const response = await api.post('/api/exchanges/validate-permissions', {
                              account_id: currentAccount.value.id
                    })
                    
                    if (response.data.success) {
                              ElMessage.success('权限验证成功')
                              currentAccount.value.validation_status = 'valid'
                    } else {
                              ElMessage.warning(`权限验证失败: ${response.data.error_message}`)
                              currentAccount.value.validation_status = 'invalid'
                              currentAccount.value.validation_error = response.data.error_message
                    }
                    
                    await loadExchangeAccounts()
          } catch (error) {
                    ElMessage.error('权限验证失败: ' + (error.response?.data?.detail || error.message))
          } finally {
                    permissionValidating.value = false
          }
}

// IP白名单相关方法
const addIpToWhitelist = () => {
          if (!newIpForWhitelist.value.trim()) {
                    ElMessage.warning('请输入有效的IP地址')
                    return
          }
          
          if (!validateIpAddress(newIpForWhitelist.value.trim())) {
                    ElMessage.error('IP地址格式不正确')
                    return
          }
          
          if (!ipWhitelistForm.ip_whitelist) {
                    ipWhitelistForm.ip_whitelist = []
          }
          
          if (ipWhitelistForm.ip_whitelist.includes(newIpForWhitelist.value.trim())) {
                    ElMessage.warning('IP地址已存在')
                    return
          }
          
          ipWhitelistForm.ip_whitelist.push(newIpForWhitelist.value.trim())
          newIpForWhitelist.value = ''
          ElMessage.success('IP地址添加成功')
}

const removeIpFromWhitelist = (index) => {
          ipWhitelistForm.ip_whitelist.splice(index, 1)
          ElMessage.success('IP地址删除成功')
}

const updateIpWhitelist = async () => {
          if (!currentAccount.value) return
          
          ipWhitelistSaving.value = true
          try {
                    await api.put(`/api/exchanges/accounts/${currentAccount.value.id}/ip-whitelist`, {
                              ip_whitelist: ipWhitelistForm.ip_whitelist
                    })
                    ElMessage.success('IP白名单更新成功')
                    showIpWhitelistDialog.value = false
                    await loadExchangeAccounts()
          } catch (error) {
                    ElMessage.error('IP白名单更新失败: ' + (error.response?.data?.detail || error.message))
          } finally {
                    ipWhitelistSaving.value = false
          }
}

const getCurrentIp = async () => {
          try {
                    const response = await api.get('/api/exchanges/current-ip')
                    currentIpAddress.value = response.data.ip
                    ElMessage.success(`当前IP: ${currentIpAddress.value}`)
          } catch (error) {
                    ElMessage.error('获取当前IP失败: ' + (error.response?.data?.detail || error.message))
          }
}

const addCurrentIpToWhitelist = async () => {
          if (!currentIpAddress.value) {
                    await getCurrentIp()
          }
          
          if (currentIpAddress.value) {
                    if (!ipWhitelistForm.ip_whitelist) {
                              ipWhitelistForm.ip_whitelist = []
                    }
                    
                    if (ipWhitelistForm.ip_whitelist.includes(currentIpAddress.value)) {
                              ElMessage.warning('当前IP已在白名单中')
                              return
                    }
                    
                    ipWhitelistForm.ip_whitelist.push(currentIpAddress.value)
                    ElMessage.success('当前IP已添加到白名单')
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

.permissions-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
}

.permission-status,
.ip-status {
          line-height: 1.6;
}

.permission-actions,
.ip-actions {
          display: flex;
          gap: 10px;
          margin-top: 20px;
          flex-wrap: wrap;
}

.ip-whitelist-container {
          width: 100%;
}

.ip-whitelist-manager {
          margin-top: 20px;
}

.ip-list {
          margin-top: 20px;
}

.ip-list h4 {
          margin-bottom: 10px;
          color: #409eff;
}

.no-ip-placeholder,
.no-ip-notice {
          text-align: center;
          padding: 20px;
          color: #909399;
}

.form-tip {
          margin-top: 8px;
          line-height: 1.4;
}

.text-muted {
          color: #909399;
          font-style: italic;
}

.flex-between {
          display: flex;
          justify-content: space-between;
          align-items: center;
}
</style>
