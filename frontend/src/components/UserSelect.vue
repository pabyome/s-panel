<template>
  <div>
    <div class="relative mt-1">
      <div v-if="loading" class="absolute inset-y-0 right-0 flex items-center pr-3">
        <svg class="h-4 w-4 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <select
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="block w-full rounded-xl border-0 py-2.5 pl-4 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm"
        :disabled="loading || disabled"
      >
        <option value="" disabled>Select a user</option>
        <option v-for="user in users" :key="user.uid" :value="user.username">
          {{ user.username }} ({{ user.uid }})
        </option>
         <!-- Fallback if current modelValue isn't in list -->
        <option v-if="modelValue && !users.find(u => u.username === modelValue)" :value="modelValue">
            {{ modelValue }} (custom)
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])

const users = ref([])
const loading = ref(false)

const fetchUsers = async () => {
    loading.value = true
    try {
        const response = await axios.get('/api/v1/system/users')
        users.value = response.data
    } catch (e) {
        console.error("Failed to fetch users", e)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchUsers()
})
</script>
