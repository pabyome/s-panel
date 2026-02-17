<template>
  <div class="h-full flex flex-col">
    <div class="border-b border-gray-200 mb-6 px-1">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="[
            currentTab === tab.id
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <div v-else-if="!deployment" class="flex-1 flex flex-col items-center justify-center text-center p-6">
      <div class="rounded-full bg-yellow-100 p-3 mb-4">
        <svg class="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">No Deployment Configuration</h3>
      <p class="mt-1 text-sm text-gray-500">This site is marked as Laravel but has no deployment configuration linked.</p>
      <button @click="createDeployment" class="mt-4 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
        Create Deployment Config
      </button>
    </div>

    <div v-else class="flex-1 overflow-y-auto pr-2">
      <StackTab v-if="currentTab === 'stack'" :website="website" :deployment="deployment" @refresh="fetchDeployment" />
      <EcosystemTab v-if="currentTab === 'ecosystem'" :website="website" :deployment="deployment" />
      <DeploymentTab v-if="currentTab === 'deployment'" :website="website" :deployment="deployment" />
      <LogsTab v-if="currentTab === 'logs'" :website="website" :deployment="deployment" />
      <BackupsTab v-if="currentTab === 'backups'" :website="website" :deployment="deployment" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import StackTab from './StackTab.vue'
import EcosystemTab from './EcosystemTab.vue'
import DeploymentTab from './DeploymentTab.vue'
import LogsTab from './LogsTab.vue'
import BackupsTab from './BackupsTab.vue'
import { useToast } from '../../composables/useToast'

const props = defineProps({
  website: {
    type: Object,
    required: true
  }
})

const toast = useToast()
const currentTab = ref('stack')
const deployment = ref(null)
const loading = ref(true)

const tabs = [
  { id: 'stack', name: 'Stack View' },
  { id: 'ecosystem', name: 'Ecosystem' },
  { id: 'deployment', name: 'Deployment' },
  { id: 'logs', name: 'Logs' },
  // { id: 'backups', name: 'Backups' } // Implement later
]

const fetchDeployment = async () => {
  if (!props.website.deployment_id) {
    deployment.value = null
    loading.value = false
    return
  }

  loading.value = true
  try {
    const { data } = await axios.get(`/api/v1/deployments/${props.website.deployment_id}`)
    deployment.value = data
  } catch (e) {
    console.error("Failed to fetch deployment", e)
    toast.error("Failed to fetch deployment configuration")
  } finally {
    loading.value = false
  }
}

const createDeployment = async () => {
    // Create a default deployment config
    try {
        const { data: newDeployment } = await axios.post('/api/v1/deployments/', {
            name: props.website.name,
            project_path: props.website.project_path,
            branch: 'main',
            is_laravel: true,
            laravel_worker_replicas: 1,
            laravel_scheduler_enabled: true
        })

        // Link to website
        await axios.put(`/api/v1/websites/${props.website.id}`, {
            deployment_id: newDeployment.id
        })

        // Update local prop/state by emitting or fetching?
        // We can't mutate prop. But we can fetch deployment using new ID.
        // Also emit update to parent to refresh website data.

        // Simulating prop update locally for now or just fetch
        deployment.value = newDeployment

        // Emit to parent to refresh website list
        // emit('refresh') // If we had emit

        toast.success("Deployment configuration created")
    } catch (e) {
        console.error("Failed to create deployment", e)
        toast.error("Failed to create deployment")
    }
}

watch(() => props.website.id, () => {
  fetchDeployment()
})

onMounted(() => {
  fetchDeployment()
})
</script>
