<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Cron Jobs</h1>
      <button
        @click="openAddModal"
        class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        Add Cron Job
      </button>
    </div>

    <!-- Jobs Table -->
    <div class="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl md:col-span-2">
      <table class="min-w-full divide-y divide-gray-300">
        <thead>
          <tr>
            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Schedule</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">User</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Command</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Comment</th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="job in jobs" :key="job.id">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ job.schedule }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ job.user || 'root' }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">{{ job.command }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ job.comment_clean }}</td>
            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
              <button @click="confirmDelete(job.id)" :disabled="deletingId !== null" class="inline-flex items-center gap-1 text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed">
                <svg v-if="deletingId === job.id" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                {{ deletingId === job.id ? 'Deleting...' : 'Delete' }}
              </button>
            </td>
          </tr>
          <tr v-if="jobs.length === 0">
            <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
              No cron jobs found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Job Modal -->
    <div v-if="showModal" class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <div class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
            <div>
              <div class="mt-3 text-center sm:mt-5">
                <h3 class="text-base font-semibold leading-6 text-gray-900" id="modal-title">Add New Cron Job</h3>
                <div class="mt-2">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium leading-6 text-gray-900 text-left">Schedule</label>
                      <input v-model="newJob.schedule" type="text" placeholder="* * * * *" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                      <p class="text-xs text-gray-500 text-left mt-1">Format: min hour dom mon dow (e.g. "*/5 * * * *")</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium leading-6 text-gray-900 text-left">Run As User</label>
                      <UserSelect v-model="newJob.user" class="mt-2" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium leading-6 text-gray-900 text-left">Command</label>
                      <input v-model="newJob.command" type="text" placeholder="/path/to/script.sh" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                    </div>
                    <div>
                      <label class="block text-sm font-medium leading-6 text-gray-900 text-left">Comment</label>
                      <input v-model="newJob.comment" type="text" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
              <button @click="createJob" :disabled="isCreating" type="button" class="inline-flex w-full items-center justify-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2 disabled:opacity-50 disabled:cursor-not-allowed">
                <svg v-if="isCreating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                {{ isCreating ? 'Creating...' : 'Create' }}
              </button>
              <button @click="showModal = false" type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0">
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Cron Job"
      message="Are you sure you want to delete this cron job? This action cannot be undone."
      confirmText="Delete"
      :isLoading="deletingId !== null"
      @confirm="deleteJob"
      @cancel="isDeleteModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import UserSelect from '../components/UserSelect.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const jobs = ref([])
const showModal = ref(false)
const isCreating = ref(false)
const deletingId = ref(null)
const isDeleteModalOpen = ref(false)
const jobToDelete = ref(null)
const newJob = ref({
  schedule: '',
  command: '',
  comment: '',
  user: 'root'
})

const fetchJobs = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/cron/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (res.ok) {
      const data = await res.json()
      // Clean up comments for display (remove spanel-id part)
      jobs.value = data.map(j => {
          let clean = j.comment || ""
          if (clean.includes('|')) {
              clean = clean.split('|')[1].trim()
          } else if (clean.startsWith('spanel-id:')) {
              clean = ""
          }
          return { ...j, comment_clean: clean }
      })
    }
  } catch (e) {
    console.error(e)
  }
}

const openAddModal = () => {
  newJob.value = { schedule: '', command: '', comment: '', user: 'root' }
  showModal.value = true
}

const createJob = async () => {
    if (isCreating.value) return
    isCreating.value = true
    try {
        const token = localStorage.getItem('token')
        const res = await fetch('/api/v1/cron/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(newJob.value)
        })
        if (res.ok) {
            toast.success('Cron job created successfully')
            showModal.value = false
            fetchJobs()
        } else {
            const err = await res.json()
            toast.error(err.detail || 'Failed to create cron job')
        }
    } catch (e) {
        console.error(e)
        toast.error('Failed to create cron job')
    } finally {
        isCreating.value = false
    }
}

const confirmDelete = (id) => {
    jobToDelete.value = id
    isDeleteModalOpen.value = true
}

const deleteJob = async () => {
    if (!jobToDelete.value || deletingId.value) return
    deletingId.value = jobToDelete.value
    try {
        const token = localStorage.getItem('token')
        const res = await fetch(`/api/v1/cron/${jobToDelete.value}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        if (res.ok) {
            toast.success('Cron job deleted successfully')
            isDeleteModalOpen.value = false
            fetchJobs()
        }
    } catch (e) {
        console.error(e)
        toast.error('Failed to delete cron job')
    } finally {
        deletingId.value = null
        jobToDelete.value = null
    }
}

onMounted(() => {
  fetchJobs()
})
</script>
