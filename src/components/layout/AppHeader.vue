<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import BirdSearchBar from '@/components/birds/BirdSearchBar.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const pageTitle = computed(() => {
  return route.meta.title || 'Overview'
})

const isProfileMenuOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const displayName = computed(() => authStore.userName)
const displayAvatar = computed(() => {
  return authStore.userAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${authStore.userEmail || 'default'}&backgroundColor=transparent`
})

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isProfileMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const toggleMenu = (event: MouseEvent) => {
  isProfileMenuOpen.value = !isProfileMenuOpen.value
}

const handleSignOut = () => {
  isProfileMenuOpen.value = false
  authStore.signOut()
  router.push('/login')
}
</script>

<template>
  <header class="h-16 border-b border-white/10 bg-surface-900/40 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
    <div class="flex items-center gap-4">
      <h1 class="text-xl font-semibold text-white tracking-tight animate-fade-in">{{ pageTitle }}</h1>
    </div>

    <div class="flex-1 max-w-md mx-8">
      <BirdSearchBar />
    </div>

    <div class="flex items-center gap-4">
      <button class="w-10 h-10 rounded-full bg-surface-800 border border-white/10 flex items-center justify-center hover:bg-surface-700 transition-colors text-slate-300 hover:text-white relative">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
        <span class="absolute top-2 right-2.5 w-2 h-2 bg-primary-500 rounded-full animate-pulse-glow"></span>
      </button>
      
      <div class="relative" ref="dropdownRef">
        <div 
          @click="toggleMenu"
          class="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-600 to-blue-500 border-2 border-surface-800 shadow-md overflow-hidden cursor-pointer"
        >
          <img :src="displayAvatar" alt="User Avatar" class="w-full h-full object-cover">
        </div>

        <!-- Dropdown Menu -->
        <div 
          v-if="isProfileMenuOpen"
          class="absolute right-0 mt-2 w-56 bg-surface-800 border border-white/10 rounded-lg shadow-xl py-1 z-50 animate-fade-in"
        >
          <div class="px-4 py-3 border-b border-white/5 mb-1">
            <p class="text-sm font-medium text-white truncate">{{ displayName }}</p>
            <p class="text-xs text-slate-400 truncate mt-0.5">{{ authStore.userEmail }}</p>
          </div>
          <button 
            @click="handleSignOut"
            class="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-red-500/10 hover:text-red-400 transition-colors flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            Sign Out
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
