<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Deployments</h1>
        <p class="mt-1 text-sm text-gray-500">Automated GitHub deployments via webhooks</p>
      </div>
      <button @click="openModal" class="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 hover:shadow-xl hover:shadow-violet-500/30 hover:-translate-y-0.5">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add Deployment
      </button>
    </div>

    <!-- Stats Cards - Responsive Grid -->
    <div class="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      <div class="rounded-2xl bg-white p-4 sm:p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="rounded-xl bg-violet-100 p-2 sm:p-2.5">
            <svg class="h-4 w-4 sm:h-5 sm:w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
            </svg>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-500">Total</p>
            <p class="text-lg sm:text-xl font-bold text-gray-900">{{ deployments.length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-4 sm:p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="rounded-xl bg-emerald-100 p-2 sm:p-2.5">
            <svg class="h-4 w-4 sm:h-5 sm:w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-500">Successful</p>
            <p class="text-lg sm:text-xl font-bold text-gray-900">{{ deployments.filter(d => d.last_status === 'success').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-4 sm:p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="rounded-xl bg-red-100 p-2 sm:p-2.5">
            <svg class="h-4 w-4 sm:h-5 sm:w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-500">Failed</p>
            <p class="text-lg sm:text-xl font-bold text-gray-900">{{ deployments.filter(d => d.last_status === 'failed').length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-4 sm:p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="rounded-xl bg-blue-100 p-2 sm:p-2.5">
            <svg class="h-4 w-4 sm:h-5 sm:w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-500">Total Deploys</p>
            <p class="text-lg sm:text-xl font-bold text-gray-900">{{ totalDeploys }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 gap-4 sm:gap-5 lg:grid-cols-2">
      <div v-for="i in 2" :key="i" class="rounded-2xl bg-white p-4 sm:p-6 shadow-sm ring-1 ring-gray-900/5 animate-pulse">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="h-11 w-11 rounded-xl bg-gray-200"></div>
            <div>
              <div class="h-4 w-32 bg-gray-200 rounded"></div>
              <div class="mt-2 h-3 w-20 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div class="h-6 w-16 bg-gray-200 rounded-full"></div>
        </div>
        <div class="mt-4 space-y-3">
          <div class="h-3 w-48 bg-gray-200 rounded"></div>
          <div class="h-3 w-32 bg-gray-200 rounded"></div>
        </div>
        <div class="mt-5 flex gap-2 border-t border-gray-100 pt-4">
          <div class="h-8 w-20 bg-gray-200 rounded-lg"></div>
          <div class="h-8 w-20 bg-gray-200 rounded-lg"></div>
          <div class="h-8 w-16 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    </div>

    <!-- Deployments Grid - Responsive -->
    <div v-else-if="deployments.length > 0" class="grid grid-cols-1 gap-4 sm:gap-5 lg:grid-cols-2">
      <div
        v-for="deploy in deployments"
        :key="deploy.id"
        class="group rounded-2xl bg-white p-4 sm:p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
      >
        <!-- Card Header -->
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-2 sm:gap-3 min-w-0">
            <div class="flex h-9 w-9 sm:h-11 sm:w-11 items-center justify-center rounded-xl bg-linear-to-br from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30 shrink-0">
              <svg class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
              </svg>
            </div>
            <div class="min-w-0">
              <h3 class="text-sm sm:text-base font-semibold text-gray-900 truncate">{{ deploy.name }}</h3>
              <p class="text-xs text-gray-500 truncate">
                <span class="font-mono">{{ deploy.branch }}</span>
                <span class="mx-1 hidden sm:inline">·</span>
                <span class="hidden sm:inline">User: {{ deploy.run_as_user || 'root' }}</span>
              </p>
            </div>
          </div>
          <span :class="getStatusBadgeClass(deploy.last_status)" class="shrink-0">
            <span v-if="deploy.last_status === 'running'" class="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-current"></span>
            <span v-else :class="getStatusDotClass(deploy.last_status)"></span>
            {{ getStatusText(deploy.last_status) }}
          </span>
        </div>

        <!-- Running Deployment Banner -->
        <div v-if="deploy.last_status === 'running'" class="mt-3 rounded-lg bg-blue-50 px-3 py-2 ring-1 ring-blue-100">
          <div class="flex items-center gap-2">
            <svg class="h-4 w-4 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="text-xs font-medium text-blue-700">Deployment in progress...</span>
            <button @click="showLogs(deploy)" class="ml-auto text-xs font-medium text-blue-600 hover:text-blue-800 underline">View Logs</button>
          </div>
        </div>

        <!-- Card Body -->
        <div class="mt-3 sm:mt-4 space-y-2 sm:space-y-3">
          <div class="flex items-center gap-2 text-xs sm:text-sm text-gray-600">
            <svg class="h-3.5 w-3.5 sm:h-4 sm:w-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
            </svg>
            <span class="truncate font-mono text-xs">{{ deploy.project_path }}</span>
          </div>

          <div v-if="deploy.notification_emails" class="flex items-center gap-2 text-xs sm:text-sm text-gray-600">
            <svg class="h-3.5 w-3.5 sm:h-4 sm:w-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
            </svg>
            <span class="truncate text-xs">{{ deploy.notification_emails }}</span>
          </div>

          <div v-if="deploy.last_deployed_at" class="flex items-center gap-2 text-xs sm:text-sm">
            <svg class="h-3.5 w-3.5 sm:h-4 sm:w-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-gray-500 text-xs">{{ formatRelativeTime(deploy.last_deployed_at) }}</span>
            <span v-if="deploy.last_commit" class="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-600 hidden sm:inline">{{ deploy.last_commit }}</span>
          </div>
        </div>

        <!-- Card Actions - Responsive -->
        <div class="mt-4 sm:mt-5 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-3 sm:pt-4">
          <button
            @click="triggerDeploy(deploy)"
            :disabled="deploy.last_status === 'running' || triggeringId === deploy.id"
            :title="deploy.last_status === 'running' ? 'A deployment is already in progress' : 'Trigger deployment'"
            class="inline-flex items-center gap-1 sm:gap-1.5 rounded-lg bg-violet-50 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-violet-700 transition-colors hover:bg-violet-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="triggeringId === deploy.id" class="h-3 w-3 sm:h-3.5 sm:w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else-if="deploy.last_status === 'running'" class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            <svg v-else class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
            <span class="hidden sm:inline">{{ deploy.last_status === 'running' ? 'Running' : 'Deploy' }}</span>
          </button>
          <button
            @click="showDetails(deploy)"
            class="inline-flex items-center gap-1 sm:gap-1.5 rounded-lg bg-gray-50 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            <svg class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
            </svg>
            <span class="hidden sm:inline">Webhook</span>
          </button>
          <button
            @click="showLogs(deploy)"
            class="inline-flex items-center gap-1 sm:gap-1.5 rounded-lg bg-gray-50 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            <svg class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <span class="hidden sm:inline">Logs</span>
          </button>
          <button
            @click="openEditModal(deploy)"
            class="inline-flex items-center gap-1 sm:gap-1.5 rounded-lg bg-gray-50 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-100"
          >
            <svg class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
            </svg>
            <span class="hidden sm:inline">Edit</span>
          </button>
          <button
            @click="confirmDelete(deploy.id)"
            :disabled="deletingId === deploy.id"
            class="ml-auto inline-flex items-center gap-1 sm:gap-1.5 rounded-lg px-2.5 sm:px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="deletingId === deploy.id" class="h-3 w-3 sm:h-3.5 sm:w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="h-3 w-3 sm:h-3.5 sm:w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!isLoading" class="rounded-2xl bg-white p-8 sm:p-12 shadow-sm ring-1 ring-gray-900/5 text-center">
      <div class="mx-auto flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-full bg-violet-100">
        <svg class="h-6 w-6 sm:h-7 sm:w-7 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-semibold text-gray-900">No deployments configured</h3>
      <p class="mt-2 text-sm text-gray-500">Set up automated deployments from GitHub with webhooks.</p>
      <button @click="openModal" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Create your first deployment
      </button>
    </div>

    <!-- Webhook Details Modal -->
    <BaseModal :isOpen="isDetailsOpen" @close="isDetailsOpen = false" title="Webhook Configuration" :showFooter="false">
      <div v-if="selectedDeploy" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Payload URL</label>
          <div class="flex rounded-xl shadow-sm">
            <input
              type="text"
              readonly
              :value="getWebhookUrl(selectedDeploy)"
              class="block w-full rounded-l-xl border-0 py-2.5 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 bg-gray-50 sm:text-sm font-mono text-xs"
            >
            <button
              @click="copyToClipboard(getWebhookUrl(selectedDeploy))"
              class="inline-flex items-center px-3 sm:px-4 border border-l-0 border-gray-300 rounded-r-xl bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Secret (HMAC)</label>
          <div class="flex rounded-xl shadow-sm">
            <input
              type="text"
              readonly
              :value="selectedDeploy.secret"
              class="block w-full rounded-l-xl border-0 py-2.5 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 bg-gray-50 sm:text-sm font-mono text-xs"
            >
            <button
              @click="copyToClipboard(selectedDeploy.secret)"
              class="inline-flex items-center px-3 sm:px-4 border border-l-0 border-gray-300 rounded-r-xl bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
              </svg>
            </button>
          </div>
        </div>

        <div class="rounded-xl bg-linear-to-br from-blue-50 to-indigo-50 p-4 sm:p-5 ring-1 ring-blue-100">
          <h4 class="flex items-center gap-2 text-sm font-semibold text-blue-900">
            <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub Setup Instructions
          </h4>
          <ol class="mt-3 space-y-2 text-xs sm:text-sm text-blue-800">
            <li class="flex items-start gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700 shrink-0">1</span>
              <span>Go to your repository <strong>Settings</strong> → <strong>Webhooks</strong></span>
            </li>
            <li class="flex items-start gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700 shrink-0">2</span>
              <span>Click <strong>Add webhook</strong></span>
            </li>
            <li class="flex items-start gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700 shrink-0">3</span>
              <span>Paste the <strong>Payload URL</strong> and <strong>Secret</strong></span>
            </li>
            <li class="flex items-start gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700 shrink-0">4</span>
              <span>Set Content type to <code class="rounded bg-blue-200/50 px-1">application/json</code></span>
            </li>
            <li class="flex items-start gap-2">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700 shrink-0">5</span>
              <span>Select <strong>"Just the push event"</strong></span>
            </li>
          </ol>
        </div>
      </div>
      <div class="mt-6">
        <button @click="isDetailsOpen = false" type="button" class="w-full rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500">
          Done
        </button>
      </div>
    </BaseModal>

    <!-- Live Logs Modal -->
    <BaseModal :isOpen="isLogsOpen" @close="closeLogs" title="Deployment Logs" size="lg" :showFooter="false">
      <div v-if="selectedDeploy" class="space-y-4">
        <div class="flex flex-wrap items-center gap-2 sm:gap-3">
          <span :class="getStatusBadgeClass(liveStatus || selectedDeploy.last_status)">
            <span v-if="(liveStatus || selectedDeploy.last_status) === 'running'" class="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-current"></span>
            {{ getStatusText(liveStatus || selectedDeploy.last_status) }}
          </span>
          <span v-if="selectedDeploy.last_deployed_at" class="text-xs sm:text-sm text-gray-500">
            {{ formatDate(selectedDeploy.last_deployed_at) }}
          </span>
          <span v-if="selectedDeploy.last_commit" class="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-600">
            {{ selectedDeploy.last_commit }}
          </span>
          <span v-if="wsConnected" class="flex items-center gap-1 text-xs text-emerald-600">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Live
          </span>
        </div>
        <div ref="logsContainer" class="rounded-xl bg-gray-900 p-3 sm:p-4 h-64 sm:h-96 overflow-auto scroll-smooth">
          <pre class="text-xs text-gray-100 font-mono whitespace-pre-wrap">{{ liveLogs || selectedDeploy.last_logs || 'No logs available' }}</pre>
        </div>
      </div>
      <div class="mt-4 sm:mt-6 flex flex-col sm:flex-row gap-2 sm:gap-3">
        <button @click="confirmClearLogs" :disabled="isClearingLogs" type="button" class="flex-1 rounded-xl bg-red-50 px-4 py-2.5 text-sm font-semibold text-red-600 transition-all hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2">
          <svg v-if="isClearingLogs" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isClearingLogs ? 'Clearing...' : 'Clear Logs' }}
        </button>
        <button @click="closeLogs" type="button" class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200">
          Close
        </button>
      </div>
    </BaseModal>

    <!-- Edit Deployment Modal -->
    <BaseModal :isOpen="isEditModalOpen" @close="isEditModalOpen = false" title="Edit Deployment" :showFooter="false">
      <form @submit.prevent="updateDeployment" class="space-y-4 sm:space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
          <input
            type="text"
            v-model="editForm.name"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Project Path</label>
          <PathInput v-model="editForm.project_path" placeholder="/var/www/my-app" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Git Branch</label>
            <input
              type="text"
              v-model="editForm.branch"
              class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Run As User</label>
            <UserSelect v-model="editForm.run_as_user" />
          </div>
        </div>

        <div class="space-y-4 rounded-xl bg-gray-50 p-4 ring-1 ring-gray-200">
          <div class="flex items-center justify-between">
            <label class="block text-sm font-medium text-gray-700">Deployment Mode</label>
            <div class="flex rounded-lg bg-gray-200 p-1">
              <button
                type="button"
                @click="editForm.mode = 'supervisor'"
                :class="[
                  'rounded-md px-3 py-1 text-sm font-medium transition-all',
                  editForm.mode === 'supervisor' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                Supervisor
              </button>
              <button
                type="button"
                @click="editForm.mode = 'docker-swarm'; editForm.post_deploy_command = ''; editForm.supervisor_process = ''"
                :class="[
                  'rounded-md px-3 py-1 text-sm font-medium transition-all',
                  editForm.mode === 'docker-swarm' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                Docker Swarm
              </button>
            </div>
          </div>

          <div v-if="editForm.mode === 'supervisor'">
            <label class="block text-sm font-medium text-gray-700 mb-2">Supervisor Process</label>
            <select
              v-model="editForm.supervisor_process"
              class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            >
              <option value="">None (optional)</option>
              <option v-for="proc in processes" :key="proc.name" :value="proc.name">{{ proc.name }}</option>
            </select>
             <p class="mt-1.5 text-xs text-gray-500">Process to restart after successful deployment.</p>
          </div>

          <div v-if="editForm.mode === 'docker-swarm'" class="space-y-4">
             <div class="grid grid-cols-2 gap-4">
                <div>
                   <label class="block text-sm font-medium text-gray-700 mb-2">Replicas</label>
                   <input
                     type="number"
                     v-model.number="editForm.swarm_replicas"
                     min="1"
                     class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                   >
                </div>
                <div>
                   <label class="block text-sm font-medium text-gray-700 mb-2">App Port</label>
                   <input
                     type="number"
                     v-model.number="editForm.current_port"
                     placeholder="3000"
                     class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                   >
                   <p class="mt-1 text-xs text-gray-500">Internal port (e.g. 3000)</p>
                </div>
             </div>

             <div class="flex items-start gap-3 rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
               <svg class="h-5 w-5 flex-shrink-0 text-blue-500" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
               </svg>
               <p>Swarm mode automatically handles build, push, and deploy. <strong>Ensure a Dockerfile exists</strong> in your repo root.</p>
             </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Post-Deploy Command</label>
          <div v-if="editForm.mode === 'docker-swarm'">
              <p class="text-sm text-gray-500 italic">Managed automatically by Swarm (Build -> Push -> Stack Deploy)</p>
          </div>
          <textarea
            v-else
            v-model="editForm.post_deploy_command"
            rows="3"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm font-mono"
            placeholder="(cd backend && npm install) && (cd frontend && npm install && npm run build)"
          ></textarea>
          <p class="mt-1.5 text-xs text-gray-500">Run after git pull. 10 min timeout.</p>
        </div>

        <!-- Notification Settings Section -->
        <div class="rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 p-4 ring-1 ring-violet-200/50">
          <div class="flex items-start gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-100">
              <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="text-sm font-semibold text-gray-900">Notification Settings</h4>
              <p class="mt-0.5 text-xs text-gray-500">Configure email alerts for deployments</p>
            </div>
          </div>

          <div class="mt-4 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1.5">Email Recipients</label>
              <div class="relative">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                </div>
                <input
                  type="text"
                  v-model="editForm.notification_emails"
                  class="block w-full rounded-lg border-0 py-2.5 pl-10 pr-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                  placeholder="admin@example.com, team@example.com"
                >
              </div>
              <p class="mt-1.5 text-xs text-gray-500">Separate multiple emails with commas. Leave empty to disable notifications.</p>
            </div>

            <div v-if="editForm.notification_emails" class="flex flex-wrap gap-1.5">
              <span v-for="email in editForm.notification_emails.split(',').filter(e => e.trim())" :key="email" class="inline-flex items-center gap-1 rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-medium text-violet-700">
                <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
                {{ email.trim() }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-2">
          <button
            type="button"
            @click="isEditModalOpen = false"
            class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isUpdating"
            class="flex-1 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
          >
            <svg v-if="isUpdating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isUpdating ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Add Deployment Modal -->
    <BaseModal :isOpen="isModalOpen" @close="isModalOpen = false" title="New Deployment" :showFooter="false">
      <form @submit.prevent="createDeployment" class="space-y-4 sm:space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
          <input
            type="text"
            v-model="form.name"
            required
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            placeholder="My Node.js App"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Project Path</label>
          <PathInput v-model="form.project_path" placeholder="/var/www/my-app" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Git Branch</label>
            <input
              type="text"
              v-model="form.branch"
              class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Run As User</label>
            <UserSelect v-model="form.run_as_user" />
          </div>
        </div>

        <div class="space-y-4 rounded-xl bg-gray-50 p-4 ring-1 ring-gray-200">
          <div class="flex items-center justify-between">
            <label class="block text-sm font-medium text-gray-700">Deployment Mode</label>
            <div class="flex rounded-lg bg-gray-200 p-1">
              <button
                type="button"
                @click="form.mode = 'supervisor'"
                :class="[
                  'rounded-md px-3 py-1 text-sm font-medium transition-all',
                  form.mode === 'supervisor' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                Supervisor
              </button>
              <button
                type="button"
                @click="form.mode = 'docker-swarm'; form.post_deploy_command = ''; form.supervisor_process = ''"
                :class="[
                  'rounded-md px-3 py-1 text-sm font-medium transition-all',
                  form.mode === 'docker-swarm' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                Docker Swarm
              </button>
            </div>
          </div>

          <div v-if="form.mode === 'supervisor'">
             <label class="block text-sm font-medium text-gray-700 mb-2">Supervisor Process</label>
              <select
                v-model="form.supervisor_process"
                class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
              >
                <option value="">None (optional)</option>
                <option v-for="proc in processes" :key="proc.name" :value="proc.name">{{ proc.name }}</option>
              </select>
              <p class="mt-1.5 text-xs text-gray-500">Process to restart after successful deployment.</p>
          </div>

          <div v-if="form.mode === 'docker-swarm'" class="space-y-4">
             <div class="grid grid-cols-2 gap-4">
                <div>
                   <label class="block text-sm font-medium text-gray-700 mb-2">Replicas</label>
                   <input
                     type="number"
                     v-model.number="form.swarm_replicas"
                     min="1"
                     class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                   >
                </div>
                <div>
                   <label class="block text-sm font-medium text-gray-700 mb-2">App Port</label>
                   <input
                     type="number"
                     v-model.number="form.current_port"
                     placeholder="3000"
                     class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                   >
                   <p class="mt-1 text-xs text-gray-500">Internal port (e.g. 3000)</p>
                </div>
             </div>
             <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Dockerfile Path</label>
                <input
                  type="text"
                  v-model="form.dockerfile_path"
                  placeholder="Dockerfile"
                  class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm font-mono"
                >
                <p class="mt-1 text-xs text-gray-500">Relative to project root (e.g. Dockerfile or docker/Dockerfile.prod)</p>
             </div>

             <div class="flex items-start gap-3 rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
               <svg class="h-5 w-5 shrink-0 text-blue-500" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
               </svg>
               <p>Swarm mode automatically handles build, push, and deploy.</p>
             </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Post-Deploy Command</label>
          <div v-if="form.mode === 'docker-swarm'">
              <p class="text-sm text-gray-500 italic">Managed automatically by Swarm (Build -> Push -> Stack Deploy)</p>
          </div>
           <input
            v-else
            type="text"
            v-model="form.post_deploy_command"
            class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm font-mono"
            placeholder="npm install && npm run build"
          >
          <p class="mt-1.5 text-xs text-gray-500">Run after git pull. Commands run as the project directory owner.</p>
        </div>

        <!-- Notification Settings Section -->
        <div class="rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 p-4 ring-1 ring-violet-200/50">
          <div class="flex items-start gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-100">
              <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="text-sm font-semibold text-gray-900">Notification Settings</h4>
              <p class="mt-0.5 text-xs text-gray-500">Get notified on deployment success or failure</p>
            </div>
          </div>

          <div class="mt-4 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1.5">Email Recipients</label>
              <div class="relative">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                </div>
                <input
                  type="text"
                  v-model="form.notification_emails"
                  class="block w-full rounded-lg border-0 py-2.5 pl-10 pr-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
                  placeholder="admin@example.com, team@example.com"
                >
              </div>
              <p class="mt-1.5 text-xs text-gray-500">Separate multiple emails with commas. Leave empty to disable notifications.</p>
            </div>

            <div v-if="form.notification_emails" class="flex flex-wrap gap-1.5">
              <span v-for="email in form.notification_emails.split(',').filter(e => e.trim())" :key="email" class="inline-flex items-center gap-1 rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-medium text-violet-700">
                <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
                {{ email.trim() }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-2">
          <button
            type="button"
            @click="isModalOpen = false"
            class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isCreating"
            class="flex-1 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
          >
            <svg v-if="isCreating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isCreating ? 'Creating...' : 'Create Deployment' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Deployment"
      message="Are you sure you want to delete this deployment? This action cannot be undone."
      confirmText="Delete"
      :isLoading="deletingId !== null"
      @confirm="deleteDeployment"
      @cancel="isDeleteModalOpen = false"
    />

    <!-- Clear Logs Confirmation Modal -->
    <ConfirmModal
      :isOpen="isClearLogsModalOpen"
      type="warning"
      title="Clear Deployment Logs"
      message="Are you sure you want to clear these deployment logs? This action cannot be undone."
      confirmText="Clear Logs"
      :isLoading="isClearingLogs"
      @confirm="clearDeploymentLogs"
      @cancel="isClearLogsModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed, nextTick } from 'vue'
import axios from 'axios'
import BaseModal from '../components/BaseModal.vue'
import PathInput from '../components/PathInput.vue'
import UserSelect from '../components/UserSelect.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'
import { useAuthStore } from '../stores/auth'

const toast = useToast()
const authStore = useAuthStore()

const deployments = ref([])
const processes = ref([])
const isModalOpen = ref(false)
const isEditModalOpen = ref(false)
const isDetailsOpen = ref(false)
const isLogsOpen = ref(false)
const selectedDeploy = ref(null)
const editingDeployId = ref(null)
const logsContainer = ref(null)
let pollInterval = null

// Loading states
const isLoading = ref(false)
const isCreating = ref(false)
const isUpdating = ref(false)
const deletingId = ref(null)
const triggeringId = ref(null)
const isClearingLogs = ref(false)

// Confirmation modals
const isDeleteModalOpen = ref(false)
const isClearLogsModalOpen = ref(false)
const deploymentToDelete = ref(null)

// WebSocket for live logs
let logsSocket = null
const liveLogs = ref('')
const liveStatus = ref('')
const wsConnected = ref(false)

const form = reactive({
    name: '',
    project_path: '',
    branch: 'main',
    supervisor_process: '',
    post_deploy_command: '',
    run_as_user: 'root',
    notification_emails: '',
    mode: 'supervisor', // 'supervisor' or 'docker-swarm'
    swarm_replicas: 2,
    current_port: 3000,
    dockerfile_path: 'Dockerfile'
})

const editForm = reactive({
    name: '',
    project_path: '',
    branch: 'main',
    supervisor_process: '',
    post_deploy_command: '',
    run_as_user: 'root',
    notification_emails: '',
    mode: 'supervisor',
    swarm_replicas: 2,
    current_port: 3000,
    dockerfile_path: 'Dockerfile'
})

const totalDeploys = computed(() => {
    return deployments.value.reduce((sum, d) => sum + (d.deploy_count || 0), 0)
})

const fetchDeployments = async (showLoading = false) => {
    if (showLoading) isLoading.value = true
    try {
        const response = await axios.get('/api/v1/deployments/')
        deployments.value = response.data

        // Update selectedDeploy if open
        if (selectedDeploy.value) {
            const updated = deployments.value.find(d => d.id === selectedDeploy.value.id)
            if (updated) {
                selectedDeploy.value = updated
            }
        }
    } catch (e) {
        console.error("Failed to fetch deployments", e)
    } finally {
        if (showLoading) isLoading.value = false
    }
}

const fetchProcesses = async () => {
    try {
        const response = await axios.get('/api/v1/supervisor/processes')
        processes.value = response.data
    } catch (e) {
        // quiet fail
    }
}

const connectLogsWebSocket = (deploymentId) => {
    if (logsSocket) {
        logsSocket.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = window.location.port ? `:${window.location.port}` : ''
    const wsUrl = `${protocol}//${host}${port}/api/v1/deployments/ws/${deploymentId}?token=${authStore.token}`

    console.log('Connecting to deployment logs WebSocket:', wsUrl)

    logsSocket = new WebSocket(wsUrl)

    logsSocket.onopen = () => {
        console.log('Deployment logs WebSocket connected')
        wsConnected.value = true
    }

    logsSocket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data)
            if (data.type === 'initial' || data.type === 'update') {
                liveLogs.value = data.logs
                liveStatus.value = data.status
                // Auto-scroll to bottom
                nextTick(() => {
                    if (logsContainer.value) {
                        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
                    }
                })
                // Refresh deployments when done
                if (data.status === 'success' || data.status === 'failed') {
                    fetchDeployments()
                }
            }
        } catch (e) {
            console.error('Error parsing WebSocket data:', e)
        }
    }

    logsSocket.onclose = () => {
        console.log('Deployment logs WebSocket disconnected')
        wsConnected.value = false
    }

    logsSocket.onerror = (error) => {
        console.error('Deployment logs WebSocket error:', error)
        wsConnected.value = false
    }
}

const disconnectLogsWebSocket = () => {
    if (logsSocket) {
        logsSocket.close()
        logsSocket = null
    }
    wsConnected.value = false
    liveLogs.value = ''
    liveStatus.value = ''
}

const openModal = () => {
    form.name = ''
    form.project_path = ''
    form.branch = 'main'
    form.supervisor_process = ''
    form.post_deploy_command = ''
    form.run_as_user = 'root'
    form.mode = 'supervisor'
    form.notification_emails = ''
    fetchProcesses()
    isModalOpen.value = true
}

const createDeployment = async () => {
    if (isCreating.value) return
    isCreating.value = true
    try {
        await axios.post('/api/v1/deployments/', {
            ...form,
            deployment_mode: form.mode, // Map mode to backend field
            supervisor_process: form.supervisor_process || null,
            post_deploy_command: form.post_deploy_command || null,
            run_as_user: form.run_as_user || 'root',
            notification_emails: form.notification_emails || null
        })
        toast.success('Deployment created successfully')
        isModalOpen.value = false
        fetchDeployments()
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to create deployment")
    } finally {
        isCreating.value = false
    }
}

const openEditModal = (deploy) => {
    editingDeployId.value = deploy.id
    editForm.name = deploy.name
    editForm.project_path = deploy.project_path
    editForm.branch = deploy.branch
    editForm.supervisor_process = deploy.supervisor_process || ''
    editForm.post_deploy_command = deploy.post_deploy_command || ''
    editForm.run_as_user = deploy.run_as_user || 'root'
    editForm.notification_emails = deploy.notification_emails || ''

    // Set deployment mode and Swarm specific fields
    editForm.mode = deploy.deployment_mode || 'supervisor'
    editForm.swarm_replicas = deploy.swarm_replicas || 2
    editForm.current_port = deploy.current_port || 3000
    editForm.dockerfile_path = deploy.dockerfile_path || 'Dockerfile'

    editingDeployId.value = deploy.id
    fetchProcesses()
    isEditModalOpen.value = true
}

const updateDeployment = async () => {
    if (isUpdating.value) return
    isUpdating.value = true
    try {
        await axios.put(`/api/v1/deployments/${editingDeployId.value}`, {
            ...editForm,
            deployment_mode: editForm.mode, // Map mode to backend field
            supervisor_process: editForm.supervisor_process || null,
            post_deploy_command: editForm.post_deploy_command || null,
            run_as_user: editForm.run_as_user || 'root',
            notification_emails: editForm.notification_emails || null
        })
        toast.success('Deployment updated successfully')
        isEditModalOpen.value = false
        fetchDeployments()
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to update deployment")
    } finally {
        isUpdating.value = false
    }
}

const confirmDelete = (id) => {
    deploymentToDelete.value = id
    isDeleteModalOpen.value = true
}

const deleteDeployment = async () => {
    if (!deploymentToDelete.value || deletingId.value) return
    deletingId.value = deploymentToDelete.value
    try {
        await axios.delete(`/api/v1/deployments/${deploymentToDelete.value}`)
        toast.success('Deployment deleted successfully')
        isDeleteModalOpen.value = false
        fetchDeployments()
    } catch (e) {
        toast.error("Failed to delete deployment")
    } finally {
        deletingId.value = null
        deploymentToDelete.value = null
    }
}

const triggerDeploy = async (deploy) => {
    if (triggeringId.value) return
    triggeringId.value = deploy.id
    try {
        await axios.post(`/api/v1/deployments/${deploy.id}/trigger`)
        // Immediately show running status
        deploy.last_status = 'running'
        // Open logs modal with live updates
        showLogs(deploy)
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to trigger deployment")
    } finally {
        triggeringId.value = null
    }
}

const startPolling = () => {
    if (pollInterval) return
    pollInterval = setInterval(async () => {
        await fetchDeployments()
        // Stop polling if no deployments are running
        const hasRunning = deployments.value.some(d => d.last_status === 'running')
        if (!hasRunning) {
            stopPolling()
        }
    }, 3000)
}

const stopPolling = () => {
    if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
    }
}

const showDetails = async (deploy) => {
    selectedDeploy.value = deploy
    isDetailsOpen.value = true

    // Fetch sensitive webhook info on demand
    try {
        const response = await axios.get(`/api/v1/deployments/${deploy.id}/webhook-info`)
        if (selectedDeploy.value && selectedDeploy.value.id === deploy.id) {
            selectedDeploy.value.secret = response.data.secret
            // We could also update webhook_url if needed
        }
    } catch (e) {
        console.error("Failed to fetch webhook info", e)
        toast.error("Failed to load webhook secret")
    }
}

const showLogs = (deploy) => {
    selectedDeploy.value = deploy
    liveLogs.value = deploy.last_logs || ''
    liveStatus.value = deploy.last_status || ''
    isLogsOpen.value = true

    // Connect WebSocket for live updates
    connectLogsWebSocket(deploy.id)
}

const closeLogs = () => {
    isLogsOpen.value = false
    disconnectLogsWebSocket()
}

const getWebhookUrl = (deploy) => {
    return `${window.location.origin}${deploy.webhook_url}`
}

const confirmClearLogs = () => {
    isClearLogsModalOpen.value = true
}

const clearDeploymentLogs = async () => {
    if (!selectedDeploy.value || isClearingLogs.value) return
    isClearingLogs.value = true
    try {
        await axios.post(`/api/v1/deployments/${selectedDeploy.value.id}/logs/clear`)
        selectedDeploy.value.last_logs = null
        liveLogs.value = ''
        // Update main list too
        const d = deployments.value.find(x => x.id === selectedDeploy.value.id)
        if (d) d.last_logs = null
        toast.success('Logs cleared successfully')
        isClearLogsModalOpen.value = false
    } catch (e) {
        toast.error(e.response?.data?.detail || e.message || "Failed to clear logs")
    } finally {
        isClearingLogs.value = false
    }
}

const copyToClipboard = (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
    } else {
        // Fallback for HTTP (non-secure context)
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-9999px'
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
    }
}

const getStatusBadgeClass = (status) => {
    const base = 'inline-flex items-center rounded-full px-2 sm:px-2.5 py-0.5 sm:py-1 text-xs font-medium'
    if (status === 'success') return `${base} bg-emerald-100 text-emerald-700`
    if (status === 'failed') return `${base} bg-red-100 text-red-700`
    if (status === 'running') return `${base} bg-blue-100 text-blue-700`
    return `${base} bg-gray-100 text-gray-600`
}

const getStatusDotClass = (status) => {
    const base = 'mr-1 sm:mr-1.5 h-1.5 w-1.5 rounded-full'
    if (status === 'success') return `${base} bg-emerald-500`
    if (status === 'failed') return `${base} bg-red-500`
    return `${base} bg-gray-400`
}

const getStatusText = (status) => {
    if (status === 'success') return 'Success'
    if (status === 'failed') return 'Failed'
    if (status === 'running') return 'Deploying...'
    return 'Pending'
}

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
}

const formatRelativeTime = (dateStr) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = Math.floor((now - date) / 1000)

    if (diff < 60) return 'just now'
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
    return date.toLocaleDateString()
}

onMounted(() => {
    fetchDeployments(true)
    // Start polling if any deployment is running
    setTimeout(() => {
        if (deployments.value.some(d => d.last_status === 'running')) {
            startPolling()
        }
    }, 500)
})

onUnmounted(() => {
    stopPolling()
    disconnectLogsWebSocket()
})
</script>
