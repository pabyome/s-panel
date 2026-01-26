<template>
  <div class="relative" ref="containerRef">
    <div class="relative rounded-md shadow-sm">
      <input
        type="text"
        :value="modelValue"
        @input="onInput"
        @focus="onFocus"
        class="block w-full rounded-md border-0 py-1.5 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
        :placeholder="placeholder"
        autocomplete="off"
      />
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer" @click="toggleDropdown">
         <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
      </div>
    </div>

    <!-- Dropdown -->
    <div v-if="isOpen" class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
        <!-- Back / Parent -->
        <div
             v-if="parentPath"
             @click="selectPath(parentPath)"
             class="relative cursor-pointer select-none py-2 pl-3 pr-9 text-gray-900 hover:bg-gray-100 italic"
        >
            <span class="block truncate">.. (Parent Directory)</span>
        </div>

        <div v-if="loading" class="py-2 pl-3 text-gray-500">Loading...</div>

        <div v-else-if="files.length === 0" class="py-2 pl-3 text-gray-500">Empty directory</div>

        <div
            v-for="file in files"
            :key="file.path"
            @click="selectPath(file.path, file.is_dir)"
            class="relative cursor-pointer select-none py-2 pl-3 pr-9 text-gray-900 hover:bg-indigo-50"
        >
            <span class="flex items-center">
                 <svg v-if="file.is_dir" class="h-4 w-4 mr-2 text-yellow-500" fill="currentColor" viewBox="0 0 20 20"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>
                 <svg v-else class="h-4 w-4 mr-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" /></svg>
                 <span class="block truncate">{{ file.name }}</span>
            </span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const props = defineProps({
    modelValue: String,
    placeholder: String
})

const emit = defineEmits(['update:modelValue'])

const containerRef = ref(null)
const isOpen = ref(false)
const loading = ref(false)
const files = ref([])
const currentPath = ref('/')
const parentPath = ref('')

const onInput = (e) => {
    emit('update:modelValue', e.target.value)
}

const onFocus = () => {
    // If empty, start at root or suggested default
    if (!props.modelValue) {
        fetchPath('/')
    } else {
        // Try to fetch current value directory
        fetchPath(props.modelValue)
    }
    isOpen.value = true
}

const toggleDropdown = () => {
    if (isOpen.value) {
        isOpen.value = false
    } else {
        onFocus()
    }
}

const fetchPath = async (path) => {
    // If path is a file (likely), try dirname?
    // For now, let's just create a robust fetcher.
    loading.value = true
    try {
        const response = await axios.get('/api/v1/system/path/list', {
            params: { path: path }
        })
        files.value = response.data.items
        currentPath.value = response.data.current_path
        parentPath.value = response.data.parent_path
    } catch (e) {
        // If 400/404, maybe it's not a dir, try parent?
        // But for "Input", users might type incomplete paths.
        // We could implement "Listing matching suggestions",
        // but for this MVP, "Browsing" is safer.
        console.warn("Failed to list path", e)
    } finally {
        loading.value = false
    }
}

const selectPath = (path, isDir) => {
    emit('update:modelValue', path)
    if (isDir) {
        fetchPath(path)
    } else {
        isOpen.value = false
    }
}

// Close when clicking outside
const handleClickOutside = (event) => {
    if (containerRef.value && !containerRef.value.contains(event.target)) {
        isOpen.value = false
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>
