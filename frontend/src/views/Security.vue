<template>
  <div>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Security</h1>
        <p class="mt-2 text-sm text-gray-700">Manage firewall rules (UFW). Ensure Port 22 and 8000 are ALLOWED so you don't lock yourself out!</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button @click="openCreateModal" type="button" class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          Add Rule
        </button>
      </div>
    </div>

    <!-- Warning Alert -->
    <div class="rounded-md bg-yellow-50 p-4 mt-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <!-- Heroicon name: mini/exclamation-triangle -->
          <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">Caution</h3>
          <div class="mt-2 text-sm text-yellow-700">
            <p>Changes apply immediately to the system firewall. Incorrect rules can block access.</p>
          </div>
        </div>
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
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">ID</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Port/Protocol</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Action</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">From</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Delete</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="rule in rules" :key="rule.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ rule.id }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.to_port }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span :class="[rule.action === 'ALLOW' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700', 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-600/20']">{{ rule.action }}</span>
                  </td>
                   <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.from_ip }}</td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button @click="deleteRule(rule.id)" class="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
                 <tr v-if="rules.length === 0">
                    <td colspan="5" class="text-center py-4 text-gray-500">
                        No active rules or UFW is inactive.
                        <br>
                        <span class="text-xs text-gray-400">(Dev Note: UFW might not be available on MacOS)</span>
                    </td>
                 </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <BaseModal :isOpen="isModalOpen" title="Add Firewall Rule" @close="closeModal" @confirm="createRule">
      <form class="space-y-4">
        <div>
          <label for="port" class="block text-sm font-medium leading-6 text-gray-900">Port</label>
          <div class="mt-2">
            <input type="number" v-model="form.port" id="port" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="80">
          </div>
        </div>
        <div>
          <label for="protocol" class="block text-sm font-medium leading-6 text-gray-900">Protocol</label>
           <div class="mt-2">
            <select v-model="form.protocol" id="protocol" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>
        </div>
         <div>
          <label for="action" class="block text-sm font-medium leading-6 text-gray-900">Action</label>
           <div class="mt-2">
            <select v-model="form.action" id="action" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
              <option value="allow">Allow</option>
              <option value="deny">Deny</option>
            </select>
          </div>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'

const rules = ref([])
const isModalOpen = ref(false)
const form = reactive({
    port: 80,
    protocol: 'tcp',
    action: 'allow'
})

const fetchRules = async () => {
    try {
        const response = await axios.get('/api/v1/firewall/')
        rules.value = response.data
    } catch (e) {
        console.error("Failed to fetch rules", e)
    }
}

const createRule = async () => {
    try {
        await axios.post('/api/v1/firewall/', form)
        closeModal()
        // Wait briefly for UFW to apply
        setTimeout(fetchRules, 500)
    } catch (e) {
        console.error("Failed to create rule", e)
        alert("Failed to create rule")
    }
}

const deleteRule = async (id) => {
    if(!confirm(`Delete rule ${id}?`)) return;
    try {
        await axios.delete(`/api/v1/firewall/${id}`)
        setTimeout(fetchRules, 500)
    } catch (e) {
        console.error("Failed to delete rule", e)
    }
}

const openCreateModal = () => {
    form.port = 80
    form.protocol = 'tcp'
    form.action = 'allow'
    isModalOpen.value = true
}

const closeModal = () => {
    isModalOpen.value = false
}

onMounted(() => {
    fetchRules()
})
</script>
