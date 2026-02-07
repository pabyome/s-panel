<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-gray-900">Running containers</h1>
      <div class="flex gap-2">
         <button @click="fetchStats" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Refresh</button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- CPU Usage -->
      <div class="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold text-gray-900">CPU usage</h3>
        </div>
        <div class="mt-4">
          <div class="flex items-end justify-between">
             <span class="text-3xl font-bold text-gray-900">{{ stats.cpu_percent ? stats.cpu_percent.toFixed(1) : '0.0' }} %</span>
          </div>
          <div class="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-100">
            <div class="h-full rounded-full bg-orange-400 transition-all duration-500" :style="{ width: (stats.cpu_percent || 0) + '%' }"></div>
          </div>
           <div class="mt-1 text-right text-xs text-gray-500">{{ stats.cpu_percent ? stats.cpu_percent.toFixed(1) : '0.0' }}%</div>
        </div>
      </div>

      <!-- Memory Usage -->
      <div class="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold text-gray-900">Memory usage</h3>
        </div>
        <div class="mt-4">
          <div class="flex items-end justify-between">
             <span class="text-3xl font-bold text-gray-900">{{ formatBytes(stats.memory?.used) }} / {{ formatBytes(stats.memory?.total) }}</span>
          </div>
          <div class="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-100">
            <div class="h-full rounded-full bg-blue-500 transition-all duration-500" :style="{ width: (stats.memory?.percent || 0) + '%' }"></div>
          </div>
           <div class="mt-1 text-right text-xs text-gray-500">{{ stats.memory?.percent || 0 }}%</div>
        </div>
      </div>
    </div>

    <!-- Running Containers Grid -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div v-for="container in runningContainers" :key="container.id" class="rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-900/5 hover:ring-indigo-500 transition-all">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
             <!-- Generic Container Icon -->
             <svg class="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" d="M21 7.5l-2.25-1.313M21 7.5v2.25m0-2.25l-2.25 1.313M3 7.5l2.25-1.313M3 7.5l2.25 1.313M3 7.5v2.25m9 3l2.25-1.313M12 12.75l-2.25-1.313M12 12.75V15m0 6.75l2.25-1.313M12 21.75V19.5m0 2.25l-2.25-1.313m0-16.875L12 2.25l2.25 1.313M21 14.25v2.25l-2.25 1.313m-13.5 0L3 16.5v-2.25" />
             </svg>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-sm font-bold text-green-600">{{ container.name }}</h3>
            <p class="truncate text-xs text-gray-500">{{ container.image }}</p>
            <p class="mt-1 text-xs text-gray-400">Create at: {{ formatDate(container.created) }}</p>
          </div>
        </div>

        <div class="mt-4 space-y-2">
            <!-- Fake individual stats for visual match as backend aggregated stats are global -->
            <div class="flex items-center gap-2 text-xs text-gray-500">
                <span class="w-8">CPU</span>
                <div class="h-1.5 flex-1 rounded-full bg-gray-100">
                    <div class="h-full rounded-full bg-orange-400" style="width: 5%"></div>
                </div>
                <span class="w-12 text-right">~ %</span>
            </div>
            <div class="flex items-center gap-2 text-xs text-gray-500">
                <span class="w-8">RAM</span>
                <div class="h-1.5 flex-1 rounded-full bg-gray-100">
                    <div class="h-full rounded-full bg-blue-500" style="width: 10%"></div>
                </div>
                <span class="w-12 text-right">~ MB</span>
            </div>
        </div>
      </div>

       <!-- Empty State -->
       <div v-if="runningContainers.length === 0" class="col-span-full py-12 text-center text-sm text-gray-500 bg-white rounded-lg border border-dashed border-gray-300">
          No running containers found.
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const stats = ref({})
const containers = ref([])

const runningContainers = computed(() => {
    return containers.value.filter(c => c.status === 'running')
})

const fetchStats = async () => {
    try {
        const [statsRes, containersRes] = await Promise.all([
            axios.get('/api/v1/swarm/stats'),
            axios.get('/api/v1/containers/')
        ])
        stats.value = statsRes.data
        containers.value = containersRes.data
    } catch (e) {
        console.error("Error fetching overview data", e)
    }
}

const formatBytes = (bytes, decimals = 2) => {
    if (!bytes) return '0 B'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

onMounted(() => {
    fetchStats()
})
</script>
