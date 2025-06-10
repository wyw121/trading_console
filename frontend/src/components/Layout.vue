<template>
          <el-container class="layout-container">
                    <el-header class="header">
                              <div class="header-left">
                                        <h1 class="app-title">交易控制台</h1>
                              </div>
                              <div class="header-right">
                                        <el-dropdown @command="handleUserCommand">
                                                  <span class="user-dropdown">
                                                            <el-avatar :size="32" :src="userAvatar" />
                                                            <span class="username">{{ authStore.user?.username }}</span>
                                                            <el-icon>
                                                                      <ArrowDown />
                                                            </el-icon>
                                                  </span>
                                                  <template #dropdown>
                                                            <el-dropdown-menu>
                                                                      <el-dropdown-item
                                                                                command="profile">个人资料</el-dropdown-item>
                                                                      <el-dropdown-item command="logout"
                                                                                divided>退出登录</el-dropdown-item>
                                                            </el-dropdown-menu>
                                                  </template>
                                        </el-dropdown>
                              </div>
                    </el-header>

                    <el-container>
                              <el-aside class="sidebar" width="200px">
                                        <el-menu :default-active="$route.path" class="sidebar-menu" router
                                                  :collapse="false">
                                                  <el-menu-item index="/dashboard">
                                                            <el-icon>
                                                                      <House />
                                                            </el-icon>
                                                            <span>控制台概览</span>
                                                  </el-menu-item>

                                                  <el-menu-item index="/strategies">
                                                            <el-icon>
                                                                      <Setting />
                                                            </el-icon>
                                                            <span>策略配置</span>
                                                  </el-menu-item>

                                                  <el-menu-item index="/trades">
                                                            <el-icon>
                                                                      <List />
                                                            </el-icon>
                                                            <span>交易记录</span>
                                                  </el-menu-item>

                                                  <el-menu-item index="/exchanges">
                                                            <el-icon>
                                                                      <Connection />
                                                            </el-icon>
                                                            <span>交易所配置</span>
                                                  </el-menu-item>
                                        </el-menu>
                              </el-aside>

                              <el-main class="main-content">
                                        <router-view />
                              </el-main>
                    </el-container>
          </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, House, Setting, List, Connection } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userAvatar = computed(() => {
          // Generate avatar based on username
          const username = authStore.user?.username || 'User'
          return `https://ui-avatars.com/api/?name=${username}&background=409eff&color=fff`
})

const handleUserCommand = async (command) => {
          switch (command) {
                    case 'profile':
                              ElMessage.info('个人资料功能开发中...')
                              break
                    case 'logout':
                              try {
                                        await ElMessageBox.confirm(
                                                  '确定要退出登录吗？',
                                                  '退出确认',
                                                  {
                                                            confirmButtonText: '确定',
                                                            cancelButtonText: '取消',
                                                            type: 'warning',
                                                  }
                                        )
                                        authStore.logout()
                                        router.push('/login')
                                        ElMessage.success('已退出登录')
                              } catch {
                                        // User cancelled
                              }
                              break
          }
}
</script>

<style scoped>
.layout-container {
          height: 100vh;
}

.header {
          background-color: #fff;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 20px;
}

.header-left {
          display: flex;
          align-items: center;
}

.app-title {
          font-size: 20px;
          font-weight: 600;
          color: #303133;
          margin: 0;
}

.header-right {
          display: flex;
          align-items: center;
}

.user-dropdown {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 5px;
          border-radius: 4px;
          transition: background-color 0.3s;
}

.user-dropdown:hover {
          background-color: #f5f7fa;
}

.username {
          margin: 0 8px;
          color: #303133;
          font-size: 14px;
}

.sidebar {
          background-color: #fff;
          border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
          border-right: none;
          height: 100%;
}

.main-content {
          background-color: #f5f7fa;
          padding: 20px;
}
</style>
