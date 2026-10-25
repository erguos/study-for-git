import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import UploadView from '../views/UploadView.vue'
import ChatView from '../views/ChatView.vue'
import ChartView from '../views/ChartView.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/', redirect: '/login' },
  { path: '/upload', component: UploadView, meta: { title: '数据管理' } },
  { path: '/chat', component: ChatView, meta: { title: 'Agent 对话' } },
  { path: '/chart', component: ChartView, meta: { title: '图表可视化' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const logged = auth.isLoggedIn
  if (to.path !== '/login' && !logged) return '/login'
  if (to.path === '/login' && logged) return auth.isAdmin ? '/upload' : '/chat'
  if (to.path === '/upload' && logged && !auth.isAdmin) return '/chat'
  return true
})

export default router
