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
         <p class="mt-0.5 text-sm text-gray-500">Configure email alerts for deployments and system events.</p>
      </div>
      <div class="p-6">
         <form @submit.prevent="saveSmtp" class="space-y-4">
            <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
                <!-- SMTP Config -->
                <div class="sm:col-span-4">
                    <label class="block text-sm font-medium text-gray-700">SMTP Host</label>
                    <input type="text" v-model="smtpForm.host" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>
                <div class="sm:col-span-2">
                    <label class="block text-sm font-medium text-gray-700">Port</label>
                    <input type="number" v-model="smtpForm.port" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
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
                    <input type="email" v-model="smtpForm.from_email" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                </div>
                 <div class="sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700">Admin Emails (comma separated)</label>
                    <input type="text" v-model="smtpForm.admin_emails_str" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="admin@example.com, dev@example.com">
                </div>

                <!-- Deployment Alerts -->
                <div class="sm:col-span-6 pt-4 border-t border-gray-100">
                    <h4 class="text-sm font-medium text-gray-900">Deployment Alerts</h4>
                    <p class="text-xs text-gray-500 mb-3">Receive email notifications when a deployment succeeds or fails.</p>

                    <div class="flex items-start gap-4">
                        <div class="flex items-center h-6">
                            <input id="deployment_alerts" type="checkbox" v-model="smtpForm.deployment_alerts_enabled" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                        </div>
                        <div class="flex-1">
                            <label for="deployment_alerts" class="text-sm font-medium text-gray-700">Enable Deployment Alerts</label>
                             <div  v-if="smtpForm.deployment_alerts_enabled" class="mt-2">
                                <label class="block text-xs font-medium text-gray-500">Alert Recipient (Optional - Global)</label>
                                <input type="email" v-model="smtpForm.alert_email_recipient" class="mt-1 block w-full max-w-sm rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="alerts@example.com">
                                <p class="text-xs text-gray-400 mt-1">If set, this email receives all deployment alerts in addition to project-specific emails.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-between pt-4 border-t border-gray-100 mt-4">
                 <div>
                    <button type="button" @click="sendTestEmail" :disabled="sendingTest" class="rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50">
                        {{ sendingTest ? 'Sending...' : 'Send Test Email' }}
                    </button>
                 </div>
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
    admin_emails_str: '',
    deployment_alerts_enabled: false,
    alert_email_recipient: ''
})

const sendingTest = ref(false)

const fetchSmtp = async () => {
    try {
        const { data } = await axios.get('/api/v1/notifications/settings')
        smtpForm.value = {
            ...data,
            admin_emails_str: data.admin_emails ? data.admin_emails.join(', ') : ''
        }
    } catch (e) {
        console.error("Failed to fetch SMTP settings", e)
    }
}

const saveSmtp = async () => {
    try {
        const payload = {
            ...smtpForm.value,
            admin_emails: smtpForm.value.admin_emails_str.split(',').map(e => e.trim()).filter(e => e),
            // Ensure empty string is null if needed, but backend accepts None or Str. Pydantic handles conversion mostly.
            alert_email_recipient: smtpForm.value.alert_email_recipient || null
        }
        await axios.post('/api/v1/notifications/settings', payload)
        toast.success("Settings saved successfully")
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to save settings")
    }
}

const sendTestEmail = async () => {
    // Basic validation
    if (!smtpForm.value.host || !smtpForm.value.from_email) {
        toast.error("Please configure SMTP Host and From Email first")
        return
    }

    // Determine where to send test
    const targetEmail = smtpForm.value.alert_email_recipient ||
                       (smtpForm.value.admin_emails_str ? smtpForm.value.admin_emails_str.split(',')[0].trim() : null) ||
                       smtpForm.value.from_email // fallback to self

    if (!targetEmail) {
        toast.error("No recipient email found. Please add an Admin Email or Alert Recipient.")
        return
    }

    sendingTest.value = true
    try {
        await axios.post('/api/v1/notifications/test-email', { to_email: targetEmail })
        toast.success(`Test email sent to ${targetEmail}`)
    } catch (e) {
        toast.error(e.response?.data?.detail || "Failed to send test email")
    } finally {
        sendingTest.value = false
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
