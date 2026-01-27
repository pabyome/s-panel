<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-900/75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
              <!-- Header -->
              <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                  <h3 class="text-lg font-semibold text-gray-900">Manage {{ website?.domain }}</h3>
                   <button @click="close" class="text-gray-400 hover:text-gray-500">
                      <span class="sr-only">Close</span>
                      <XMarkIcon class="h-6 w-6" />
                   </button>
              </div>

              <div class="px-6 py-4 min-h-[500px] flex flex-col">
                  <!-- Tabs -->
                  <div class="border-b border-gray-200 mb-6">
                    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                      <button
                        v-for="tab in tabs" :key="tab.name"
                        @click="currentTab = tab.name"
                        :class="[currentTab === tab.name ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']"
                      >
                        {{ tab.name }}
                      </button>
                    </nav>
                  </div>

                  <!-- Tab Panels -->

                  <!-- Config Editor -->
                  <div v-if="currentTab === 'Nginx Config'" class="flex-1 flex flex-col">
                      <div class="bg-amber-50 rounded-md p-3 mb-4 text-xs text-amber-700">
                          Warning: Incorrect configuration can break the website. Ensure you validate syntax before saving.
                      </div>
                      <textarea v-model="configContent" class="flex-1 font-mono text-xs w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-4" spellcheck="false"></textarea>
                      <div class="mt-4 flex justify-end gap-3">
                          <button @click="fetchConfig" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Reload</button>
                          <button @click="saveConfig" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Save & Reload Nginx</button>
                      </div>
                  </div>

                  <!-- Logs Viewer -->
                  <div v-if="currentTab === 'Logs'" class="flex-1 flex flex-col">
                      <div class="flex justify-between items-center mb-4">
                          <select v-model="logType" class="rounded-md border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500">
                              <option value="access">Access Log</option>
                              <option value="error">Error Log</option>
                          </select>
                          <button @click="fetchLogs" class="text-sm text-indigo-600 hover:text-indigo-500">Refresh</button>
                      </div>
                      <div class="flex-1 bg-gray-900 text-gray-300 font-mono text-xs p-4 rounded-md overflow-y-auto max-h-[500px]">
                          <pre>{{ logContent || 'No logs available' }}</pre>
                      </div>
                  </div>

              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import axios from 'axios'

const props = defineProps({
  isOpen: Boolean,
  website: Object
})

const emit = defineEmits(['close'])

const tabs = [
  { name: 'Nginx Config', href: '#' },
  { name: 'Logs', href: '#' },
]

const currentTab = ref('Nginx Config')
const configContent = ref('')
const logContent = ref('')
const logType = ref('access')

const close = () => {
    emit('close')
}

const fetchConfig = async () => {
    if (!props.website?.id) return
    try {
        const { data } = await axios.get(`/api/v1/websites/${props.website.id}/config`)
        configContent.value = data.content
    } catch (e) {
        configContent.value = "Failed to load config: " + (e.response?.data?.detail || e.message)
    }
}

const saveConfig = async () => {
    if (!confirm("Are you sure? Bad config can stop Nginx.")) return
    try {
        const { data } = await axios.post(`/api/v1/websites/${props.website.id}/config`, {
            content: configContent.value
        })
        if (data.ok) {
            alert(data.message)
        } else {
            alert("Error: " + data.message)
        }
    } catch (e) {
        alert("Failed to save: " + (e.response?.data?.detail || e.message))
    }
}

const fetchLogs = async () => {
    if (!props.website?.id) return
    try {
        const { data } = await axios.get(`/api/v1/websites/${props.website.id}/logs?type=${logType.value}&lines=200`)
        logContent.value = data.content
    } catch (e) {
        logContent.value = "Failed to load logs"
    }
}

watch(() => props.isOpen, (newVal) => {
    if (newVal && props.website) {
        fetchConfig()
        fetchLogs()
    }
})

watch(logType, () => {
    fetchLogs()
})
</script>
