<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="mt-1 text-sm text-gray-500">System configuration and updates</p>
      </div>
    </div>

    <!-- System Update Card -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
        <h3 class="text-base font-semibold text-gray-900">System Update</h3>
      </div>
      <div class="p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-900">Current Version</p>
            <p class="text-xs text-gray-500 font-mono mt-1">{{ updateInfo.current_commit || 'Unknown' }}</p>
          </div>
          <div class="text-right">
             <p class="text-sm font-medium text-gray-900">Status</p>
             <p :class="[
               updateInfo.updates_available ? 'text-amber-600' : 'text-emerald-600',
               'text-sm font-medium'
             ]">
               {{ updateInfo.message || 'Ready to check' }}
             </p>
          </div>
        </div>

        <div class="mt-6 flex items-center gap-3">
          <button
            @click="checkForUpdates"
            :disabled="checking"
            class="rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
          >
            {{ checking ? 'Checking...' : 'Check for Updates' }}
          </button>

          <button
            v-if="updateInfo.updates_available"
            @click="applyUpdate"
            :disabled="updating"
            class="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500 disabled:opacity-50"
          >
           {{ updating ? 'Updating...' : 'Update & Restart' }}
          </button>
        </div>

        <div v-if="updateInfo.updates_available" class="mt-4 rounded-lg bg-amber-50 p-3 text-xs text-amber-700">
           Latest commit: <span class="font-mono">{{ updateInfo.latest_commit }}</span>.
           Clicking Update will pull the latest code, install dependencies, rebuild the frontend, and restart the service. The panel will be unavailable for a few minutes.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const checking = ref(false)
const updating = ref(false)
const updateInfo = ref({
    updates_available: false,
    current_commit: '',
    latest_commit: '',
    message: ''
})

const checkForUpdates = async () => {
    checking.value = true
    try {
        const response = await axios.get('/api/v1/system/update/check')
        updateInfo.value = response.data
    } catch (e) {
        console.error("Failed to check for updates", e)
        updateInfo.value.message = "Failed to check (Git Error)"
    } finally {
        checking.value = false
    }
}

const applyUpdate = async () => {
    if (!confirm("Are you sure? This will restart the server.")) return
    updating.value = true
    try {
        await axios.post('/api/v1/system/update/apply')
        alert("Update started! expecting service restart. Please reload this page in 2-3 minutes.")
    } catch (e) {
        alert("Failed to start update")
        updating.value = false
    }
}

onMounted(() => {
    checkForUpdates()
})
</script>
