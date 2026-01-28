<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">PostgreSQL Manager</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your PostgreSQL databases, users, and configuration.</p>
      </div>
      <div class="flex items-center gap-3" v-if="status.installed">
        <span v-if="status.running" class="inline-flex items-center gap-x-1.5 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-medium text-emerald-700">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          Running (v{{ status.version }})
        </span>
        <span v-else class="inline-flex items-center gap-x-1.5 rounded-full bg-red-100 px-3 py-1.5 text-xs font-medium text-red-700">
          <svg class="h-1.5 w-1.5 fill-red-500" viewBox="0 0 6 6"><circle cx="3" cy="3" r="3" /></svg>
          Stopped
        </span>
        <div class="flex items-center gap-1">
          <button v-if="!status.running" @click="controlService('start')" :disabled="controllingService" class="rounded-lg bg-emerald-50 p-2 text-emerald-600 hover:bg-emerald-100 disabled:opacity-50" title="Start">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347c-.75.412-1.667-.13-1.667-.986V5.653Z" /></svg>
          </button>
          <button v-if="status.running" @click="controlService('stop')" :disabled="controllingService" class="rounded-lg bg-red-50 p-2 text-red-600 hover:bg-red-100 disabled:opacity-50" title="Stop">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 7.5A2.25 2.25 0 0 1 7.5 5.25h9a2.25 2.25 0 0 1 2.25 2.25v9a2.25 2.25 0 0 1-2.25 2.25h-9a2.25 2.25 0 0 1-2.25-2.25v-9Z" /></svg>
          </button>
          <button @click="controlService('restart')" :disabled="controllingService" class="rounded-lg bg-amber-50 p-2 text-amber-600 hover:bg-amber-100 disabled:opacity-50" title="Restart">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingStatus" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Not Installed State -->
    <div v-else-if="!status.installed" class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 p-12 text-center">
      <div class="mx-auto rounded-2xl bg-indigo-100 p-4 w-fit">
        <svg class="h-10 w-10 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
        </svg>
      </div>
      <h3 class="mt-4 text-lg font-semibold text-gray-900">PostgreSQL is not installed</h3>
      <p class="mt-2 text-sm text-gray-500">Get started by installing the PostgreSQL service on your server.</p>
      <button
        @click="installService"
        :disabled="installing"
        class="mt-6 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500 disabled:opacity-50"
      >
        <svg v-if="installing" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
        {{ installing ? 'Installing...' : 'Install PostgreSQL' }}
      </button>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
          <div class="flex items-center gap-3">
            <div class="rounded-xl bg-indigo-100 p-2.5">
              <svg class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" /></svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Databases</p>
              <p class="text-xl font-bold text-gray-900">{{ databases.length }}</p>
            </div>
          </div>
        </div>
        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
          <div class="flex items-center gap-3">
            <div class="rounded-xl bg-emerald-100 p-2.5">
              <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" /></svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Users</p>
              <p class="text-xl font-bold text-gray-900">{{ users.length }}</p>
            </div>
          </div>
        </div>
        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
          <div class="flex items-center gap-3">
            <div class="rounded-xl bg-violet-100 p-2.5">
              <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 0 1-3-3m3 3a3 3 0 1 0 0 6h13.5a3 3 0 1 0 0-6m-16.5-3a3 3 0 0 1 3-3h13.5a3 3 0 0 1 3 3m-19.5 0a4.5 4.5 0 0 1 .9-2.7L5.737 5.1a3.375 3.375 0 0 1 2.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 0 1 .9 2.7m0 0a3 3 0 0 1-3 3m0 3h.008v.008h-.008v-.008Zm0-6h.008v.008h-.008v-.008Zm-3 6h.008v.008h-.008v-.008Zm0-6h.008v.008h-.008v-.008Z" /></svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Total Size</p>
              <p class="text-xl font-bold text-gray-900">{{ totalSize }}</p>
            </div>
          </div>
        </div>
        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
          <div class="flex items-center gap-3">
            <div :class="[status.remote_access ? 'bg-amber-100' : 'bg-gray-100', 'rounded-xl p-2.5']">
              <svg :class="[status.remote_access ? 'text-amber-600' : 'text-gray-600', 'h-5 w-5']" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418" /></svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Remote Access</p>
              <p :class="[status.remote_access ? 'text-amber-600' : 'text-gray-900', 'text-xl font-bold']">{{ status.remote_access ? 'Enabled' : 'Disabled' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
        <div class="border-b border-gray-100 bg-gray-50/50">
          <nav class="flex -mb-px px-4" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              :class="[
                currentTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                'flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-4 text-sm font-medium transition-colors'
              ]"
            >
              {{ tab.name }}
            </button>
          </nav>
        </div>

        <!-- Databases Tab -->
        <div v-if="currentTab === 'databases'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Databases</h2>
            <button @click="openCreateDbModal" class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
              Create Database
            </button>
          </div>

          <div class="overflow-hidden rounded-xl ring-1 ring-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Name</th>
                  <th class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Owner</th>
                  <th class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Size</th>
                  <th class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 bg-white">
                <tr v-for="db in databases" :key="db.name" class="hover:bg-gray-50 transition-colors">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3">
                    <div class="flex items-center gap-3">
                      <div class="rounded-lg bg-indigo-100 p-2">
                        <svg class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" /></svg>
                      </div>
                      <span class="font-medium text-gray-900">{{ db.name }}</span>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ db.owner }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ db.size }}</td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <button @click="openBackupModal(db)" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" title="Backup">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" /></svg>
                      </button>
                      <button @click="runVacuum(db.name)" :disabled="vacuumingDb === db.name" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-50" title="Vacuum & Analyze">
                        <svg v-if="vacuumingDb === db.name" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 0 0-3.7-3.7 48.678 48.678 0 0 0-7.324 0 4.006 4.006 0 0 0-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 0 0 3.7 3.7 48.656 48.656 0 0 0 7.324 0 4.006 4.006 0 0 0 3.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3-3 3" /></svg>
                      </button>
                      <button @click="openExtensionsModal(db)" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" title="Extensions">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.25 6.087c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003 0-1.036-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003.215.283.401.604.401.959v0a.64.64 0 0 1-.657.643 48.39 48.39 0 0 1-4.163-.3c.186 1.613.293 3.25.315 4.907a.656.656 0 0 1-.658.663v0c-.355 0-.676-.186-.959-.401a1.647 1.647 0 0 0-1.003-.349c-1.036 0-1.875 1.007-1.875 2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401v0c.31 0 .555.26.532.57a48.039 48.039 0 0 1-.642 5.056c1.518.19 3.058.309 4.616.354a.64.64 0 0 0 .657-.643v0c0-.355-.186-.676-.401-.959a1.647 1.647 0 0 1-.349-1.003c0-1.035 1.008-1.875 2.25-1.875 1.243 0 2.25.84 2.25 1.875 0 .369-.128.713-.349 1.003-.215.283-.4.604-.4.959v0c0 .333.277.599.61.58a48.1 48.1 0 0 0 5.427-.63 48.05 48.05 0 0 0 .582-4.717.532.532 0 0 0-.533-.57v0c-.355 0-.676.186-.959.401-.29.221-.634.349-1.003.349-1.035 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25c.37 0 .713.128 1.003.349.283.215.604.401.96.401v0a.656.656 0 0 0 .658-.663 48.422 48.422 0 0 0-.37-5.36c-1.886.342-3.81.574-5.766.689a.578.578 0 0 1-.61-.58v0Z" /></svg>
                      </button>
                      <button @click="confirmDeleteDatabase(db.name)" :disabled="deletingDbName !== null" class="rounded-lg p-1.5 text-red-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-50" title="Delete">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="databases.length === 0">
                  <td colspan="4" class="px-6 py-8 text-center text-sm text-gray-500">No databases found. Create your first database to get started.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="currentTab === 'users'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Users & Roles</h2>
            <button @click="openCreateUserModal" class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
              Create User
            </button>
          </div>

          <div class="overflow-hidden rounded-xl ring-1 ring-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="py-3.5 pl-6 pr-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Username</th>
                  <th class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Superuser</th>
                  <th class="px-3 py-3.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Create DB</th>
                  <th class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 bg-white">
                <tr v-for="user in users" :key="user.name" class="hover:bg-gray-50 transition-colors">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3">
                    <div class="flex items-center gap-3">
                      <div :class="[user.superuser ? 'bg-amber-100' : 'bg-gray-100', 'rounded-lg p-2']">
                        <svg :class="[user.superuser ? 'text-amber-600' : 'text-gray-600', 'h-4 w-4']" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" /></svg>
                      </div>
                      <div>
                        <span class="font-medium text-gray-900">{{ user.name }}</span>
                        <span v-if="user.superuser" class="ml-2 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700">Admin</span>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span v-if="user.superuser" class="inline-flex items-center rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">Yes</span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span v-if="user.createdb" class="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">Yes</span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <button @click="openGrantModal(user)" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" title="Grant Access">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 1 1 9 0v3.75M3.75 21.75h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H3.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>
                      </button>
                      <button @click="openChangePasswordModal(user)" class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" title="Change Password">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z" /></svg>
                      </button>
                      <button v-if="user.name !== 'postgres'" @click="confirmDeleteUser(user.name)" :disabled="deletingUserName !== null" class="rounded-lg p-1.5 text-red-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-50" title="Delete">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="users.length === 0">
                  <td colspan="4" class="px-6 py-8 text-center text-sm text-gray-500">No users found. Create your first database user to get started.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Config Tab -->
        <div v-if="currentTab === 'config'" class="p-6 space-y-6">
          <!-- Remote Access -->
          <div class="rounded-xl bg-gray-50 p-6">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-sm font-semibold text-gray-900">Remote Access</h3>
                <p class="mt-1 text-sm text-gray-500">Allow connections from external hosts. Enabling this opens port 5432 and enforces password authentication.</p>
              </div>
              <button
                @click="confirmToggleRemoteAccess"
                :disabled="isTogglingRemote"
                :class="[status.remote_access ? 'bg-indigo-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 disabled:opacity-50']"
              >
                <span v-if="isTogglingRemote" class="absolute inset-0 flex items-center justify-center">
                  <svg class="h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                </span>
                <span v-else :class="[status.remote_access ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']"></span>
              </button>
            </div>
          </div>

          <!-- Connection Info -->
          <div class="rounded-xl bg-gray-50 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Connection Information</h3>
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <dt class="text-xs font-medium text-gray-500">Host</dt>
                <dd class="mt-1 font-mono text-sm text-gray-900">{{ status.remote_access ? 'Your Server IP' : 'localhost' }}</dd>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <dt class="text-xs font-medium text-gray-500">Port</dt>
                <dd class="mt-1 font-mono text-sm text-gray-900">5432</dd>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200 sm:col-span-2">
                <dt class="text-xs font-medium text-gray-500">Data Directory</dt>
                <dd class="mt-1 font-mono text-sm text-gray-900">{{ status.data_dir || '/var/lib/postgresql/data' }}</dd>
              </div>
            </dl>
          </div>

          <!-- Connection String Generator -->
          <div class="rounded-xl bg-gray-50 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Connection String Generator</h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3 mb-4">
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Database</label>
                <select v-model="connStringDb" class="block w-full rounded-lg border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500">
                  <option v-for="db in databases" :key="db.name" :value="db.name">{{ db.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">User</label>
                <select v-model="connStringUser" class="block w-full rounded-lg border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500">
                  <option v-for="user in users" :key="user.name" :value="user.name">{{ user.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Host</label>
                <input v-model="connStringHost" type="text" class="block w-full rounded-lg border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500" placeholder="localhost">
              </div>
            </div>
            <div class="relative">
              <pre class="rounded-lg bg-gray-900 p-4 text-sm text-gray-100 font-mono overflow-x-auto">{{ connectionString }}</pre>
              <button @click="copyConnectionString" class="absolute top-2 right-2 rounded-md bg-gray-700 p-1.5 text-gray-300 hover:bg-gray-600 hover:text-white">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" /></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Advanced Tab -->
        <div v-if="currentTab === 'advanced'" class="p-6 space-y-6">
          <!-- Maintenance Actions -->
          <div class="rounded-xl bg-gray-50 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Maintenance</h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <button @click="runVacuumAll" :disabled="vacuumingAll" class="flex items-center justify-between rounded-lg bg-white p-4 ring-1 ring-gray-200 hover:bg-gray-50 transition-colors disabled:opacity-50">
                <div class="flex items-center gap-3">
                  <div class="rounded-lg bg-violet-100 p-2">
                    <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 0 0-3.7-3.7 48.678 48.678 0 0 0-7.324 0 4.006 4.006 0 0 0-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 0 0 3.7 3.7 48.656 48.656 0 0 0 7.324 0 4.006 4.006 0 0 0 3.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3-3 3" /></svg>
                  </div>
                  <div class="text-left">
                    <p class="text-sm font-medium text-gray-900">Vacuum All Databases</p>
                    <p class="text-xs text-gray-500">Reclaim storage and update statistics</p>
                  </div>
                </div>
                <svg v-if="vacuumingAll" class="h-5 w-5 animate-spin text-violet-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                <svg v-else class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" /></svg>
              </button>
              <button @click="openBackupAllModal" class="flex items-center justify-between rounded-lg bg-white p-4 ring-1 ring-gray-200 hover:bg-gray-50 transition-colors">
                <div class="flex items-center gap-3">
                  <div class="rounded-lg bg-emerald-100 p-2">
                    <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" /></svg>
                  </div>
                  <div class="text-left">
                    <p class="text-sm font-medium text-gray-900">Backup All Databases</p>
                    <p class="text-xs text-gray-500">Create a full pg_dumpall backup</p>
                  </div>
                </div>
                <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" /></svg>
              </button>
            </div>
          </div>

          <!-- PostgreSQL Version Update -->
          <div class="rounded-xl bg-gray-50 p-6">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-sm font-semibold text-gray-900">PostgreSQL Version</h3>
                <p class="mt-1 text-sm text-gray-500">Current: v{{ status.version }}. Check for available updates.</p>
              </div>
              <button @click="checkPostgresUpdate" :disabled="checkingUpdate" class="inline-flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm font-medium text-gray-700 ring-1 ring-gray-200 hover:bg-gray-50 disabled:opacity-50">
                <svg v-if="checkingUpdate" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Check for Updates
              </button>
            </div>
            <div v-if="updateAvailable" class="mt-4 rounded-lg bg-amber-50 p-4">
              <div class="flex items-center gap-3">
                <svg class="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" /></svg>
                <div>
                  <p class="text-sm font-medium text-amber-800">Update Available: v{{ updateAvailable }}</p>
                  <p class="text-xs text-amber-700 mt-0.5">Run <code class="bg-amber-100 px-1 rounded">sudo apt update && sudo apt upgrade postgresql</code> to update.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Remote Server Commands -->
          <div class="rounded-xl bg-gray-50 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Remote Server Update Commands</h3>
            <p class="text-sm text-gray-500 mb-4">Common commands for updating and managing PostgreSQL on remote servers:</p>
            <div class="space-y-3">
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <div class="flex justify-between items-start mb-2">
                  <p class="text-xs font-medium text-gray-700">Update System Packages</p>
                  <button @click="copyCommand('sudo apt update && sudo apt upgrade -y')" class="text-xs text-indigo-600 hover:text-indigo-500">Copy</button>
                </div>
                <code class="text-xs text-gray-600 font-mono">sudo apt update && sudo apt upgrade -y</code>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <div class="flex justify-between items-start mb-2">
                  <p class="text-xs font-medium text-gray-700">Upgrade PostgreSQL</p>
                  <button @click="copyCommand('sudo apt update && sudo apt install --only-upgrade postgresql postgresql-contrib')" class="text-xs text-indigo-600 hover:text-indigo-500">Copy</button>
                </div>
                <code class="text-xs text-gray-600 font-mono">sudo apt update && sudo apt install --only-upgrade postgresql postgresql-contrib</code>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <div class="flex justify-between items-start mb-2">
                  <p class="text-xs font-medium text-gray-700">Check PostgreSQL Service Status</p>
                  <button @click="copyCommand('sudo systemctl status postgresql')" class="text-xs text-indigo-600 hover:text-indigo-500">Copy</button>
                </div>
                <code class="text-xs text-gray-600 font-mono">sudo systemctl status postgresql</code>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <div class="flex justify-between items-start mb-2">
                  <p class="text-xs font-medium text-gray-700">View PostgreSQL Logs</p>
                  <button @click="copyCommand('sudo journalctl -u postgresql --since today')" class="text-xs text-indigo-600 hover:text-indigo-500">Copy</button>
                </div>
                <code class="text-xs text-gray-600 font-mono">sudo journalctl -u postgresql --since today</code>
              </div>
              <div class="rounded-lg bg-white p-4 ring-1 ring-gray-200">
                <div class="flex justify-between items-start mb-2">
                  <p class="text-xs font-medium text-gray-700">Restart PostgreSQL</p>
                  <button @click="copyCommand('sudo systemctl restart postgresql')" class="text-xs text-indigo-600 hover:text-indigo-500">Copy</button>
                </div>
                <code class="text-xs text-gray-600 font-mono">sudo systemctl restart postgresql</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Create DB Modal -->
    <BaseModal :isOpen="isCreateDbOpen" @close="isCreateDbOpen = false" title="Create Database" :showFooter="false">
      <form @submit.prevent="createDatabase" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Database Name</label>
          <input
            type="text"
            v-model="createDbForm.name"
            required
            pattern="^[a-zA-Z0-9_]+$"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
            placeholder="my_app_db"
          >
          <p class="mt-1 text-xs text-gray-500">Only letters, numbers, and underscores allowed</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Owner</label>
          <select
            v-model="createDbForm.owner"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
          >
            <option v-for="u in users" :key="u.name" :value="u.name">{{ u.name }}</option>
          </select>
          <p class="mt-1 text-xs text-gray-500">The PostgreSQL user who will own this database</p>
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="isCreateDbOpen = false" class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">Cancel</button>
          <button type="submit" :disabled="isCreatingDb" class="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
            <svg v-if="isCreatingDb" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isCreatingDb ? 'Creating...' : 'Create Database' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Create User Modal -->
    <BaseModal :isOpen="isCreateUserOpen" @close="isCreateUserOpen = false" title="Create PostgreSQL User" :showFooter="false">
      <form @submit.prevent="createUser" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
          <input
            type="text"
            v-model="createUserForm.name"
            required
            pattern="^[a-zA-Z0-9_]+$"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
            placeholder="db_user"
          >
          <p class="mt-1 text-xs text-gray-500">Only letters, numbers, and underscores allowed</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input
            type="password"
            v-model="createUserForm.password"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
            placeholder="••••••••"
          >
        </div>
        <div class="rounded-xl bg-gray-50 p-4 space-y-3">
          <p class="text-sm font-medium text-gray-700">Permissions</p>
          <label class="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" v-model="createUserForm.createdb" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
            <div>
              <span class="text-sm font-medium text-gray-900">Can Create Databases</span>
              <p class="text-xs text-gray-500">Allow this user to create new databases</p>
            </div>
          </label>
          <label class="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" v-model="createUserForm.superuser" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
            <div>
              <span class="text-sm font-medium text-gray-900">Superuser</span>
              <p class="text-xs text-gray-500">Full administrative access (use with caution)</p>
            </div>
          </label>
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="isCreateUserOpen = false" class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">Cancel</button>
          <button type="submit" :disabled="isCreatingUser" class="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
            <svg v-if="isCreatingUser" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isCreatingUser ? 'Creating...' : 'Create User' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Change Password Modal -->
    <BaseModal :isOpen="isPassOpen" @close="isPassOpen = false" :title="'Change Password for ' + passForm.name" :showFooter="false">
      <form @submit.prevent="changePassword" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">New Password</label>
          <input
            type="password"
            v-model="passForm.password"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
            placeholder="••••••••"
          >
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="isPassOpen = false" class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">Cancel</button>
          <button type="submit" :disabled="isChangingPassword" class="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
            <svg v-if="isChangingPassword" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isChangingPassword ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Grant Access Modal -->
    <BaseModal :isOpen="isGrantOpen" @close="isGrantOpen = false" :title="'Grant Access to ' + grantForm.user" :showFooter="false">
      <form @submit.prevent="grantAccess" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Database</label>
          <select
            v-model="grantForm.database"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">Select a database</option>
            <option v-for="db in databases" :key="db.name" :value="db.name">{{ db.name }}</option>
          </select>
        </div>
        <div class="rounded-xl bg-amber-50 p-4">
          <div class="flex gap-3">
            <svg class="h-5 w-5 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" /></svg>
            <p class="text-sm text-amber-800">This will grant <strong>ALL privileges</strong> on the selected database to <strong>{{ grantForm.user }}</strong>.</p>
          </div>
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="isGrantOpen = false" class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">Cancel</button>
          <button type="submit" :disabled="isGranting" class="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
            <svg v-if="isGranting" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isGranting ? 'Granting...' : 'Grant Access' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Extensions Modal -->
    <BaseModal :isOpen="isExtensionsOpen" @close="isExtensionsOpen = false" :title="'Extensions - ' + selectedDb?.name" :showFooter="false">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Installed Extensions</label>
          <div v-if="extensions.length === 0" class="text-sm text-gray-500">No extensions installed.</div>
          <div v-else class="space-y-2">
            <div v-for="ext in extensions" :key="ext.name" class="flex items-center justify-between rounded-lg bg-gray-50 p-3">
              <div>
                <span class="font-medium text-gray-900">{{ ext.name }}</span>
                <span class="ml-2 text-xs text-gray-500">v{{ ext.version }}</span>
              </div>
              <button @click="manageExtension(ext.name, 'drop')" class="text-sm text-red-600 hover:text-red-500">Remove</button>
            </div>
          </div>
        </div>
        <div class="border-t pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Add Extension</label>
          <div class="flex gap-2">
            <select v-model="newExtension" class="flex-1 rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              <option value="">Select extension</option>
              <option v-for="ext in availableExtensions" :key="ext" :value="ext">{{ ext }}</option>
            </select>
            <button @click="manageExtension(newExtension, 'create')" :disabled="!newExtension || managingExtension" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">Add</button>
          </div>
        </div>
      </div>
    </BaseModal>

    <!-- Backup Modal -->
    <BaseModal :isOpen="isBackupOpen" @close="isBackupOpen = false" :title="'Backup - ' + (selectedDb?.name || 'All Databases')" :showFooter="false">
      <div class="space-y-4">
        <p class="text-sm text-gray-500">Create a backup of <strong>{{ selectedDb?.name || 'all databases' }}</strong>. The backup will be saved as a .sql file.</p>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Backup Format</label>
          <select v-model="backupFormat" class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
            <option value="plain">Plain SQL (.sql)</option>
            <option value="custom">Custom Format (.dump)</option>
          </select>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button type="button" @click="isBackupOpen = false" class="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Cancel</button>
          <button @click="createBackup" :disabled="creatingBackup" class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
            <svg v-if="creatingBackup" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ creatingBackup ? 'Creating...' : 'Create Backup' }}
          </button>
        </div>
      </div>
    </BaseModal>

    <!-- Confirmation Modals -->
    <ConfirmModal
      :isOpen="isDeleteDbModalOpen"
      type="danger"
      title="Delete Database"
      :message="`Are you sure you want to delete database '${dbToDelete}'? This action cannot be undone.`"
      confirmText="Delete"
      :isLoading="deletingDbName !== null"
      @confirm="deleteDatabase"
      @cancel="isDeleteDbModalOpen = false"
    />

    <ConfirmModal
      :isOpen="isDeleteUserModalOpen"
      type="danger"
      title="Delete User"
      :message="`Are you sure you want to delete user '${userToDelete}'?`"
      confirmText="Delete"
      :isLoading="deletingUserName !== null"
      @confirm="deleteUser"
      @cancel="isDeleteUserModalOpen = false"
    />

    <ConfirmModal
      :isOpen="isRemoteAccessModalOpen"
      type="warning"
      title="Enable Remote Access"
      message="Warning: Enabling remote access will expose your database to the internet. Password authentication will be enforced and port 5432 will be opened. Are you sure?"
      confirmText="Enable"
      :isLoading="isTogglingRemote"
      @confirm="toggleRemoteAccess"
      @cancel="isRemoteAccessModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const tabs = [
  { id: 'databases', name: 'Databases' },
  { id: 'users', name: 'Users' },
  { id: 'config', name: 'Config' },
  { id: 'advanced', name: 'Advanced' },
]
const currentTab = ref('databases')

// Status
const status = ref({ installed: false, running: false, remote_access: false, version: '', data_dir: '' })
const loadingStatus = ref(true)
const installing = ref(false)
const controllingService = ref(false)

// Data
const databases = ref([])
const users = ref([])
const extensions = ref([])

// Create DB Modal
const isCreateDbOpen = ref(false)
const createDbForm = ref({ name: '', owner: 'postgres' })
const isCreatingDb = ref(false)

// Create User Modal
const isCreateUserOpen = ref(false)
const createUserForm = ref({ name: '', password: '', superuser: false, createdb: false })
const isCreatingUser = ref(false)

// Password Modal
const isPassOpen = ref(false)
const passForm = ref({ name: '', password: '' })
const isChangingPassword = ref(false)

// Grant Modal
const isGrantOpen = ref(false)
const grantForm = ref({ user: '', database: '' })
const isGranting = ref(false)

// Extensions Modal
const isExtensionsOpen = ref(false)
const selectedDb = ref(null)
const newExtension = ref('')
const managingExtension = ref(false)
const availableExtensions = ['uuid-ossp', 'pgcrypto', 'pg_trgm', 'hstore', 'postgis', 'citext', 'ltree', 'tablefunc']

// Backup Modal
const isBackupOpen = ref(false)
const backupFormat = ref('plain')
const creatingBackup = ref(false)

// Confirmation modals
const isDeleteDbModalOpen = ref(false)
const isDeleteUserModalOpen = ref(false)
const isRemoteAccessModalOpen = ref(false)
const dbToDelete = ref(null)
const userToDelete = ref(null)

// Loading states
const deletingDbName = ref(null)
const deletingUserName = ref(null)
const isTogglingRemote = ref(false)
const vacuumingDb = ref(null)
const vacuumingAll = ref(false)
const checkingUpdate = ref(false)
const updateAvailable = ref(null)

// Connection string
const connStringDb = ref('')
const connStringUser = ref('postgres')
const connStringHost = ref('localhost')

const totalSize = computed(() => {
  if (databases.value.length === 0) return '0 MB'
  let total = 0
  for (const db of databases.value) {
    const match = db.size?.match(/([\d.]+)\s*(\w+)/)
    if (match) {
      const val = parseFloat(match[1])
      const unit = match[2].toUpperCase()
      if (unit === 'GB') total += val * 1024
      else if (unit === 'MB') total += val
      else if (unit === 'KB') total += val / 1024
    }
  }
  if (total >= 1024) return (total / 1024).toFixed(1) + ' GB'
  return total.toFixed(1) + ' MB'
})

const connectionString = computed(() => {
  const db = connStringDb.value || 'dbname'
  const user = connStringUser.value || 'postgres'
  const host = connStringHost.value || 'localhost'
  return `postgresql://${user}:PASSWORD@${host}:5432/${db}`
})

// Fetch functions
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

const fetchDatabases = async () => {
  try {
    const { data } = await axios.get('/api/v1/postgres/databases')
    databases.value = data
    if (data.length > 0 && !connStringDb.value) {
      connStringDb.value = data[0].name
    }
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

const fetchExtensions = async (db) => {
  try {
    const { data } = await axios.get(`/api/v1/postgres/databases/${db.name}/extensions`)
    extensions.value = data
  } catch (e) {
    console.error("Failed to fetch extensions", e)
  }
}

// Actions
const installService = async () => {
  installing.value = true
  try {
    await axios.post('/api/v1/postgres/install')
    await fetchStatus()
    toast.success('PostgreSQL installed successfully')
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Installation failed")
  } finally {
    installing.value = false
  }
}

const controlService = async (action) => {
  controllingService.value = true
  try {
    await axios.post(`/api/v1/postgres/control/${action}`)
    toast.success(`Service ${action}ed successfully`)
    setTimeout(fetchStatus, 1000)
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || `Failed to ${action} service`)
  } finally {
    controllingService.value = false
  }
}

// Database CRUD
const openCreateDbModal = () => {
  createDbForm.value = { name: '', owner: 'postgres' }
  isCreateDbOpen.value = true
}

const createDatabase = async () => {
  if (isCreatingDb.value) return
  isCreatingDb.value = true
  try {
    await axios.post('/api/v1/postgres/databases', createDbForm.value)
    toast.success('Database created successfully')
    isCreateDbOpen.value = false
    fetchDatabases()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to create database")
  } finally {
    isCreatingDb.value = false
  }
}

const confirmDeleteDatabase = (name) => {
  dbToDelete.value = name
  isDeleteDbModalOpen.value = true
}

const deleteDatabase = async () => {
  if (!dbToDelete.value || deletingDbName.value) return
  deletingDbName.value = dbToDelete.value
  try {
    await axios.delete(`/api/v1/postgres/databases/${dbToDelete.value}`)
    toast.success('Database deleted successfully')
    isDeleteDbModalOpen.value = false
    fetchDatabases()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to delete database")
  } finally {
    deletingDbName.value = null
    dbToDelete.value = null
  }
}

// User CRUD
const openCreateUserModal = () => {
  createUserForm.value = { name: '', password: '', superuser: false, createdb: false }
  isCreateUserOpen.value = true
}

const createUser = async () => {
  if (isCreatingUser.value) return
  isCreatingUser.value = true
  try {
    await axios.post('/api/v1/postgres/users', createUserForm.value)
    toast.success('User created successfully')
    isCreateUserOpen.value = false
    fetchUsers()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to create user")
  } finally {
    isCreatingUser.value = false
  }
}

const confirmDeleteUser = (name) => {
  userToDelete.value = name
  isDeleteUserModalOpen.value = true
}

const deleteUser = async () => {
  if (!userToDelete.value || deletingUserName.value) return
  deletingUserName.value = userToDelete.value
  try {
    await axios.delete(`/api/v1/postgres/users/${userToDelete.value}`)
    toast.success('User deleted successfully')
    isDeleteUserModalOpen.value = false
    fetchUsers()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to delete user")
  } finally {
    deletingUserName.value = null
    userToDelete.value = null
  }
}

const openChangePasswordModal = (user) => {
  passForm.value = { name: user.name, password: '' }
  isPassOpen.value = true
}

const changePassword = async () => {
  if (isChangingPassword.value) return
  isChangingPassword.value = true
  try {
    await axios.put(`/api/v1/postgres/users/${passForm.value.name}/password`, { password: passForm.value.password })
    isPassOpen.value = false
    toast.success("Password updated successfully")
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to update password")
  } finally {
    isChangingPassword.value = false
  }
}

const openGrantModal = (user) => {
  grantForm.value = { user: user.name, database: '' }
  isGrantOpen.value = true
}

const grantAccess = async () => {
  if (isGranting.value || !grantForm.value.database) return
  isGranting.value = true
  try {
    await axios.post('/api/v1/postgres/grant', grantForm.value)
    isGrantOpen.value = false
    toast.success("Access granted successfully")
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to grant access")
  } finally {
    isGranting.value = false
  }
}

// Remote Access
const confirmToggleRemoteAccess = () => {
  if (!status.value.remote_access) {
    isRemoteAccessModalOpen.value = true
  } else {
    toggleRemoteAccess()
  }
}

const toggleRemoteAccess = async () => {
  const newState = !status.value.remote_access
  if (isTogglingRemote.value) return
  isTogglingRemote.value = true
  try {
    await axios.post('/api/v1/postgres/remote-access', { enable: newState })
    await fetchStatus()
    isRemoteAccessModalOpen.value = false
    toast.success(`Remote access ${newState ? 'enabled' : 'disabled'}. Service restarted.`)
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to toggle remote access")
  } finally {
    isTogglingRemote.value = false
  }
}

// Extensions
const openExtensionsModal = async (db) => {
  selectedDb.value = db
  await fetchExtensions(db)
  isExtensionsOpen.value = true
}

const manageExtension = async (name, action) => {
  if (!name || managingExtension.value) return
  managingExtension.value = true
  try {
    await axios.post(`/api/v1/postgres/databases/${selectedDb.value.name}/extensions`, { name, action })
    toast.success(`Extension ${action === 'create' ? 'added' : 'removed'} successfully`)
    await fetchExtensions(selectedDb.value)
    newExtension.value = ''
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to manage extension")
  } finally {
    managingExtension.value = false
  }
}

// Backup
const openBackupModal = (db) => {
  selectedDb.value = db
  backupFormat.value = 'plain'
  isBackupOpen.value = true
}

const openBackupAllModal = () => {
  selectedDb.value = { name: 'all' }
  backupFormat.value = 'plain'
  isBackupOpen.value = true
}

const createBackup = async () => {
  if (creatingBackup.value) return
  creatingBackup.value = true
  try {
    const endpoint = selectedDb.value.name === 'all'
      ? '/api/v1/postgres/backup-all'
      : `/api/v1/postgres/databases/${selectedDb.value.name}/backup`
    await axios.post(endpoint, { format: backupFormat.value })
    isBackupOpen.value = false
    toast.success('Backup created successfully')
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to create backup")
  } finally {
    creatingBackup.value = false
  }
}

// Maintenance
const runVacuum = async (dbName) => {
  vacuumingDb.value = dbName
  try {
    await axios.post(`/api/v1/postgres/databases/${dbName}/vacuum`)
    toast.success(`Vacuum completed for ${dbName}`)
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Vacuum failed")
  } finally {
    vacuumingDb.value = null
  }
}

const runVacuumAll = async () => {
  vacuumingAll.value = true
  try {
    await axios.post('/api/v1/postgres/vacuum-all')
    toast.success('Vacuum completed for all databases')
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Vacuum failed")
  } finally {
    vacuumingAll.value = false
  }
}

const checkPostgresUpdate = async () => {
  checkingUpdate.value = true
  try {
    const { data } = await axios.get('/api/v1/postgres/check-update')
    updateAvailable.value = data.available_version
    if (!data.available_version) {
      toast.success('PostgreSQL is up to date')
    }
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || "Failed to check for updates")
  } finally {
    checkingUpdate.value = false
  }
}

const copyConnectionString = () => {
  navigator.clipboard.writeText(connectionString.value)
  toast.success('Connection string copied to clipboard')
}

const copyCommand = (cmd) => {
  navigator.clipboard.writeText(cmd)
  toast.success('Command copied to clipboard')
}

onMounted(() => {
  fetchStatus()
})
</script>
