<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
        <div class="flex items-center gap-4">
            <button @click="$router.push('/supervisor')" class="text-gray-500 hover:text-gray-700">
                &larr; Back
            </button>
            <h1 class="text-2xl font-bold text-gray-900">{{ route.params.name }}</h1>
        </div>

        <!-- Tabs -->
        <div class="flex space-x-1 rounded-xl bg-gray-200 p-1">
             <button
                v-for="tab in ['Logs', 'Config']"
                :key="tab"
                @click="currentTab = tab"
                :class="[
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5 px-8',
                  currentTab === tab
                    ? 'bg-white text-indigo-700 shadow'
                    : 'text-gray-800 hover:bg-white/[0.12] hover:text-indigo-600'
                ]"
              >
                {{ tab }}
              </button>
        </div>
    </div>

    <!-- Logs Tab -->
    <div v-if="currentTab === 'Logs'" class="bg-black rounded-lg p-4 font-mono text-sm text-green-400 h-[600px] overflow-auto whitespace-pre-wrap">
        <div v-if="logs">{{ logs }}</div>
        <div v-else class="text-gray-500 italic">No logs available or loading...</div>
    </div>

    <!-- Config Tab -->
    <div v-if="currentTab === 'Config'" class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Edit Configuration</h3>
        <textarea
            v-model="configContent"
            class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono min-h-[400px]"
            spellcheck="false"
        ></textarea>
        <div class="mt-4 flex justify-end">
             <button @click="saveConfig" type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
              Save & Reload
            </button>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const currentTab = ref('Logs')
const logs = ref('')
const configContent = ref('')
let pollInterval = null

const fetchLogs = async () => {
    try {
        // Simple polling of last 5000 chars for now
        const response = await axios.get(`/api/v1/supervisor/processes/${route.params.name}/logs?length=5000`)
        logs.value = response.data.log
    } catch (e) {
        console.error("Failed to fetch logs")
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

const saveConfig = async () => {
    if(!confirm("Saving will reload supervisor configuration. Continue?")) return;
    try {
        await axios.put(`/api/v1/supervisor/processes/${route.params.name}/config`, {
            content: configContent.value
        })
        alert("Configuration saved and reloaded.")
    } catch (e) {
        alert("Failed to save configuration.")
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
    // Initial load
    fetchLogs()
    pollInterval = setInterval(fetchLogs, 3000)
})

onUnmounted(() => {
    clearInterval(pollInterval)
})
</script>
