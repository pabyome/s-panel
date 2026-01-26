<template>
  <div class="flex h-screen overflow-hidden bg-gray-100">
    <!-- Sidebar -->
    <div class="hidden md:flex md:w-64 md:flex-col">
      <Sidebar />
    </div>

    <!-- Main Content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Top header can go here if needed -->

      <main class="flex-1 overflow-y-auto p-8">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
</script>
