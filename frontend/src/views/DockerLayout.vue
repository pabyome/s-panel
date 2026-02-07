<template>
  <div class="h-full flex flex-col">
    <!-- Tab Navigation -->
    <div class="border-b border-gray-200 bg-white">
      <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        <router-link
          v-for="tab in tabs"
          :key="tab.name"
          :to="tab.href"
          :class="[
            isCurrent(tab.href)
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium'
          ]"
        >
          {{ tab.name }}
        </router-link>
      </nav>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-y-auto p-6">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { name: 'Overview', href: '/docker/overview' },
  { name: 'Container', href: '/docker/containers' },
  { name: 'Swarm', href: '/docker/swarm' },
  // Placeholders for future features as per layout
  { name: 'Images', href: '/docker/images' },
  { name: 'Networks', href: '/docker/networks' },
  { name: 'Volumes', href: '/docker/volumes' },
]

const isCurrent = (href) => {
    return route.path.startsWith(href)
}
</script>
