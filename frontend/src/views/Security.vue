<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Firewall</h1>
        <p class="mt-1 text-sm text-gray-500">Manage UFW firewall rules and protect your server</p>
      </div>
      <button @click="openCreateModal" type="button" class="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-500 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add Rule
      </button>
    </div>

    <!-- Warning Banner -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 p-5 shadow-lg shadow-amber-500/20">
      <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
      <div class="absolute right-10 bottom-0 -mb-6 h-20 w-20 rounded-full bg-white/5"></div>
      <div class="relative flex items-start gap-4">
        <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
          <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-white">Important Security Notice</h3>
          <p class="mt-1 text-sm text-white/80">Changes apply immediately. Always keep ports <span class="font-mono font-bold">22</span> (SSH) and <span class="font-mono font-bold">8000</span> (Panel) allowed to prevent lockout.</p>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-emerald-100 p-2.5">
            <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Allowed</p>
            <p class="text-xl font-bold text-gray-900">{{ rules.filter(r => r.action === 'ALLOW').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-red-100 p-2.5">
            <svg class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Denied</p>
            <p class="text-xl font-bold text-gray-900">{{ rules.filter(r => r.action === 'DENY').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-blue-100 p-2.5">
            <svg class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total Rules</p>
            <p class="text-xl font-bold text-gray-900">{{ rules.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Rules Table -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
        <h3 class="text-sm font-semibold text-gray-900">Active Rules</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead>
            <tr class="bg-gray-50/50">
              <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">ID</th>
              <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Port / Protocol</th>
              <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Action</th>
              <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Source</th>
              <th scope="col" class="relative py-3.5 pl-3 pr-6">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="rule in rules" :key="rule.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm">
                <span class="inline-flex items-center rounded-lg bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  #{{ rule.id }}
                </span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-sm">
                <span class="font-mono font-medium text-gray-900">{{ rule.to_port }}</span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-sm">
                <span :class="[
                  rule.action === 'ALLOW'
                    ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
                    : 'bg-red-50 text-red-700 ring-red-600/20',
                  'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset'
                ]">
                  <span :class="[rule.action === 'ALLOW' ? 'bg-emerald-500' : 'bg-red-500', 'h-1.5 w-1.5 rounded-full']"></span>
                  {{ rule.action }}
                </span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                <span class="font-mono">{{ rule.from_ip || 'Anywhere' }}</span>
              </td>
              <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm">
                <button @click="confirmDelete(rule.id)" :disabled="deletingId === rule.id" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg v-if="deletingId === rule.id" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                  {{ deletingId === rule.id ? 'Deleting...' : 'Delete' }}
                </button>
              </td>
            </tr>
            <tr v-if="rules.length === 0">
              <td colspan="5" class="py-12 text-center">
                <div class="flex flex-col items-center">
                  <div class="rounded-xl bg-gray-100 p-3">
                    <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                  </div>
                  <p class="mt-3 text-sm font-medium text-gray-900">No firewall rules</p>
                  <p class="mt-1 text-sm text-gray-500">UFW may be inactive or no rules configured.</p>
                  <button @click="openCreateModal" class="mt-4 text-sm font-medium text-blue-600 hover:text-blue-500">
                    Add your first rule →
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Modal -->
    <BaseModal :isOpen="isModalOpen" title="Add Firewall Rule" @close="closeModal" :showFooter="false">
      <form @submit.prevent="createRule" class="space-y-5">
        <div>
          <label for="port" class="block text-sm font-medium text-gray-700">Port</label>
          <div class="mt-2">
            <input type="number" v-model="form.port" id="port" required class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm" placeholder="80">
          </div>
        </div>
        <div>
          <label for="protocol" class="block text-sm font-medium text-gray-700">Protocol</label>
          <div class="mt-2">
            <select v-model="form.protocol" id="protocol" class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm">
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>
        </div>
        <div>
          <label for="action" class="block text-sm font-medium text-gray-700">Action</label>
          <div class="mt-2">
            <select v-model="form.action" id="action" class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm">
              <option value="allow">Allow</option>
              <option value="deny">Deny</option>
            </select>
          </div>
        </div>

        <div class="flex gap-3 pt-2">
          <button
            type="button"
            @click="closeModal"
            class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isCreating"
            class="flex-1 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
          >
            <svg v-if="isCreating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isCreating ? 'Adding...' : 'Add Rule' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Firewall Rule"
      :message="`Are you sure you want to delete rule ${ruleToDelete}?`"
      confirmText="Delete"
      :isLoading="deletingId !== null"
      @confirm="deleteRule"
      @cancel="isDeleteModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const rules = ref([])
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const ruleToDelete = ref(null)
const isLoading = ref(false)
const isCreating = ref(false)
const deletingId = ref(null)
const form = reactive({
    port: 80,
    protocol: 'tcp',
    action: 'allow'
})

const fetchRules = async (showLoading = false) => {
    if (showLoading) isLoading.value = true
    try {
        const response = await axios.get('/api/v1/firewall/')
        rules.value = response.data
    } catch (e) {
        console.error("Failed to fetch rules", e)
    } finally {
        if (showLoading) isLoading.value = false
    }
}

const createRule = async () => {
    if (isCreating.value) return
    isCreating.value = true
    try {
        await axios.post('/api/v1/firewall/', form)
        toast.success('Firewall rule created successfully')
        closeModal()
        // Wait briefly for UFW to apply
        setTimeout(fetchRules, 500)
    } catch (e) {
        console.error("Failed to create rule", e)
        toast.error(e.response?.data?.detail || "Failed to create rule")
    } finally {
        isCreating.value = false
    }
}

const confirmDelete = (id) => {
    ruleToDelete.value = id
    isDeleteModalOpen.value = true
}

const deleteRule = async () => {
    if (!ruleToDelete.value || deletingId.value) return
    deletingId.value = ruleToDelete.value
    try {
        await axios.delete(`/api/v1/firewall/${ruleToDelete.value}`)
        toast.success('Firewall rule deleted successfully')
        isDeleteModalOpen.value = false
        setTimeout(fetchRules, 500)
    } catch (e) {
        console.error("Failed to delete rule", e)
        toast.error("Failed to delete rule")
    } finally {
        deletingId.value = null
        ruleToDelete.value = null
    }
}

const openCreateModal = () => {
    form.port = 80
    form.protocol = 'tcp'
    form.action = 'allow'
    isModalOpen.value = true
}

const closeModal = () => {
    isModalOpen.value = false
}

onMounted(() => {
    fetchRules(true)
})
</script>
