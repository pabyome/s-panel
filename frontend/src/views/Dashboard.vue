<template>
  <div class="space-y-6 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-100 pb-4">
      <div>
        <h2 class="text-xl font-bold tracking-tight text-gray-900">System Overview</h2>
        <p class="text-xs text-gray-500">Real-time monitoring.</p>
      </div>
      <div class="flex items-center gap-3">
         <span class="inline-flex items-center gap-x-1.5 rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
            Online
         </span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div v-if="stats" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <!-- CPU Card -->
      <div class="relative overflow-hidden rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <dt class="text-xs font-semibold leading-6 text-gray-500 uppercase tracking-wider">CPU Load</dt>
                <dd class="mt-1 text-sm text-gray-600">
                    <div class="flex items-baseline gap-2">
                         <span class="text-2xl font-bold text-slate-900 tracking-tight">{{ stats.cpu.count }}</span>
                         <span class="text-xs font-medium text-gray-500">Cores</span>
                    </div>
                </dd>
            </div>
            <CircularGauge :value="stats.cpu.percent" label="%" :size="70" />
        </div>
      </div>

       <!-- RAM Card -->
      <div class="relative overflow-hidden rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <dt class="text-xs font-semibold leading-6 text-gray-500 uppercase tracking-wider">Memory</dt>
                <dd class="mt-1 text-sm text-gray-600">
                     <div class="text-2xl font-bold text-slate-900 tracking-tight">{{ formatBytes(stats.memory.used) }}</div>
                     <div class="text-[10px] font-medium text-gray-400 mt-1">/ {{ formatBytes(stats.memory.total) }}</div>
                </dd>
            </div>
            <CircularGauge :value="stats.memory.percent" label="%" :size="70" />
        </div>
      </div>

      <!-- Disk Card -->
      <div class="relative overflow-hidden rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md">
         <div class="flex items-center justify-between">
            <div>
                <dt class="text-xs font-semibold leading-6 text-gray-500 uppercase tracking-wider">Storage</dt>
                <dd class="mt-1 text-sm text-gray-600">
                     <div class="text-2xl font-bold text-slate-900 tracking-tight">{{ formatBytes(stats.disk.used) }}</div>
                     <div class="text-[10px] font-medium text-gray-400 mt-1">/ {{ formatBytes(stats.disk.total) }}</div>
                </dd>
            </div>
            <CircularGauge :value="stats.disk.percent" label="%" :size="70" />
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-else class="flex h-48 items-center justify-center rounded-xl bg-white border border-dashed border-gray-300 shadow-sm">
        <div class="text-center">
            <svg class="mx-auto h-8 w-8 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <h3 class="mt-2 text-xs font-semibold text-gray-900">Connecting...</h3>
        </div>
    </div>

    <!-- Lower Section Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Quick Actions (1/3) -->
        <div class="flex flex-col gap-y-3">
             <h3 class="text-sm font-semibold leading-6 text-gray-900">Quick Actions</h3>
             <div class="grid grid-cols-2 gap-3">
                <router-link to="/websites" class="flex flex-col items-center justify-center rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-indigo-500 hover:bg-indigo-50/50 group text-center">
                    <span class="mb-2 rounded-md bg-indigo-50 p-2 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
                    </span>
                    <span class="text-xs font-medium text-gray-900">New Site</span>
                </router-link>

                 <router-link to="/supervisor" class="flex flex-col items-center justify-center rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-pink-500 hover:bg-pink-50/50 group text-center">
                    <span class="mb-2 rounded-md bg-pink-50 p-2 text-pink-600 group-hover:bg-pink-600 group-hover:text-white transition-colors">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" /></svg>
                    </span>
                    <span class="text-xs font-medium text-gray-900">Processes</span>
                </router-link>
                
                 <router-link to="/security" class="flex flex-col items-center justify-center rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-blue-500 hover:bg-blue-50/50 group text-center">
                    <span class="mb-2 rounded-md bg-blue-50 p-2 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" /></svg>
                    </span>
                    <span class="text-xs font-medium text-gray-900">Firewall</span>
                </router-link>

                 <router-link to="/cron" class="flex flex-col items-center justify-center rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-amber-500 hover:bg-amber-50/50 group text-center">
                    <span class="mb-2 rounded-md bg-amber-50 p-2 text-amber-600 group-hover:bg-amber-600 group-hover:text-white transition-colors">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </span>
                    <span class="text-xs font-medium text-gray-900">Cron Jobs</span>
                </router-link>
            </div>
        </div>

        <!-- System Info (2/3) -->
         <div class="lg:col-span-2 flex flex-col gap-y-3">
            <h3 class="text-sm font-semibold leading-6 text-gray-900">System Status</h3>
            <div class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5 h-full">
                <div class="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-gray-100 h-full">
                    <!-- Left Side Info -->
                    <div class="p-6 space-y-4">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-gray-500">Load Average</span>
                            <span class="text-xs font-mono font-bold text-gray-700 bg-gray-50 px-2 py-1 rounded" v-if="stats && stats.load_avg">
                                {{ stats.load_avg['1min'] }} / {{ stats.load_avg['5min'] }} / {{ stats.load_avg['15min'] }}
                            </span>
                             <span class="text-xs text-gray-400" v-else>...</span>
                        </div>
                         <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-gray-500">Uptime</span>
                            <span class="text-xs text-gray-900">24 days, 3 hours</span> <!-- Placeholder -->
                        </div>
                    </div>
                    
                    <!-- Right Side Info -->
                     <div class="p-6 space-y-4">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-gray-500">OS</span>
                            <span class="text-xs text-gray-900 flex items-center gap-1.5">
                                <span class="h-1.5 w-1.5 rounded-full bg-slate-400"></span>
                                Ubuntu Linux
                            </span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium text-gray-500">Panel Version</span>
                            <span class="text-xs text-gray-900 font-mono">v0.1.0</span>
                        </div>
                     </div>
                </div>
             </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CircularGauge from '../components/CircularGauge.vue'
import { useAuthStore } from '../stores/auth'

const stats = ref(null)
const authStore = useAuthStore()
let socket = null
let reconnectTimer = null

const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  const port = window.location.port ? `:${window.location.port}` : ''
  const wsUrl = `${protocol}//${host}${port}/api/v1/monitor/ws`

  console.log('Connecting to WebSocket:', wsUrl)

  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log('WebSocket Connected')
  }

  socket.onmessage = (event) => {
    try {
      stats.value = JSON.parse(event.data)
    } catch (e) {
      console.error('Error parsing WS data:', e)
    }
  }

  socket.onclose = (event) => {
    console.log('WebSocket Disconnected', event.reason)
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }

  socket.onerror = (error) => {
    console.error('WebSocket Error:', error)
    socket.close()
  }
}

const formatBytes = (bytes, decimals = 1) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
})
</script>