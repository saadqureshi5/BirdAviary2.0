<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleSignOut() {
  authStore.signOut()
  router.push('/login')
}

function handleRetry() {
  // Re-check license then navigate to dashboard if now valid
  authStore.verifyLicense().then(() => {
    if (authStore.hasValidLicense) {
      router.push('/')
    }
  })
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-950 relative overflow-hidden">
    <!-- Background decorative elements -->
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-amber-600/10 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-red-600/10 rounded-full blur-3xl opacity-30 pointer-events-none"></div>

    <!-- Card -->
    <div class="relative z-10 w-full max-w-md mx-4">
      <div class="glass-card p-10 text-center">
        <!-- Icon -->
        <div class="mb-6">
          <span class="text-6xl inline-block">⏳</span>
        </div>

        <!-- Title -->
        <h1 class="text-2xl font-bold text-white mb-2">
          Subscription Expired
        </h1>
        <p class="text-slate-400 text-sm mb-6">
          Your <span class="text-white font-medium">{{ authStore.licenseData?.plan || '' }}</span> plan has expired.
          Renew your subscription to continue using Aviary Pro.
        </p>

        <!-- License Info -->
        <div class="bg-surface-800/50 border border-surface-700 rounded-xl p-4 mb-6 text-left space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-slate-400">Account</span>
            <span class="text-white">{{ authStore.userEmail }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-slate-400">Plan</span>
            <span class="text-amber-400 capitalize">{{ authStore.licenseData?.plan || 'None' }}</span>
          </div>
          <div v-if="authStore.licenseData?.expires_at" class="flex justify-between text-sm">
            <span class="text-slate-400">Expired on</span>
            <span class="text-red-400">{{ new Date(authStore.licenseData.expires_at).toLocaleDateString() }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="space-y-3">
          <!-- Retry button (re-checks license) -->
          <button
            @click="handleRetry"
            class="w-full bg-primary-600 hover:bg-primary-500 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
            :disabled="authStore.isCheckingLicense"
          >
            <svg v-if="authStore.isCheckingLicense" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-if="authStore.isCheckingLicense">Checking...</span>
            <span v-else>I've Renewed — Check Again</span>
          </button>

          <!-- Sign out -->
          <button
            @click="handleSignOut"
            class="w-full bg-surface-800 hover:bg-surface-700 text-slate-300 font-medium py-3 px-6 rounded-xl transition-all duration-200 border border-surface-600"
          >
            Sign Out
          </button>
        </div>

        <p class="text-slate-500 text-xs mt-6">
          Contact support if you believe this is a mistake.
        </p>
      </div>

      <!-- Footer -->
      <p class="text-center text-slate-600 text-xs mt-8">
        Bird Aviary v2.0 &bull; Powered by Google Drive
      </p>
    </div>
  </div>
</template>
