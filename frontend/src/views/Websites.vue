<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">Websites</h1>
        <p class="mt-1 text-sm text-slate-500">Manage Nginx hosts and Node.js apps.</p>
      </div>
      <button 
        @click="resetForm" 
        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-colors"
      >
        <span class="flex items-center gap-2">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
            New Website
        </span>
      </button>
    </div>

    <!-- Master-Detail Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 min-h-0 flex-1">
      
      <!-- Left Column: List (1/3) -->
      <div class="flex flex-col gap-4 min-h-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
         <!-- Search/Filter Header -->
         <div class="p-4 border-b border-slate-100 bg-slate-50/50">
            <div class="relative">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <svg class="h-4 w-4 text-slate-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
                    </svg>
                </div>
                <input 
                    type="text" 
                    placeholder="Search websites..." 
                    class="block w-full rounded-md border-0 py-1.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                >
            </div>
         </div>

         <!-- Scrollable List -->
         <div class="flex-1 overflow-y-auto p-2 space-y-2">
            <div 
                v-for="site in websites" 
                :key="site.id" 
                @click="selectWebsite(site)"
                :class="[
                    selectedWebsite?.id === site.id ? 'bg-indigo-50 ring-1 ring-indigo-200' : 'hover:bg-slate-50 border-transparent',
                    'group relative flex items-center gap-x-4 rounded-lg p-3 cursor-pointer transition-all border border-slate-100'
                ]"
            >
                <div 
                    :class="[
                        selectedWebsite?.id === site.id ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-white group-hover:ring-1 group-hover:ring-slate-200',
                        'flex h-10 w-10 flex-none items-center justify-center rounded-lg text-[10px] font-bold uppercase transition-colors'
                    ]"
                >
                    {{ site.name.substring(0,2) }}
                </div>
                <div class="min-w-0 flex-auto">
                    <p class="text-sm font-semibold leading-6 text-slate-900">
                        {{ site.name }}
                    </p>
                    <p class="flex items-center text-xs leading-5 text-slate-500 truncate">
                        <span class="truncate">{{ site.domain }}</span>
                        <span class="mx-1.5">&middot;</span>
                        <span class="text-xs text-slate-400">Port {{ site.port }}</span>
                    </p>
                </div>
                <div class="flex-none flex items-center gap-2">
                     <span class="inline-flex items-center rounded-full bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">Active</span>
                </div>
            </div>

            <!-- Empty State for List -->
            <div v-if="websites.length === 0" class="text-center py-10 px-4">
                 <p class="text-sm text-slate-500">No websites found.</p>
                 <button @click="resetForm" class="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-500">Create your first one</button>
            </div>
         </div>
      </div>

      <!-- Right Column: Detail/Form (2/3) -->
      <div class="lg:col-span-2 flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <!-- Form Header -->
        <div class="border-b border-slate-100 px-6 py-4 flex justify-between items-center bg-slate-50/50">
            <h3 class="text-base font-semibold leading-7 text-slate-900">
                {{ selectedWebsite?.id ? 'Website Details' : 'New Website Configuration' }}
            </h3>
            <div v-if="selectedWebsite?.id" class="flex items-center gap-3">
                 <a :href="'http://' + selectedWebsite.domain" target="_blank" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    Visit Site &rarr;
                 </a>
                 <button @click="deleteWebsite(selectedWebsite.id)" class="text-sm font-medium text-red-600 hover:text-red-500">
                    Delete
                 </button>
            </div>
        </div>

        <!-- Form Content -->
        <div class="p-8">
             <form @submit.prevent="handleSubmit" class="space-y-6 max-w-2xl">
                <!-- Top Row: Name & Domain -->
                <div class="grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-2">
                    <div class="col-span-1">
                        <label for="name" class="block text-sm font-medium leading-6 text-slate-900">Application Name</label>
                        <div class="mt-2">
                            <input 
                                type="text" 
                                v-model="form.name" 
                                id="name" 
                                :disabled="!!selectedWebsite?.id"
                                class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 disabled:bg-slate-50 disabled:text-slate-500 disabled:ring-slate-200"
                                placeholder="e.g. Corporate Blog"
                            >
                        </div>
                    </div>

                     <div class="col-span-1">
                        <label for="domain" class="block text-sm font-medium leading-6 text-slate-900">Domain Name</label>
                        <div class="mt-2">
                            <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-slate-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                                <span class="flex select-none items-center pl-3 text-slate-500 sm:text-sm">http://</span>
                                <input 
                                    type="text" 
                                    v-model="form.domain" 
                                    id="domain" 
                                    :disabled="!!selectedWebsite?.id"
                                    class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-slate-900 placeholder:text-slate-400 focus:ring-0 sm:text-sm sm:leading-6 disabled:text-slate-500" 
                                    placeholder="www.example.com"
                                >
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Middle Row: Path & Port -->
                <div class="grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-6">
                     <div class="sm:col-span-4">
                        <label for="path" class="block text-sm font-medium leading-6 text-slate-900">Project Path</label>
                        <div class="mt-2">
                             <PathInput v-model="form.project_path" :disabled="!!selectedWebsite?.id" placeholder="/var/www/html/my-project" />
                             <p class="mt-1 text-xs text-slate-500">Absolute path to your project root.</p>
                        </div>
                    </div>

                    <div class="sm:col-span-2">
                        <label for="port" class="block text-sm font-medium leading-6 text-slate-900">Internal Port</label>
                        <div class="mt-2">
                            <input 
                                type="number" 
                                v-model="form.port" 
                                id="port" 
                                :disabled="!!selectedWebsite?.id"
                                class="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 disabled:bg-slate-50 disabled:text-slate-500 disabled:ring-slate-200"
                                placeholder="3000"
                            >
                        </div>
                    </div>
                </div>

                <!-- Footer / Actions -->
                 <div class="pt-6 border-t border-slate-100 flex items-center justify-end gap-x-4">
                    <button 
                        v-if="!selectedWebsite?.id"
                        type="button" 
                        class="text-sm font-semibold leading-6 text-slate-900"
                        @click="resetForm"
                    >
                        Reset
                    </button>
                    <button 
                        v-if="!selectedWebsite?.id"
                        type="submit" 
                        class="rounded-md bg-indigo-600 px-8 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all"
                    >
                        Create Application
                    </button>
                    <div v-else class="text-sm text-slate-500 italic">
                        Editing active deployments is currently disabled to prevent downtime.
                    </div>
                </div>
             </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import PathInput from '../components/PathInput.vue'

const websites = ref([])
const selectedWebsite = ref(null)
const form = reactive({
    name: '',
    domain: '',
    port: 3000,
    project_path: ''
})

const fetchWebsites = async () => {
    try {
        const response = await axios.get('/api/v1/websites/')
        websites.value = response.data
    } catch (e) {
        console.error("Failed to fetch websites", e)
    }
}

const selectWebsite = (site) => {
    selectedWebsite.value = site
    // Populate form
    form.name = site.name
    form.domain = site.domain
    form.port = site.port
    form.project_path = site.project_path || '' // Handle missing path
}

const resetForm = () => {
    selectedWebsite.value = null
    form.name = ''
    form.domain = ''
    form.port = 3000
    form.project_path = ''
}

const handleSubmit = async () => {
    try {
        await axios.post('/api/v1/websites/', form)
        resetForm()
        fetchWebsites()
    } catch (e) {
        console.error("Failed to create website", e)
        alert("Failed to create website")
    }
}

const deleteWebsite = async (id) => {
    if(!confirm("Are you sure? This will remove Nginx config.")) return;
    try {
        await axios.delete(`/api/v1/websites/${id}`)
        resetForm()
        fetchWebsites()
    } catch (e) {
        console.error("Failed to delete website", e)
    }
}

onMounted(() => {
    fetchWebsites()
})
</script>
