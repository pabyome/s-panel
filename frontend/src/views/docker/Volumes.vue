<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Volumes</h1>
        <p class="mt-1 text-sm text-gray-500">Manage Docker volumes</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="fetchVolumes"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Volume List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mountpoint</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="vol in volumes" :key="vol.name">
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ vol.name }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ vol.driver }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500 truncate max-w-xs" :title="vol.mountpoint">{{ vol.mountpoint }}</div>
              </td>
               <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ formatDate(vol.created) }}</div>
              </td>
            </tr>
            <tr v-if="volumes.length === 0 && !isLoading">
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                    No volumes found.
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

const volumes = ref([])
const isLoading = ref(false)

const fetchVolumes = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/volumes/')
    volumes.value = response.data
  } catch (error) {
    console.error('Error fetching volumes:', error)
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
}

onMounted(() => {
  fetchVolumes()
})
</script>
