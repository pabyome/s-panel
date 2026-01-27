<template>
  <div class="space-y-8 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="min-w-0 flex-1">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight font-display">
          System Overview
        </h2>
        <p class="mt-2 text-sm text-gray-500">
          Real-time monitoring and control center.
        </p>
      </div>
      <div class="mt-4 flex md:ml-4 md:mt-0">
         <span class="inline-flex items-center gap-x-1.5 rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
            System Online
         </span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div v-if="stats" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <!-- CPU Card -->
      <div class="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-lg hover:ring-gray-900/10">
        <div class="flex items-center justify-between">
            <div>
                <dt class="text-sm font-semibold leading-6 text-gray-500">CPU Usage</dt>
                <dd class="mt-2 text-sm text-gray-600">
                    <div class="flex items-baseline gap-2">
                         <span class="text-3xl font-bold text-slate-900 tracking-tight">{{ stats.cpu.count }}</span>
                         <span class="text-sm font-medium text-gray-500">Cores</span>
                    </div>
                </dd>
            </div>
            <CircularGauge :value="stats.cpu.percent" label="Load" :size="90" />
        </div>
      </div>

       <!-- RAM Card -->
      <div class="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-lg hover:ring-gray-900/10">
        <div class="flex items-center justify-between">
            <div>
                <dt class="text-sm font-semibold leading-6 text-gray-500">Memory</dt>
                <dd class="mt-2 text-sm text-gray-600">
                     <div class="text-3xl font-bold text-slate-900 tracking-tight">{{ formatBytes(stats.memory.used) }}</div>
                     <div class="text-xs font-medium text-gray-400 mt-1">of {{ formatBytes(stats.memory.total) }}</div>
                </dd>
            </div>
            <CircularGauge :value="stats.memory.percent" label="Used" :size="90" />
        </div>
      </div>

      <!-- Disk Card -->
      <div class="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-lg hover:ring-gray-900/10">
         <div class="flex items-center justify-between">
            <div>
                <dt class="text-sm font-semibold leading-6 text-gray-500">Storage (/)</dt>
                <dd class="mt-2 text-sm text-gray-600">
                     <div class="text-3xl font-bold text-slate-900 tracking-tight">{{ formatBytes(stats.disk.used) }}</div>
                     <div class="text-xs font-medium text-gray-400 mt-1">of {{ formatBytes(stats.disk.total) }}</div>
                </dd>
            </div>
            <CircularGauge :value="stats.disk.percent" label="Full" :size="90" />
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-else class="flex h-64 items-center justify-center rounded-2xl bg-white border border-dashed border-gray-300 shadow-sm">
        <div class="text-center">
            <svg class="mx-auto h-12 w-12 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <h3 class="mt-4 text-sm font-semibold text-gray-900">Connecting to Server...</h3>
        </div>
    </div>

    <!-- Grid: Quick Actions + Info -->
    <div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <!-- Quick Actions -->
        <div class="flex flex-col gap-y-4">
             <h3 class="text-base font-semibold leading-6 text-gray-900">Quick Actions</h3>
             <div class="grid grid-cols-2 gap-4">
                <router-link to="/websites" class="flex flex-col items-center justify-center rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-indigo-500 hover:shadow-md hover:-translate-y-0.5 group">
                    <span class="mb-3 rounded-lg bg-indigo-50 p-3 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
                    </span>
                    <span class="text-sm font-medium text-gray-900">New Website</span>
                </router-link>

                 <router-link to="/supervisor" class="flex flex-col items-center justify-center rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-indigo-500 hover:shadow-md hover:-translate-y-0.5 group">
                    <span class="mb-3 rounded-lg bg-pink-50 p-3 text-pink-600 group-hover:bg-pink-600 group-hover:text-white transition-colors">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" /></svg>
                    </span>
                    <span class="text-sm font-medium text-gray-900">Manage Processes</span>
                </router-link>
                
                 <router-link to="/security" class="flex flex-col items-center justify-center rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-indigo-500 hover:shadow-md hover:-translate-y-0.5 group">
                    <span class="mb-3 rounded-lg bg-blue-50 p-3 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" /></svg>
                    </span>
                    <span class="text-sm font-medium text-gray-900">Firewall Rules</span>
                </router-link>

                 <router-link to="/cron" class="flex flex-col items-center justify-center rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:ring-indigo-500 hover:shadow-md hover:-translate-y-0.5 group">
                    <span class="mb-3 rounded-lg bg-amber-50 p-3 text-amber-600 group-hover:bg-amber-600 group-hover:text-white transition-colors">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </span>
                    <span class="text-sm font-medium text-gray-900">Cron Jobs</span>
                </router-link>
            </div>
        </div>

        <!-- System Info -->
         <div class="flex flex-col gap-y-4">
            <h3 class="text-base font-semibold leading-6 text-gray-900">System Information</h3>
            <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5">
                <dl class="divide-y divide-gray-100">
                    <div class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <dt class="text-sm font-medium text-gray-500">Load Average</dt>
                        <dd class="text-sm font-mono text-gray-900" v-if="stats && stats.load_avg">
                             {{ stats.load_avg['1min'] }} <span class="text-gray-400">/</span> {{ stats.load_avg['5min'] }} <span class="text-gray-400">/</span> {{ stats.load_avg['15min'] }}
                        </dd>
                         <dd class="text-sm text-gray-400" v-else>Loading...</dd>
                    </div>
                     <div class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <dt class="text-sm font-medium text-gray-500">Service Status</dt>
                        <dd class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                             Active (Running)
                        </dd>
                    </div>
                    <div class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <dt class="text-sm font-medium text-gray-500">Operating System</dt>
                        <dd class="text-sm text-gray-900 flex items-center gap-2">
                            <span class="h-4 w-4 bg-gray-200 rounded-full flex items-center justify-center text-[10px]">🐧</span>
                            Linux / Ubuntu
                        </dd>
                    </div>
                    <div class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <dt class="text-sm font-medium text-gray-500">Panel Version</dt>
                        <dd class="text-sm text-gray-900">v0.1.0-mvp</dd>
                    </div>
                </dl>
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