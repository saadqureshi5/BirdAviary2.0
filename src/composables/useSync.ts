import { onMounted, onUnmounted, watch } from 'vue'
import { useSyncStore } from '@/stores/syncStore'

export function useSync() {
  const syncStore = useSyncStore()
  let syncInterval: ReturnType<typeof setInterval> | null = null
  
  function startAutoSync(intervalMs = 5 * 60 * 1000) {
    if (syncInterval) clearInterval(syncInterval)
    syncInterval = setInterval(() => {
      if (syncStore.isAuthenticated && !syncStore.isSyncing) {
        syncStore.performSync()
      }
    }, intervalMs)
  }
  
  function stopAutoSync() {
    if (syncInterval) {
      clearInterval(syncInterval)
      syncInterval = null
    }
  }
  
  onMounted(() => {
    syncStore.checkAuthStatus()
    syncStore.fetchPendingCount()
    if (syncStore.autoSync) startAutoSync()
  })
  
  onUnmounted(() => stopAutoSync())
  
  // Watch autoSync toggle
  watch(() => syncStore.autoSync, (enabled) => {
    if (enabled) startAutoSync()
    else stopAutoSync()
  })
  
  return { syncStore, startAutoSync, stopAutoSync }
}
