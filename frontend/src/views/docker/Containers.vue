<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Containers</h1>
        <p class="mt-1 text-sm text-gray-500">Manage Docker containers</p>
      </div>
      <div class="flex gap-2">
        <button
            @click="isCreateModalOpen = true"
            class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5"
          >
            <PlusIcon class="h-4 w-4" />
            Run Container
          </button>
        <button
          @click="fetchContainers"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Container List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ports</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="container in containers" :key="container.id">
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ container.name }}</div>
                <div class="text-xs text-gray-500" title="Container ID">{{ container.short_id }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ container.image }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <span :class="[
                  'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset',
                  container.status === 'running' ? 'bg-green-50 text-green-700 ring-green-600/20' :
                  container.status === 'exited' ? 'bg-gray-50 text-gray-600 ring-gray-500/10' :
                  container.status === 'paused' ? 'bg-yellow-50 text-yellow-800 ring-yellow-600/20' :
                  'bg-gray-50 text-gray-800 ring-gray-500/20'
                ]">
                  {{ container.status }}
                </span>
              </td>
               <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">
                    <div v-for="(bindings, port) in container.ports" :key="port">
                        {{ bindings ? bindings[0].HostPort + ':' : '' }}{{ port }}
                    </div>
                </div>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button v-if="container.status !== 'running'" @click="performAction(container.id, 'start')" class="text-green-600 hover:text-green-900" title="Start">
                    <PlayIcon class="h-5 w-5" />
                  </button>
                  <button v-if="container.status === 'running'" @click="performAction(container.id, 'stop')" class="text-red-600 hover:text-red-900" title="Stop">
                    <StopIcon class="h-5 w-5" />
                  </button>
                  <button v-if="container.status === 'running'" @click="performAction(container.id, 'restart')" class="text-indigo-600 hover:text-indigo-900" title="Restart">
                    <ArrowPathIcon class="h-5 w-5" />
                  </button>
                  <button v-if="container.status === 'running'" @click="performAction(container.id, 'pause')" class="text-yellow-600 hover:text-yellow-900" title="Pause">
                    <PauseIcon class="h-5 w-5" />
                  </button>
                  <button v-if="container.status === 'paused'" @click="performAction(container.id, 'unpause')" class="text-green-600 hover:text-green-900" title="Unpause">
                    <PlayIcon class="h-5 w-5" />
                  </button>
                  <button @click="showLogs(container)" class="text-gray-600 hover:text-gray-900" title="Logs">
                    <DocumentTextIcon class="h-5 w-5" />
                  </button>
                   <button v-if="container.status !== 'running'" @click="performAction(container.id, 'remove')" class="text-red-600 hover:text-red-900" title="Remove">
                    <TrashIcon class="h-5 w-5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="containers.length === 0 && !isLoading">
                <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                    No containers found.
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Logs Modal -->
    <div v-if="selectedContainer" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex min-h-screen items-end justify-center px-4 pb-20 pt-4 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeLogs"></div>
        <span class="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>
        <div class="relative inline-block transform overflow-hidden rounded-lg bg-white text-left align-bottom shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:align-middle">
          <div class="bg-gray-900 px-4 py-3 sm:px-6 flex justify-between items-center">
            <h3 class="text-lg font-medium leading-6 text-white" id="modal-title">
              Logs: {{ selectedContainer.name }}
            </h3>
            <button @click="closeLogs" class="text-gray-400 hover:text-white">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>
          <div class="bg-gray-900 p-4 h-96 overflow-auto font-mono text-xs text-gray-300 whitespace-pre-wrap">
             <div v-if="logsLoading">Loading logs...</div>
             <div v-else>{{ logsContent }}</div>
          </div>
           <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
            <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto" @click="closeLogs">Close</button>
            <button type="button" class="mr-3 inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:mt-0 sm:w-auto" @click="refreshLogs">Refresh</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
     <div v-if="isCreateModalOpen" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-screen items-end justify-center px-4 pb-20 pt-4 text-center sm:block sm:p-0">
             <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="isCreateModalOpen = false"></div>
             <span class="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>
             <div class="relative inline-block transform overflow-hidden rounded-lg bg-white text-left align-bottom shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:align-middle">
                <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                    <h3 class="text-lg font-semibold leading-6 text-gray-900 mb-4">Run New Container</h3>
                    <form @submit.prevent="createContainer">
                        <div class="space-y-4">
                            <div>
                                <label for="image" class="block text-sm font-medium text-gray-700">Image</label>
                                <input id="image" v-model="createForm.image" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300" placeholder="nginx:latest">
                            </div>
                            <div>
                                <label for="name" class="block text-sm font-medium text-gray-700">Name (Optional)</label>
                                <input id="name" v-model="createForm.name" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300" placeholder="my-nginx">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Host Port</label>
                                    <input v-model.number="createForm.hostPort" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300" placeholder="8080">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Container Port</label>
                                    <input v-model.number="createForm.containerPort" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300" placeholder="80">
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Restart Policy</label>
                                <select v-model="createForm.restartPolicy" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300">
                                    <option value="no">No</option>
                                    <option value="always">Always</option>
                                    <option value="unless-stopped">Unless Stopped</option>
                                    <option value="on-failure">On Failure</option>
                                </select>
                            </div>

                            <!-- Environment Variables -->
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Environment Variables</label>
                                <div v-for="(env, index) in createForm.envVars" :key="'env-'+index" class="flex gap-2 mt-2">
                                    <input v-model="env.key" type="text" placeholder="KEY" class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300">
                                    <input v-model="env.value" type="text" placeholder="VALUE" class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300">
                                    <button type="button" @click="removeEnv(index)" class="text-red-600 hover:text-red-800"><TrashIcon class="h-5 w-5"/></button>
                                </div>
                                <button type="button" @click="addEnv" class="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-500 inline-flex items-center gap-1">
                                    <PlusIcon class="h-3 w-3" /> Add Variable
                                </button>
                            </div>

                            <!-- Volumes -->
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Volumes</label>
                                <div v-for="(vol, index) in createForm.volumes" :key="'vol-'+index" class="flex gap-2 mt-2">
                                    <input v-model="vol.hostPath" type="text" placeholder="/host/path" class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300">
                                    <input v-model="vol.containerPath" type="text" placeholder="/container/path" class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 ring-1 ring-inset ring-gray-300">
                                    <button type="button" @click="removeVol(index)" class="text-red-600 hover:text-red-800"><TrashIcon class="h-5 w-5"/></button>
                                </div>
                                <button type="button" @click="addVol" class="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-500 inline-flex items-center gap-1">
                                    <PlusIcon class="h-3 w-3" /> Add Volume
                                </button>
                            </div>
                        </div>
                        <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                            <button type="submit" :disabled="isCreating" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2 disabled:opacity-50">
                                {{ isCreating ? 'Creating...' : 'Run' }}
                            </button>
                            <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0" @click="isCreateModalOpen = false">Cancel</button>
                        </div>
                    </form>
                </div>
             </div>
        </div>
     </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ArrowPathIcon, PlayIcon, StopIcon, DocumentTextIcon, XMarkIcon, TrashIcon, PlusIcon, PauseIcon } from '@heroicons/vue/24/outline'
import axios from 'axios'

const containers = ref([])
const isLoading = ref(false)
const selectedContainer = ref(null)
const logsContent = ref('')
const logsLoading = ref(false)
const isCreateModalOpen = ref(false)
const isCreating = ref(false)

const createForm = reactive({
    image: '',
    name: '',
    hostPort: null,
    containerPort: null,
    restartPolicy: 'unless-stopped',
    envVars: [],
    volumes: []
})

const fetchContainers = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/containers/')
    containers.value = response.data
  } catch (error) {
    console.error('Error fetching containers:', error)
  } finally {
    isLoading.value = false
  }
}

const performAction = async (id, action) => {
  try {
    await axios.post(`/api/v1/containers/${id}/${action}`)
    fetchContainers() // Refresh list
  } catch (error) {
    console.error(`Error performing ${action}:`, error)
    alert(`Failed to ${action} container`)
  }
}

const showLogs = async (container) => {
  selectedContainer.value = container
  await fetchLogs(container.id)
}

const fetchLogs = async (id) => {
  logsLoading.value = true
  try {
    const response = await axios.get(`/api/v1/containers/${id}/logs?tail=200`)
    logsContent.value = response.data.logs
  } catch (error) {
    console.error('Error fetching logs:', error)
    logsContent.value = 'Error loading logs.'
  } finally {
    logsLoading.value = false
  }
}

const refreshLogs = () => {
    if (selectedContainer.value) {
        fetchLogs(selectedContainer.value.id)
    }
}

const closeLogs = () => {
  selectedContainer.value = null
  logsContent.value = ''
}

const addEnv = () => createForm.envVars.push({ key: '', value: '' })
const removeEnv = (index) => createForm.envVars.splice(index, 1)
const addVol = () => createForm.volumes.push({ hostPath: '', containerPath: '' })
const removeVol = (index) => createForm.volumes.splice(index, 1)

const createContainer = async () => {
    isCreating.value = true
    try {
        const payload = {
            image: createForm.image,
            name: createForm.name || undefined,
            restart_policy: createForm.restartPolicy,
            ports: [],
            env_vars: {},
            volumes: []
        }

        if (createForm.hostPort && createForm.containerPort) {
            payload.ports.push({
                host_port: createForm.hostPort,
                container_port: createForm.containerPort,
                protocol: 'tcp'
            })
        }

        createForm.envVars.forEach(env => {
            if (env.key) payload.env_vars[env.key] = env.value
        })

        createForm.volumes.forEach(vol => {
            if (vol.hostPath && vol.containerPath) {
                payload.volumes.push({
                    host_path: vol.hostPath,
                    container_path: vol.containerPath,
                    mode: 'rw'
                })
            }
        })

        await axios.post('/api/v1/containers/run', payload)
        isCreateModalOpen.value = false
        // Reset form
        createForm.image = ''
        createForm.name = ''
        createForm.hostPort = null
        createForm.containerPort = null
        createForm.restartPolicy = 'unless-stopped'
        createForm.envVars = []
        createForm.volumes = []

        fetchContainers()
    } catch (e) {
        console.error("Failed to create container", e)
        alert("Failed to create container: " + (e.response?.data?.detail || e.message))
    } finally {
        isCreating.value = false
    }
}

onMounted(() => {
  fetchContainers()
})
</script>
