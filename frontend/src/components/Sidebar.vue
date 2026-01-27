<template>
  <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-gray-900 px-6 pb-4">
    <div class="flex h-16 shrink-0 items-center">
      <img class="h-8 w-auto" src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500" alt="s-panel" />
      <span class="ml-4 text-white font-bold text-xl">s-panel</span>
    </div>
    <nav class="flex flex-1 flex-col">
      <ul role="list" class="flex flex-1 flex-col gap-y-7">
        <li>
          <ul role="list" class="-mx-2 space-y-1">
            <li v-for="item in navigation" :key="item.name">
              <router-link :to="item.href" :class="[item.current ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                {{ item.name }}
              </router-link>
            </li>
          </ul>
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
