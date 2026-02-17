<template>
  <div class="space-y-6">
    <!-- .env Editor -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">Environment Variables</h3>
          <p class="text-sm text-gray-500">Edit your .env file. Saving will trigger a config refresh.</p>
        </div>
        <button
          @click="saveEnv"
          :disabled="savingEnv"
          class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          <svg v-if="savingEnv" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ savingEnv ? 'Saving...' : 'Save & Refresh' }}
        </button>
      </div>

      <div class="relative rounded-md shadow-sm">
        <textarea
          v-model="envContent"
          rows="12"
          class="block w-full rounded-lg border-0 bg-gray-50 py-3 px-4 font-mono text-sm text-gray-900 shadow-inner ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
          spellcheck="false"
          placeholder="APP_NAME=Laravel..."
        ></textarea>
      </div>
    </div>

    <!-- Artisan Runner -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-2xl p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Artisan Command Runner</h3>
      <div class="flex gap-2">
        <div class="flex-none flex items-center px-3 rounded-l-lg border border-r-0 border-gray-200 bg-gray-50 text-gray-500 font-mono text-sm">
          php artisan
        </div>
        <input
          v-model="artisanCommand"
          @keyup.enter="runArtisan"
          type="text"
          class="flex-1 min-w-0 block w-full rounded-none rounded-r-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono"
          placeholder="migrate:status"
        >
        <button
          @click="runArtisan"
          :disabled="runningArtisan || !artisanCommand"
          class="ml-2 inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-50"
        >
          {{ runningArtisan ? 'Running...' : 'Run Command' }}
        </button>
      </div>

      <!-- Output Console -->
      <transition name="fade">
        <div v-if="artisanOutput || artisanError" class="mt-4 rounded-lg bg-gray-900 p-4 font-mono text-xs text-gray-300 overflow-x-auto">
          <div v-if="artisanError" class="text-red-400 mb-2 font-bold">Error: {{ artisanError }}</div>
          <pre class="whitespace-pre-wrap">{{ artisanOutput }}</pre>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../composables/useToast'

const props = defineProps({
  website: Object,
  deployment: Object
})

const toast = useToast()
const envContent = ref('')
const savingEnv = ref(false)
const artisanCommand = ref('')
const runningArtisan = ref(false)
const artisanOutput = ref('')
const artisanError = ref('')

const fetchEnv = async () => {
    try {
        const path = `${props.website.project_path}/.env`
        // Use FileManager API or a specific one if implemented
        // Assuming FileManager API: /api/v1/files/content?path=...
        const { data } = await axios.get('/api/v1/files/content', { params: { path } })
        envContent.value = data.content
    } catch (e) {
        console.error("Failed to fetch .env", e)
        // If 404, maybe create one?
        if (e.response?.status === 404) {
            envContent.value = "# .env file not found\nAPP_NAME=Laravel"
        } else {
             toast.error("Failed to load .env file")
        }
    }
}

const saveEnv = async () => {
    savingEnv.value = true
    try {
        const path = `${props.website.project_path}/.env`
        await axios.post('/api/v1/files/content', {
            path,
            content: envContent.value
        })
        toast.success(".env saved. Don't forget to deploy or restart to apply changes.")

        // Optionally trigger 'config:cache' via artisan?
        // User asked for "automatically triggers a 'Config Refresh' across all containers"
        // We can try to run artisan config:cache
        await axios.post(`/api/v1/websites/${props.website.id}/artisan`, {
            command: 'config:cache'
        })
        toast.success("Config cache refreshed")

    } catch (e) {
        console.error("Failed to save .env", e)
        toast.error("Failed to save .env file")
    } finally {
        savingEnv.value = false
    }
}

const runArtisan = async () => {
    if (!artisanCommand.value) return

    runningArtisan.value = true
    artisanOutput.value = ''
    artisanError.value = ''

    try {
        const { data } = await axios.post(`/api/v1/websites/${props.website.id}/artisan`, null, {
            params: { command: artisanCommand.value }
        })

        if (data.success) {
            artisanOutput.value = data.output || "Command executed successfully (no output)"
            toast.success("Command executed")
        } else {
            artisanError.value = data.output || "Command failed"
            toast.error("Command failed")
        }
    } catch (e) {
        console.error("Artisan error", e)
        artisanError.value = e.response?.data?.detail || "Failed to execute command"
        toast.error("Failed to execute command")
    } finally {
        runningArtisan.value = false
    }
}

onMounted(() => {
    fetchEnv()
})
</script>
