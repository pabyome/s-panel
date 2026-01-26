<template>
  <div>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-base font-semibold leading-6 text-gray-900">Auto Deployments</h1>
        <p class="mt-2 text-sm text-gray-700">Manage GitHub Webhooks for auto-deploying your projects.</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button @click="openModal" class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Add Deployment</button>
      </div>
    </div>

    <!-- Table -->
    <div class="mt-8 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <table class="min-w-full divide-y divide-gray-300">
            <thead>
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">Name</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Project Path</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Branch</th>
                 <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Post-Deploy</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="deploy in deployments" :key="deploy.id">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">{{ deploy.name }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ deploy.project_path }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ deploy.branch }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 truncate max-w-xs">{{ deploy.post_deploy_command || '-' }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span :class="getStatusClass(deploy.last_status)">{{ deploy.last_status || 'Pending' }}</span>
                     <div v-if="deploy.last_deployed_at" class="text-xs text-gray-400">{{ formatDate(deploy.last_deployed_at) }}</div>
                </td>
                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                  <button @click="showDetails(deploy)" class="text-indigo-600 hover:text-indigo-900 mr-4">Details</button>
                  <button @click="deleteDeployment(deploy.id)" class="text-red-600 hover:text-red-900">Delete</button>
                </td>
              </tr>
              <tr v-if="deployments.length === 0">
                 <td colspan="6" class="text-center py-4 text-gray-500">No deployments configured.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Details/Guide Modal -->
     <BaseModal :isOpen="isDetailsOpen" @close="isDetailsOpen = false" title="Webhook Configuration">
        <div v-if="selectedDeploy">
             <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700">Payload URL</label>
                <div class="mt-1 flex rounded-md shadow-sm">
                    <input type="text" readonly :value="getWebhookUrl(selectedDeploy)" class="block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-gray-50">
                     <button @click="copyToClipboard(getWebhookUrl(selectedDeploy))" class="ml-2 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">Copy</button>
                </div>
            </div>
             <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700">Secret (HMAC)</label>
                <div class="mt-1 flex rounded-md shadow-sm">
                    <input type="text" readonly :value="selectedDeploy.secret" class="block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-gray-50">
                     <button @click="copyToClipboard(selectedDeploy.secret)" class="ml-2 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">Copy</button>
                </div>
            </div>

            <div class="rounded-md bg-blue-50 p-4">
                <h3 class="text-sm font-medium text-blue-800">How to setup in GitHub:</h3>
                <ol class="mt-2 text-sm text-blue-700 list-decimal list-inside">
                    <li>Go to your Repo <strong>Settings</strong> > <strong>Webhooks</strong>.</li>
                    <li>Click <strong>Add webhook</strong>.</li>
                    <li>Paste the <strong>Payload URL</strong> above.</li>
                    <li>Set Content type to <code>application/json</code>.</li>
                    <li>Paste the <strong>Secret</strong> above.</li>
                    <li>Select "Just the push event".</li>
                    <li>Click <strong>Add webhook</strong>.</li>
                </ol>
            </div>
        </div>
        <div class="mt-5 sm:mt-6">
            <button @click="isDetailsOpen = false" type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Done</button>
        </div>
    </BaseModal>

    <!-- Add Modal -->
    <BaseModal :isOpen="isModalOpen" @close="isModalOpen = false" title="Add Deployment">
      <form @submit.prevent="createDeployment" class="space-y-4">
        <div>
          <label class="block text-sm font-medium leading-6 text-gray-900">Name</label>
          <input type="text" v-model="form.name" required class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="My NestJS App">
        </div>
         <div>
          <label class="block text-sm font-medium leading-6 text-gray-900">Project Path</label>
          <PathInput v-model="form.project_path" placeholder="/var/www/my-app" />
        </div>
         <div class="flex gap-4">
             <div class="w-1/2">
                 <label class="block text-sm font-medium leading-6 text-gray-900">Git Branch</label>
                 <input type="text" v-model="form.branch" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
             </div>
             <div class="w-1/2">
                 <label class="block text-sm font-medium leading-6 text-gray-900">Supervisor Process (Optional)</label>
                  <select v-model="form.supervisor_process" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                    <option value="">None</option>
                    <option v-for="proc in processes" :key="proc.name" :value="proc.name">{{ proc.name }}</option>
                  </select>
             </div>
         </div>
          <div>
            <label class="block text-sm font-medium leading-6 text-gray-900">Post-Deploy Command (Optional)</label>
            <input type="text" v-model="form.post_deploy_command" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="npm install && npm run build">
            <p class="mt-1 text-xs text-gray-500">Run after successful git pull. Careful with long running tasks.</p>
        </div>

        <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
          <button type="submit" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2">Create</button>
          <button type="button" @click="isModalOpen = false" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0">Cancel</button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import PathInput from '../components/PathInput.vue'

const deployments = ref([])
const processes = ref([])
const isModalOpen = ref(false)
const isDetailsOpen = ref(false)
const selectedDeploy = ref(null)

const form = reactive({
    name: '',
    project_path: '',
    branch: 'main',
    supervisor_process: '',
    post_deploy_command: ''
})

const fetchDeployments = async () => {
    try {
        const response = await axios.get('/api/v1/deployments/')
        deployments.value = response.data
    } catch (e) {
        console.error("Failed to fetch deployments", e)
    }
}

const fetchProcesses = async () => {
    try {
        const response = await axios.get('/api/v1/supervisor/processes')
        processes.value = response.data
    } catch (e) {
        // quiet fail
    }
}

const openModal = () => {
    form.name = ''
    form.project_path = ''
    form.branch = 'main'
    form.supervisor_process = ''
    form.post_deploy_command = ''
    fetchProcesses()
    isModalOpen.value = true
}

const createDeployment = async () => {
    try {
        await axios.post('/api/v1/deployments/', {
            ...form,
            supervisor_process: form.supervisor_process || null,
            post_deploy_command: form.post_deploy_command || null
        })
        isModalOpen.value = false
        fetchDeployments()
    } catch (e) {
        alert("Failed to create deployment")
    }
}

const deleteDeployment = async (id) => {
    if(!confirm("Are you sure?")) return;
    try {
        await axios.delete(`/api/v1/deployments/${id}`)
        fetchDeployments()
    } catch (e) {
        alert("Failed to delete")
    }
}

const showDetails = (deploy) => {
    selectedDeploy.value = deploy
    isDetailsOpen.value = true
}

const getWebhookUrl = (deploy) => {
    // We use the current window origin.
    // This assumes that the `/api` route is accessible from the same origin
    // (via proxy in dev, or Nginx in prod).
    return `${window.location.origin}${deploy.webhook_url}`
}

const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert("Copied!")
}

const getStatusClass = (status) => {
    if (status === 'success') return 'inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20'
    if (status === 'failed') return 'inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20'
    return 'inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10'
}

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
}

onMounted(() => {
    fetchDeployments()
})
</script>
