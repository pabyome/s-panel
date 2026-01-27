<template>
  <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-gray-900 px-6 pb-4 shadow-xl ring-1 ring-white/10">
    <!-- Logo -->
    <div class="flex h-16 shrink-0 items-center border-b border-gray-800">
      <div class="flex items-center gap-x-3">
          <div class="h-8 w-8 rounded-lg bg-indigo-500 flex items-center justify-center">
             <span class="text-white font-bold text-lg">S</span>
          </div>
          <span class="text-white font-bold text-lg tracking-wide">Panel</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex flex-1 flex-col">
      <ul role="list" class="flex flex-1 flex-col gap-y-7">
        <li>
          <ul role="list" class="-mx-2 space-y-1">
            <li v-for="item in navigation" :key="item.name">
              <router-link 
                :to="item.href" 
                :class="[
                    item.current 
                    ? 'bg-indigo-600 text-white shadow-md' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-800', 
                    'group flex gap-x-3 rounded-lg p-2.5 text-sm leading-6 font-semibold transition-all duration-200'
                ]"
              >
                <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </li>
        
        <!-- Bottom Section -->
        <li class="mt-auto">
          <a href="#" class="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-gray-400 hover:bg-gray-800 hover:text-white">
            <Cog6ToothIcon class="h-6 w-6 shrink-0" aria-hidden="true" />
            Settings
          </a>
          <div class="mt-4 border-t border-gray-800 pt-4 flex items-center gap-x-3">
              <div class="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center text-xs text-white">
                  Admin
              </div>
              <div class="flex flex-col">
                  <span class="text-sm font-medium text-white">Administrator</span>
                  <span class="text-xs text-gray-500">View Profile</span>
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
  Cog6ToothIcon 
} from '@heroicons/vue/24/outline'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navigation = computed(() => [
  { name: 'Dashboard', href: '/', icon: HomeIcon, current: route.path === '/' },
  { name: 'Websites', href: '/websites', icon: ServerIcon, current: route.path.startsWith('/websites') },
  { name: 'Security', href: '/security', icon: ShieldCheckIcon, current: route.path.startsWith('/security') },
  { name: 'Supervisor', href: '/supervisor', icon: CpuChipIcon, current: route.path.startsWith('/supervisor') },
  { name: 'Deployments', href: '/deployments', icon: CloudArrowUpIcon, current: route.path.startsWith('/deployments') },
  { name: 'Redis', href: '/redis', icon: CircleStackIcon, current: route.path.startsWith('/redis') },
  { name: 'Cron Jobs', href: '/cron', icon: ClockIcon, current: route.path.startsWith('/cron') },
])
</script>