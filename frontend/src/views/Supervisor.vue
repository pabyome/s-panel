<template>
  <div>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Supervisor Manager</h1>
        <p class="mt-2 text-sm text-gray-700">Manage background processes and services (Node.js, Python, Workers).</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button @click="fetchProcesses" class="text-indigo-600 hover:text-indigo-900 text-sm">Refresh</button>
      </div>
    </div>

    <!-- Help Section -->
    <div class="mt-6 rounded-md bg-blue-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3 flex-1 md:flex md:justify-between">
          <p class="text-sm text-blue-700">Supervisor must be running locally with XML-RPC enabled.</p>
          <p class="mt-3 text-sm md:ml-6 md:mt-0">
            <button @click="showHelp = !showHelp" class="whitespace-nowrap font-medium text-blue-700 hover:text-blue-600">
              {{ showHelp ? 'Hide Guide' : 'Setup Guide' }}
              <span aria-hidden="true">&rarr;</span>
            </button>
          </p>
        </div>
      </div>
      <div v-if="showHelp" class="mt-4 text-sm text-blue-700 border-t border-blue-200 pt-4">
        <p class="font-bold">How to enable XML-RPC:</p>
        <ol class="list-decimal list-inside mt-2 space-y-1">
          <li>Install Supervisor: <code class="bg-blue-100 px-1 rounded">sudo apt install supervisor</code></li>
          <li>Edit Config: <code class="bg-blue-100 px-1 rounded">/etc/supervisor/supervisord.conf</code></li>
          <li>Add or uncomment these lines to enable port 9001:
            <pre class="bg-gray-800 text-white p-2 rounded mt-2 text-xs">
[inet_http_server]
port = 127.0.0.1:9001
;username = user  (Optional: Basic Auth not supported in MVP)
;password = 123
            </pre>
          </li>
          <li>Restart Supervisor: <code class="bg-blue-100 px-1 rounded">sudo service supervisor restart</code></li>
        </ol>
      </div>
    </div>

    <!-- Table -->
    <div class="mt-8 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">State</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Description</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="process in processes" :key="process.name" class="hover:bg-gray-50 cursor-pointer" @click="goToDetail(process.name)">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ process.name }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span :class="getStatusClass(process.statename)" class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-600/20">
                        {{ process.statename }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ process.description }}</td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6" @click.stop>
                    <button @click="controlProcess(process.name, 'start')" v-if="process.statename === 'STOPPED' || process.statename === 'FATAL'" class="text-green-600 hover:text-green-900 mr-4">Start</button>
                    <button @click="controlProcess(process.name, 'stop')" v-if="process.statename === 'RUNNING'" class="text-red-600 hover:text-red-900 mr-4">Stop</button>
                    <button @click="controlProcess(process.name, 'restart')" v-if="process.statename === 'RUNNING'" class="text-indigo-600 hover:text-indigo-900">Restart</button>
                  </td>
                </tr>
                 <tr v-if="processes.length === 0">
                    <td colspan="4" class="text-center py-4 text-gray-500">
                        No processes found or Supervisor not running.
                    </td>
                 </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const processes = ref([])
const showHelp = ref(false)
const router = useRouter()

const fetchProcesses = async () => {
    try {
        const response = await axios.get('/api/v1/supervisor/processes')
        processes.value = response.data
    } catch (e) {
        console.error("Failed to fetch processes", e)
    }
}

const controlProcess = async (name, action) => {
    try {
        await axios.post(`/api/v1/supervisor/processes/${name}/${action}`)
        fetchProcesses()
    } catch (e) {
        console.error(`Failed to ${action} process`, e)
        alert(`Failed to ${action} process`)
    }
}

const goToDetail = (name) => {
    router.push(`/supervisor/${name}`)
}

const getStatusClass = (status) => {
    switch (status) {
        case 'RUNNING': return 'bg-green-50 text-green-700'
        case 'STOPPED': return 'bg-gray-50 text-gray-700'
        case 'FATAL':
        case 'BACKOFF': return 'bg-red-50 text-red-700'
        default: return 'bg-yellow-50 text-yellow-700'
    }
}

onMounted(() => {
    fetchProcesses()
})
</script>
