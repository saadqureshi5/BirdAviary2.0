<script setup lang="ts">
import { ref } from 'vue'

import { useCamera } from '@/composables/useCamera'
import { Capacitor } from '@capacitor/core'

const props = defineProps<{
  modelValue?: string | null
  label: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string | null): void
  (e: 'file', file: File): void
}>()

const isDragging = ref(false)
const previewUrl = ref<string | null>(props.modelValue || null)
const { takePhoto } = useCamera()
const isNative = Capacitor.isNativePlatform()

const handleDrop = (e: DragEvent) => {
  if (isNative) return
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleNativeClick = async () => {
  if (!isNative || previewUrl.value) return
  const photoUrl = await takePhoto()
  if (photoUrl) {
    previewUrl.value = photoUrl
    emit('update:modelValue', photoUrl)
    // We would need to fetch the blob to emit a File object if needed by backend,
    // but returning the local URI often works for native display
  }
}

const processFile = (file: File) => {
  // Create local preview URL
  previewUrl.value = URL.createObjectURL(file)
  emit('file', file)
  // In a real implementation, you might upload here and then emit the resulting URL
  // emit('update:modelValue', uploadedUrl)
}

const removePhoto = () => {
  previewUrl.value = null
  emit('update:modelValue', null)
}
</script>

<template>
  <div class="w-full">
    <label class="label">{{ label }}</label>
    
    <div 
      class="relative mt-2 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-6 transition-colors duration-200 overflow-hidden cursor-pointer"
      :class="[
        isDragging ? 'border-primary-500 bg-primary-500/10' : 'border-white/20 bg-surface-800/50 hover:border-white/40 hover:bg-surface-800',
        previewUrl ? 'p-1' : 'min-h-[160px]'
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="handleNativeClick"
    >
      <input 
        v-if="!isNative"
        type="file" 
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
        accept="image/*"
        @change="handleFileSelect"
        :disabled="!!previewUrl"
      />
      
      <template v-if="previewUrl">
        <div class="relative w-full h-48 bg-black rounded-lg overflow-hidden z-20">
          <img :src="previewUrl" class="w-full h-full object-cover" alt="Preview" />
          <div class="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 flex items-center justify-center transition-opacity">
            <button @click.prevent="removePhoto" class="btn-danger p-2 bg-red-500/80 hover:bg-red-500 text-white rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
      </template>
      
      <template v-else>
        <div class="w-12 h-12 mb-3 rounded-full bg-surface-700 flex items-center justify-center text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
        </div>
        <p class="text-sm font-medium text-white mb-1">Click to upload or drag and drop</p>
        <p class="text-xs text-slate-400">SVG, PNG, JPG or GIF (max. 5MB)</p>
      </template>
    </div>
  </div>
</template>
