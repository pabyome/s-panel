<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm" @click="handleCancel"></div>

          <!-- Modal -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div v-if="isOpen" class="relative w-full max-w-md transform rounded-2xl bg-white p-6 shadow-2xl ring-1 ring-gray-900/5">
              <!-- Icon -->
              <div class="flex items-center gap-4">
                <div :class="['flex h-12 w-12 items-center justify-center rounded-xl', iconBgClass]">
                  <svg v-if="type === 'danger'" class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  <svg v-else-if="type === 'warning'" class="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                  </svg>
                  <svg v-else class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
                  <p class="mt-1 text-sm text-gray-500">{{ message }}</p>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-6 flex gap-3">
                <button
                  @click="handleCancel"
                  class="flex-1 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-200"
                >
                  {{ cancelText }}
                </button>
                <button
                  @click="handleConfirm"
                  :disabled="isLoading"
                  :class="[
                    'flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold text-white shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2',
                    confirmButtonClass
                  ]"
                >
                  <svg v-if="isLoading" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ isLoading ? loadingText : confirmText }}
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  type: { type: String, default: 'danger' }, // danger, warning, info
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure you want to proceed?' },
  confirmText: { type: String, default: 'Confirm' },
  cancelText: { type: String, default: 'Cancel' },
  loadingText: { type: String, default: 'Processing...' },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])

const iconBgClass = computed(() => {
  switch (props.type) {
    case 'danger': return 'bg-red-100'
    case 'warning': return 'bg-amber-100'
    default: return 'bg-blue-100'
  }
})

const confirmButtonClass = computed(() => {
  switch (props.type) {
    case 'danger': return 'bg-red-600 hover:bg-red-500 shadow-red-500/25'
    case 'warning': return 'bg-amber-600 hover:bg-amber-500 shadow-amber-500/25'
    default: return 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/25'
  }
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  if (!props.isLoading) {
    emit('cancel')
  }
}
</script>
