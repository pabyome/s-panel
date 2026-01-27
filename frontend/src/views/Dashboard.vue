<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="mt-1 text-sm text-gray-500">Real-time server monitoring and quick actions</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 ring-1 ring-emerald-500/20">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          <span class="text-sm font-medium text-emerald-700">Live</span>
        </div>
      </div>
    </div>

    <!-- Main Stats Grid -->
    <div v-if="stats" class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- CPU Card -->
      <div class="group relative overflow-hidden rounded-2xl bg-linear-to-br from-violet-500 to-purple-600 p-5 shadow-lg shadow-violet-500/25 transition-all hover:shadow-xl hover:shadow-violet-500/30 hover:-translate-y-0.5">
        <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
        <div class="absolute right-0 bottom-0 -mr-8 -mb-8 h-32 w-32 rounded-full bg-white/5"></div>
        <div class="relative">
          <div class="flex items-center justify-between">
            <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
              <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <span class="text-xs font-medium text-white/70">{{ stats.cpu.count }} cores</span>
          </div>
          <div class="mt-4">
            <p class="text-sm font-medium text-white/80">CPU Usage</p>
            <p class="mt-1 text-3xl font-bold text-white">{{ stats.cpu.percent }}<span class="text-lg">%</span></p>
          </div>
          <div class="mt-4">
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-white/20">
              <div class="h-full rounded-full bg-white transition-all duration-500" :style="{ width: stats.cpu.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Memory Card -->
      <div class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 p-5 shadow-lg shadow-cyan-500/25 transition-all hover:shadow-xl hover:shadow-cyan-500/30 hover:-translate-y-0.5">
        <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
        <div class="absolute right-0 bottom-0 -mr-8 -mb-8 h-32 w-32 rounded-full bg-white/5"></div>
        <div class="relative">
          <div class="flex items-center justify-between">
            <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
              <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h12M6 6v12a2 2 0 002 2h8a2 2 0 002-2V6M6 6l1-3h10l1 3" />
              </svg>
            </div>
            <span class="text-xs font-medium text-white/70">{{ formatBytes(stats.memory.total) }}</span>
          </div>
          <div class="mt-4">
            <p class="text-sm font-medium text-white/80">Memory</p>
            <p class="mt-1 text-3xl font-bold text-white">{{ formatBytes(stats.memory.used, 0) }}</p>
          </div>
          <div class="mt-4">
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-white/20">
              <div class="h-full rounded-full bg-white transition-all duration-500" :style="{ width: stats.memory.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Disk Card -->
      <div class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 p-5 shadow-lg shadow-amber-500/25 transition-all hover:shadow-xl hover:shadow-amber-500/30 hover:-translate-y-0.5">
        <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
        <div class="absolute right-0 bottom-0 -mr-8 -mb-8 h-32 w-32 rounded-full bg-white/5"></div>
        <div class="relative">
          <div class="flex items-center justify-between">
            <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
              <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
              </svg>
            </div>
            <span class="text-xs font-medium text-white/70">{{ formatBytes(stats.disk.total) }}</span>
          </div>
          <div class="mt-4">
            <p class="text-sm font-medium text-white/80">Storage</p>
            <p class="mt-1 text-3xl font-bold text-white">{{ formatBytes(stats.disk.used, 0) }}</p>
          </div>
          <div class="mt-4">
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-white/20">
              <div class="h-full rounded-full bg-white transition-all duration-500" :style="{ width: stats.disk.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load Average Card -->
      <div class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 p-5 shadow-lg shadow-emerald-500/25 transition-all hover:shadow-xl hover:shadow-emerald-500/30 hover:-translate-y-0.5">
        <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
        <div class="absolute right-0 bottom-0 -mr-8 -mb-8 h-32 w-32 rounded-full bg-white/5"></div>
        <div class="relative">
          <div class="flex items-center justify-between">
            <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
              <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            </div>
            <span class="text-xs font-medium text-white/70">System Load</span>
          </div>
          <div class="mt-4">
            <p class="text-sm font-medium text-white/80">Load Average</p>
            <p class="mt-1 text-3xl font-bold text-white">{{ stats.load_avg['1min'].toFixed(2) }}</p>
          </div>
          <div class="mt-4 flex items-center gap-3 text-xs text-white/70">
            <span class="rounded bg-white/10 px-2 py-0.5">5m: {{ stats.load_avg['5min'].toFixed(2) }}</span>
            <span class="rounded bg-white/10 px-2 py-0.5">15m: {{ stats.load_avg['15min'].toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="h-44 animate-pulse rounded-2xl bg-gray-200"></div>
    </div>

    <!-- Bottom Section -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Quick Actions -->
      <div class="lg:col-span-1">
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5">
          <h3 class="text-base font-semibold text-gray-900">Quick Actions</h3>
          <p class="mt-1 text-sm text-gray-500">Common tasks and shortcuts</p>
          <div class="mt-5 grid grid-cols-2 gap-3">
            <router-link to="/websites" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-indigo-50 hover:to-indigo-100 hover:shadow-md">
              <div class="rounded-lg bg-indigo-500 p-2.5 text-white shadow-lg shadow-indigo-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Websites</span>
            </router-link>

            <router-link to="/supervisor" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-pink-50 hover:to-pink-100 hover:shadow-md">
              <div class="rounded-lg bg-pink-500 p-2.5 text-white shadow-lg shadow-pink-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Processes</span>
            </router-link>

            <router-link to="/security" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-blue-50 hover:to-blue-100 hover:shadow-md">
              <div class="rounded-lg bg-blue-500 p-2.5 text-white shadow-lg shadow-blue-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Firewall</span>
            </router-link>

            <router-link to="/cron" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-amber-50 hover:to-amber-100 hover:shadow-md">
              <div class="rounded-lg bg-amber-500 p-2.5 text-white shadow-lg shadow-amber-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Cron Jobs</span>
            </router-link>

            <router-link to="/redis" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-red-50 hover:to-red-100 hover:shadow-md">
              <div class="rounded-lg bg-red-500 p-2.5 text-white shadow-lg shadow-red-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Redis</span>
            </router-link>

            <router-link to="/deployments" class="group flex flex-col items-center gap-2 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 transition-all hover:from-violet-50 hover:to-violet-100 hover:shadow-md">
              <div class="rounded-lg bg-violet-500 p-2.5 text-white shadow-lg shadow-violet-500/30 transition-transform group-hover:scale-110">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" /></svg>
              </div>
              <span class="text-xs font-medium text-gray-700">Deploy</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- System Info Panel -->
      <div class="lg:col-span-2">
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-semibold text-gray-900">System Information</h3>
              <p class="mt-1 text-sm text-gray-500">Server details and status</p>
            </div>
            <span class="inline-flex items-center rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
              Healthy
            </span>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-gray-200 p-2">
                  <svg class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Operating System</p>
                  <p class="text-sm font-medium text-gray-900">{{ stats?.os_info?.system || 'Linux' }} {{ stats?.os_info?.release }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-gray-200 p-2">
                  <svg class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Panel Version</p>
                  <p class="text-sm font-medium text-gray-900">v1.2.0</p>
                </div>
              </div>
            </div>

            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-gray-200 p-2">
                  <svg class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Uptime</p>
                  <p class="text-sm font-medium text-gray-900">{{ formatUptime(stats?.uptime) }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-xl bg-gray-50 p-4">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-gray-200 p-2">
                  <svg class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0z" />
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Connection</p>
                  <p class="text-sm font-medium text-gray-900">WebSocket Active</p>
                </div>
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

const formatUptime = (seconds) => {
    if (!seconds || seconds <= 0) return '0s'
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return days > 0 ? `${days}d ${hours}h` : `${hours}h ${minutes}m`
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
