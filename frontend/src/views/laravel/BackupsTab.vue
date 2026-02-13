<template>
  <div class="space-y-6">
    <!-- Volume List -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Volume Browser</h3>
        <p class="text-sm text-gray-500 mb-4">Browse and manage persistent data volumes for this application.</p>

        <div v-if="loadingVolumes" class="flex justify-center p-4">
            <svg class="h-6 w-6 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>
        <ul v-else-if="volumes.length > 0" class="divide-y divide-gray-100">
            <li v-for="vol in volumes" :key="vol.name" class="py-4 flex items-center justify-between">
                <div class="min-w-0 flex-1 mr-4">
                    <p class="text-sm font-medium text-gray-900 truncate" :title="vol.name">{{ vol.name }}</p>
                    <p class="text-xs text-gray-500 font-mono truncate" :title="vol.mountpoint">{{ vol.mountpoint }}</p>
                </div>
                <a :href="`/files?path=${encodeURIComponent(vol.mountpoint)}`" target="_blank" class="whitespace-nowrap text-sm font-semibold text-indigo-600 hover:text-indigo-500">
                    Browse Files &rarr;
                </a>
            </li>
        </ul>
        <div v-else class="text-sm text-gray-500 italic">
            No volumes found for stack "{{ stackName }}".
        </div>
    </div>

    <!-- Database Backups -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-4">
             <h3 class="text-lg font-semibold text-gray-900">Database Snapshots</h3>
        </div>
        <p class="text-sm text-gray-500 mb-4">Download a snapshot of your database.</p>
        <div class="flex gap-2 items-center">
            <input
                v-model="dbName"
                type="text"
                placeholder="Database Name"
                class="block rounded-lg border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            >
            <a
                :href="`/api/v1/backups/database/stream?database=${dbName}`"
                target="_blank"
                :class="[!dbName ? 'opacity-50 pointer-events-none' : '', 'inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600']"
            >
                Download SQL
            </a>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  website: Object,
  deployment: Object
})

const volumes = ref([])
const loadingVolumes = ref(true)
const dbName = ref('')

const stackName = computed(() => {
    return props.deployment.name.toLowerCase().replace(" ", "-").replace("_", "-")
})

const fetchVolumes = async () => {
    loadingVolumes.value = true
    try {
        const { data } = await axios.get('/api/v1/volumes/')
        // Filter volumes belonging to this stack
        // Docker stack volumes usually prefixed with stack name or have labels
        // We check if name starts with stackName_
        // Or if labels["com.docker.stack.namespace"] == stackName

        volumes.value = data.filter(v => {
            const nameMatch = v.name.startsWith(`${stackName.value}_`)
            const labelMatch = v.labels && v.labels["com.docker.stack.namespace"] === stackName.value
            return nameMatch || labelMatch
        })
    } catch (e) {
        console.error("Failed to fetch volumes", e)
    } finally {
        loadingVolumes.value = false
    }
}

onMounted(() => {
    fetchVolumes()
})
</script>
