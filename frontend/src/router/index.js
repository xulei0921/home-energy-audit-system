import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/index'
    },
    {
      path: '/index',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '用户登录与注册', requiresAuth: false }
    },
    {
      path: '/devices',
      component: () => import('@/views/DevicesView.vue'),
      meta: { title: '设备管理', requiresAuth: true }
    }
  ],
})

// 路由守卫 - 验证登录状态
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  document.title = to.meta.title || '家庭能耗系统'

  console.log(`是否有效登录:${userStore.isLogin()}`)

  if (to.meta.requiresAuth && !userStore.isLogin()) {
    next('/login')
  } else {
    next()
  }
})

export default router
