<template>
  <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-slate-900 px-6 pb-4 shadow-xl ring-1 ring-white/5">
    <!-- Logo -->
    <div class="flex h-14 shrink-0 items-center border-b border-slate-800">
      <div class="flex items-center gap-x-3">
          <div class="h-8 w-8 rounded-lg bg-indigo-600 shadow-lg shadow-indigo-500/30 flex items-center justify-center">
             <span class="text-white font-bold text-lg">S</span>
          </div>
          <span class="text-white font-bold text-lg tracking-wide">Panel</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex flex-1 flex-col mt-2">
      <ul role="list" class="flex flex-1 flex-col gap-y-4">
        <li>
          <ul role="list" class="-mx-2 space-y-1">
            <li v-for="item in navigation" :key="item.name">
              <router-link
                :to="item.href"
                @click="$emit('navigate')"
                :class="[
                    item.current
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800',
                    'group flex gap-x-3 rounded-lg p-2 text-sm leading-6 font-medium transition-all duration-200'
                ]"
              >
                <component
                  :is="item.icon"
                  :class="[
                    item.current ? 'text-white' : 'text-slate-500 group-hover:text-white',
                    'h-5 w-5 shrink-0 transition-colors'
                  ]"
                  aria-hidden="true"
                />
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Bottom Section -->
        <li class="mt-auto">
          <router-link to="/settings" @click="$emit('navigate')" class="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
            <Cog6ToothIcon class="h-5 w-5 shrink-0 text-slate-500 group-hover:text-white" aria-hidden="true" />
            Settings
          </router-link>
          <div class="mt-4 border-t border-slate-800 pt-4 flex items-center gap-x-3">
              <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-[10px] text-white font-bold shadow-sm">
                  {{ userInitials }}
              </div>
              <div class="flex flex-col">
                  <span class="text-sm font-medium text-white leading-tight">{{ displayName }}</span>
                  <span class="text-[10px] text-slate-500 leading-tight">{{ userRole }}</span>
              </div>
          </div>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import {
  HomeIcon,
  ServerIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  CloudArrowUpIcon,
  CircleStackIcon,
  ClockIcon,
  Cog6ToothIcon,
  ArchiveBoxIcon,
  DocumentTextIcon,
  TableCellsIcon,
  ChartBarIcon,
  UsersIcon
} from '@heroicons/vue/24/outline'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineEmits(['navigate'])

const route = useRoute()
const authStore = useAuthStore()

const userInitials = computed(() => {
  if (!authStore.user?.username) return 'AD'
  return authStore.user.username.substring(0, 2).toUpperCase()
})

const displayName = computed(() => {
  return authStore.user?.username || 'Admin User'
})

const userRole = computed(() => {
  if (!authStore.user?.role) return 'User'
  return authStore.user.role === 'admin' ? 'System Administrator' : 'User'
})

const navigation = computed(() => [
  { name: 'Dashboard', href: '/', icon: HomeIcon, current: route.path === '/' },
  { name: 'Websites', href: '/websites', icon: ServerIcon, current: route.path.startsWith('/websites') },
  { name: 'Security', href: '/security', icon: ShieldCheckIcon, current: route.path.startsWith('/security') },
  { name: 'Supervisor', href: '/supervisor', icon: CpuChipIcon, current: route.path.startsWith('/supervisor') },
  { name: 'Deployments', href: '/deployments', icon: CloudArrowUpIcon, current: route.path.startsWith('/deployments') },
  { name: 'Redis', href: '/redis', icon: CircleStackIcon, current: route.path.startsWith('/redis') },
  { name: 'Databases', href: '/databases', icon: TableCellsIcon, current: route.path.startsWith('/databases') },
  { name: 'Cron Jobs', href: '/cron', icon: ClockIcon, current: route.path.startsWith('/cron') },
  { name: 'Backups', href: '/backups', icon: ArchiveBoxIcon, current: route.path.startsWith('/backups') },
  { name: 'Monitor', href: '/monitor', icon: ChartBarIcon, current: route.path.startsWith('/monitor') },
  { name: 'Logs', href: '/logs', icon: DocumentTextIcon, current: route.path.startsWith('/logs') },
  { name: 'Users', href: '/users', icon: UsersIcon, current: route.path.startsWith('/users') },
])
</script>
