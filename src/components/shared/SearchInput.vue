<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const innerValue = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  innerValue.value = newVal
})

const handleInput = () => {
  emit('update:modelValue', innerValue.value)
}

const clearInput = () => {
  innerValue.value = ''
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="relative group">
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400 group-focus-within:text-primary-400 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-400 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
    </div>
    <input
      type="text"
      v-model="innerValue"
      @input="handleInput"
      :placeholder="placeholder || 'Search...'"
      class="w-full bg-surface-800/80 backdrop-blur-sm border border-white/5 hover:border-white/10 rounded-lg pl-11 pr-10 py-2 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all duration-200"
    />
    <button
      v-if="innerValue"
      @click="clearInput"
      class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-white transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
  </div>
</template>
