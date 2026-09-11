<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useSyncStore } from '@/stores/syncStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const syncStore = useSyncStore()

onMounted(async () => {
  const code = route.query.code as string
  
  if (!code) {
    router.push('/login')
    return
  }

  const success = await authStore.handleCallback(code)
  
  if (success) {
    // Also update sync store auth status since we now have Google tokens
    syncStore.checkAuthStatus()
    router.push('/')
  } else {
    router.push('/login')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-950">
    <div class="text-center">
      <!-- Spinner -->
      <div class="mb-6">
        <svg class="animate-spin h-10 w-10 text-primary-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <h2 class="text-xl font-semibold text-white mb-2">Signing you in...</h2>
      <p class="text-slate-400 text-sm">Please wait while we complete authentication.</p>
    </div>
  </div>
</template>
