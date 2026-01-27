<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">File Manager</h1>
        <p class="mt-1 text-sm text-gray-500">Manage files and directories on the server</p>
      </div>
      <div class="flex gap-2">
         <button @click="openCreateModal(true)" class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            New Folder
         </button>
         <button @click="openCreateModal(false)" class="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 hover:shadow-xl hover:shadow-violet-500/30 hover:-translate-y-0.5">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            New File
         </button>
      </div>
    </div>

    <!-- Breadcrumbs -->
    <nav class="flex" aria-label="Breadcrumb">
      <ol role="list" class="flex items-center space-x-2">
        <li>
          <div>
            <a href="#" @click.prevent="navigateTo('/')" class="text-gray-400 hover:text-gray-500">
              <svg class="h-5 w-5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M9.293 2.293a1 1 0 011.414 0l7 7A1 1 0 0117 11h-1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-3a1 1 0 00-1-1H9a1 1 0 00-1 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-6H3a1 1 0 01-.707-1.707l7-7z" clip-rule="evenodd" />
              </svg>
              <span class="sr-only">Root</span>
            </a>
          </div>
        </li>
        <li v-for="(part, index) in breadcrumbs" :key="index">
          <div class="flex items-center">
            <svg class="h-5 w-5 flex-shrink-0 text-gray-300" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
            </svg>
            <a href="#" @click.prevent="navigateTo(part.path)" class="ml-2 text-sm font-medium text-gray-500 hover:text-gray-700">{{ part.name }}</a>
          </div>
        </li>
      </ol>
    </nav>

    <!-- File List -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5">
        <div v-if="loading" class="p-8 text-center text-gray-500">Loading...</div>
        <div v-else-if="error" class="p-8 text-center text-red-500">{{ error }}</div>
        <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-300">
                <thead>
                    <tr>
                        <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Size</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Permissions</th>
                        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Modified</th>
                        <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                            <span class="sr-only">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                    <tr v-if="currentPath !== '/' && currentPath !== ''" @click="navigateUp" class="cursor-pointer hover:bg-gray-50">
                         <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 flex items-center gap-2">
                            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
                            </svg>
                            ..
                        </td>
                        <td colspan="4"></td>
                    </tr>
                    <tr v-for="item in items" :key="item.path" class="hover:bg-gray-50 group">
                        <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 cursor-pointer" @click="handleItemClick(item)">
                            <div class="flex items-center gap-2">
                                <svg v-if="item.is_dir" class="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-15a3 3 0 00-3 3V18a3 3 0 003 3h15zM1.5 10.146V6a3 3 0 013-3h5.379a2.25 2.25 0 011.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 013 3v1.146A4.483 4.483 0 0019.5 9h-15a4.483 4.483 0 00-3 1.146z" />
                                </svg>
                                <svg v-else class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                                </svg>
                                {{ item.name }}
                            </div>
                        </td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatSize(item.size) }}</td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">{{ item.permissions }}</td>
                        <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatDate(item.modified) }}</td>
                        <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                            <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900 opacity-0 group-hover:opacity-100 transition-opacity">Delete</button>
                        </td>
                    </tr>
                    <tr v-if="items.length === 0">
                        <td colspan="5" class="py-8 text-center text-sm text-gray-500">
                            This directory is empty
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Edit File Modal -->
    <BaseModal :isOpen="isEditModalOpen" @close="isEditModalOpen = false" :title="editingFile ? editingFile.name : 'Edit File'" size="xl" :showFooter="false">
        <div class="space-y-4">
            <div v-if="loadingContent" class="text-center py-8 text-gray-500">Loading content...</div>
             <textarea v-else v-model="fileContent" class="w-full h-96 p-4 font-mono text-sm border rounded-lg bg-gray-50 focus:ring-2 focus:ring-violet-500 focus:border-violet-500" spellcheck="false"></textarea>

             <div class="flex justify-end gap-3 pt-4">
                 <button @click="isEditModalOpen = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                 <button @click="saveFile" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2">
                    <svg v-if="saving" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                 </button>
             </div>
        </div>
    </BaseModal>

    <!-- Create Item Modal -->
    <BaseModal :isOpen="isCreateModalOpen" @close="isCreateModalOpen = false" :title="createType === 'directory' ? 'New Folder' : 'New File'" :showFooter="false">
        <form @submit.prevent="createItem" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input v-model="newItemName" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 sm:text-sm" placeholder="Enter name..." required />
            </div>
            <div class="flex justify-end gap-3 pt-4">
                 <button type="button" @click="isCreateModalOpen = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                 <button type="submit" :disabled="creating" class="px-4 py-2 text-sm font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2">
                     <svg v-if="creating" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Create
                 </button>
            </div>
        </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Item"
      :message="`Are you sure you want to delete '${itemToDelete?.name}'? This action cannot be undone.`"
      confirmText="Delete"
      :isLoading="deleting"
      @confirm="deleteItem"
      @cancel="isDeleteModalOpen = false"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const items = ref([])
const currentPath = ref('/')
const loading = ref(false)
const error = ref(null)

// Edit State
const isEditModalOpen = ref(false)
const editingFile = ref(null)
const fileContent = ref('')
const loadingContent = ref(false)
const saving = ref(false)

// Create State
const isCreateModalOpen = ref(false)
const createType = ref('file') // 'file' or 'directory'
const newItemName = ref('')
const creating = ref(false)

// Delete State
const isDeleteModalOpen = ref(false)
const itemToDelete = ref(null)
const deleting = ref(false)

const breadcrumbs = computed(() => {
    const parts = currentPath.value.split('/').filter(p => p)
    let path = ''
    return parts.map(part => {
        path += '/' + part
        return { name: part, path: path }
    })
})

const fetchFiles = async (path) => {
    loading.value = true
    error.value = null
    try {
        const response = await axios.get('/api/v1/files/list', { params: { path } })
        items.value = response.data
        currentPath.value = path
    } catch (e) {
        error.value = e.response?.data?.detail || "Failed to load files"
        toast.error(error.value)
    } finally {
        loading.value = false
    }
}

const navigateTo = (path) => {
    fetchFiles(path || '/')
}

const navigateUp = () => {
    const parts = currentPath.value.split('/').filter(p => p)
    parts.pop()
    const parent = parts.length > 0 ? '/' + parts.join('/') : '/'
    navigateTo(parent)
}

const handleItemClick = (item) => {
    if (item.is_dir) {
        navigateTo(item.path)
    } else {
        openEditModal(item)
    }
}

const openEditModal = async (item) => {
    editingFile.value = item
    isEditModalOpen.value = true
    loadingContent.value = true
    fileContent.value = ''

    try {
        const response = await axios.get('/api/v1/files/content', { params: { path: item.path } })
        fileContent.value = response.data.content
    } catch (e) {
        toast.error(e.response?.data?.detail || "Failed to load file content")
        isEditModalOpen.value = false
    } finally {
        loadingContent.value = false
    }
}

const saveFile = async () => {
    if (!editingFile.value) return
    saving.value = true
    try {
        await axios.post('/api/v1/files/content', {
            path: editingFile.value.path,
            content: fileContent.value
        })
        toast.success("File saved successfully")
        isEditModalOpen.value = false
        // refresh list to update size/modified
        fetchFiles(currentPath.value)
    } catch (e) {
        toast.error(e.response?.data?.detail || "Failed to save file")
    } finally {
        saving.value = false
    }
}

const openCreateModal = (isDir) => {
    createType.value = isDir ? 'directory' : 'file'
    newItemName.value = ''
    isCreateModalOpen.value = true
}

const createItem = async () => {
    creating.value = true
    try {
        const newPath = (currentPath.value === '/' ? '' : currentPath.value) + '/' + newItemName.value
        await axios.post('/api/v1/files/create', {
            path: newPath,
            is_directory: createType.value === 'directory'
        })
        toast.success(`${createType.value === 'directory' ? 'Folder' : 'File'} created successfully`)
        isCreateModalOpen.value = false
        fetchFiles(currentPath.value)
    } catch (e) {
        toast.error(e.response?.data?.detail || "Failed to create item")
    } finally {
        creating.value = false
    }
}

const confirmDelete = (item) => {
    itemToDelete.value = item
    isDeleteModalOpen.value = true
}

const deleteItem = async () => {
    if (!itemToDelete.value) return
    deleting.value = true
    try {
        await axios.delete('/api/v1/files/', { params: { path: itemToDelete.value.path } })
        toast.success("Item deleted successfully")
        isDeleteModalOpen.value = false
        fetchFiles(currentPath.value)
    } catch (e) {
        toast.error(e.response?.data?.detail || "Failed to delete item")
    } finally {
        deleting.value = false
    }
}

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString()
}

onMounted(() => {
    fetchFiles('/')
})
</script>
