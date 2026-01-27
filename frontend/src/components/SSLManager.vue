<template>
  <div class="mt-8 rounded-xl bg-gray-50 border border-gray-100 p-5">
    <div class="flex items-start justify-between">
      <div>
        <h3 class="text-sm font-semibold text-gray-900">SSL Certificate</h3>
        <p class="mt-1 text-xs text-gray-500">Secure your website with HTTPS (Let's Encrypt)</p>
      </div>
      <div
        :class="[
          sslEnabled ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-600',
          'inline-flex items-center rounded-lg px-2 py-1 text-xs font-medium'
        ]"
      >
        <svg v-if="sslEnabled" class="mr-1.5 h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <svg v-else class="mr-1.5 h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        {{ sslEnabled ? 'Active' : 'Not Enabled' }}
      </div>
    </div>

    <!-- Enable SSL Form -->
    <div v-if="!sslEnabled" class="mt-4">
      <div v-if="!showForm">
        <button
          @click="showForm = true"
          class="inline-flex items-center text-xs font-medium text-indigo-600 hover:text-indigo-500"
        >
          Enable HTTPS via Let's Encrypt →
        </button>
      </div>

      <form v-else @submit.prevent="enableSSL" class="space-y-4">
        <div>
          <label for="email" class="block text-xs font-medium text-gray-700">Email Address (for renewal)</label>
          <input
            type="email"
            v-model="email"
            id="email"
            required
            class="mt-1 block w-full rounded-lg border-gray-300 py-1.5 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="admin@example.com"
          >
        </div>

        <div v-if="error" class="rounded-md bg-red-50 p-2 text-xs text-red-600">
          {{ error }}
        </div>

        <div class="flex items-center gap-2">
          <button
            type="submit"
            :disabled="loading"
            class="inline-flex items-center rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
          >
            <svg v-if="loading" class="mr-2 h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? 'Generating...' : 'Enable HTTPS' }}
          </button>
          <button
            type="button"
            @click="showForm = false"
            class="text-xs font-medium text-gray-500 hover:text-gray-700"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <div v-else class="mt-3 text-xs text-gray-500">
      Your site is securely served over HTTPS. Auto-renewal is handled by Certbot.
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  websiteId: {
    type: Number,
    required: true
  },
  sslEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update'])

const showForm = ref(false)
const email = ref('')
const loading = ref(false)
const error = ref('')

const enableSSL = async () => {
  loading.value = true
  error.value = ''

  try {
    await axios.post(`/api/v1/websites/${props.websiteId}/ssl`, null, {
      params: { email: email.value }
    })
    emit('update')
    showForm.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || "Failed to enable SSL. Ensure domain points to this server."
  } finally {
    loading.value = false
  }
}
</script>
