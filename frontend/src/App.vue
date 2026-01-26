<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <!-- Sidebar -->
    <div class="fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white transition-transform transform translate-x-0">
      <div class="flex items-center justify-center h-16 border-b border-gray-800">
        <span class="text-xl font-bold tracking-wide uppercase">S-Panel</span>
      </div>
      <nav class="mt-5 px-2 space-y-1">
        <router-link to="/" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path === '/' ? 'bg-gray-800 text-white' : 'text-gray-300'">
            <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
            Dashboard
        </router-link>
        <router-link to="/websites" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/websites') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
            Websites
        </router-link>
        <router-link to="/security" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/security') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            Security
        </router-link>
         <router-link to="/supervisor" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/supervisor') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
            Supervisor
        </router-link>
         <router-link to="/deployments" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/deployments') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            Deployments
        </router-link>

        <div class="mt-8 px-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Databases
        </div>
        <router-link to="/redis" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/redis') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
            Redis
        </router-link>
        <router-link to="/cron" class="group flex items-center px-2 py-2 text-base font-medium rounded-md hover:bg-gray-700 hover:text-white" :class="$route.path.startsWith('/cron') ? 'bg-gray-800 text-white' : 'text-gray-300'">
             <svg class="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            Cron Jobs
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col ml-64 overflow-hidden">
        <header class="bg-white shadow-sm z-10">
          <div class="px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <h2 class="text-lg font-medium text-gray-900 leading-tight">Control Panel</h2>
            <div class="flex items-center">
                <span class="text-sm text-gray-500 mr-4">admin</span>
                 <!-- We could add logout here -->
            </div>
          </div>
        </header>

        <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
            <div class="px-4 py-8 sm:px-6 lg:px-8">
                <router-view></router-view>
            </div>
        </main>
    </div>
  </div>
</template>

<script setup>
</script>
