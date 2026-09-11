<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { UpdateInfo } from '@/types'
import * as updateService from '@/services/updateService'

const updateInfo = ref<UpdateInfo | null>(null)
const dismissed = ref(false)
const isForceUpdate = ref(false)

onMounted(async () => {
  const info = await updateService.checkForUpdate()
  if (!info) return

  // Force updates can't be dismissed
  if (info.force_update) {
    isForceUpdate.value = true
    updateInfo.value = info
    return
  }

  // Skip if user already dismissed this version
  if (updateService.isVersionDismissed(info.version)) return

  updateInfo.value = info
})

function handleDismiss() {
  if (updateInfo.value && !isForceUpdate.value) {
    updateService.dismissVersion(updateInfo.value.version)
  }
  dismissed.value = true
}

function handleDownload() {
  if (updateInfo.value?.download_url) {
    window.open(updateInfo.value.download_url, '_blank')
  }
}
</script>

<template>
  <Transition name="slide-down">
    <div
      v-if="updateInfo && !dismissed"
      :class="[
        'relative flex items-center gap-3 px-5 py-3 text-sm border-b',
        isForceUpdate
          ? 'bg-red-500/10 border-red-500/20 text-red-300'
          : 'bg-amber-500/10 border-amber-500/20 text-amber-300'
      ]"
    >
      <!-- Icon -->
      <div class="flex-shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
      </div>

      <!-- Message -->
      <div class="flex-1 min-w-0">
        <span class="font-medium">
          {{ isForceUpdate ? 'Critical update required' : 'Update available' }}
        </span>
        <span class="text-white/60 ml-1">
          v{{ updateService.getCurrentVersion() }} → v{{ updateInfo.version }}
        </span>
        <span v-if="updateInfo.changelog" class="text-white/40 ml-2 hidden md:inline">
          — {{ updateInfo.changelog.split('\n')[0] }}
        </span>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <button
          @click="handleDownload"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]',
            isForceUpdate
              ? 'bg-red-500 hover:bg-red-400 text-white'
              : 'bg-amber-500 hover:bg-amber-400 text-surface-950'
          ]"
        >
          Download
        </button>
        <button
          v-if="!isForceUpdate"
          @click="handleDismiss"
          class="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/40 hover:text-white/70"
          title="Dismiss"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-100%);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}
</style>
