<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <!-- Mobile sidebar backdrop -->
    <Transition
      enter-active-class="transition-opacity ease-linear duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity ease-linear duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-gray-900/80 md:hidden"
        @click="sidebarOpen = false"
      ></div>
    </Transition>

    <!-- Mobile sidebar -->
    <Transition
      enter-active-class="transition ease-in-out duration-300 transform"
      enter-from-class="-translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition ease-in-out duration-300 transform"
      leave-from-class="translate-x-0"
      leave-to-class="-translate-x-full"
    >
      <div v-if="sidebarOpen" class="fixed inset-y-0 left-0 z-50 w-64 md:hidden">
        <div class="absolute right-0 top-0 -mr-12 pt-2">
          <button
            type="button"
            class="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
            @click="sidebarOpen = false"
          >
            <span class="sr-only">Close sidebar</span>
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <Sidebar @navigate="sidebarOpen = false" />
      </div>
    </Transition>

    <!-- Desktop Sidebar -->
    <div class="hidden md:flex md:w-64 md:flex-col">
      <Sidebar />
    </div>

    <!-- Main Content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Mobile header with hamburger -->
      <div class="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm md:hidden">
        <button
          type="button"
          class="-m-2.5 p-2.5 text-gray-700"
          @click="sidebarOpen = true"
        >
          <span class="sr-only">Open sidebar</span>
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
        <div class="flex items-center gap-x-2">
          <div class="h-7 w-7 rounded-lg bg-indigo-600 shadow-lg shadow-indigo-500/30 flex items-center justify-center">
            <span class="text-white font-bold text-sm">S</span>
          </div>
          <span class="text-gray-900 font-bold text-lg tracking-wide">Panel</span>
        </div>
      </div>

      <main class="flex-1 overflow-y-auto p-4 md:p-8">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'

const sidebarOpen = ref(false)
</script>
