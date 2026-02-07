<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Networks</h1>
        <p class="mt-1 text-sm text-gray-500">Manage Docker networks</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="fetchNetworks"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Network List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scope</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="net in networks" :key="net.id">
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ net.name }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ net.id }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ net.driver }}</div>
              </td>
               <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ net.scope }}</div>
              </td>
            </tr>
            <tr v-if="networks.length === 0 && !isLoading">
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                    No networks found.
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import axios from 'axios'

const networks = ref([])
const isLoading = ref(false)

const fetchNetworks = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/networks/')
    networks.value = response.data
  } catch (error) {
    console.error('Error fetching networks:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchNetworks()
})
</script>
