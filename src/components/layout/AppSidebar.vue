<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import { useSyncStore } from '@/stores/syncStore'

const route = useRoute()
const birdsStore = useBirdsStore()
const syncStore = useSyncStore()

const isCollapsed = ref(false)

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/birds', label: 'Birds', icon: '🐦' },
  { path: '/breeding', label: 'Breeding', icon: '🥚' },
  { path: '/sales', label: 'Sales', icon: '💰' },
  { path: '/dna', label: 'DNA Records', icon: '🧬' },
  { path: '/reminders', label: 'Reminders', icon: '⏰' },
  { path: '/soft-food', label: 'Soft Food', icon: '🍽️' },
  { path: '/accounting', label: 'Accounting', icon: '📒' },
  { path: '/sync', label: 'Cloud Sync', icon: '☁️' },
]

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside 
    class="glass-panel flex flex-col transition-all duration-300 ease-in-out relative z-20"
    :class="isCollapsed ? 'w-20' : 'w-64'"
  >
    <!-- Logo area -->
    <div class="h-16 flex items-center justify-center border-b border-white/10 px-4">
      <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">
        <span class="text-2xl drop-shadow-[0_0_8px_rgba(20,184,166,0.5)]">🦜</span>
        <span v-if="!isCollapsed" class="font-bold text-lg bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent animate-fade-in">
          Aviary Pro
        </span>
      </div>
    </div>

    <!-- Nav Menu -->
    <nav class="flex-1 py-6 px-3 space-y-2 overflow-y-auto overflow-x-hidden">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 group relative"
        :class="[
          route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
            ? 'bg-primary-500/10 text-primary-400 font-medium'
            : 'text-slate-400 hover:bg-white/5 hover:text-white'
        ]"
      >
        <!-- Active indicator line -->
        <div 
          v-if="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))"
          class="absolute left-0 top-1/4 bottom-1/4 w-1 bg-primary-500 rounded-r-md shadow-[0_0_8px_rgba(20,184,166,0.8)]"
        ></div>
        
        <span class="text-xl group-hover:scale-110 transition-transform" :class="{'mx-auto': isCollapsed}">{{ item.icon }}</span>
        
        <span v-if="!isCollapsed" class="whitespace-nowrap flex-1">
          {{ item.label }}
        </span>
        
        <!-- Badge for birds count -->
        <span 
          v-if="!isCollapsed && item.path === '/birds' && birdsStore.totalCount > 0" 
          class="bg-surface-800 text-xs px-2 py-0.5 rounded-full border border-white/10 group-hover:border-primary-500/30"
        >
          {{ birdsStore.totalCount }}
        </span>
      </router-link>
    </nav>

    <!-- Sync Status Indicator -->
    <div v-if="!isCollapsed" class="px-4 py-3 border-t border-white/10 flex items-center gap-3">
      <div 
        class="w-2.5 h-2.5 rounded-full relative"
        :class="[
          syncStore.syncError ? 'bg-red-500' : 
          syncStore.isSyncing || syncStore.pendingCount > 0 ? 'bg-amber-500' : 
          syncStore.isAuthenticated ? 'bg-green-500' : 'bg-slate-500'
        ]"
      >
        <div v-if="syncStore.isSyncing" class="absolute inset-0 rounded-full bg-amber-500 animate-ping opacity-75"></div>
      </div>
      <div class="flex flex-col flex-1">
        <span class="text-xs font-medium text-slate-300">
          {{ syncStore.syncError ? 'Sync Error' : syncStore.isSyncing ? 'Syncing...' : syncStore.isAuthenticated ? (syncStore.pendingCount > 0 ? `${syncStore.pendingCount} Pending` : 'Synced') : 'Offline' }}
        </span>
      </div>
      <router-link to="/sync" class="text-slate-400 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path><circle cx="12" cy="12" r="3"></circle></svg>
      </router-link>
    </div>

    <!-- Toggle button -->
    <div class="p-4 border-t border-white/10 flex justify-center">
      <button 
        @click="toggleCollapse" 
        class="w-full flex items-center justify-center p-2 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
      >
        <svg v-if="!isCollapsed" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
      </button>
    </div>
  </aside>
</template>
