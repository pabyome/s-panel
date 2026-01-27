<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Supervisor</h1>
        <p class="mt-1 text-sm text-gray-500">Manage background processes and services</p>
      </div>
      <button @click="fetchData" class="inline-flex items-center gap-2 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>
        Refresh
      </button>
      <button @click="openCreateModal" class="ml-2 inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 hover:shadow-xl hover:shadow-violet-500/30 hover:-translate-y-0.5">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add Service
      </button>
    </div>

    <!-- Supervisor Status Banner -->
    <div v-if="!supervisorStatus.running" class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-red-500 to-rose-500 p-5 shadow-lg shadow-red-500/20">
      <div class="absolute right-0 top-0 -mr-4 -mt-4 h-24 w-24 rounded-full bg-white/10"></div>
      <div class="relative flex items-start gap-4">
        <div class="rounded-xl bg-white/20 p-2.5 backdrop-blur-sm">
          <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-white">Supervisor Not Running</h3>
          <p class="mt-1 text-sm text-white/80">{{ supervisorStatus.error || 'Cannot connect to Supervisor XML-RPC.' }}</p>
          <button @click="showHelp = true" class="mt-2 text-sm font-medium text-white/90 hover:text-white underline underline-offset-2">
            View setup guide →
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div :class="[supervisorStatus.running ? 'bg-emerald-100' : 'bg-gray-100', 'rounded-xl p-2.5']">
            <svg :class="[supervisorStatus.running ? 'text-emerald-600' : 'text-gray-400', 'h-5 w-5']" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Daemon</p>
            <p :class="[supervisorStatus.running ? 'text-emerald-600' : 'text-red-600', 'text-xl font-bold']">
              {{ supervisorStatus.running ? 'Running' : 'Stopped' }}
            </p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-emerald-100 p-2.5">
            <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Running</p>
            <p class="text-xl font-bold text-gray-900">{{ processes.filter(p => p.statename === 'RUNNING').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-gray-100 p-2.5">
            <svg class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Stopped</p>
            <p class="text-xl font-bold text-gray-900">{{ processes.filter(p => p.statename === 'STOPPED').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-red-100 p-2.5">
            <svg class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Failed</p>
            <p class="text-xl font-bold text-gray-900">{{ processes.filter(p => p.statename === 'FATAL' || p.statename === 'BACKOFF').length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Processes Grid -->
    <div v-if="processes.length > 0" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div
        v-for="process in processes"
        :key="process.name"
        class="group rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md cursor-pointer"
        @click="goToDetail(process.name)"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div :class="[getStatusIconClass(process.statename), 'flex h-11 w-11 items-center justify-center rounded-xl text-white shadow-lg']">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
              </svg>
            </div>
            <div>
              <h3 class="text-base font-semibold text-gray-900">{{ process.name }}</h3>
              <p class="text-xs text-gray-500">{{ process.group }}</p>
            </div>
          </div>
          <span :class="getStatusBadgeClass(process.statename)">
            <span :class="getStatusDotClass(process.statename)"></span>
            {{ process.statename }}
          </span>
        </div>

        <div class="mt-4 space-y-2">
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
            </svg>
            <span class="truncate">{{ process.description || 'No description' }}</span>
          </div>
          <div v-if="process.pid && process.statename === 'RUNNING'" class="flex items-center gap-2 text-sm text-gray-600">
            <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5l-3.9 19.5m-2.1-19.5l-3.9 19.5" />
            </svg>
            <span>PID: <span class="font-mono">{{ process.pid }}</span></span>
            <span class="text-gray-300">|</span>
            <span>Uptime: {{ formatUptime(process.uptime_seconds) }}</span>
          </div>
        </div>

        <div class="mt-4 flex items-center gap-2 border-t border-gray-100 pt-4" @click.stop>
          <button
            v-if="process.statename === 'STOPPED' || process.statename === 'FATAL'"
            @click="controlProcess(process.name, 'start')"
            class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-100"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
            Start
          </button>
          <button
            v-if="process.statename === 'RUNNING'"
            @click="controlProcess(process.name, 'stop')"
            class="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 transition-colors hover:bg-red-100"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
            </svg>
            Stop
          </button>
          <button
            v-if="process.statename === 'RUNNING'"
            @click="controlProcess(process.name, 'restart')"
            class="inline-flex items-center gap-1.5 rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 transition-colors hover:bg-blue-100"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
            Restart
          </button>
          <button
            @click="goToDetail(process.name)"
            class="ml-auto inline-flex items-center gap-1.5 rounded-lg bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            Logs & Config
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="rounded-2xl bg-white p-12 shadow-sm ring-1 ring-gray-900/5 text-center">
      <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
        <svg class="h-7 w-7 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-semibold text-gray-900">No processes found</h3>
      <p class="mt-2 text-sm text-gray-500">
        {{ supervisorStatus.running ? 'No supervisor processes configured.' : 'Supervisor may not be running or accessible.' }}
      </p>
      <button @click="showHelp = true" class="mt-4 text-sm font-medium text-violet-600 hover:text-violet-500">
        View setup guide →
      </button>
    </div>

    <!-- Help Modal -->
    <BaseModal :isOpen="showHelp" @close="showHelp = false" title="Supervisor Setup Guide" :showFooter="false">
      <div class="space-y-5">
        <div class="rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 p-5 ring-1 ring-blue-100">
          <h4 class="text-sm font-semibold text-blue-900">Enable XML-RPC for Remote Management</h4>
          <p class="mt-2 text-sm text-blue-700">Supervisor needs XML-RPC enabled on port 9001 for this panel to work.</p>
        </div>

        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700">1</span>
            <div>
              <p class="text-sm font-medium text-gray-900">Install Supervisor</p>
              <code class="mt-1 block rounded-lg bg-gray-100 px-3 py-2 font-mono text-xs text-gray-700">sudo apt install supervisor</code>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700">2</span>
            <div>
              <p class="text-sm font-medium text-gray-900">Edit Configuration</p>
              <code class="mt-1 block rounded-lg bg-gray-100 px-3 py-2 font-mono text-xs text-gray-700">sudo nano /etc/supervisor/supervisord.conf</code>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700">3</span>
            <div>
              <p class="text-sm font-medium text-gray-900">Add inet_http_server section</p>
              <pre class="mt-1 rounded-lg bg-gray-900 px-3 py-2 font-mono text-xs text-gray-100 overflow-x-auto">[inet_http_server]
port = 127.0.0.1:9001</pre>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700">4</span>
            <div>
              <p class="text-sm font-medium text-gray-900">Restart Supervisor</p>
              <code class="mt-1 block rounded-lg bg-gray-100 px-3 py-2 font-mono text-xs text-gray-700">sudo systemctl restart supervisor</code>
            </div>
          </div>
        </div>
      </div>
      <div class="mt-6">
        <button @click="showHelp = false" class="w-full rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500">
          Got it
        </button>
      </div>
    </BaseModal>

    <!-- Create Service Modal -->
    <BaseModal :isOpen="isCreateModalOpen" @close="isCreateModalOpen = false" title="Add New Service" :showFooter="false">
      <form @submit.prevent="createProcess" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Service Name</label>
          <input
            type="text"
            v-model="createForm.name"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            placeholder="my-worker"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Command</label>
          <input
            type="text"
            v-model="createForm.command"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm font-mono"
            placeholder="/usr/bin/python3 /path/to/script.py"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Working Directory</label>
           <PathInput v-model="createForm.directory" placeholder="/var/www/my-app" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Run As User</label>
          <input
            type="text"
            v-model="createForm.user"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            placeholder="root"
          >
        </div>

        <div class="flex gap-6">
          <label class="flex items-center gap-2">
            <input type="checkbox" v-model="createForm.autostart" class="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-600">
            <span class="text-sm text-gray-700">Autostart</span>
          </label>
          <label class="flex items-center gap-2">
            <input type="checkbox" v-model="createForm.autorestart" class="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-600">
            <span class="text-sm text-gray-700">Autorestart</span>
          </label>
        </div>

         <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Number of Processes</label>
          <input
            type="number"
            v-model="createForm.numprocs"
            min="1"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
          >
        </div>

        <div class="flex gap-3 pt-2">
          <button
            type="button"
            @click="isCreateModalOpen = false"
            class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="flex-1 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500"
          >
            Create Service
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import PathInput from '../components/PathInput.vue'

const processes = ref([])
const supervisorStatus = ref({ running: false, state: 'UNKNOWN', version: null, error: null })
const showHelp = ref(false)
const isCreateModalOpen = ref(false)
const router = useRouter()

const createForm = reactive({
    name: '',
    command: '',
    directory: '',
    user: 'root',
    autostart: true,
    autorestart: true,
    numprocs: 1
})

const fetchData = async () => {
    await Promise.all([fetchStatus(), fetchProcesses()])
}

const fetchStatus = async () => {
    try {
        const response = await axios.get('/api/v1/supervisor/status')
        supervisorStatus.value = response.data
    } catch (e) {
        supervisorStatus.value = { running: false, state: 'ERROR', error: 'Failed to connect to API' }
    }
}

const fetchProcesses = async () => {
    try {
        const response = await axios.get('/api/v1/supervisor/processes')
        processes.value = response.data
    } catch (e) {
        console.error("Failed to fetch processes", e)
    }
}

const controlProcess = async (name, action) => {
    try {
        await axios.post(`/api/v1/supervisor/processes/${name}/${action}`)
        // Wait a bit for process state to change
        setTimeout(fetchProcesses, 500)
    } catch (e) {
        console.error(`Failed to ${action} process`, e)
        alert(`Failed to ${action} process`)
    }
}

const goToDetail = (name) => {
    router.push(`/supervisor/${name}`)
}

const openCreateModal = () => {
    createForm.name = ''
    createForm.command = ''
    createForm.directory = ''
    createForm.user = 'root'
    createForm.autostart = true
    createForm.autorestart = true
    createForm.numprocs = 1
    isCreateModalOpen.value = true
}

const createProcess = async () => {
    try {
        await axios.post('/api/v1/supervisor/processes', createForm)
        isCreateModalOpen.value = false
        // Refresh list
        setTimeout(fetchProcesses, 1000)
    } catch (e) {
        console.error("Failed to create process", e)
        alert("Failed to create process: " + (e.response?.data?.detail || e.message))
    }
}

const getStatusBadgeClass = (status) => {
    const base = 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium'
    switch (status) {
        case 'RUNNING': return `${base} bg-emerald-100 text-emerald-700`
        case 'STOPPED': return `${base} bg-gray-100 text-gray-700`
        case 'FATAL':
        case 'BACKOFF': return `${base} bg-red-100 text-red-700`
        default: return `${base} bg-amber-100 text-amber-700`
    }
}

const getStatusDotClass = (status) => {
    const base = 'h-1.5 w-1.5 rounded-full'
    switch (status) {
        case 'RUNNING': return `${base} bg-emerald-500 animate-pulse`
        case 'STOPPED': return `${base} bg-gray-400`
        case 'FATAL':
        case 'BACKOFF': return `${base} bg-red-500`
        default: return `${base} bg-amber-500`
    }
}

const getStatusIconClass = (status) => {
    switch (status) {
        case 'RUNNING': return 'bg-gradient-to-br from-emerald-500 to-green-600 shadow-emerald-500/30'
        case 'STOPPED': return 'bg-gradient-to-br from-gray-400 to-gray-500 shadow-gray-500/30'
        case 'FATAL':
        case 'BACKOFF': return 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/30'
        default: return 'bg-gradient-to-br from-amber-500 to-orange-600 shadow-amber-500/30'
    }
}

const formatUptime = (seconds) => {
    if (!seconds || seconds <= 0) return '0s'
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (days > 0) return `${days}d ${hours}h`
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m ${secs}s`
    return `${secs}s`
}

onMounted(() => {
    fetchData()
})
</script>
