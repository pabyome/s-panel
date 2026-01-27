<template>
  <div class="relative flex items-center justify-center">
    <svg :width="size" :height="size" class="transform -rotate-90">
      <!-- Background Ring -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        stroke="currentColor"
        stroke-width="8"
        fill="transparent"
        class="text-gray-200"
      />
      <!-- Progress Ring -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        stroke="currentColor"
        stroke-width="8"
        fill="transparent"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
        stroke-linecap="round"
        class="transition-all duration-1000 ease-out"
        :class="colorClass"
      />
    </svg>
    <!-- Value Text -->
    <div class="absolute flex flex-col items-center justify-center text-gray-700">
      <span class="text-xl font-bold">{{ value }}%</span>
      <span v-if="label" class="text-xs text-gray-500 uppercase tracking-wider">{{ label }}</span>
    </div>
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
  size: {
    type: Number,
    default: 120
  },
  label: {
    type: String,
    default: ''
  }
})

const center = computed(() => props.size / 2)
const radius = computed(() => (props.size / 2) - 10)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashoffset = computed(() => {
  const progress = props.value / 100
  return circumference.value * (1 - progress)
})

const colorClass = computed(() => {
  if (props.value > 80) return 'text-red-500'
  if (props.value > 60) return 'text-yellow-500'
  return 'text-emerald-500'
})
</script>