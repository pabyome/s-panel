import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Websites from '../views/Websites.vue'
import Security from '../views/Security.vue'
import Supervisor from '../views/Supervisor.vue'
import SupervisorDetail from '../views/SupervisorDetail.vue'
import Deployments from '../views/Deployments.vue'
import Redis from '../views/Redis.vue'
import CronJobs from '../views/CronJobs.vue'

// Placeholder for Dashboard if not created yet (User summary says "Implement Dashboard... [x]" but I didn't see the file creation in this session history?
// Wait, I see "Implement Dashboard with Real-time Monitor Data" was checked in task.md.
// Let's assume Dashboard.vue exists or I'll create a placeholder.
// Actually, checking previous history, "Implement Dashboard... [x]" might have been marked but I don't see the file "Dashboard.vue" created in THIS session.
// I will create a simple Dashboard placeholder if it's missing to avoid import errors.

const routes = [
  { path: '/', component: Dashboard },
  { path: '/websites', component: Websites },
  { path: '/security', component: Security },
  { path: '/supervisor', component: Supervisor },
  { path: '/supervisor/:name', component: SupervisorDetail },
  { path: '/deployments', component: Deployments },
  { path: '/redis', component: Redis },
  { path: '/cron', component: CronJobs },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
