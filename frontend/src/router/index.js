import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
          {
                    path: '/login',
                    name: 'Login',
                    component: () => import('@/views/Login.vue')
          },
          {
                    path: '/register',
                    name: 'Register',
                    component: () => import('@/views/Register.vue')
          },
          {
                    path: '/',
                    name: 'Layout',
                    component: () => import('@/components/Layout.vue'),
                    redirect: '/dashboard',
                    meta: { requiresAuth: true },
                    children: [
                              {
                                        path: '/dashboard',
                                        name: 'Dashboard',
                                        component: () => import('@/views/Dashboard.vue'),
                                        meta: { title: '控制台概览' }
                              },
                              {
                                        path: '/strategies',
                                        name: 'Strategies',
                                        component: () => import('@/views/Strategies.vue'),
                                        meta: { title: '策略配置' }
                              },
                              {
                                        path: '/trades',
                                        name: 'Trades',
                                        component: () => import('@/views/Trades.vue'),
                                        meta: { title: '交易记录' }
                              },
                              {
                                        path: '/exchanges',
                                        name: 'Exchanges',
                                        component: () => import('@/views/Exchanges.vue'),
                                        meta: { title: '交易所配置' }
                              }
                    ]
          }
]

const router = createRouter({
          history: createWebHistory(),
          routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
          const authStore = useAuthStore()

          if (to.meta.requiresAuth && !authStore.isAuthenticated) {
                    next('/login')
          } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
                    next('/dashboard')
          } else {
                    next()
          }
})

export default router
