<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      <TransitionGroup
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="translate-x-full opacity-0"
        enter-to-class="translate-x-0 opacity-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="translate-x-0 opacity-100"
        leave-to-class="translate-x-full opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'pointer-events-auto flex items-start gap-3 rounded-xl p-4 shadow-lg ring-1 backdrop-blur-sm',
            getToastClasses(toast.type)
          ]"
        >
          <!-- Icon -->
          <div :class="['flex h-8 w-8 items-center justify-center rounded-lg', getIconBgClass(toast.type)]">
            <svg v-if="toast.type === 'success'" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="toast.type === 'error'" class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <svg v-else-if="toast.type === 'warning'" class="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <svg v-else class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p :class="['text-sm font-medium', getTextClass(toast.type)]">
              {{ toast.message }}
            </p>
          </div>

          <!-- Close Button -->
          <button
            @click="removeToast(toast.id)"
            :class="['rounded-lg p-1 transition-colors', getCloseButtonClass(toast.type)]"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()

const getToastClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-emerald-50/95 ring-emerald-200/50 text-emerald-900'
    case 'error':
      return 'bg-red-50/95 ring-red-200/50 text-red-900'
    case 'warning':
      return 'bg-amber-50/95 ring-amber-200/50 text-amber-900'
    default:
      return 'bg-blue-50/95 ring-blue-200/50 text-blue-900'
  }
}

const getIconBgClass = (type) => {
  switch (type) {
    case 'success': return 'bg-emerald-100'
    case 'error': return 'bg-red-100'
    case 'warning': return 'bg-amber-100'
    default: return 'bg-blue-100'
  }
}

const getTextClass = (type) => {
  switch (type) {
    case 'success': return 'text-emerald-800'
    case 'error': return 'text-red-800'
    case 'warning': return 'text-amber-800'
    default: return 'text-blue-800'
  }
}

const getCloseButtonClass = (type) => {
  switch (type) {
    case 'success': return 'text-emerald-500 hover:bg-emerald-100'
    case 'error': return 'text-red-500 hover:bg-red-100'
    case 'warning': return 'text-amber-500 hover:bg-amber-100'
    default: return 'text-blue-500 hover:bg-blue-100'
  }
}
</script>
