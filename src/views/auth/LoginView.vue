<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-950 relative overflow-hidden">
    <!-- Background decorative elements -->
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-3xl opacity-30 pointer-events-none"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-primary-500/5 rounded-full blur-3xl pointer-events-none"></div>

    <!-- Login Card -->
    <div class="relative z-10 w-full max-w-md mx-4">
      <div class="glass-card p-10 text-center">
        <!-- App Logo -->
        <div class="mb-6">
          <span class="text-6xl drop-shadow-[0_0_16px_rgba(20,184,166,0.5)] inline-block animate-fade-in">
            🦜
          </span>
        </div>

        <!-- App Name -->
        <h1 class="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent mb-2">
          Aviary Pro
        </h1>
        <p class="text-slate-400 text-sm mb-8">
          Professional Bird Aviary Management
        </p>

        <!-- Error Alert -->
        <div 
          v-if="authStore.loginError" 
          class="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-left"
        >
          <p class="text-red-400 text-sm">{{ authStore.loginError }}</p>
        </div>

        <!-- Sign In Button -->
        <button 
          @click="authStore.signIn"
          class="w-full bg-white hover:bg-slate-100 text-slate-900 font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
        >
          <!-- Google Icon -->
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Sign in with Google
        </button>

        <p class="text-slate-500 text-xs mt-6">
          Sign in to access your aviary data across all devices
        </p>
      </div>

      <!-- Footer -->
      <p class="text-center text-slate-600 text-xs mt-8">
        Bird Aviary v2.0 &bull; Powered by Google Drive
      </p>
    </div>
  </div>
</template>
