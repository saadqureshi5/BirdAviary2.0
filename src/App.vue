<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()

// Public routes render without the app layout (sidebar, header)
const isPublicRoute = computed(() => {
  return route.meta.public === true
})
</script>

<template>
  <!-- Public routes (login, callback, expired) render full-screen without layout -->
  <router-view v-if="isPublicRoute" />
  
  <!-- Authenticated routes render inside the app layout (sidebar + header) -->
  <AppLayout v-else />
</template>
