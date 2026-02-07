import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Layout from '../layout/Layout.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: Dashboard },
      {
        path: 'docker',
        name: 'docker',
        component: () => import('../views/DockerLayout.vue'),
        children: [
            { path: '', redirect: '/docker/overview' },
            { path: 'overview', name: 'docker-overview', component: () => import('../views/docker/Overview.vue') },
            { path: 'containers', name: 'docker-containers', component: () => import('../views/docker/Containers.vue') },
            { path: 'swarm', name: 'docker-swarm', component: () => import('../views/docker/Swarm.vue') },
        ]
      },
      { path: 'containers', redirect: '/docker/containers' },
      { path: 'websites', name: 'websites', component: () => import('../views/Websites.vue') },
      { path: 'security', name: 'security', component: () => import('../views/Security.vue') },
      { path: 'supervisor', name: 'supervisor', component: () => import('../views/Supervisor.vue') },
      { path: 'supervisor/:name', name: 'supervisor-detail', component: () => import('../views/SupervisorDetail.vue') },
      { path: 'deployments', name: 'deployments', component: () => import('../views/Deployments.vue') },
      { path: 'redis', name: 'redis', component: () => import('../views/Redis.vue') },
      { path: 'cron', name: 'cron', component: () => import('../views/CronJobs.vue') },
      { path: 'users', name: 'users', component: () => import('../views/Users.vue') },
      { path: 'backups', name: 'backups', component: () => import('../views/Backups.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/Settings.vue') },
      { path: 'logs', name: 'logs', component: () => import('../views/Logs.vue') },
      { path: 'files', name: 'files', component: () => import('../views/FileManager.vue') },
      { path: 'databases', name: 'databases', component: () => import('../views/Databases.vue') },
      { path: 'monitor', name: 'monitor', component: () => import('../views/Monitor.vue') },
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
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
