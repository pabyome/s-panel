<template>
  <div class="h-[calc(100vh-6rem)] flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">File Manager</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your server files</p>
      </div>
      <div class="flex gap-2">
         <input
            type="file"
            ref="fileInput"
            class="hidden"
            @change="handleFileUpload"
        />
         <button
            @click="createDirectory"
            class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all"
        >
            <FolderPlusIcon class="h-4 w-4 text-gray-500" />
            New Folder
        </button>
        <button
            @click="triggerUpload"
            class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all"
        >
            <ArrowUpTrayIcon class="h-4 w-4 text-gray-500" />
            Upload
        </button>
        <button
            @click="createFile"
            class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-all"
        >
            <DocumentPlusIcon class="h-4 w-4 text-white" />
            New File
        </button>
      </div>
    </div>

    <!-- Path Bar -->
    <div class="flex items-center gap-2 bg-white p-2 rounded-lg shadow-sm ring-1 ring-gray-900/5">
        <button @click="navigateUp" :disabled="currentPath === '/'" class="p-1 hover:bg-gray-100 rounded disabled:opacity-50">
            <ArrowUpIcon class="h-5 w-5 text-gray-500" />
        </button>
        <input
            v-model="inputPath"
            @keyup.enter="navigateTo(inputPath)"
            class="flex-1 border-none focus:ring-0 text-sm font-mono text-gray-700 bg-transparent"
        />
        <button @click="loadPath(currentPath)" class="p-1 hover:bg-gray-100 rounded">
            <ArrowPathIcon class="h-5 w-5 text-gray-500" />
        </button>
    </div>

    <!-- Main Content -->
    <div class="flex flex-1 gap-6 min-h-0 bg-white rounded-2xl shadow-sm ring-1 ring-gray-900/5 flex-col overflow-hidden">
         <!-- File List Header -->
        <div class="grid grid-cols-12 gap-4 border-b border-gray-100 bg-gray-50/50 px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <div class="col-span-6">Name</div>
            <div class="col-span-2 text-right">Size</div>
            <div class="col-span-2 text-center">Permissions</div>
            <div class="col-span-2 text-right">Actions</div>
        </div>

        <!-- File List Body -->
        <div class="flex-1 overflow-y-auto">
            <div v-if="loading" class="flex justify-center p-8 text-gray-500">
                Loading...
            </div>
             <div v-else-if="error" class="flex justify-center p-8 text-red-500">
                {{ error }}
            </div>
            <div v-else>
                 <div
                    v-for="item in items"
                    :key="item.path"
                    class="grid grid-cols-12 gap-4 px-6 py-3 hover:bg-gray-50 items-center border-b border-gray-50 last:border-0 transition-colors cursor-pointer"
                    @click="onItemClick(item)"
                >
                    <div class="col-span-6 flex items-center gap-3">
                         <FolderIcon v-if="item.is_dir" class="h-5 w-5 text-indigo-400" />
                         <DocumentIcon v-else class="h-5 w-5 text-gray-400" />
                         <span class="text-sm font-medium text-gray-900 truncate">{{ item.name }}</span>
                    </div>
                    <div class="col-span-2 text-right text-sm text-gray-500">
                        {{ item.is_dir ? '-' : formatBytes(item.size) }}
                    </div>
                     <div class="col-span-2 text-center text-xs font-mono text-gray-500">
                        {{ item.permissions }}
                    </div>
                    <div class="col-span-2 text-right flex justify-end gap-2" @click.stop>
                        <button @click="confirmDelete(item)" class="p-1 text-gray-400 hover:text-red-600 transition-colors">
                            <TrashIcon class="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Edit File Modal -->
     <TransitionRoot as="template" :show="isEditModalOpen">
        <Dialog as="div" class="relative z-50" @close="isEditModalOpen = false">
             <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-gray-900/75 transition-opacity" />
            </TransitionChild>

            <div class="fixed inset-0 z-10 overflow-y-auto">
                 <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                     <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                        <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:p-6">
                             <div>
                                <div class="mt-3 text-center sm:mt-5">
                                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                                        {{ editingFile ? editingFile.name : 'New File' }}
                                    </DialogTitle>
                                    <div class="mt-2">
                                        <textarea
                                            v-model="fileContent"
                                            rows="20"
                                            class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono"
                                        ></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                                <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2" @click="saveFile">Save</button>
                                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0" @click="isEditModalOpen = false">Cancel</button>
                            </div>
                        </DialogPanel>
                     </TransitionChild>
                 </div>
            </div>
        </Dialog>
     </TransitionRoot>

     <!-- Confirm Delete Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Item"
      :message="`Are you sure you want to delete ${itemToDelete?.name}? This action cannot be undone.`"
      confirmText="Delete"
      :isLoading="isDeleting"
      @confirm="deleteItem"
      @cancel="isDeleteModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { FolderIcon, DocumentIcon, ArrowUpIcon, ArrowPathIcon, FolderPlusIcon, DocumentPlusIcon, TrashIcon, ArrowUpTrayIcon } from '@heroicons/vue/24/outline'
import ConfirmModal from '../components/ConfirmModal.vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { useToast } from '../composables/useToast' // Assuming useToast is available here like in Logs.vue, if not I will check.

// Wait, I should double check where useToast comes from.
// In Logs.vue: import { useToast } from '../composables/useToast'
// Let's assume it exists.

const toast = useToast()

const currentPath = ref('/')
const inputPath = ref('/')
const items = ref([])
const loading = ref(false)
const error = ref(null)

const isEditModalOpen = ref(false)
const editingFile = ref(null)
const fileContent = ref('')

const isDeleteModalOpen = ref(false)
const itemToDelete = ref(null)
const isDeleting = ref(false)
const fileInput = ref(null)

const formatBytes = (bytes, decimals = 1) => {
    if (!+bytes) return '0 B'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const loadPath = async (path) => {
    loading.value = true
    error.value = null
    try {
        const response = await axios.get('/api/v1/files/list', { params: { path } })
        items.value = response.data
        currentPath.value = path
        inputPath.value = path
    } catch (e) {
        error.value = e.response?.data?.detail || e.message
        toast.error(`Failed to list directory: ${error.value}`)
    } finally {
        loading.value = false
    }
}

const navigateTo = (path) => {
    loadPath(path)
}

const navigateUp = () => {
    if (currentPath.value === '/') return
    const parts = currentPath.value.split('/')
    parts.pop()
    const newPath = parts.join('/') || '/'
    loadPath(newPath)
}

const onItemClick = (item) => {
    if (item.is_dir) {
        loadPath(item.path)
    } else {
        openFile(item)
    }
}

const openFile = async (item) => {
    try {
        const response = await axios.get('/api/v1/files/content', { params: { path: item.path } })
        editingFile.value = item
        fileContent.value = response.data.content
        isEditModalOpen.value = true
    } catch (e) {
        toast.error(`Failed to open file: ${e.response?.data?.detail || e.message}`)
    }
}

const saveFile = async () => {
    if (!editingFile.value) return // Creating new file not fully implemented yet in UI flow with name input

    try {
        await axios.post('/api/v1/files/content', {
            path: editingFile.value.path,
            content: fileContent.value
        })
        toast.success('File saved successfully')
        isEditModalOpen.value = false
        // Reload path to update size/mtime
        loadPath(currentPath.value)
    } catch (e) {
        toast.error(`Failed to save file: ${e.response?.data?.detail || e.message}`)
    }
}

const confirmDelete = (item) => {
    itemToDelete.value = item
    isDeleteModalOpen.value = true
}

const deleteItem = async () => {
    if (!itemToDelete.value) return
    isDeleting.value = true
    try {
        await axios.post('/api/v1/files/delete', { path: itemToDelete.value.path })
        toast.success('Item deleted successfully')
        isDeleteModalOpen.value = false
        loadPath(currentPath.value)
    } catch (e) {
        toast.error(`Failed to delete item: ${e.response?.data?.detail || e.message}`)
    } finally {
        isDeleting.value = false
        itemToDelete.value = null
    }
}

const triggerUpload = () => {
    fileInput.value.click()
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('path', currentPath.value)
    formData.append('file', file)

    loading.value = true
    try {
        await axios.post('/api/v1/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        toast.success('File uploaded successfully')
        loadPath(currentPath.value)
    } catch (e) {
        toast.error(`Failed to upload file: ${e.response?.data?.detail || e.message}`)
    } finally {
        loading.value = false
        // Reset input so the same file can be selected again if needed
        event.target.value = ''
    }
}

const createDirectory = async () => {
    const name = prompt("Enter directory name:")
    if (!name) return

    const newPath = currentPath.value === '/' ? `/${name}` : `${currentPath.value}/${name}`

    try {
        await axios.post('/api/v1/files/directory', { path: newPath })
        toast.success('Directory created successfully')
        loadPath(currentPath.value)
    } catch (e) {
        toast.error(`Failed to create directory: ${e.response?.data?.detail || e.message}`)
    }
}

const createFile = async () => {
     const name = prompt("Enter file name:")
    if (!name) return

    const newPath = currentPath.value === '/' ? `/${name}` : `${currentPath.value}/${name}`

     try {
        // Just create empty file
        await axios.post('/api/v1/files/content', { path: newPath, content: "" })
        toast.success('File created successfully')
        loadPath(currentPath.value)
    } catch (e) {
        toast.error(`Failed to create file: ${e.response?.data?.detail || e.message}`)
    }
}

onMounted(() => {
    loadPath('/')
})
</script>
