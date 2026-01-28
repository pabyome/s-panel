<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">File Manager</h1>
      <div class="flex space-x-3">
        <button
          @click="openCreateModal('dir')"
          :disabled="isRoot"
          :class="[isRoot ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50', 'rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300']"
        >
          New Folder
        </button>
        <button
          @click="openCreateModal('file')"
          :disabled="isRoot"
          :class="[isRoot ? 'opacity-50 cursor-not-allowed' : 'hover:bg-indigo-500', 'rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600']"
        >
          New File
        </button>
      </div>
    </div>

    <!-- Breadcrumbs -->
    <div class="flex items-center space-x-2 text-sm text-gray-500 bg-white p-3 rounded-lg shadow-sm overflow-x-auto">
      <span class="cursor-pointer hover:text-indigo-600 font-medium" @click="navigateTo('/')">root</span>
      <template v-for="(part, index) in pathParts" :key="index">
        <span>/</span>
        <span
          class="cursor-pointer hover:text-indigo-600 whitespace-nowrap"
          @click="navigateTo(part.fullPath)"
        >
          {{ part.name }}
        </span>
      </template>
    </div>

    <!-- File List -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl overflow-hidden">
      <div v-if="loading" class="p-6 text-center text-gray-500">Loading...</div>
      <div v-else-if="error" class="p-6 text-center text-red-500">{{ error }}</div>
      <table v-else class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Size</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Modified</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Permissions</th>
            <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-if="parentPath" @click="navigateTo(parentPath)" class="cursor-pointer hover:bg-gray-50">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6" colspan="5">
              .. (Parent Directory)
            </td>
          </tr>
          <tr v-if="items.length === 0" class="text-center text-gray-500">
            <td colspan="5" class="py-6">This folder is empty</td>
          </tr>
          <tr v-for="item in items" :key="item.path" class="group hover:bg-gray-50">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 cursor-pointer" @click="handleItemClick(item)">
              <div class="flex items-center">
                <component :is="item.is_dir ? FolderIcon : DocumentIcon" class="h-5 w-5 mr-2 text-gray-400 group-hover:text-indigo-600" />
                {{ item.name }}
              </div>
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.is_dir ? '-' : formatSize(item.size) }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatDate(item.modified) }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.permissions }}</td>
            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
              <button @click="deleteItem(item)" class="text-red-600 hover:text-red-900">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50">
      <div class="bg-white rounded-lg p-6 w-96 shadow-xl">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Create New {{ createType === 'dir' ? 'Folder' : 'File' }}</h3>
        <input
          v-model="newItemName"
          @keyup.enter="createItem"
          type="text"
          class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          placeholder="Name"
          ref="createInputRef"
        />
        <div class="mt-5 flex justify-end space-x-3">
          <button @click="showCreateModal = false" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
          <button @click="createItem" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Create</button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50">
      <div class="bg-white rounded-lg p-6 w-3/4 h-3/4 flex flex-col shadow-xl">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Edit {{ editingFile?.name }}</h3>
        <textarea v-model="fileContent" class="flex-1 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono"></textarea>
        <div class="mt-5 flex justify-end space-x-3">
          <button @click="showEditModal = false" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
          <button @click="saveFile" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Save</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from 'axios'
import { FolderIcon, DocumentIcon } from '@heroicons/vue/24/outline'

const items = ref([])
const currentPath = ref('/')
const parentPath = ref('')
const loading = ref(false)
const error = ref(null)

// Create Modal
const showCreateModal = ref(false)
const createType = ref('file') // 'file' or 'dir'
const newItemName = ref('')
const createInputRef = ref(null)

// Edit Modal
const showEditModal = ref(false)
const editingFile = ref(null)
const fileContent = ref('')

const fetchFiles = async (path) => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/v1/files/list', { params: { path } })
    items.value = response.data.items
    currentPath.value = response.data.current_path
    parentPath.value = response.data.parent_path
  } catch (e) {
    error.value = e.response?.data?.detail || "Failed to list files"
    items.value = []
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => {
  fetchFiles(path)
}

const handleItemClick = (item) => {
  if (item.is_dir) {
    navigateTo(item.path)
  } else {
    openEditModal(item)
  }
}

const isRoot = computed(() => {
  return !currentPath.value || currentPath.value === '/'
})

const pathParts = computed(() => {
  if (!currentPath.value || currentPath.value === '/') return []
  // Handle windows or unix paths roughly?
  // Assuming unix paths from backend
  const parts = currentPath.value.split('/').filter(p => p)
  let accum = ''
  return parts.map(p => {
    accum += '/' + p
    return { name: p, fullPath: accum }
  })
})

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (isoString) => {
  return new Date(isoString).toLocaleString()
}

// Create Logic
const openCreateModal = (type) => {
  createType.value = type
  newItemName.value = ''
  showCreateModal.value = true
  nextTick(() => {
      if(createInputRef.value) createInputRef.value.focus()
  })
}

const createItem = async () => {
  if (!newItemName.value) return
  const separator = currentPath.value.endsWith('/') ? '' : '/'
  const newPath = currentPath.value + separator + newItemName.value
  try {
    await axios.post('/api/v1/files/create', {
      path: newPath,
      is_dir: createType.value === 'dir'
    })
    showCreateModal.value = false
    fetchFiles(currentPath.value)
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to create item")
  }
}

// Delete Logic
const deleteItem = async (item) => {
  if (!confirm(`Are you sure you want to delete ${item.name}?`)) return
  try {
    await axios.delete('/api/v1/files/delete', { params: { path: item.path } })
    fetchFiles(currentPath.value)
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to delete item")
  }
}

// Edit Logic
const openEditModal = async (item) => {
  try {
    const response = await axios.get('/api/v1/files/content', { params: { path: item.path } })
    fileContent.value = response.data.content
    editingFile.value = item
    showEditModal.value = true
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to read file")
  }
}

const saveFile = async () => {
  try {
    await axios.post('/api/v1/files/content', {
      path: editingFile.value.path,
      content: fileContent.value
    })
    showEditModal.value = false
    fetchFiles(currentPath.value)
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to save file")
  }
}

onMounted(() => {
  fetchFiles('/')
})
</script>
