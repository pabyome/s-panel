<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Websites</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your Nginx-hosted websites and Node.js applications</p>
      </div>
      <button
        @click="resetForm"
        class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        New Website
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-indigo-100 p-2.5">
            <svg class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total Sites</p>
            <p class="text-xl font-bold text-gray-900">{{ websites.length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-violet-100 p-2.5">
            <svg class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Static</p>
            <p class="text-xl font-bold text-gray-900">{{ websites.filter(w => w.is_static).length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-emerald-100 p-2.5">
            <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500">Dynamic</p>
            <p class="text-xl font-bold text-gray-900">{{ websites.filter(w => !w.is_static).length }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5 cursor-help group/nginx">
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-gray-100 p-2.5">
            <svg class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start">
              <div>
                <p class="text-sm text-gray-500">Nginx</p>
                <p :class="['text-xl font-bold', nginxInfo.running ? 'text-emerald-600' : 'text-red-600']">
                  {{ nginxInfo.status_text || (nginxInfo.version ? 'Running' : 'Stopped') }}
                </p>
              </div>
              <div class="text-right opacity-0 transition-opacity group-hover/nginx:opacity-100">
                <p v-if="nginxInfo.version" class="text-xs text-gray-400 font-mono">{{ nginxInfo.version }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Left Column: Sites List -->
      <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden flex flex-col max-h-[600px]">
        <div class="border-b border-gray-100 bg-gray-50/50 px-5 py-4">
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search websites..."
              class="block w-full rounded-xl border-0 py-2 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm"
            >
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-3 space-y-2">
          <div
            v-for="site in websites"
            :key="site.id"
            @click="selectWebsite(site)"
            :class="[
              selectedWebsite?.id === site.id
                ? 'bg-indigo-50 ring-2 ring-indigo-500'
                : 'bg-gray-50 hover:bg-gray-100 ring-1 ring-gray-200',
              'group relative flex items-center gap-4 rounded-xl p-4 cursor-pointer transition-all'
            ]"
          >
            <div
              :class="[
                selectedWebsite?.id === site.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'bg-white text-gray-600 ring-1 ring-gray-200',
                'flex h-11 w-11 flex-none items-center justify-center rounded-xl text-xs font-bold uppercase transition-all'
              ]"
            >
              {{ site.name.substring(0,2) }}
            </div>
            <div class="min-w-0 flex-auto">
              <p class="text-sm font-semibold text-gray-900">{{ site.name }}</p>
              <p class="mt-0.5 flex items-center gap-2 text-xs text-gray-500">
                <span class="truncate">{{ site.domain }}</span>
                <span v-if="site.is_static" class="inline-flex items-center rounded bg-violet-100 px-1.5 py-0.5 text-[10px] font-medium text-violet-600">Static</span>
                <span v-else class="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600">:{{ site.port }}</span>
              </p>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="relative flex h-2 w-2">
                <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
              </span>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="websites.length === 0" class="flex flex-col items-center justify-center py-12 px-4">
            <div class="rounded-xl bg-gray-100 p-3">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
              </svg>
            </div>
            <p class="mt-3 text-sm font-medium text-gray-900">No websites yet</p>
            <p class="mt-1 text-sm text-gray-500">Create your first website</p>
            <button @click="resetForm" class="mt-4 text-sm font-medium text-indigo-600 hover:text-indigo-500">
              Get started →
            </button>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2 space-y-6">
        <!-- Details Card -->
        <div class="rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 overflow-hidden">
        <div class="border-b border-gray-100 bg-gray-50/50 px-6 py-4 flex justify-between items-center">
          <div>
            <h3 class="text-base font-semibold text-gray-900">
              {{ selectedWebsite?.id ? 'Website Details' : 'New Website' }}
            </h3>
            <p class="mt-0.5 text-sm text-gray-500">
              {{ selectedWebsite?.id ? 'View configuration details' : 'Configure a new Nginx site' }}
            </p>
          </div>
          <div v-if="selectedWebsite?.id" class="flex items-center gap-3">
            <a :href="'http://' + selectedWebsite.domain" target="_blank" class="inline-flex items-center gap-1.5 rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-200">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
              </svg>
              Visit
            </a>
            <button v-if="!isEditing" @click="startEditing" class="inline-flex items-center gap-1.5 rounded-lg bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 transition-colors hover:bg-amber-100">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
              </svg>
              Edit
            </button>
            <button @click="isManageOpen = true" class="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 transition-colors hover:bg-indigo-100">
               <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
               </svg>
               Manage
            </button>
            <button @click="confirmDelete(selectedWebsite.id)" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
              </svg>
              Delete
            </button>
          </div>
        </div>

        <div class="p-6">
          <form @submit.prevent="selectedWebsite?.id ? updateWebsite() : handleSubmit()" class="space-y-6">
            <!-- Name & Domain -->
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label for="name" class="block text-sm font-medium text-gray-700">Application Name</label>
                <div class="mt-2">
                  <input
                    type="text"
                    v-model="form.name"
                    id="name"
                    :disabled="selectedWebsite?.id && !isEditing"
                    class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="My App"
                  >
                </div>
              </div>

              <div>
                <label for="domain" class="block text-sm font-medium text-gray-700">Domain Name</label>
                <div class="mt-2">
                  <div class="flex rounded-xl shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500" :class="selectedWebsite?.id ? 'bg-gray-50' : ''">
                    <span class="flex select-none items-center pl-4 text-gray-500 sm:text-sm">http://</span>
                    <input
                      type="text"
                      v-model="form.domain"
                      id="domain"
                      :disabled="!!selectedWebsite?.id"
                      class="block flex-1 border-0 bg-transparent py-2.5 pl-1 pr-4 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm disabled:text-gray-500"
                      placeholder="example.com"
                    >
                  </div>
                  <p v-if="selectedWebsite?.id" class="mt-1 text-xs text-gray-400">Domain cannot be changed after creation</p>
                </div>
              </div>
            </div>

            <!-- Path & Port -->
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-6">
              <div class="sm:col-span-4">
                <label for="path" class="block text-sm font-medium text-gray-700">Project Path</label>
                <div class="mt-2">
                  <PathInput v-model="form.project_path" :disabled="selectedWebsite?.id && !isEditing" placeholder="/var/www/my-project" />
                </div>
                <p class="mt-1.5 text-xs text-gray-500">{{ form.is_static ? 'Directory containing your index.html and static files' : 'Absolute path to your project root directory' }}</p>
              </div>

              <div class="sm:col-span-2">
                <label for="port" class="block text-sm font-medium text-gray-700">{{ form.is_static ? 'Listen Port' : 'Internal Port' }}</label>
                <div class="mt-2">
                  <input
                    type="number"
                    v-model="form.port"
                    id="port"
                    :disabled="selectedWebsite?.id && !isEditing"
                    class="block w-full rounded-xl border-0 py-2.5 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="3000"
                  >
                </div>
                <p class="mt-1.5 text-xs text-gray-500">{{ form.is_static ? 'Port Nginx will listen on (e.g., 3089)' : 'Port your app runs on locally' }}</p>
              </div>
            </div>

            <!-- Site Type Toggle -->
            <div class="rounded-xl bg-gray-50 p-4 ring-1 ring-inset ring-gray-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div :class="[form.is_static ? 'bg-violet-100' : 'bg-indigo-100', 'rounded-lg p-2 transition-colors']">
                    <svg v-if="form.is_static" class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                    <svg v-else class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ form.is_static ? 'Static Site' : 'Dynamic Application' }}</p>
                    <p class="text-xs text-gray-500">{{ form.is_static ? 'Serve HTML/CSS/JS files directly via Nginx' : 'Proxy requests to a running application server' }}</p>
                  </div>
                </div>
                <button
                  type="button"
                  :disabled="selectedWebsite?.id && !isEditing"
                  @click="form.is_static = !form.is_static"
                  :class="[
                    form.is_static ? 'bg-violet-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-violet-600 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
                  ]"
                >
                  <span :class="[form.is_static ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']"></span>
                </button>
              </div>
            </div>

            <!-- Actions -->
            <div class="pt-5 border-t border-gray-100 flex items-center justify-end gap-3">
              <!-- Create mode -->
              <template v-if="!selectedWebsite?.id">
                <button
                  type="button"
                  class="rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100"
                  @click="resetForm"
                >
                  Reset
                </button>
                <button
                  type="submit"
                  :disabled="isCreating"
                  class="rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
                >
                  <svg v-if="isCreating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ isCreating ? 'Creating...' : 'Create Website' }}
                </button>
              </template>
              <!-- Edit mode -->
              <template v-else-if="isEditing">
                <button
                  type="button"
                  class="rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100"
                  @click="cancelEditing"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isUpdating"
                  class="rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
                >
                  <svg v-if="isUpdating" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ isUpdating ? 'Saving...' : 'Save Changes' }}
                </button>
              </template>
              <!-- View mode -->
              <div v-else class="flex items-center gap-2 text-sm text-gray-500">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                </svg>
                Click Edit to modify website settings
              </div>
            </div>
          </form>

            <!-- SSL Manager -->
            <SSLManager
              v-if="selectedWebsite?.id"
              :websiteId="selectedWebsite.id"
              :sslEnabled="selectedWebsite.ssl_enabled"
              @update="fetchWebsites"
            />
        </div>
        </div>
      </div>
    </div>

    <ManageWebsiteModal
      :isOpen="isManageOpen"
      :website="selectedWebsite"
      @close="isManageOpen = false"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :isOpen="isDeleteModalOpen"
      type="danger"
      title="Delete Website"
      message="Are you sure? This will remove the Nginx configuration. This action cannot be undone."
      confirmText="Delete"
      :isLoading="deletingId !== null"
      @confirm="deleteWebsite"
      @cancel="isDeleteModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import PathInput from '../components/PathInput.vue'
import SSLManager from '../components/SSLManager.vue'
import ManageWebsiteModal from '../components/ManageWebsiteModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()

const websites = ref([])
const nginxInfo = ref({ version: '', path: '', running: false, status_text: 'Checking...' })
const selectedWebsite = ref(null)
const isManageOpen = ref(false)
const isLoading = ref(false)
const isCreating = ref(false)
const isEditing = ref(false)
const isUpdating = ref(false)
const deletingId = ref(null)
const isDeleteModalOpen = ref(false)
const websiteToDelete = ref(null)
const form = reactive({
    name: '',
    domain: '',
    port: 3000,
    project_path: '',
    is_static: false
})

const fetchNginxInfo = async () => {
    try {
        const response = await axios.get('/api/v1/websites/nginx')
        nginxInfo.value = response.data
    } catch (e) {
        console.error("Failed to fetch nginx info", e)
    }
}

const fetchWebsites = async (showLoading = false) => {
    if (showLoading) isLoading.value = true
    try {
        const response = await axios.get('/api/v1/websites/')
        websites.value = response.data
    } catch (e) {
        console.error("Failed to fetch websites", e)
    } finally {
        if (showLoading) isLoading.value = false
    }
}

const selectWebsite = (site) => {
    selectedWebsite.value = site
    isEditing.value = false
    // Populate form
    form.name = site.name
    form.domain = site.domain
    form.port = site.port
    form.project_path = site.project_path || '' // Handle missing path
    form.is_static = site.is_static || false
}

const startEditing = () => {
    isEditing.value = true
}

const cancelEditing = () => {
    isEditing.value = false
    // Reset form to current selected website values
    if (selectedWebsite.value) {
        form.name = selectedWebsite.value.name
        form.domain = selectedWebsite.value.domain
        form.port = selectedWebsite.value.port
        form.project_path = selectedWebsite.value.project_path || ''
        form.is_static = selectedWebsite.value.is_static || false
    }
}

const resetForm = () => {
    selectedWebsite.value = null
    isEditing.value = false
    form.name = ''
    form.domain = ''
    form.port = 3000
    form.project_path = ''
    form.is_static = false
}

const handleSubmit = async () => {
    if (isCreating.value) return
    isCreating.value = true
    try {
        await axios.post('/api/v1/websites/', form)
        toast.success('Website created successfully')
        resetForm()
        fetchWebsites()
    } catch (e) {
        console.error("Failed to create website", e)
        toast.error(e.response?.data?.detail || "Failed to create website")
    } finally {
        isCreating.value = false
    }
}

const updateWebsite = async () => {
    if (isUpdating.value || !selectedWebsite.value) return
    isUpdating.value = true
    try {
        const updateData = {
            name: form.name,
            port: form.port,
            project_path: form.project_path,
            is_static: form.is_static
        }
        const { data } = await axios.put(`/api/v1/websites/${selectedWebsite.value.id}`, updateData)
        toast.success('Website updated successfully')
        // Update selected website with new data
        selectedWebsite.value = data
        isEditing.value = false
        fetchWebsites()
    } catch (e) {
        console.error("Failed to update website", e)
        toast.error(e.response?.data?.detail || "Failed to update website")
    } finally {
        isUpdating.value = false
    }
}

const confirmDelete = (id) => {
    websiteToDelete.value = id
    isDeleteModalOpen.value = true
}

const deleteWebsite = async () => {
    if (!websiteToDelete.value || deletingId.value) return
    deletingId.value = websiteToDelete.value
    try {
        await axios.delete(`/api/v1/websites/${websiteToDelete.value}`)
        toast.success('Website deleted successfully')
        isDeleteModalOpen.value = false
        resetForm()
        fetchWebsites()
    } catch (e) {
        console.error("Failed to delete website", e)
        toast.error("Failed to delete website")
    } finally {
        deletingId.value = null
        websiteToDelete.value = null
    }
}

onMounted(() => {
    fetchWebsites(true)
    fetchNginxInfo()
})
</script>
