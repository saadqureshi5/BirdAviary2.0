<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  show: boolean
  title: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'max-w-sm'
    case 'lg': return 'max-w-4xl'
    case 'xl': return 'max-w-6xl'
    case 'md':
    default: return 'max-w-2xl'
  }
})

const handleBackdropClick = (e: MouseEvent) => {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <transition name="modal">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-950/80 backdrop-blur-sm"
      @click="handleBackdropClick"
    >
      <div 
        class="glass-card w-full max-h-[90vh] flex flex-col overflow-hidden animate-slide-up"
        :class="sizeClass"
      >
        <!-- Header -->
        <div class="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-surface-900/50">
          <h3 class="text-xl font-semibold text-white">{{ title }}</h3>
          <button @click="$emit('close')" class="text-slate-400 hover:text-white transition-colors p-1 rounded-md hover:bg-white/10">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        
        <!-- Body -->
        <div class="p-6 overflow-y-auto">
          <slot></slot>
        </div>
        
        <!-- Footer -->
        <div v-if="$slots.footer" class="px-6 py-4 border-t border-white/10 bg-surface-900/50 flex justify-end gap-3">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
