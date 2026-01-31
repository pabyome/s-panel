<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl font-bold text-gray-900">File Manager</h1>
      <div class="flex gap-x-3">
         <button
            @click="fetchFiles(currentPath)"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 flex items-center gap-2"
         >
            <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': loading }" />
            Refresh
         </button>
         <button
            @click="showCreateFolderModal = true"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2"
         >
            <FolderPlusIcon class="w-4 h-4" />
            New Folder
         </button>
      </div>
    </div>

    <!-- Breadcrumb -->
    <nav class="flex px-4 py-3 text-gray-700 border border-gray-200 rounded-lg bg-gray-50" aria-label="Breadcrumb">
      <ol class="inline-flex items-center flex-wrap gap-1 md:gap-2">
         <li class="inline-flex items-center">
            <button @click="navigateTo('/')" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-indigo-600">
               <HomeIcon class="w-4 h-4 mr-2" />
               Root
            </button>
         </li>
         <li v-for="(crumb, index) in breadcrumbs" :key="index">
            <div class="flex items-center">
               <ChevronRightIcon class="w-5 h-5 text-gray-400" />
               <button
                  @click="navigateTo(crumb.path)"
                  class="ml-1 text-sm font-medium text-gray-700 hover:text-indigo-600 md:ml-2"
               >
                  {{ crumb.name }}
               </button>
            </div>
         </li>
      </ol>
    </nav>

    <!-- Content -->
    <div class="overflow-hidden bg-white shadow ring-1 ring-black/5 sm:rounded-lg">
      <div v-if="loading && files.length === 0" class="p-8 text-center text-gray-500">
         Loading...
      </div>
      <div v-else-if="error" class="p-8 text-center text-red-500">
         {{ error }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-300">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
              <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Size</th>
              <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Permissions</th>
              <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Owner</th>
              <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-if="currentPath !== '/'" @click="navigateUp" class="cursor-pointer hover:bg-gray-50">
                 <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 flex items-center gap-x-2">
                    <FolderIcon class="h-5 w-5 text-yellow-500" />
                    ..
                 </td>
                 <td colspan="4"></td>
              </tr>
              <tr v-for="item in files" :key="item.name" class="group hover:bg-gray-50">
                 <td
                    class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 cursor-pointer flex items-center gap-x-2"
                    @click="item.is_dir ? navigateTo(item.path) : openFile(item)"
                 >
                    <FolderIcon v-if="item.is_dir" class="h-5 w-5 text-yellow-500" />
                    <DocumentIcon v-else class="h-5 w-5 text-gray-400" />
                    {{ item.name }}
                 </td>
                 <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatSize(item.size) }}</td>
                 <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.permissions }}</td>
                 <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.owner }}:{{ item.group }}</td>
                 <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button @click.stop="deleteItem(item)" class="text-red-600 hover:text-red-900">Delete</button>
                 </td>
              </tr>
              <tr v-if="files.length === 0" class="text-center text-gray-500">
                  <td colspan="5" class="py-8">Empty directory</td>
              </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Editor Modal -->
    <BaseModal
        :isOpen="showEditor"
        title="Edit File"
        size="xl"
        confirmText="Save"
        @close="closeEditor"
        @confirm="saveFile"
    >
       <div class="mt-2">
          <textarea
             v-model="editorContent"
             rows="20"
             class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono"
          ></textarea>
       </div>
    </BaseModal>

    <!-- Create Folder Modal -->
    <BaseModal
        :isOpen="showCreateFolderModal"
        title="Create New Folder"
        confirmText="Create"
        @close="showCreateFolderModal = false"
        @confirm="createFolder"
    >
         <div class="mt-2">
             <input
                 v-model="newFolderName"
                 type="text"
                 placeholder="Folder Name"
                 class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                 @keyup.enter="createFolder"
             />
         </div>
     </BaseModal>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { FolderIcon, DocumentIcon, HomeIcon, ChevronRightIcon, ArrowPathIcon, FolderPlusIcon } from '@heroicons/vue/24/outline'
import BaseModal from '../components/BaseModal.vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const files = ref([])
const currentPath = ref('/')
const loading = ref(false)
const error = ref(null)

const showEditor = ref(false)
const editorContent = ref('')
const currentFile = ref(null)

const showCreateFolderModal = ref(false)
const newFolderName = ref('')

const breadcrumbs = computed(() => {
    if (currentPath.value === '/') return []
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
        files.value = response.data
        currentPath.value = path
    } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to fetch files'
        toast.error(error.value)
    } finally {
        loading.value = false
    }
}

const navigateTo = (path) => {
    fetchFiles(path)
}

const navigateUp = () => {
    const parent = currentPath.value.split('/').slice(0, -1).join('/') || '/'
    navigateTo(parent)
}

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const openFile = async (file) => {
    try {
        const response = await axios.get('/api/v1/files/content', { params: { path: file.path } })
        editorContent.value = response.data.content
        currentFile.value = file
        showEditor.value = true
    } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to read file')
    }
}

const closeEditor = () => {
    showEditor.value = false
    editorContent.value = ''
    currentFile.value = null
}

const saveFile = async () => {
    if (!currentFile.value) return
    try {
        await axios.post('/api/v1/files/content', {
            path: currentFile.value.path,
            content: editorContent.value
        })
        toast.success('File saved successfully')
        closeEditor()
        fetchFiles(currentPath.value) // Refresh to update size/modified
    } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to save file')
    }
}

const deleteItem = async (item) => {
    if (!confirm(`Are you sure you want to delete ${item.name}? This cannot be undone.`)) return
    try {
        await axios.delete('/api/v1/files/', { params: { path: item.path } })
        toast.success('Item deleted successfully')
        fetchFiles(currentPath.value)
    } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to delete item')
    }
}

const createFolder = async () => {
    if (!newFolderName.value) return
    const path = currentPath.value === '/' ? '/' + newFolderName.value : currentPath.value + '/' + newFolderName.value
    try {
        await axios.post('/api/v1/files/folder', { path })
        toast.success('Folder created successfully')
        showCreateFolderModal.value = false
        newFolderName.value = ''
        fetchFiles(currentPath.value)
    } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to create folder')
    }
}

onMounted(() => {
    fetchFiles('/')
})
</script>
