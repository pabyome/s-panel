<template>
  <div class="h-[calc(100vh-6rem)] flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">System Logs</h1>
        <p class="mt-1 text-sm text-gray-500">View application and server logs</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="confirmClearLog"
          :disabled="!selectedFile || isClearing"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-red-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
            <svg v-if="isClearing" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
            {{ isClearing ? 'Clearing...' : 'Clear Log' }}
        </button>
        <button
            @click="refreshLog"
            class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all"
        >
            <svg class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
            Refresh
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex flex-1 gap-6 min-h-0">
      <!-- File List -->
      <div class="w-1/4 rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden flex flex-col">
        <div class="border-b border-gray-100 bg-gray-50/50 px-4 py-3">
          <h3 class="text-sm font-medium text-gray-900">Log Files</h3>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-1">
          <button
            v-for="file in logFiles"
            :key="file.path"
            @click="selectFile(file)"
            :class="[
              selectedFile?.path === file.path
                ? 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200'
                : 'text-gray-700 hover:bg-gray-50',
              'w-full flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors text-left'
            ]"
          >
            <span class="truncate">{{ file.name }}</span>
            <span class="text-xs text-gray-400">{{ formatBytes(file.size_bytes) }}</span>
          </button>
        </div>
      </div>

      <!-- Log Viewer -->
      <div class="flex-1 rounded-2xl bg-gray-900 shadow-sm ring-1 ring-gray-900/5 overflow-hidden flex flex-col">
        <!-- Toolbar -->
        <div class="flex items-center justify-between border-b border-gray-800 bg-gray-900/50 px-4 py-2">
            <div class="flex items-center gap-3">
                <span class="text-sm font-medium text-gray-300">{{ selectedFile?.name || 'Select a log file' }}</span>
            </div>
            <div class="flex items-center gap-2">
                <span v-if="loading" class="text-xs text-indigo-400">Loading...</span>
                <span class="text-xs text-gray-500">Last 100 lines</span>
            </div>
        </div>

        <!-- Code Content -->
        <div class="flex-1 overflow-auto bg-[#0d1117] p-4 font-mono text-sm">
            <pre v-if="logContent" class="text-gray-300 whitespace-pre-wrap break-all">{{ logContent }}</pre>
            <div v-else-if="loading" class="flex h-full items-center justify-center text-gray-500">
                Loading...
            </div>
            <div v-else class="flex h-full items-center justify-center text-gray-600">
                Select a file to view logs
            </div>
        </div>
      </div>
    </div>

    <!-- Clear Log Confirmation Modal -->
    <ConfirmModal
      :isOpen="isClearModalOpen"
      type="warning"
      title="Clear Log File"
      :message="`Are you sure you want to clear/truncate ${selectedFile?.name}?`"
      confirmText="Clear Log"
      :isLoading="isClearing"
      @confirm="clearLog"
      @cancel="isClearModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const logFiles = ref([])
const selectedFile = ref(null)
const logContent = ref('')
const loading = ref(false)
const isClearing = ref(false)
const isClearModalOpen = ref(false)

const formatBytes = (bytes, decimals = 1) => {
    if (!+bytes) return '0 B'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const fetchFiles = async () => {
    try {
        const response = await axios.get('/api/v1/logs/files')
        logFiles.value = response.data
    } catch (e) {
        console.error("Failed to fetch log files", e)
    }
}

const selectFile = async (file) => {
    selectedFile.value = file
    await refreshLog()
}

const refreshLog = async () => {
    if (!selectedFile.value) return
    loading.value = true
    try {
        const response = await axios.get('/api/v1/logs/content', {
            params: { path: selectedFile.value.path, lines: 1000 } // Fetch more lines
        })
        logContent.value = response.data.content
    } catch (e) {
        logContent.value = `Error loading log: ${e.response?.data?.detail || e.message}`
    } finally {
        loading.value = false
    }
}

const confirmClearLog = () => {
    isClearModalOpen.value = true
}

const clearLog = async () => {
    if (!selectedFile.value || isClearing.value) return
    isClearing.value = true
    try {
        await axios.post('/api/v1/logs/clear_file', { path: selectedFile.value.path })
        toast.success('Log file cleared successfully')
        isClearModalOpen.value = false
        refreshLog()
        fetchFiles() // Update size
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to clear log")
    } finally {
        isClearing.value = false
    }
}

onMounted(() => {
    fetchFiles()
})
</script>
