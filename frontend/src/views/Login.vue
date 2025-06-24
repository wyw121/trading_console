<template>
          <div class="login-container">
                    <div class="login-box">
                              <div class="login-header">
                                        <h2>交易控制台</h2>
                                        <p>登录您的账户</p>
                              </div>

                              <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form"
                                        @submit.prevent="handleLogin">
                                        <el-form-item prop="username">
                                                  <el-input v-model="loginForm.username" placeholder="用户名" size="large"
                                                            prefix-icon="User" />
                                        </el-form-item>

                                        <el-form-item prop="password">
                                                  <el-input v-model="loginForm.password" type="password"
                                                            placeholder="密码" size="large" prefix-icon="Lock"
                                                            show-password @keyup.enter="handleLogin" />
                                        </el-form-item>

                                        <el-form-item>
                                                  <el-button type="primary" size="large" :loading="loading"
                                                            class="login-btn" @click="handleLogin">
                                                            登录
                                                  </el-button>
                                        </el-form-item>

                                        <div class="login-footer">
                                                  <span>还没有账户？</span>
                                                  <el-link type="primary" @click="$router.push('/register')">
                                                            立即注册
                                                  </el-link>
                                        </div>
                              </el-form>
                    </div>
          </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
          username: '',
          password: ''
})

const loginRules = {
          username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' }
          ],
          password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
          ]
}

const handleLogin = async () => {
          console.log('🔥 handleLogin被调用')
          console.log('表单引用:', loginFormRef.value)
          console.log('登录数据:', loginForm)
          
          if (!loginFormRef.value) {
                    console.error('❌ 表单引用为空')
                    return
          }

          await loginFormRef.value.validate(async (valid) => {
                    console.log('✅ 表单验证结果:', valid)
                    if (valid) {
                              loading.value = true
                              console.log('🚀 开始登录请求...')

                              try {
                                        const result = await authStore.login(loginForm.username, loginForm.password)
                                        console.log('📥 登录结果:', result)

                                        if (result.success) {
                                                  ElMessage.success('登录成功')
                                                  console.log('✅ 登录成功，准备跳转')
                                                  router.push('/dashboard')
                                        } else {
                                                  console.error('❌ 登录失败:', result.message)
                                                  ElMessage.error(result.message)
                                        }
                              } catch (error) {
                                        console.error('💥 登录异常:', error)
                                        ElMessage.error('登录请求失败')
                              } finally {
                                        loading.value = false
                                        console.log('🏁 登录流程结束')
                              }
                    } else {
                              console.warn('⚠️ 表单验证失败')
                    }
          })
}
</script>

<style scoped>
.login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
          width: 400px;
          padding: 40px;
          background: white;
          border-radius: 10px;
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.login-header {
          text-align: center;
          margin-bottom: 30px;
}

.login-header h2 {
          font-size: 28px;
          color: #303133;
          margin-bottom: 10px;
}

.login-header p {
          color: #909399;
          font-size: 14px;
}

.login-form {
          margin-bottom: 20px;
}

.login-btn {
          width: 100%;
}

.login-footer {
          text-align: center;
          color: #909399;
          font-size: 14px;
}
</style>
