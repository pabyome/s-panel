<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Backups</h1>
        <p class="mt-1 text-sm text-gray-500">Manage database and system backups</p>
      </div>
      <button
        @click="createBackup"
        :disabled="creating"
        class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-70"
      >
        <svg v-if="creating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        {{ creating ? 'Creating...' : 'Create Backup' }}
      </button>
    </div>

    <!-- Backups List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div v-if="backups.length === 0" class="flex flex-col items-center justify-center py-12 px-4">
        <div class="rounded-xl bg-gray-100 p-3">
          <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
          </svg>
        </div>
        <p class="mt-3 text-sm font-medium text-gray-900">No backups found</p>
        <p class="mt-1 text-sm text-gray-500">Create your first backup to secure your data</p>
      </div>

      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filename</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            <th scope="col" class="relative px-6 py-3">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="backup in backups" :key="backup.filename" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ backup.filename }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatBytes(backup.size_bytes) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ new Date(backup.created_at).toLocaleString() }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex items-center justify-end gap-3">
                <button
                  @click="restoreBackup(backup)"
                  class="text-indigo-600 hover:text-indigo-900 font-medium"
                >
                  Restore
                </button>
                <button
                  @click="deleteBackup(backup)"
                  class="text-red-600 hover:text-red-900 font-medium"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const backups = ref([])
const creating = ref(false)

const formatBytes = (bytes, decimals = 2) => {
    if (!+bytes) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const fetchBackups = async () => {
    try {
        const response = await axios.get('/api/v1/backups/')
        backups.value = response.data
    } catch (e) {
        console.error("Failed to fetch backups", e)
    }
}

const createBackup = async () => {
    creating.value = true
    try {
        await axios.post('/api/v1/backups/')
        fetchBackups()
    } catch (e) {
        alert("Failed to create backup")
        console.error(e)
    } finally {
        creating.value = false
    }
}

const deleteBackup = async (backup) => {
    if (!confirm(`Are you sure you want to delete ${backup.filename}?`)) return
    try {
        await axios.delete(`/api/v1/backups/${backup.filename}`)
        fetchBackups()
    } catch (e) {
        console.error("Failed to delete backup", e)
    }
}

const restoreBackup = async (backup) => {
    if (!confirm(`WARNING: This will overwrite the current database with ${backup.filename}. Are you sure?`)) return
    try {
        await axios.post(`/api/v1/backups/${backup.filename}/restore`)
        alert("Restore successful. The service may need to be restarted.")
        // Ideally, force logout or reload
        window.location.reload()
    } catch (e) {
        console.error("Failed to restore backup", e)
        alert("Restore failed")
    }
}

onMounted(() => {
    fetchBackups()
})
</script>
