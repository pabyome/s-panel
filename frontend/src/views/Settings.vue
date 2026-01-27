<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="mt-1 text-sm text-gray-500">System configuration and updates</p>
      </div>
    </div>

    <!-- System Update Card -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
        <h3 class="text-base font-semibold text-gray-900">System Update</h3>
      </div>
      <div class="p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-900">Current Version</p>
            <p class="text-xs text-gray-500 font-mono mt-1">{{ updateInfo.current_commit || 'Unknown' }}</p>
          </div>
          <div class="text-right">
             <p class="text-sm font-medium text-gray-900">Status</p>
             <p :class="[
               updateInfo.updates_available ? 'text-amber-600' : 'text-emerald-600',
               'text-sm font-medium'
             ]">
               {{ updateInfo.message || 'Ready to check' }}
             </p>
          </div>
        </div>

        <div class="mt-6 flex items-center gap-3">
          <button
            @click="checkForUpdates"
            :disabled="checking"
            class="rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
          >
            {{ checking ? 'Checking...' : 'Check for Updates' }}
          </button>

          <button
            v-if="updateInfo.updates_available"
            @click="confirmUpdate"
            :disabled="updating"
            class="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500 disabled:opacity-50"
          >
           {{ updating ? 'Updating...' : 'Update & Restart' }}
          </button>
        </div>

        <div v-if="updateInfo.updates_available" class="mt-4 rounded-lg bg-amber-50 p-3 text-xs text-amber-700">
           Latest commit: <span class="font-mono">{{ updateInfo.latest_commit }}</span>.
           Clicking Update will pull the latest code, install dependencies, rebuild the frontend, and restart the service. The panel will be unavailable for a few minutes.
        </div>
      </div>
    </div>
    <!-- Notification Settings -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
         <h3 class="text-base font-semibold text-gray-900">Notification Settings</h3>
         <p class="mt-0.5 text-sm text-gray-500">Configure email alerts for deployments.</p>
      </div>
      <div class="p-6">
         <form @submit.prevent="saveSmtp" class="space-y-4">
            <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
                <div class="sm:col-span-4">
                    <label class="block text-sm font-medium text-gray-700">SMTP Host</label>
                    <input type="text" v-model="smtpForm.host" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>
                <div class="sm:col-span-2">
                    <label class="block text-sm font-medium text-gray-700">Port</label>
                    <input type="number" v-model="smtpForm.port" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>

                <div class="sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700">Username</label>
                    <input type="text" v-model="smtpForm.user" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>
                <div class="sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700">Password</label>
                    <input type="password" v-model="smtpForm.password" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>

                 <div class="sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700">From Email</label>
                    <input type="email" v-model="smtpForm.from_email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>
                 <div class="sm:col-span-6">
                    <label class="block text-sm font-medium text-gray-700">Admin Emails (comma separated)</label>
                    <input type="text" v-model="smtpForm.admin_emails_str" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="admin@example.com, dev@example.com">
                </div>
            </div>

            <div class="flex justify-end pt-4">
                 <button type="submit" class="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500">
                    Save Settings
                 </button>
            </div>
         </form>
      </div>
    </div>

    <!-- Update Confirmation Modal -->
    <ConfirmModal
      :isOpen="isUpdateModalOpen"
      type="warning"
      title="Update & Restart"
      message="Are you sure you want to update? This will restart the server and the panel will be unavailable for a few minutes."
      confirmText="Update Now"
      :isLoading="updating"
      @confirm="applyUpdate"
      @cancel="isUpdateModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const checking = ref(false)
const updating = ref(false)
const isUpdateModalOpen = ref(false)
const updateInfo = ref({
    updates_available: false,
    current_commit: '',
    latest_commit: '',
    message: ''
})

const smtpForm = ref({
    host: '',
    port: 587,
    user: '',
    password: '',
    from_email: '',
    admin_emails_str: ''
})

const fetchSmtp = async () => {
    try {
        const { data } = await axios.get('/api/v1/system/settings/smtp')
        smtpForm.value = {
            ...data,
            admin_emails_str: data.admin_emails.join(', ')
        }
    } catch (e) {
        console.error("Failed to fetch SMTP settings", e)
    }
}

const saveSmtp = async () => {
    try {
        const payload = {
            ...smtpForm.value,
            admin_emails: smtpForm.value.admin_emails_str.split(',').map(e => e.trim()).filter(e => e)
        }
        await axios.post('/api/v1/system/settings/smtp', payload)
        toast.success("Settings saved successfully")
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to save settings")
    }
}

const checkForUpdates = async () => {
    checking.value = true
    try {
        const response = await axios.get('/api/v1/system/update/check')
        updateInfo.value = response.data
    } catch (e) {
        console.error("Failed to check for updates", e)
        updateInfo.value.message = "Failed to check (Git Error)"
    } finally {
        checking.value = false
    }
}

const confirmUpdate = () => {
    isUpdateModalOpen.value = true
}

const applyUpdate = async () => {
    updating.value = true
    try {
        await axios.post('/api/v1/system/update/apply')
        toast.info("Update started! The service will restart. Please reload this page in 2-3 minutes.")
        isUpdateModalOpen.value = false
    } catch (e) {
        toast.error("Failed to start update")
        updating.value = false
    }
}

onMounted(() => {
    checkForUpdates()
    fetchSmtp()
})
</script>
