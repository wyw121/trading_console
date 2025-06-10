<template>
          <div class="register-container">
                    <div class="register-box">
                              <div class="register-header">
                                        <h2>创建账户</h2>
                                        <p>注册新的交易控制台账户</p>
                              </div>

                              <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules"
                                        class="register-form" @submit.prevent="handleRegister">
                                        <el-form-item prop="username">
                                                  <el-input v-model="registerForm.username" placeholder="用户名"
                                                            size="large" prefix-icon="User" />
                                        </el-form-item>

                                        <el-form-item prop="email">
                                                  <el-input v-model="registerForm.email" placeholder="邮箱地址" size="large"
                                                            prefix-icon="Message" />
                                        </el-form-item>

                                        <el-form-item prop="password">
                                                  <el-input v-model="registerForm.password" type="password"
                                                            placeholder="密码" size="large" prefix-icon="Lock"
                                                            show-password />
                                        </el-form-item>

                                        <el-form-item prop="confirmPassword">
                                                  <el-input v-model="registerForm.confirmPassword" type="password"
                                                            placeholder="确认密码" size="large" prefix-icon="Lock"
                                                            show-password @keyup.enter="handleRegister" />
                                        </el-form-item>

                                        <el-form-item>
                                                  <el-button type="primary" size="large" :loading="loading"
                                                            class="register-btn" @click="handleRegister">
                                                            注册
                                                  </el-button>
                                        </el-form-item>

                                        <div class="register-footer">
                                                  <span>已有账户？</span>
                                                  <el-link type="primary" @click="$router.push('/login')">
                                                            立即登录
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

const registerFormRef = ref()
const loading = ref(false)

const registerForm = reactive({
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
          if (value !== registerForm.password) {
                    callback(new Error('两次输入的密码不一致'))
          } else {
                    callback()
          }
}

const registerRules = {
          username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 3, max: 50, message: '用户名长度在3-50位之间', trigger: 'blur' }
          ],
          email: [
                    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
                    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
          ],
          password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
          ],
          confirmPassword: [
                    { required: true, message: '请确认密码', trigger: 'blur' },
                    { validator: validateConfirmPassword, trigger: 'blur' }
          ]
}

const handleRegister = async () => {
          if (!registerFormRef.value) return

          await registerFormRef.value.validate(async (valid) => {
                    if (valid) {
                              loading.value = true

                              try {
                                        const result = await authStore.register(
                                                  registerForm.username,
                                                  registerForm.email,
                                                  registerForm.password
                                        )

                                        if (result.success) {
                                                  ElMessage.success('注册成功，请登录')
                                                  router.push('/login')
                                        } else {
                                                  ElMessage.error(result.message)
                                        }
                              } finally {
                                        loading.value = false
                              }
                    }
          })
}
</script>

<style scoped>
.register-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
          width: 400px;
          padding: 40px;
          background: white;
          border-radius: 10px;
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.register-header {
          text-align: center;
          margin-bottom: 30px;
}

.register-header h2 {
          font-size: 28px;
          color: #303133;
          margin-bottom: 10px;
}

.register-header p {
          color: #909399;
          font-size: 14px;
}

.register-form {
          margin-bottom: 20px;
}

.register-btn {
          width: 100%;
}

.register-footer {
          text-align: center;
          color: #909399;
          font-size: 14px;
}
</style>
