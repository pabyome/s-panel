<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900">Redis Manager</h1>

    <div v-if="loading" class="mt-4 text-gray-500">Loading Redis status...</div>
    <div v-else-if="error" class="mt-4 p-4 rounded-md bg-red-50 text-red-700">
      <div class="flex">
        <svg class="h-5 w-5 text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>{{ error }}</span>
      </div>
       <p class="mt-2 text-sm text-red-600">Please ensure Redis is installed and running.</p>
    </div>

    <div v-else class="mt-6">
      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <a href="#" @click.prevent="activeTab = 'overview'" :class="[activeTab === 'overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']">Overview</a>
          <a href="#" @click.prevent="activeTab = 'config'" :class="[activeTab === 'config' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']">Configuration</a>
          <a href="#" @click.prevent="activeTab = 'explorer'" :class="[activeTab === 'explorer' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']">Data Explorer</a>
        </nav>
      </div>

      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="mt-6">
         <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
             <div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
                <dt class="text-sm font-medium text-gray-500 truncate">Version</dt>
                <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ info.redis_version }}</dd>
             </div>
             <div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
                <dt class="text-sm font-medium text-gray-500 truncate">Clients Connected</dt>
                <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ info.connected_clients }}</dd>
             </div>
             <div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
                <dt class="text-sm font-medium text-gray-500 truncate">Memory Used</dt>
                <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ info.used_memory_human }}</dd>
             </div>
             <div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
                <dt class="text-sm font-medium text-gray-500 truncate">Uptime</dt>
                <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ formatUptime(info.uptime_in_seconds) }}</dd>
             </div>
         </div>
         <div class="mt-6">
             <button @click="confirmFlushDb" :disabled="isFlushing" class="inline-flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded shadow hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed">
               <svg v-if="isFlushing" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
               {{ isFlushing ? 'Flushing...' : 'Flush All Data' }}
             </button>
         </div>
      </div>

      <!-- Config Tab -->
      <div v-if="activeTab === 'config'" class="mt-6">
         <div v-if="configError" class="mb-4 text-red-600">{{ configError }}</div>
         <form @submit.prevent="saveConfig" class="bg-white shadow sm:rounded-lg p-6 space-y-4 max-w-2xl">
            <div class="grid grid-cols-2 gap-4">
                <div>
                   <label class="block text-sm font-medium text-gray-700">Bind IP</label>
                   <input v-model="configForm.bind" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                   <p class="text-xs text-gray-500 mt-1">Careful: 0.0.0.0 exposes to all</p>
                </div>
                <div>
                   <label class="block text-sm font-medium text-gray-700">Port</label>
                   <input v-model="configForm.port" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                </div>
                 <div>
                   <label class="block text-sm font-medium text-gray-700">Detailed Timeout (0 = off)</label>
                   <input v-model="configForm.timeout" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                </div>
                 <div>
                   <label class="block text-sm font-medium text-gray-700">Max Clients</label>
                   <input v-model="configForm.maxclients" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                </div>
                 <div>
                   <label class="block text-sm font-medium text-gray-700">Max Memory</label>
                   <input v-model="configForm.maxmemory" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                   <p class="text-xs text-gray-500 mt-1">e.g. 2gb, 512mb. 0 = no limit.</p>
                </div>
                 <div>
                   <label class="block text-sm font-medium text-gray-700">Databases</label>
                   <input v-model="configForm.databases" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
                </div>
                 <div class="col-span-2">
                   <label class="block text-sm font-medium text-gray-700">Require Pass</label>
                   <input v-model="configForm.requirepass" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" placeholder="Leave empty for no password">
                </div>
            </div>
            <div class="flex justify-end pt-4">
                <button type="submit" :disabled="isSavingConfig" class="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg v-if="isSavingConfig" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  {{ isSavingConfig ? 'Saving...' : 'Save Config' }}
                </button>
            </div>
         </form>
      </div>

       <!-- Explorer Tab -->
      <div v-if="activeTab === 'explorer'" class="mt-6">
          <div class="flex gap-4 mb-4">
              <input v-model="keyPattern" @keyup.enter="loadKeys" type="text" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2" placeholder="Search keys (e.g. *)">
              <button @click="loadKeys" class="bg-gray-100 px-4 py-2 rounded border hover:bg-gray-200">Search</button>
          </div>

          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <ul class="divide-y divide-gray-200">
                <li v-for="key in keys" :key="key" class="px-4 py-4 flex items-center justify-between sm:px-6 hover:bg-gray-50 cursor-pointer" @click="inspectKey(key)">
                    <span class="text-sm font-medium text-indigo-600 truncate">{{ key }}</span>
                     <button @click.stop="confirmDeleteKey(key)" :disabled="deletingKey !== null" class="inline-flex items-center gap-1 text-red-600 hover:text-red-900 text-sm disabled:opacity-50 disabled:cursor-not-allowed">
                       <svg v-if="deletingKey === key" class="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                       {{ deletingKey === key ? 'Deleting...' : 'Delete' }}
                     </button>
                </li>
                 <li v-if="keys.length === 0" class="px-4 py-4 text-gray-500 text-sm text-center">No keys found.</li>
            </ul>
          </div>

          <!-- Key Detail Modal (Inline) -->
          <div v-if="selectedKey" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
             <div class="bg-white rounded-lg p-6 max-w-lg w-full">
                 <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Key: {{ selectedKey.key }}</h3>
                 <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">Type</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedKey.type }}</dd>
                    </div>
                    <div class="sm:col-span-1">
                      <dt class="text-sm font-medium text-gray-500">TTL</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ selectedKey.ttl }}</dd>
                    </div>
                     <div class="sm:col-span-2">
                      <dt class="text-sm font-medium text-gray-500">Value</dt>
                      <dd class="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded overflow-auto max-h-60">{{ selectedKey.value }}</dd>
                    </div>
                 </dl>
                 <div class="mt-5 sm:mt-6">
                    <button @click="selectedKey = null" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 sm:text-sm">Close</button>
                 </div>
             </div>
          </div>
      </div>

    </div>

    <!-- Delete Key Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteKeyModalOpen"
      type="danger"
      title="Delete Key"
      :message="`Are you sure you want to delete key '${keyToDelete}'?`"
      confirmText="Delete"
      :isLoading="deletingKey !== null"
      @confirm="deleteKey"
      @cancel="isDeleteKeyModalOpen = false"
    />

    <!-- Flush DB Confirmation Modal -->
    <ConfirmModal
      :isOpen="isFlushDbModalOpen"
      type="danger"
      title="Flush Database"
      message="Are you sure? This will delete ALL keys in the current database. This action cannot be undone."
      confirmText="Flush All"
      :isLoading="isFlushing"
      @confirm="flushDb"
      @cancel="isFlushDbModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const activeTab = ref('overview')
const loading = ref(true)
const error = ref(null)
const info = ref({})
const configError = ref(null)
const configForm = ref({
    bind: '',
    port: 6379,
    timeout: 0,
    maxclients: 10000,
    maxmemory: '',
    databases: 16,
    requirepass: ''
})
const keys = ref([])
const keyPattern = ref('*')
const selectedKey = ref(null)

// Modal states
const isDeleteKeyModalOpen = ref(false)
const isFlushDbModalOpen = ref(false)
const keyToDelete = ref(null)

// Loading states
const isSavingConfig = ref(false)
const isFlushing = ref(false)
const deletingKey = ref(null)

const API_BASE = window.location.origin + '/api/v1/redis' // Uses proxy in dev

const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (3600*24));
    const hours = Math.floor(seconds % (3600*24) / 3600);
    return `${days}d ${hours}h`;
}

const fetchInfo = async () => {
    try {
        const res = await fetch(`${API_BASE}/info`, {
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        if (!res.ok) throw new Error("Failed to fetch info")
        info.value = await res.json()
        if (info.value.error) {
             error.value = info.value.error
        }
    } catch (e) {
        error.value = e.message
    }
}

const fetchConfig = async () => {
    try {
        const res = await fetch(`${API_BASE}/config`, {
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        const data = await res.json()
        if (data.config) {
            // Merge defaults
            configForm.value = { ...configForm.value, ...data.config }
        } else if (data.error) {
            configError.value = data.error
        }
    } catch (e) {
        console.error(e)
    }
}

const saveConfig = async () => {
    if (isSavingConfig.value) return
    isSavingConfig.value = true
    try {
        const res = await fetch(`${API_BASE}/config`, {
            method: 'PUT',
             headers: {
                 'Content-Type': 'application/json',
                 'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(configForm.value)
        })
        if (!res.ok) toast.error("Failed to save config")
        else toast.success("Config saved! You may need to restart Redis for changes to apply.")
    } catch (e) {
        toast.error(e.message)
    } finally {
        isSavingConfig.value = false
    }
}

const loadKeys = async () => {
    try {
        const res = await fetch(`${API_BASE}/keys?pattern=${encodeURIComponent(keyPattern.value)}`, {
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        const data = await res.json()
        keys.value = data.keys || []
    } catch (e) {
        toast.error(e.message)
    }
}

const inspectKey = async (key) => {
     try {
        // Handle slashes in key by encoding? or just let path param handle if configured
        // Our backend: /keys/{key:path}
        const res = await fetch(`${API_BASE}/keys/${key}`, {
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        selectedKey.value = await res.json()
    } catch (e) {
        toast.error(e.message)
    }
}

const confirmDeleteKey = (key) => {
    keyToDelete.value = key
    isDeleteKeyModalOpen.value = true
}

const deleteKey = async () => {
    if (!keyToDelete.value || deletingKey.value) return
    deletingKey.value = keyToDelete.value
    try {
        const res = await fetch(`${API_BASE}/keys/${keyToDelete.value}`, {
             method: 'DELETE',
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        if(res.ok) {
            toast.success('Key deleted successfully')
            isDeleteKeyModalOpen.value = false
            loadKeys()
        }
    } catch (e) {
        toast.error(e.message)
    } finally {
        deletingKey.value = null
        keyToDelete.value = null
    }
}

const confirmFlushDb = () => {
    isFlushDbModalOpen.value = true
}

const flushDb = async () => {
    if (isFlushing.value) return
    isFlushing.value = true
    try {
        const res = await fetch(`${API_BASE}/flush`, {
             method: 'POST',
             headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        if(res.ok) {
            toast.success("Database flushed")
            isFlushDbModalOpen.value = false
            loadKeys()
            fetchInfo()
        }
    } catch (e) {
        toast.error(e.message)
    } finally {
        isFlushing.value = false
    }
}

onMounted(async () => {
    await fetchInfo()
    loading.value = false
    if (!error.value) {
        fetchConfig()
        loadKeys()
    }
})
</script>
