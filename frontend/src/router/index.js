import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Layout from '../layout/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Websites from '../views/Websites.vue'
import Security from '../views/Security.vue'
import Supervisor from '../views/Supervisor.vue'
import SupervisorDetail from '../views/SupervisorDetail.vue'
import Deployments from '../views/Deployments.vue'
import Redis from '../views/Redis.vue'
import CronJobs from '../views/CronJobs.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: Dashboard },
      { path: 'websites', name: 'websites', component: Websites },
      { path: 'security', name: 'security', component: Security },
      { path: 'supervisor', name: 'supervisor', component: Supervisor },
      { path: 'supervisor/:name', name: 'supervisor-detail', component: SupervisorDetail },
      { path: 'deployments', name: 'deployments', component: Deployments },
      { path: 'redis', name: 'redis', component: Redis },
      { path: 'cron', name: 'cron', component: CronJobs },
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next({ name: 'login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router