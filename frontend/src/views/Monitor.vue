<template>
  <div class="px-4 sm:px-6 lg:px-8 py-6">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-bold text-gray-900">System Monitor</h1>
        <p class="mt-1 text-sm text-gray-500">Real-time server performance metrics and process list.</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium animate-pulse" v-if="connected">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Live
          </div>
          <div v-else class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-100 text-red-700 text-xs font-medium">
             Disconnected
          </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <!-- CPU Config -->
        <div class="bg-white overflow-hidden shadow rounded-2xl ring-1 ring-gray-900/5">
            <div class="p-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25z" />
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">CPU Usage</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-semibold text-gray-900">{{ stats.cpu?.percent }}%</div>
                            </dd>
                        </dl>
                    </div>
                </div>
                <div class="mt-4">
                     <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: `${stats.cpu?.percent}%` }"></div>
                    </div>
                     <p class="mt-2 text-xs text-gray-500">Cores: {{ stats.cpu?.count }}</p>
                </div>
            </div>
        </div>

        <!-- Memory -->
        <div class="bg-white overflow-hidden shadow rounded-2xl ring-1 ring-gray-900/5 relative">
            <div class="absolute top-5 right-5">
                <button
                    @click="openClearRamModal"
                    class="text-xs bg-violet-50 text-violet-700 px-2 py-1 rounded hover:bg-violet-100 transition-colors border border-violet-200"
                    title="Clear System RAM Cache"
                >
                    Clear Cache
                </button>
            </div>
            <div class="p-5">
                <div class="flex items-center">
                     <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">Memory Usage</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-semibold text-gray-900">{{ stats.memory?.percent }}%</div>
                            </dd>
                        </dl>
                    </div>
                </div>
                 <div class="mt-4">
                     <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-violet-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: `${stats.memory?.percent}%` }"></div>
                    </div>
                    <p class="mt-2 text-xs text-gray-500">{{ formatBytes(stats.memory?.used) }} / {{ formatBytes(stats.memory?.total) }}</p>
                </div>
            </div>
        </div>

        <!-- Disk -->
        <div class="bg-white overflow-hidden shadow rounded-2xl ring-1 ring-gray-900/5">
            <div class="p-5">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">Disk Usage</dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-semibold text-gray-900">{{ stats.disk?.percent }}%</div>
                            </dd>
                        </dl>
                    </div>
                </div>
                <div class="mt-4">
                     <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-emerald-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: `${stats.disk?.percent}%` }"></div>
                    </div>
                    <p class="mt-2 text-xs text-gray-500">{{ formatBytes(stats.disk?.used) }} / {{ formatBytes(stats.disk?.total) }}</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Process List -->
    <div class="mt-8">
        <h3 class="text-base font-semibold leading-6 text-gray-900 mb-4">Top Processes</h3>
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                    <tr>
                        <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">PID</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Name</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">User</th>
                         <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">CPU %</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Mem %</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                    <tr v-for="proc in processes" :key="proc.pid">
                        <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ proc.pid }}</td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ proc.name }}</td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ proc.username }}</td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">{{ proc.cpu_percent?.toFixed(1) }}%</td>
                         <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">{{ proc.memory_percent?.toFixed(1) }}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <ConfirmModal
      :isOpen="isClearRamModalOpen"
      type="warning"
      title="Clear RAM Cache"
      message="This will clear the system page cache, dentries, and inodes. This is generally safe but may temporarily impact performance while caches are rebuilt. Are you sure?"
      confirmText="Clear Memory"
      :isLoading="isClearingRam"
      @confirm="handleClearRam"
      @cancel="isClearRamModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast.js'

const toast = useToast()
const stats = ref({}) // cpu, memory, disk, load_avg
const processes = ref([])
const connected = ref(false)
const isClearRamModalOpen = ref(false)
const isClearingRam = ref(false)
let ws = null
let procInterval = null

const formatBytes = (bytes, decimals = 2) => {
    if (!+bytes) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/monitor/ws`

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
        connected.value = true
        console.log('Monitor WebSocket connected')
    }

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        stats.value = data
    }

    ws.onclose = () => {
        connected.value = false
        console.log('Monitor WebSocket disconnected, retrying...')
        setTimeout(connectWebSocket, 3000)
    }

    ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws.close()
    }
}

const fetchProcesses = async () => {
    try {
        const { data } = await axios.get('/api/v1/monitor/processes?limit=20')
        processes.value = data
    } catch (e) {
        console.error("Failed to fetch processes:", e)
    }
}

const openClearRamModal = () => {
    isClearRamModalOpen.value = true
}

const handleClearRam = async () => {
    isClearingRam.value = true
    try {
        await axios.post('/api/v1/system/memory/clear')
        toast.success("System memory cleared successfully")
        isClearRamModalOpen.value = false
    } catch (e) {
        console.error("Failed to clear memory:", e)
        toast.error("Failed to clear system memory")
    } finally {
        isClearingRam.value = false
    }
}

onMounted(() => {
    connectWebSocket()
    fetchProcesses()
    // Poll processes every 5 seconds (not real-time via WS to save bandwidth)
    procInterval = setInterval(fetchProcesses, 5000)
})

onUnmounted(() => {
    if (ws) ws.close()
    if (procInterval) clearInterval(procInterval)
})
</script>
