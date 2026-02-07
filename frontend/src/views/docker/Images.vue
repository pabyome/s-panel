<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Images</h1>
        <p class="mt-1 text-sm text-gray-500">Manage Docker images</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="fetchImages"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Image List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tags</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="image in images" :key="image.id">
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ image.id }}</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div v-for="tag in image.tags" :key="tag" class="text-sm text-gray-500">{{ tag }}</div>
                <div v-if="!image.tags || image.tags.length === 0" class="text-sm text-gray-400 italic">None</div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ formatBytes(image.size) }}</div>
              </td>
               <td class="whitespace-nowrap px-6 py-4">
                <div class="text-sm text-gray-500">{{ formatDate(image.created) }}</div>
              </td>
            </tr>
            <tr v-if="images.length === 0 && !isLoading">
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                    No images found.
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

const images = ref([])
const isLoading = ref(false)

const fetchImages = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/images/')
    images.value = response.data
  } catch (error) {
    console.error('Error fetching images:', error)
  } finally {
    isLoading.value = false
  }
}

const formatBytes = (bytes, decimals = 2) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
}

onMounted(() => {
  fetchImages()
})
</script>
