<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
        <p class="mt-1 text-sm text-gray-500">Manage panel users and access permissions</p>
      </div>
      <button
        @click="openCreateModal"
        class="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 hover:shadow-xl hover:shadow-violet-500/30 hover:-translate-y-0.5"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add User
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-violet-100 p-2.5">
            <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total Users</p>
            <p class="text-xl font-bold text-gray-900">{{ users.length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-amber-100 p-2.5">
            <svg class="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Admins</p>
            <p class="text-xl font-bold text-gray-900">{{ users.filter(u => u.role === 'admin').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-emerald-100 p-2.5">
            <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Regular Users</p>
            <p class="text-xl font-bold text-gray-900">{{ users.filter(u => u.role === 'user').length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <div class="animate-pulse p-6 space-y-4">
        <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        <div class="space-y-3">
          <div class="h-12 bg-gray-200 rounded"></div>
          <div class="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div v-else class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">User</th>
            <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Role</th>
            <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Created</th>
            <th scope="col" class="relative py-3.5 pl-3 pr-6">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 bg-white">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition-colors">
            <td class="whitespace-nowrap py-4 pl-6 pr-3">
              <div class="flex items-center gap-3">
                <div :class="['flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white', user.role === 'admin' ? 'bg-gradient-to-br from-violet-500 to-purple-600' : 'bg-gradient-to-br from-gray-400 to-gray-500']">
                  {{ user.username.substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ user.username }}</p>
                  <p class="text-xs text-gray-500">ID: {{ user.id }}</p>
                </div>
              </div>
            </td>
            <td class="whitespace-nowrap px-3 py-4">
              <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium', user.role === 'admin' ? 'bg-violet-100 text-violet-700' : 'bg-gray-100 text-gray-700']">
                <svg v-if="user.role === 'admin'" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
                {{ user.role }}
              </span>
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
              {{ user.created_at ? formatDate(user.created_at) : '-' }}
            </td>
            <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm">
              <div class="flex items-center justify-end gap-2">
                <button
                  @click="openEditModal(user)"
                  class="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                  </svg>
                </button>
                <button
                  @click="confirmDelete(user)"
                  :disabled="deletingId === user.id"
                  class="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors disabled:opacity-50"
                >
                  <svg v-if="deletingId === user.id" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="4" class="px-6 py-12 text-center">
              <div class="flex flex-col items-center">
                <svg class="h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                </svg>
                <p class="mt-2 text-sm text-gray-500">No users found</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit User Modal -->
    <BaseModal :isOpen="isModalOpen" @close="closeModal" :title="editingUser ? 'Edit User' : 'Create User'" :showFooter="false">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
          <input
            type="text"
            v-model="form.username"
            required
            :disabled="!!editingUser"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="johndoe"
          >
          <p v-if="editingUser" class="mt-1 text-xs text-gray-500">Username cannot be changed</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ editingUser ? 'New Password (leave blank to keep current)' : 'Password' }}
          </label>
          <input
            type="password"
            v-model="form.password"
            :required="!editingUser"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            placeholder="••••••••"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
          <select
            v-model="form.role"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <p class="mt-1 text-xs text-gray-500">Admins have full access to all features</p>
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
            :disabled="isSubmitting"
            class="flex-1 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
          >
            <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? 'Saving...' : (editingUser ? 'Update User' : 'Create User') }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete User"
      :message="`Are you sure you want to delete user '${userToDelete?.username}'? This action cannot be undone.`"
      confirmText="Delete"
      :isLoading="deletingId !== null"
      @confirm="deleteUser"
      @cancel="isDeleteModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const users = ref([])
const isLoading = ref(true)
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isSubmitting = ref(false)
const deletingId = ref(null)
const editingUser = ref(null)
const userToDelete = ref(null)

const form = ref({
  username: '',
  password: '',
  role: 'user'
})

const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/v1/auth/users')
    users.value = response.data
  } catch (e) {
    toast.error('Failed to load users')
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const openCreateModal = () => {
  editingUser.value = null
  form.value = { username: '', password: '', role: 'user' }
  isModalOpen.value = true
}

const openEditModal = (user) => {
  editingUser.value = user
  form.value = {
    username: user.username,
    password: '',
    role: user.role
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  editingUser.value = null
}

const handleSubmit = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true

  try {
    if (editingUser.value) {
      // Update user
      const updateData = { role: form.value.role }
      if (form.value.password) {
        updateData.password = form.value.password
      }
      await axios.put(`/api/v1/auth/users/${editingUser.value.id}`, updateData)
      toast.success('User updated successfully')
    } else {
      // Create user
      await axios.post('/api/v1/auth/users', form.value)
      toast.success('User created successfully')
    }
    closeModal()
    fetchUsers()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save user')
  } finally {
    isSubmitting.value = false
  }
}

const confirmDelete = (user) => {
  userToDelete.value = user
  isDeleteModalOpen.value = true
}

const deleteUser = async () => {
  if (!userToDelete.value || deletingId.value) return
  deletingId.value = userToDelete.value.id

  try {
    await axios.delete(`/api/v1/auth/users/${userToDelete.value.id}`)
    toast.success('User deleted successfully')
    isDeleteModalOpen.value = false
    fetchUsers()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to delete user')
  } finally {
    deletingId.value = null
    userToDelete.value = null
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchUsers()
})
</script>
