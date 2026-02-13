<template>
  <div class="flex flex-col h-full space-y-6">
    <!-- Main Deployment Actions -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Manual Deployment</h3>
        <div class="flex items-center gap-4">
            <button
                @click="triggerDeploy"
                :disabled="deploying"
                class="inline-flex items-center rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <svg v-if="deploying" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ deploying ? 'Deploying...' : 'Deploy Now' }}
            </button>
            <div class="text-sm text-gray-500">
                Using <strong>{{ deployment.branch }}</strong> branch.
            </div>
        </div>
    </div>

    <!-- Deployment Log Stream -->
    <div class="flex-1 bg-gray-900 rounded-2xl p-4 overflow-hidden flex flex-col min-h-[400px]">
        <div class="flex justify-between items-center mb-2">
             <h4 class="text-gray-400 text-xs uppercase font-bold tracking-wider">Live Logs</h4>
             <span class="text-xs" :class="connectionStatus === 'Connected' ? 'text-green-400' : 'text-red-400'">{{ connectionStatus }}</span>
        </div>
        <div ref="logContainer" class="flex-1 overflow-y-auto font-mono text-xs text-gray-300 whitespace-pre-wrap">
            {{ logs || 'Waiting for logs...' }}
        </div>
    </div>

    <!-- Deployment History -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
            <h3 class="text-lg font-semibold text-gray-900">Deployment History</h3>
        </div>
        <ul role="list" class="divide-y divide-gray-100">
            <li v-for="record in history" :key="record.id" class="p-6 hover:bg-gray-50 transition-colors">
                <div class="flex items-center justify-between">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-2">
                             <span :class="[
                                 record.status === 'success' ? 'bg-green-100 text-green-700' :
                                 record.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700',
                                 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-500/10'
                             ]">
                                 {{ record.status }}
                             </span>
                             <span class="text-sm font-medium text-gray-900">
                                 Commit: {{ record.commit_hash || 'Unknown' }}
                             </span>
                        </div>
                        <p class="text-xs text-gray-500">
                             {{ formatDate(record.deployed_at) }}
                        </p>
                        <p class="text-xs font-mono text-gray-400">
                             Image: {{ record.image_tag }}
                        </p>
                    </div>

                    <button
                        @click="triggerRollback(record)"
                        :disabled="rollingBack === record.id || !record.image_tag"
                        class="text-sm font-semibold text-indigo-600 hover:text-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {{ rollingBack === record.id ? 'Rolling back...' : 'Rollback' }}
                    </button>
                </div>
            </li>
            <li v-if="history.length === 0" class="p-6 text-center text-gray-500 text-sm">
                No deployment history found.
            </li>
        </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { useToast } from '../../composables/useToast'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
    website: Object,
    deployment: Object
})

const toast = useToast()
const authStore = useAuthStore()
const deploying = ref(false)
const history = ref([])
const rollingBack = ref(null)
const logs = ref('')
const connectionStatus = ref('Disconnected')
const logContainer = ref(null)
let socket = null

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

const fetchHistory = async () => {
    try {
        const { data } = await axios.get(`/api/v1/deployments/${props.deployment.id}/history`)
        history.value = data
    } catch (e) {
        console.error("Failed to fetch history", e)
    }
}

const triggerDeploy = async () => {
    deploying.value = true
    try {
        await axios.post(`/api/v1/deployments/${props.deployment.id}/trigger`)
        toast.success("Deployment triggered")
        // Logs will stream automatically via WebSocket
    } catch (e) {
        toast.error("Failed to trigger deployment")
    } finally {
        deploying.value = false
    }
}

const triggerRollback = async (record) => {
    if (!confirm(`Are you sure you want to rollback to commit ${record.commit_hash}?`)) return

    rollingBack.value = record.id
    try {
        await axios.post(`/api/v1/deployments/${props.deployment.id}/rollback`, {
            history_id: record.id
        })
        toast.success("Rollback triggered")
    } catch (e) {
        toast.error(e.response?.data?.detail || "Rollback failed")
    } finally {
        rollingBack.value = null
    }
}

const connectWebSocket = () => {
    if (socket) socket.close()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    // We assume backend runs on same host/port during dev proxy, or we use explicit port?
    // Vite proxy handles /api, but WS needs explicit URL usually or relative path if configured.
    // Assuming backend is at standard API location.
    // Since we are inside the browser, window.location.host includes port (e.g. 8000 or 5173).
    // If dev mode (5173), we need to connect to 8000.
    // If prod, same host.

    // Simple heuristic: if port 5173, use 8000.
    let wsHost = window.location.host
    if (wsHost.includes('5173')) {
        wsHost = wsHost.replace('5173', '8000')
    }

    const wsUrl = `${protocol}//${wsHost}/api/v1/deployments/ws/${props.deployment.id}?token=${authStore.token}`

    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
        connectionStatus.value = 'Connected'
    }

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'initial' || data.type === 'update') {
            logs.value = data.logs
            nextTick(() => {
                if (logContainer.value) {
                    logContainer.value.scrollTop = logContainer.value.scrollHeight
                }
            })
            // If status changed to success/failed, refresh history
            if (['success', 'failed'].includes(data.status)) {
                fetchHistory()
            }
        }
    }

    socket.onclose = () => {
        connectionStatus.value = 'Disconnected'
        // Auto-reconnect after delay?
        setTimeout(connectWebSocket, 3000)
    }

    socket.onerror = (error) => {
        console.error("WebSocket error", error)
        connectionStatus.value = 'Error'
    }
}

watch(() => props.deployment.id, () => {
    logs.value = ''
    fetchHistory()
    connectWebSocket()
})

onMounted(() => {
    fetchHistory()
    connectWebSocket()
})

onUnmounted(() => {
    if (socket) socket.close()
})
</script>
