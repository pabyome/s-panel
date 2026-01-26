<template>
  <div>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Websites</h1>
        <p class="mt-2 text-sm text-gray-700">Manage your Nginx-hosted websites and Node.js applications.</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button @click="openCreateModal" type="button" class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          Add Website
        </button>
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
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Domain</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Port</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="site in websites" :key="site.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ site.name }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ site.domain }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ site.port }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Active</span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button @click="deleteWebsite(site.id)" class="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
                 <tr v-if="websites.length === 0">
                    <td colspan="5" class="text-center py-4 text-gray-500">No websites found.</td>
                 </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <BaseModal :isOpen="isModalOpen" title="Add New Website" @close="closeModal" @confirm="createWebsite">
      <form class="space-y-4">
        <div>
          <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Name</label>
          <div class="mt-2">
            <input type="text" v-model="form.name" id="name" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="My Blog">
          </div>
        </div>
        <div>
          <label for="domain" class="block text-sm font-medium leading-6 text-gray-900">Domain</label>
          <div class="mt-2">
            <input type="text" v-model="form.domain" id="domain" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="example.com">
          </div>
        </div>
        <div class="flex gap-4">
             <div class="w-1/2">
                <label for="port" class="block text-sm font-medium leading-6 text-gray-900">Port</label>
                <div class="mt-2">
                    <input type="number" v-model="form.port" id="port" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="3000">
                </div>
            </div>
            <div class="w-1/2">
                <label for="path" class="block text-sm font-medium leading-6 text-gray-900">Project Path</label>
                <div class="mt-2">
                    <PathInput v-model="form.project_path" placeholder="/var/www/html" />
                </div>
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
import PathInput from '../components/PathInput.vue'

const websites = ref([])
const isModalOpen = ref(false)
const form = reactive({
    name: '',
    domain: '',
    port: 3000,
    project_path: ''
})

const fetchWebsites = async () => {
    try {
        const response = await axios.get('/api/v1/websites/')
        websites.value = response.data
    } catch (e) {
        console.error("Failed to fetch websites", e)
    }
}

const createWebsite = async () => {
    try {
        await axios.post('/api/v1/websites/', form)
        closeModal()
        fetchWebsites()
    } catch (e) {
        console.error("Failed to create website", e)
        alert("Failed to create website")
    }
}

const deleteWebsite = async (id) => {
    if(!confirm("Are you sure? This will remove Nginx config.")) return;
    try {
        await axios.delete(`/api/v1/websites/${id}`)
        fetchWebsites()
    } catch (e) {
        console.error("Failed to delete website", e)
    }
}

const openCreateModal = () => {
    form.name = ''
    form.domain = ''
    form.port = 3000
    form.project_path = ''
    isModalOpen.value = true
}

const closeModal = () => {
    isModalOpen.value = false
}

onMounted(() => {
    fetchWebsites()
})
</script>
