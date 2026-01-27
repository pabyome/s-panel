<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/supervisor')" class="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ route.params.name }}</h1>
          <p class="mt-0.5 text-sm text-gray-500">Process logs and configuration</p>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="flex rounded-xl bg-gray-100 p-1">
        <button
          v-for="tab in ['Logs', 'Config']"
          :key="tab"
          @click="currentTab = tab"
          :class="[
            'rounded-lg px-5 py-2 text-sm font-medium transition-all',
            currentTab === tab
              ? 'bg-white text-violet-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg v-if="tab === 'Logs'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ tab }}
          </span>
        </button>
      </div>
    </div>

    <!-- Logs Tab -->
    <div v-if="currentTab === 'Logs'" class="rounded-2xl bg-gray-900 shadow-xl overflow-hidden">
      <div class="flex items-center justify-between border-b border-gray-700 px-5 py-3">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <span class="h-3 w-3 rounded-full bg-red-500"></span>
            <span class="h-3 w-3 rounded-full bg-yellow-500"></span>
            <span class="h-3 w-3 rounded-full bg-green-500"></span>
          </div>
          <span class="text-sm text-gray-400">stdout</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Auto-refresh: 3s</span>
          <button @click="confirmClearLogs" :disabled="isClearingLogs" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-red-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" title="Clear Logs">
             <svg v-if="isClearingLogs" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
             <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
             </svg>
          </button>
          <button @click="fetchLogs" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white transition-colors" title="Refresh">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
          </button>
        </div>
      </div>
      <div class="h-[550px] overflow-auto p-5 font-mono text-sm leading-relaxed">
        <pre v-if="logs" class="text-green-400 whitespace-pre-wrap">{{ logs }}</pre>
        <div v-else class="flex h-full items-center justify-center">
          <div class="text-center">
            <svg class="mx-auto h-10 w-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p class="mt-3 text-gray-500">No logs available</p>
            <p class="text-xs text-gray-600">Process may not have generated output yet</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Config Tab -->
    <div v-if="currentTab === 'Config'" class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-semibold text-gray-900">Configuration File</h3>
            <p class="text-xs text-gray-500">/etc/supervisor/conf.d/{{ route.params.name }}.conf</p>
          </div>
          <button
            @click="confirmSaveConfig"
            :disabled="isSavingConfig"
            class="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          >
            <svg v-if="isSavingConfig" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ isSavingConfig ? 'Saving...' : 'Save & Reload' }}
          </button>
        </div>
      </div>
      <div class="p-6">
        <textarea
          v-model="configContent"
          class="block w-full rounded-xl border-0 bg-gray-50 py-4 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm font-mono min-h-[450px] resize-none"
          spellcheck="false"
          placeholder="[program:example]
command=/usr/bin/node /var/www/app/index.js
directory=/var/www/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/example.err.log
stdout_logfile=/var/log/supervisor/example.out.log"
        ></textarea>

        <div class="mt-4 rounded-xl bg-amber-50 p-4 ring-1 ring-amber-100">
          <div class="flex gap-3">
            <svg class="h-5 w-5 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <div class="text-sm text-amber-800">
              <p class="font-medium">Configuration will reload Supervisor</p>
              <p class="mt-1 text-amber-700">Saving will apply changes immediately. The process may restart.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Clear Logs Confirmation Modal -->
    <ConfirmModal
      :isOpen="isClearLogsModalOpen"
      type="warning"
      title="Clear Logs"
      message="Are you sure you want to clear these logs? This action cannot be undone."
      confirmText="Clear Logs"
      :isLoading="isClearingLogs"
      @confirm="clearLogs"
      @cancel="isClearLogsModalOpen = false"
    />

    <!-- Save Config Confirmation Modal -->
    <ConfirmModal
      :isOpen="isSaveConfigModalOpen"
      type="warning"
      title="Save Configuration"
      message="Saving will reload supervisor configuration. The process may restart. Continue?"
      confirmText="Save & Reload"
      :isLoading="isSavingConfig"
      @confirm="saveConfig"
      @cancel="isSaveConfigModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()
const route = useRoute()
const currentTab = ref('Logs')
const logs = ref('')
const configContent = ref('')
let pollInterval = null

// Loading states
const isClearingLogs = ref(false)
const isSavingConfig = ref(false)
const isClearLogsModalOpen = ref(false)
const isSaveConfigModalOpen = ref(false)

const fetchLogs = async () => {
    try {
        const response = await axios.get(`/api/v1/supervisor/processes/${route.params.name}/logs?length=10000`)
        logs.value = response.data.log
    } catch (e) {
        console.error("Failed to fetch logs")
    }
}

const confirmClearLogs = () => {
    isClearLogsModalOpen.value = true
}

const clearLogs = async () => {
    if (isClearingLogs.value) return
    isClearingLogs.value = true
    try {
        await axios.post(`/api/v1/supervisor/processes/${route.params.name}/logs/clear`)
        logs.value = ''
        toast.success('Logs cleared successfully')
        isClearLogsModalOpen.value = false
        fetchLogs()
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to clear logs")
    } finally {
        isClearingLogs.value = false
    }
}

const fetchConfig = async () => {
    try {
        const response = await axios.get(`/api/v1/supervisor/processes/${route.params.name}/config`)
        configContent.value = response.data.content
    } catch (e) {
        console.error("Failed to fetch config")
    }
}

const confirmSaveConfig = () => {
    isSaveConfigModalOpen.value = true
}

const saveConfig = async () => {
    if (isSavingConfig.value) return
    isSavingConfig.value = true
    try {
        await axios.put(`/api/v1/supervisor/processes/${route.params.name}/config`, {
            content: configContent.value
        })
        toast.success("Configuration saved and reloaded successfully")
        isSaveConfigModalOpen.value = false
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to save configuration")
    } finally {
        isSavingConfig.value = false
    }
}

// Poll logs when on Logs tab
watch(currentTab, (newTab) => {
    if (newTab === 'Logs') {
        fetchLogs()
        pollInterval = setInterval(fetchLogs, 3000)
    } else {
        clearInterval(pollInterval)
        if (newTab === 'Config') fetchConfig()
    }
})

onMounted(() => {
    fetchLogs()
    pollInterval = setInterval(fetchLogs, 3000)
})

onUnmounted(() => {
    clearInterval(pollInterval)
})
</script>
