<template>
  <div class="px-4 sm:px-6 lg:px-8 py-6">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-bold text-gray-900">PostgreSQL Manager</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your PostgreSQL databases, users, and configuration.</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none" v-if="status.installed && status.running">
        <span class="inline-flex items-center gap-x-1.5 rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
          <svg class="h-1.5 w-1.5 fill-green-500" viewBox="0 0 6 6" aria-hidden="true">
            <circle cx="3" cy="3" r="3" />
          </svg>
          Running (v{{ status.version }})
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingStatus" class="mt-6 flex justify-center">
        <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    </div>

    <!-- Not Installed State -->
    <div v-else-if="!status.installed" class="mt-8 rounded-xl border-2 border-dashed border-gray-300 p-12 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
      <h3 class="mt-2 text-sm font-semibold text-gray-900">PostgreSQL is not installed</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by installing the PostgreSQL service.</p>
      <div class="mt-6">
        <button
          type="button"
          @click="installService"
          :disabled="installing"
          class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
        >
          <svg v-if="installing" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ installing ? 'Installing...' : 'Install PostgreSQL' }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="mt-6">

        <!-- Tabs -->
        <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                <a
                    v-for="tab in tabs"
                    :key="tab.name"
                    href="#"
                    @click.prevent="currentTab = tab.name"
                    :class="[currentTab === tab.name ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']"
                >
                    {{ tab.name }}
                </a>
            </nav>
        </div>

        <!-- Databases Tab -->
        <div v-if="currentTab === 'Databases'" class="mt-6">
             <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-medium text-gray-900">Databases</h2>
                <button @click="openCreateDbModal" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                    Create Database
                </button>
             </div>

             <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Owner</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Size</th>
                            <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                <span class="sr-only">Actions</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                        <tr v-for="db in databases" :key="db.name">
                            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ db.name }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ db.owner }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ db.size }}</td>
                            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                <button @click="deleteDatabase(db.name)" class="text-red-600 hover:text-red-900">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="databases.length === 0">
                            <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">No databases found.</td>
                        </tr>
                    </tbody>
                </table>
             </div>
        </div>

        <!-- Users Tab -->
        <div v-if="currentTab === 'Users'" class="mt-6">
             <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-medium text-gray-900">Users & Roles</h2>
                <button @click="openCreateUserModal" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                    Create User
                </button>
             </div>

             <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Username</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Superuser</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Create DB</th>
                            <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                <span class="sr-only">Actions</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                        <tr v-for="user in users" :key="user.name">
                            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ user.name }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                <span v-if="user.superuser" class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Yes</span>
                                <span v-else class="text-gray-400">-</span>
                            </td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                <span v-if="user.createdb" class="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">Yes</span>
                                <span v-else class="text-gray-400">-</span>
                            </td>
                            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                <button @click="openChangePasswordModal(user)" class="text-indigo-600 hover:text-indigo-900 mr-4">Password</button>
                                <button v-if="user.name !== 'postgres'" @click="deleteUser(user.name)" class="text-red-600 hover:text-red-900">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
             </div>
        </div>

        <!-- Config Tab -->
        <div v-if="currentTab === 'Config'" class="mt-6">
             <div class="bg-white shadow sm:rounded-lg">
                <div class="px-4 py-5 sm:p-6">
                  <h3 class="text-base font-semibold leading-6 text-gray-900">Remote Access</h3>
                  <div class="mt-2 max-w-xl text-sm text-gray-500">
                    <p>By default, PostgreSQL only listens on localhost. Enabling remote access will allow connections from any IP address (0.0.0.0/0). <br/>
                    <strong>Security Note:</strong> Enabling this will enforce password authentication (MD5) for external connections and open port 5432 in the firewall.</p>
                  </div>
                  <div class="mt-5">
                    <button
                        @click="toggleRemoteAccess"
                        type="button"
                        :class="[status.remote_access ? 'bg-indigo-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2']"
                        role="switch"
                        :aria-checked="status.remote_access"
                    >
                        <span aria-hidden="true" :class="[status.remote_access ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']"></span>
                    </button>
                    <span class="ml-3 text-sm font-medium text-gray-900" v-if="status.remote_access">Enabled (Publicly Accessible)</span>
                    <span class="ml-3 text-sm font-medium text-gray-500" v-else>Disabled (Localhost Only)</span>
                  </div>
                </div>
             </div>

              <div class="mt-6 bg-white shadow sm:rounded-lg">
                <div class="px-4 py-5 sm:p-6">
                  <h3 class="text-base font-semibold leading-6 text-gray-900">Connection Info</h3>
                   <dl class="mt-4 grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Host</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ status.remote_access ? 'Your Server IP' : 'localhost' }}</dd>
                        </div>
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Port</dt>
                            <dd class="mt-1 text-sm text-gray-900">5432</dd>
                        </div>
                         <div class="sm:col-span-2">
                            <dt class="text-sm font-medium text-gray-500">Data Directory</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ status.data_dir }}</dd>
                        </div>
                   </dl>
                </div>
              </div>
        </div>

    </div>

    <!-- Create DB Modal -->
    <BaseModal :isOpen="isCreateDbOpen" @close="isCreateDbOpen = false" title="Create Database">
        <form @submit.prevent="createDatabase" class="space-y-4">
             <div>
                <label class="block text-sm font-medium text-gray-700">Database Name</label>
                <input type="text" v-model="createDbForm.name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="my_app_db">
             </div>
             <div>
                 <label class="block text-sm font-medium text-gray-700">Owner</label>
                 <select v-model="createDbForm.owner" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                     <option v-for="u in users" :key="u.name" :value="u.name">{{ u.name }}</option>
                 </select>
             </div>
             <div class="mt-5 flex justify-end gap-3">
                 <button type="button" @click="isCreateDbOpen = false" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
                 <button type="submit" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Create</button>
             </div>
        </form>
    </BaseModal>

    <!-- Create User Modal -->
    <BaseModal :isOpen="isCreateUserOpen" @close="isCreateUserOpen = false" title="Create User">
        <form @submit.prevent="createUser" class="space-y-4">
             <div>
                <label class="block text-sm font-medium text-gray-700">Username</label>
                <input type="text" v-model="createUserForm.name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="db_user">
             </div>
             <div>
                <label class="block text-sm font-medium text-gray-700">Password</label>
                <input type="password" v-model="createUserForm.password" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
             </div>
             <div class="flex items-center gap-4">
                 <div class="flex items-center">
                    <input id="createdb" type="checkbox" v-model="createUserForm.createdb" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
                    <label for="createdb" class="ml-2 block text-sm text-gray-900">Can Create DBs</label>
                </div>
                <div class="flex items-center">
                    <input id="superuser" type="checkbox" v-model="createUserForm.superuser" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
                    <label for="superuser" class="ml-2 block text-sm text-gray-900">Superuser</label>
                </div>
             </div>
             <div class="mt-5 flex justify-end gap-3">
                 <button type="button" @click="isCreateUserOpen = false" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
                 <button type="submit" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Create</button>
             </div>
        </form>
    </BaseModal>

    <!-- Change Password Modal -->
    <BaseModal :isOpen="isPassOpen" @close="isPassOpen = false" :title="'Change Password for ' + passForm.name">
        <form @submit.prevent="changePassword" class="space-y-4">
             <div>
                <label class="block text-sm font-medium text-gray-700">New Password</label>
                <input type="password" v-model="passForm.password" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
             </div>
             <div class="mt-5 flex justify-end gap-3">
                 <button type="button" @click="isPassOpen = false" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
                 <button type="submit" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Update</button>
             </div>
        </form>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'

const tabs = [
    { name: 'Databases' },
    { name: 'Users' },
    { name: 'Config' },
]
const currentTab = ref('Databases')

const status = ref({ installed: false, running: false, remote_access: false })
const loadingStatus = ref(true)
const installing = ref(false)

const databases = ref([])
const users = ref([])

// Modals
const isCreateDbOpen = ref(false)
const createDbForm = ref({ name: '', owner: 'postgres' })

const isCreateUserOpen = ref(false)
const createUserForm = ref({ name: '', password: '', superuser: false, createdb: false })

const isPassOpen = ref(false)
const passForm = ref({ name: '', password: '' })

// Actions
const fetchStatus = async () => {
    try {
        const { data } = await axios.get('/api/v1/postgres/status')
        status.value = data
        if (data.installed && data.running) {
            fetchDatabases()
            fetchUsers()
        }
    } catch (e) {
        console.error("Failed to fetch postgres status", e)
    } finally {
        loadingStatus.value = false
    }
}

const installService = async () => {
    installing.value = true
    try {
        await axios.post('/api/v1/postgres/install')
        await fetchStatus()
    } catch (e) {
        alert("Installation failed: " + (e.response?.data?.detail || e.message))
    } finally {
        installing.value = false
    }
}

const fetchDatabases = async () => {
    try {
        const { data } = await axios.get('/api/v1/postgres/databases')
        databases.value = data
    } catch (e) {
        console.error("Failed to fetch databases", e)
    }
}

const fetchUsers = async () => {
    try {
        const { data } = await axios.get('/api/v1/postgres/users')
        users.value = data
    } catch (e) {
        console.error("Failed to fetch users", e)
    }
}

const createDatabase = async () => {
    try {
        await axios.post('/api/v1/postgres/databases', createDbForm.value)
        isCreateDbOpen.value = false
        createDbForm.value.name = '' // keep owner
        fetchDatabases()
    } catch (e) {
        alert("Failed to create database: " + (e.response?.data?.detail || e.message))
    }
}

const deleteDatabase = async (name) => {
    if (!confirm(`Are you sure you want to delete database '${name}'? This cannot be undone.`)) return
    try {
        await axios.delete(`/api/v1/postgres/databases/${name}`)
        fetchDatabases()
    } catch (e) {
        alert("Failed to delete database: " + (e.response?.data?.detail || e.message))
    }
}

const createUser = async () => {
    try {
        await axios.post('/api/v1/postgres/users', createUserForm.value)
        isCreateUserOpen.value = false
        createUserForm.value = { name: '', password: '', superuser: false, createdb: false }
        fetchUsers()
    } catch (e) {
         alert("Failed to create user: " + (e.response?.data?.detail || e.message))
    }
}

const deleteUser = async (name) => {
    if (!confirm(`Are you sure you want to delete user '${name}'?`)) return
    try {
        await axios.delete(`/api/v1/postgres/users/${name}`)
        fetchUsers()
    } catch (e) {
        alert("Failed to delete user: " + (e.response?.data?.detail || e.message))
    }
}

const openChangePasswordModal = (user) => {
    passForm.value.name = user.name
    passForm.value.password = ''
    isPassOpen.value = true
}

const changePassword = async () => {
    try {
        await axios.put(`/api/v1/postgres/users/${passForm.value.name}/password`, { password: passForm.value.password })
        isPassOpen.value = false
        alert("Password updated successfully")
    } catch (e) {
         alert("Failed to update password: " + (e.response?.data?.detail || e.message))
    }
}

const toggleRemoteAccess = async () => {
    const newState = !status.value.remote_access
    if (newState && !confirm("Warning: Enabling remote access will expose your database to the internet. Password authentication will be enforced. Are you sure?")) return

    try {
        await axios.post('/api/v1/postgres/remote-access', { enable: newState })
        await fetchStatus() // Refresh
        alert(`Remote access ${newState ? 'enabled' : 'disabled'}. Service restarted.`)
    } catch (e) {
        alert("Failed to toggle remote access: " + (e.response?.data?.detail || e.message))
    }
}

const openCreateDbModal = () => {
    isCreateDbOpen.value = true
}

const openCreateUserModal = () => {
    isCreateUserOpen.value = true
}


onMounted(() => {
    fetchStatus()
})
</script>
