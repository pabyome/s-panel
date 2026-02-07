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
                          <button @click="confirmSaveConfig" :disabled="isSaving" class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
                              <svg v-if="isSaving" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                              {{ isSaving ? 'Saving...' : 'Save & Reload Nginx' }}
                          </button>
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

                  <!-- WAF Manager -->
                  <div v-if="currentTab === 'WAF'" class="flex-1 flex flex-col overflow-y-auto">
                      <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                          <div class="flex">
                              <div class="flex-shrink-0">
                                  <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                                  </svg>
                              </div>
                              <div class="ml-3">
                                  <p class="text-sm text-blue-700">
                                      Web Application Firewall (WAF) helps protect your site from attacks. Enabling this will regenerate your Nginx configuration.
                                  </p>
                              </div>
                          </div>
                      </div>

                      <div class="space-y-6">
                          <!-- Enable Toggle -->
                          <div class="flex items-center justify-between">
                              <span class="flex-grow flex flex-col">
                                  <span class="text-sm font-medium text-gray-900">Enable WAF</span>
                                  <span class="text-sm text-gray-500">Activate Nginx-based firewall rules</span>
                              </span>
                              <button
                                  type="button"
                                  @click="wafConfig.enabled = !wafConfig.enabled"
                                  :class="[wafConfig.enabled ? 'bg-indigo-600' : 'bg-gray-200', 'relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500']"
                              >
                                  <span aria-hidden="true" :class="[wafConfig.enabled ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200']"></span>
                              </button>
                          </div>

                          <template v-if="wafConfig.enabled">
                              <!-- CC Defense -->
                              <div class="border-t border-gray-200 pt-6">
                                  <h4 class="text-sm font-medium text-gray-900 mb-4">CC Attack Defense</h4>
                                  <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                                      <div>
                                          <label class="block text-sm font-medium text-gray-700">Rate Limit (req/sec)</label>
                                          <div class="mt-1">
                                              <input type="number" v-model.number="wafConfig.cc_deny_rate" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md">
                                          </div>
                                          <p class="mt-1 text-xs text-gray-500">Max requests per second from one IP</p>
                                      </div>
                                      <div>
                                          <label class="block text-sm font-medium text-gray-700">Burst</label>
                                          <div class="mt-1">
                                              <input type="number" v-model.number="wafConfig.cc_deny_burst" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md">
                                          </div>
                                          <p class="mt-1 text-xs text-gray-500">Allowed burst beyond rate limit</p>
                                      </div>
                                  </div>
                              </div>

                              <!-- Blocking Rules -->
                              <div class="border-t border-gray-200 pt-6">
                                  <h4 class="text-sm font-medium text-gray-900 mb-4">Blocking Rules</h4>

                                  <div class="space-y-4">
                                      <div class="relative flex items-start">
                                          <div class="flex items-center h-5">
                                              <input id="block_scanners" type="checkbox" v-model="wafConfig.rule_scan_block" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded">
                                          </div>
                                          <div class="ml-3 text-sm">
                                              <label for="block_scanners" class="font-medium text-gray-700">Block Common Scanners</label>
                                              <p class="text-gray-500">Block known malicious user agents (e.g. sqlmap, nikto)</p>
                                          </div>
                                      </div>

                                      <div class="relative flex items-start">
                                          <div class="flex items-center h-5">
                                              <input id="block_hacking" type="checkbox" v-model="wafConfig.rule_hacking_block" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded">
                                          </div>
                                          <div class="ml-3 text-sm">
                                              <label for="block_hacking" class="font-medium text-gray-700">Block Hacking Attempts</label>
                                              <p class="text-gray-500">Block common SQL Injection and XSS patterns in query strings</p>
                                          </div>
                                      </div>

                                      <div>
                                          <label class="block text-sm font-medium text-gray-700">Blocked URI Keywords</label>
                                          <div class="mt-1">
                                              <textarea v-model="wafKeywords" rows="4" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md" placeholder="Enter keywords to block in URI, one per line (e.g. /admin)"></textarea>
                                          </div>
                                      </div>
                                  </div>
                              </div>
                          </template>
                      </div>

                      <div class="mt-6 flex justify-end">
                          <button @click="saveWafConfig" :disabled="isSaving" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                              <svg v-if="isSaving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                              {{ isSaving ? 'Saving...' : 'Save WAF Settings' }}
                          </button>
                      </div>
                  </div>

              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Save Config Confirmation Modal -->
  <ConfirmModal
    :isOpen="isSaveConfigModalOpen"
    type="warning"
    title="Save Nginx Configuration"
    message="Are you sure you want to save this configuration? Bad config can stop Nginx."
    confirmText="Save & Reload"
    :isLoading="isSaving"
    @confirm="saveConfig"
    @cancel="isSaveConfigModalOpen = false"
  />
</template>

<script setup>
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import axios from 'axios'
import ConfirmModal from './ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const props = defineProps({
  isOpen: Boolean,
  website: Object
})

const emit = defineEmits(['close'])

const tabs = [
  { name: 'Nginx Config', href: '#' },
  { name: 'Logs', href: '#' },
  { name: 'WAF', href: '#' },
]

const currentTab = ref('Nginx Config')
const configContent = ref('')
const logContent = ref('')
const logType = ref('access')
const isSaveConfigModalOpen = ref(false)
const isSaving = ref(false)

// WAF State
const wafConfig = ref({
    enabled: false,
    cc_deny_rate: 100,
    cc_deny_burst: 10,
    rule_scan_block: false,
    rule_hacking_block: false,
    rule_keywords: []
})
const wafKeywords = ref('')

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

const confirmSaveConfig = () => {
    isSaveConfigModalOpen.value = true
}

const saveConfig = async () => {
    if (isSaving.value) return
    isSaving.value = true
    try {
        const { data } = await axios.post(`/api/v1/websites/${props.website.id}/config`, {
            content: configContent.value
        })
        if (data.ok) {
            toast.success(data.message || 'Configuration saved successfully')
        } else {
            toast.error(data.message || 'Error saving configuration')
        }
        isSaveConfigModalOpen.value = false
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to save")
    } finally {
        isSaving.value = false
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

const fetchWafConfig = async () => {
    if (!props.website?.id) return
    try {
        const { data } = await axios.get(`/api/v1/waf/${props.website.id}`)
        wafConfig.value = data
        wafKeywords.value = (data.rule_keywords || []).join('\n')
    } catch (e) {
        console.error("Failed to load WAF config", e)
        toast.error("Failed to load WAF settings")
    }
}

const saveWafConfig = async () => {
    if (isSaving.value) return
    isSaving.value = true
    try {
        const payload = {
            ...wafConfig.value,
            rule_keywords: wafKeywords.value.split('\n').map(k => k.trim()).filter(k => k)
        }
        // Exclude fields not in schema if necessary, but schemas usually ignore extras
        const { data } = await axios.post(`/api/v1/waf/${props.website.id}`, payload)
        wafConfig.value = data
        wafKeywords.value = (data.rule_keywords || []).join('\n')
        toast.success("WAF settings saved successfully")

        // Refresh nginx config view as it might have changed
        if (currentTab.value === 'Nginx Config') fetchConfig()
    } catch (e) {
        console.error("Failed to save WAF config", e)
        toast.error(e.response?.data?.detail || "Failed to save WAF settings")
    } finally {
        isSaving.value = false
    }
}

watch(() => props.isOpen, (newVal) => {
    if (newVal && props.website) {
        fetchConfig()
        fetchLogs()
        fetchWafConfig()
    }
})

watch(currentTab, (newVal) => {
    if (newVal === 'WAF') {
        fetchWafConfig()
    } else if (newVal === 'Nginx Config') {
        fetchConfig()
    } else if (newVal === 'Logs') {
        fetchLogs()
    }
})

watch(logType, () => {
    fetchLogs()
})
</script>
