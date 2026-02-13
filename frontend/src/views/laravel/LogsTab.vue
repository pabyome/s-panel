<template>
  <div class="space-y-6">
    <!-- Service Selector -->
    <div class="flex gap-4">
        <button v-for="role in ['web', 'worker', 'scheduler']" :key="role"
            @click="selectedRole = role"
            :class="[selectedRole === role ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50', 'px-4 py-2 rounded-lg text-sm font-medium shadow-sm ring-1 ring-gray-900/5 transition-colors uppercase']"
        >
            {{ role }}
        </button>
    </div>

    <!-- Container List -->
    <div v-if="containers.length > 0" class="flex gap-2 overflow-x-auto pb-2">
        <button v-for="c in containers" :key="c.id"
            @click="selectedContainerId = c.id"
            :class="[selectedContainerId === c.id ? 'bg-indigo-100 text-indigo-700 ring-indigo-500' : 'bg-white text-gray-600 ring-gray-200', 'px-3 py-1.5 rounded-md text-xs font-mono whitespace-nowrap ring-1 ring-inset']"
        >
            {{ c.name.substring(0, 20) }}...
        </button>
    </div>
    <div v-else class="text-sm text-gray-500 italic">
        No running containers found for {{ selectedRole }}.
    </div>

    <!-- Logs Display -->
    <div class="bg-gray-900 rounded-2xl p-4 h-[500px] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-2">
             <h4 class="text-gray-400 text-xs uppercase font-bold tracking-wider">
                 {{ selectedContainerId ? 'Container Logs' : 'Select a container' }}
             </h4>
             <div class="flex items-center gap-4">
                <label class="flex items-center gap-2 text-xs text-gray-400">
                    <input type="checkbox" v-model="autoRefresh" class="rounded bg-gray-800 border-gray-700 text-indigo-600 focus:ring-indigo-500">
                    Auto-refresh
                </label>
                <button @click="fetchLogs" class="text-xs text-indigo-400 hover:text-indigo-300">Refresh Now</button>
             </div>
        </div>
        <div ref="logContainer" class="flex-1 overflow-y-auto font-mono text-xs text-gray-300 whitespace-pre-wrap">
            {{ logs || (selectedContainerId ? 'Loading...' : 'Select a container to view logs.') }}
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../composables/useToast'

const props = defineProps({
  website: Object,
  deployment: Object
})

const toast = useToast()
const selectedRole = ref('web')
const stackStatus = ref({})
const containers = ref([])
const selectedContainerId = ref(null)
const logs = ref('')
const autoRefresh = ref(false)
let pollInterval = null

const fetchStackStatus = async () => {
    try {
        const { data } = await axios.get(`/api/v1/websites/${props.website.id}/stack`)
        stackStatus.value = data
        updateContainers()
    } catch (e) {
        console.error("Failed to fetch stack status", e)
    }
}

const updateContainers = () => {
    if (!stackStatus.value[selectedRole.value]) {
        containers.value = []
        return
    }
    const roleData = stackStatus.value[selectedRole.value]
    containers.value = roleData.containers || []

    // Select first container if none selected or selection invalid
    if (containers.value.length > 0) {
        if (!selectedContainerId.value || !containers.value.find(c => c.id === selectedContainerId.value)) {
            selectedContainerId.value = containers.value[0].id
        }
    } else {
        selectedContainerId.value = null
        logs.value = ''
    }
}

const fetchLogs = async () => {
    if (!selectedContainerId.value) return

    try {
        const { data } = await axios.get(`/api/v1/containers/${selectedContainerId.value}/logs?tail=200`)
        logs.value = data.logs || 'No logs found.'
    } catch (e) {
        console.error("Failed to fetch logs", e)
        logs.value = 'Failed to fetch logs.'
    }
}

watch(selectedRole, () => {
    updateContainers()
})

watch(selectedContainerId, () => {
    fetchLogs()
})

watch(autoRefresh, (val) => {
    if (val) {
        pollInterval = setInterval(fetchLogs, 3000)
    } else {
        if (pollInterval) clearInterval(pollInterval)
    }
})

onMounted(async () => {
    await fetchStackStatus()
})

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
})
</script>
