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
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4 flex justify-between items-center">
        <div>
          <h3 class="text-base font-semibold text-gray-900">System Information</h3>
          <p class="text-sm text-gray-500">View version status and manage updates</p>
        </div>
      </div>
      <div class="p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-900">Current Commit</p>
            <div class="flex items-center gap-2 mt-1">
               <code class="text-xs bg-gray-100 px-2 py-1 rounded text-gray-600 font-mono">{{ updateInfo.current_commit || 'Unknown' }}</code>
               <span v-if="!updateInfo.updates_available" class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Up to date</span>
               <span v-else class="inline-flex items-center rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700 ring-1 ring-inset ring-amber-600/20">Update available</span>
            </div>
          </div>
          <div class="flex gap-3">
             <button
               @click="checkForUpdates"
               :disabled="checking"
               class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
             >
               <svg v-if="checking" class="-ml-0.5 mr-1.5 h-4 w-4 animate-spin inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
               {{ checking ? 'Checking...' : 'Check Status' }}
             </button>

             <button
               v-if="updateInfo.updates_available"
               @click="confirmUpdate"
               :disabled="updating"
               class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
             >
               {{ updating ? 'Updating...' : 'Update System' }}
             </button>
          </div>
        </div>

        <div v-if="updateInfo.updates_available" class="mt-4 rounded-md bg-blue-50 p-4">
          <div class="flex">
            <div class="shrink-0">
              <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3 flex-1 md:flex md:justify-between">
              <p class="text-sm text-blue-700">Latest commit <strong>{{ updateInfo.latest_commit }}</strong> is available.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Settings -->
    <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4">
         <h3 class="text-base font-semibold text-gray-900">Notification Channels</h3>
         <p class="mt-0.5 text-sm text-gray-500">Configure email delivery and alert rules.</p>
      </div>
      <div class="p-6">
         <form @submit.prevent="saveSmtp" class="space-y-6">

            <!-- SMTP Configuration -->
            <div>
                 <h4 class="text-sm font-medium leading-6 text-gray-900 mb-4">SMTP Configuration</h4>
                 <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
                    <div class="sm:col-span-4">
                        <label class="block text-sm font-medium text-gray-700">SMTP Host</label>
                        <input type="text" v-model="smtpForm.host" required placeholder="smtp.gmail.com" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border">
                    </div>
                    <div class="sm:col-span-2">
                        <label class="block text-sm font-medium text-gray-700">Port</label>
                        <input type="number" v-model="smtpForm.port" required placeholder="587" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border">
                    </div>

                    <div class="sm:col-span-3">
                        <label class="block text-sm font-medium text-gray-700">Username</label>
                        <input type="text" v-model="smtpForm.user" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border">
                    </div>
                    <div class="sm:col-span-3">
                        <label class="block text-sm font-medium text-gray-700">Password</label>
                        <input type="password" v-model="smtpForm.password" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border">
                    </div>

                     <div class="sm:col-span-3">
                        <label class="block text-sm font-medium text-gray-700">From Email</label>
                        <input type="email" v-model="smtpForm.from_email" required placeholder="notifications@yourdomain.com" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border">
                    </div>
                     <div class="sm:col-span-3">
                        <label class="block text-sm font-medium text-gray-700">Admin Email(s)</label>
                        <input type="text" v-model="smtpForm.admin_emails_str" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border" placeholder="admin@example.com">
                        <p class="text-xs text-gray-500 mt-1">Comma separated list of admins who receive system alerts.</p>
                    </div>
                 </div>
            </div>

            <!-- Deployment Alerts -->
            <div class="pt-4 border-t border-gray-100">
                <div class="flex items-start gap-4">
                    <div class="flex items-center h-6">
                        <input id="deployment_alerts" type="checkbox" v-model="smtpForm.deployment_alerts_enabled" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                    </div>
                    <div class="flex-1">
                        <label for="deployment_alerts" class="text-sm font-medium text-gray-900">Enable Deployment Alerts</label>
                        <p class="text-sm text-gray-500">Send an email when a deployment succeeds or fails.</p>

                         <div v-if="smtpForm.deployment_alerts_enabled" class="mt-4 bg-gray-50 p-4 rounded-md border border-gray-200">
                            <label class="block text-sm font-medium text-gray-700">Global Alert Recipient (Optional)</label>
                            <input type="email" v-model="smtpForm.alert_email_recipient" class="mt-1 block w-full max-w-sm rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border" placeholder="alerts@example.com">
                            <p class="text-xs text-gray-500 mt-1">If set, this email receives alerts for ALL deployments, in addition to any project-specific emails.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center pt-4 border-t border-gray-100">
                 <div class="flex items-center gap-2">
                    <button type="button" @click="promptTestEmail" :disabled="sendingTest" class="inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50">
                        <svg v-if="sendingTest" class="h-4 w-4 animate-spin text-gray-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        {{ sendingTest ? 'Sending...' : 'Send Test Email' }}
                    </button>
                    <span v-if="testEmailResult" :class="['text-sm', testEmailSuccess ? 'text-green-600' : 'text-red-600']">{{ testEmailResult }}</span>
                 </div>
                 <button type="submit" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                    Save Changes
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
const testEmailResult = ref(null)
const testEmailSuccess = ref(false)

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
        testEmailResult.value = null
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to save settings")
    }
}

const promptTestEmail = async () => {
    // Basic validation
    if (!smtpForm.value.host || !smtpForm.value.from_email) {
        toast.error("Please configure SMTP Host and From Email first")
        return
    }

    const defaultEmail = smtpForm.value.alert_email_recipient || smtpForm.value.from_email
    const email = prompt("Enter email address to send test to:", defaultEmail)

    if (!email) return

    sendingTest.value = true
    testEmailResult.value = null
    try {
        const res = await axios.post('/api/v1/notifications/test-email', { to_email: email })
        testEmailSuccess.value = true
        testEmailResult.value = "Email sent successfully!"
        toast.success(`Test email sent to ${email}`)
    } catch (e) {
        testEmailSuccess.value = false
        // Extract detailed error
        const detail = e.response?.data?.detail || e.message
        testEmailResult.value = `Failed: ${detail}`
        toast.error("Failed to send test email")
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
