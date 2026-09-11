import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import { driveSyncService } from '@/services/GoogleDriveSyncService'
import * as authService from '@/services/authService'
import type { SyncLogEntry, SyncStatus } from '@/types'

function getOrCreateDeviceId(): string {
  let id = localStorage.getItem('device_id')
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('device_id', id)
  }
  return id
}

export const useSyncStore = defineStore('sync', () => {
  // State
  const isAuthenticated = ref(authService.isAuthenticated())
  const isSyncing = ref(false)
  const lastSyncTime = ref<string | null>(localStorage.getItem('last_sync_time'))
  const pendingCount = ref(0)
  const syncError = ref<string | null>(null)
  const autoSync = ref(localStorage.getItem('auto_sync') === 'true')
  const syncHistory = ref<{ timestamp: string; uploaded: number; downloaded: number; status: string }[]>([])
  const deviceId = getOrCreateDeviceId()
  
  const { get, post } = useApi()
  
  // Actions
  async function checkAuthStatus() {
    isAuthenticated.value = authService.isAuthenticated()
  }
  
  async function signIn() {
    try {
      await authService.startOAuthFlow()
    } catch (e: any) {
      syncError.value = e.message || 'Failed to start sign in'
    }
  }
  
  async function signOut() {
    authService.clearTokens()
    isAuthenticated.value = false
    syncError.value = null
  }
  
  async function fetchPendingCount() {
    try {
      const status = await get<{ total_entries: number; unsynced_count: number; last_sync: string | null }>('/sync/status')
      if (status) {
        pendingCount.value = status.unsynced_count
      }
    } catch (e) {
      console.error('Failed to fetch pending count:', e)
    }
  }
  
  async function performSync() {
    if (!isAuthenticated.value || isSyncing.value) return
    
    isSyncing.value = true
    syncError.value = null
    let uploaded = 0
    let downloaded = 0
    
    try {
      // 1. Fetch pending entries from backend
      const pendingResp = await get<{ items: SyncLogEntry[]; total: number }>('/sync/pending')
      const pendingEntries = pendingResp?.items || []
      
      // 2. Upload them to Google Drive
      if (pendingEntries.length > 0) {
        await driveSyncService.uploadEntries(pendingEntries)
        
        // 3. Mark them as synced in backend
        const entry_ids = pendingEntries.map(e => e.id)
        await post('/sync/mark-synced', { entry_ids })
        uploaded = pendingEntries.length
      }
      
      // 4. Download remote entries from Drive
      const remoteEntries = await driveSyncService.downloadEntries()
      
      // 5. Filter to only entries not from this device
      const foreignEntries = remoteEntries.filter(e => e.device_id !== deviceId)
      
      // 6. Replay them into local DB
      if (foreignEntries.length > 0) {
        await post('/sync/replay', { entries: foreignEntries })
        downloaded = foreignEntries.length
      }
      
      // 7. Update state
      const now = new Date().toISOString()
      lastSyncTime.value = now
      localStorage.setItem('last_sync_time', now)
      pendingCount.value = 0
      
      syncHistory.value.unshift({ timestamp: now, uploaded, downloaded, status: 'Success' })
      if (syncHistory.value.length > 10) syncHistory.value.pop()
      
    } catch (e: any) {
      console.error('Sync failed:', e)
      syncError.value = e.message || 'Sync failed due to an error'
      syncHistory.value.unshift({ 
        timestamp: new Date().toISOString(), 
        uploaded, 
        downloaded, 
        status: `Error: ${syncError.value}` 
      })
      if (syncHistory.value.length > 10) syncHistory.value.pop()
    } finally {
      isSyncing.value = false
    }
  }
  
  async function toggleAutoSync() {
    autoSync.value = !autoSync.value
    localStorage.setItem('auto_sync', autoSync.value.toString())
  }
  
  return {
    isAuthenticated,
    isSyncing,
    lastSyncTime,
    pendingCount,
    syncError,
    autoSync,
    syncHistory,
    deviceId,
    checkAuthStatus,
    signIn,
    signOut,
    fetchPendingCount,
    performSync,
    toggleAutoSync
  }
})
