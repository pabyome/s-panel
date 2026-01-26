<template>
  <div class="relative flex flex-col items-center">
    <svg class="h-32 w-32 -rotate-90 transform" viewBox="0 0 100 100">
      <!-- Background Circle -->
      <circle
        class="text-gray-200"
        stroke-width="10"
        stroke="currentColor"
        fill="transparent"
        r="40"
        cx="50"
        cy="50"
      />
      <!-- Progress Circle -->
      <circle
        class="transition-all duration-500 ease-out"
        :class="colorClass"
        stroke-width="10"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
        stroke-linecap="round"
        stroke="currentColor"
        fill="transparent"
        r="40"
        cx="50"
        cy="50"
      />
    </svg>
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
      <span class="text-xl font-bold text-gray-700">{{ value }}%</span>
    </div>
    <span class="mt-2 text-sm font-medium text-gray-500">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    required: true,
    default: 0
  },
  label: {
    type: String,
    required: true
  }
})

const circumference = 2 * Math.PI * 40
const strokeDashoffset = computed(() => {
  const percent = Math.min(Math.max(props.value, 0), 100)
  return circumference - (percent / 100) * circumference
})

const colorClass = computed(() => {
  if (props.value < 60) return 'text-green-500'
  if (props.value < 80) return 'text-yellow-500'
  return 'text-red-500'
})
</script>
