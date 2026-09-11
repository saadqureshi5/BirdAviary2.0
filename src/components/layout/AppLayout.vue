<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import UpdateBanner from '@/components/shared/UpdateBanner.vue'
</script>

<template>
  <div class="min-h-screen flex bg-surface-950 overflow-hidden text-slate-200">
    <!-- Sidebar Component -->
    <AppSidebar />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <AppHeader />

      <!-- Update Banner -->
      <UpdateBanner />

      <!-- Scrollable Main Content -->
      <main class="flex-1 overflow-y-auto overflow-x-hidden p-6 relative">
        <!-- Background decorative elements for premium feel -->
        <div class="fixed top-0 right-0 -z-10 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
        <div class="fixed bottom-0 left-0 -z-10 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl opacity-30 pointer-events-none"></div>
        
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
