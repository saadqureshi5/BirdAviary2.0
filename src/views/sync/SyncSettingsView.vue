<script setup lang="ts">
import { onMounted } from 'vue'
import { useSyncStore } from '@/stores/syncStore'
import { useAuthStore } from '@/stores/authStore'

const syncStore = useSyncStore()
const authStore = useAuthStore()

onMounted(() => {
  syncStore.checkAuthStatus()
  syncStore.fetchPendingCount()
})
</script>

<template>
  <div class="max-w-4xl mx-auto pb-12">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">Cloud Sync</h1>
      <p class="text-slate-400">Keep your aviary data synchronized across all your devices using Google Drive.</p>
    </div>

    <!-- Error Alert -->
    <div v-if="syncStore.syncError" class="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
      <span class="text-red-400 mt-0.5">⚠️</span>
      <div>
        <h3 class="text-red-400 font-medium">Sync Error</h3>
        <p class="text-red-300/80 text-sm mt-1">{{ syncStore.syncError }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <!-- Google Account Card -->
      <div class="glass-card p-6 flex flex-col h-full">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
            <span class="text-xl">☁️</span>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-white">Google Drive</h2>
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-green-500"></span>
              <span class="text-sm text-slate-400">Connected</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 mb-4">
          <img 
            v-if="authStore.userAvatar" 
            :src="authStore.userAvatar" 
            class="w-8 h-8 rounded-full" 
            alt="avatar"
          >
          <div class="min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ authStore.userName }}</p>
            <p class="text-xs text-slate-400 truncate">{{ authStore.userEmail }}</p>
          </div>
        </div>

        <p class="text-slate-400 text-sm flex-1">
          Your data is stored securely in an isolated app folder on your Google Drive that only this app can access.
        </p>
      </div>

      <!-- Sync Status Card -->
      <div class="glass-card p-6 flex flex-col h-full relative overflow-hidden">
        <!-- Background animation when syncing -->
        <div v-if="syncStore.isSyncing" class="absolute inset-0 bg-primary-500/5 animate-pulse"></div>
        
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-white flex items-center gap-2">
              Sync Status
            </h2>
            <div class="flex items-center gap-2">
              <span class="text-sm text-slate-400">Auto-sync</span>
              <button 
                @click="syncStore.toggleAutoSync"
                class="w-12 h-6 rounded-full transition-colors relative"
                :class="syncStore.autoSync ? 'bg-primary-500' : 'bg-slate-700'"
              >
                <div 
                  class="absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform"
                  :class="syncStore.autoSync ? 'translate-x-6' : 'translate-x-0'"
                ></div>
              </button>
            </div>
          </div>

          <div class="space-y-4 mb-6 flex-1">
            <div class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
              <span class="text-slate-400">Last Synced</span>
              <span class="text-white font-medium">
                {{ syncStore.lastSyncTime ? new Date(syncStore.lastSyncTime).toLocaleString() : 'Never' }}
              </span>
            </div>
            <div class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
              <span class="text-slate-400">Pending Changes</span>
              <div class="flex items-center gap-2">
                <span v-if="syncStore.pendingCount > 0" class="w-2 h-2 rounded-full bg-amber-500"></span>
                <span class="text-white font-medium" :class="{'text-amber-400': syncStore.pendingCount > 0}">
                  {{ syncStore.pendingCount }}
                </span>
              </div>
            </div>
          </div>

          <button 
            @click="syncStore.performSync"
            :disabled="!syncStore.isAuthenticated || syncStore.isSyncing"
            class="mt-auto w-full bg-primary-500 text-white hover:bg-primary-600 disabled:bg-slate-800 disabled:text-slate-500 font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 relative overflow-hidden"
          >
            <span v-if="syncStore.isSyncing" class="absolute inset-0 flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span :class="{'opacity-0': syncStore.isSyncing}">Sync Now</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Sync History -->
    <div class="glass-card overflow-hidden">
      <div class="p-6 border-b border-white/10">
        <h2 class="text-lg font-semibold text-white">Sync Log</h2>
      </div>
      <div class="p-0">
        <div v-if="syncStore.syncHistory.length === 0" class="p-8 text-center text-slate-500">
          No sync history available.
        </div>
        <table v-else class="w-full text-left text-sm">
          <thead class="text-slate-400 bg-white/5">
            <tr>
              <th class="px-6 py-3 font-medium">Time</th>
              <th class="px-6 py-3 font-medium">Status</th>
              <th class="px-6 py-3 font-medium">Uploaded</th>
              <th class="px-6 py-3 font-medium">Downloaded</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="(log, i) in syncStore.syncHistory" :key="i" class="hover:bg-white/[0.02]">
              <td class="px-6 py-4 text-slate-300">{{ new Date(log.timestamp).toLocaleString() }}</td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  :class="log.status.includes('Error') ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'"
                >
                  {{ log.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-300">{{ log.uploaded }}</td>
              <td class="px-6 py-4 text-slate-300">{{ log.downloaded }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
