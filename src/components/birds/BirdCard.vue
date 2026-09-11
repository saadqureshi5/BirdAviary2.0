<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Bird } from '@/types'
import Badge from '@/components/shared/Badge.vue'

const props = defineProps<{
  bird: Bird
}>()

const router = useRouter()

const navigateToProfile = () => {
  router.push(`/birds/${props.bird.id}`)
}

const statusBadge = computed(() => {
  switch (props.bird.status) {
    case 'in_stock': return { label: 'In Stock', variant: 'success' as const }
    case 'sold': return { label: 'Sold', variant: 'warning' as const }
    case 'deceased': return { label: 'Deceased', variant: 'danger' as const }
    default: return { label: 'Unknown', variant: 'neutral' as const }
  }
})
</script>

<template>
  <div 
    @click="navigateToProfile"
    class="glass-card overflow-hidden group cursor-pointer hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.5)] hover:border-primary-500/30 transition-all duration-300 flex flex-col"
  >
    <!-- Image Header -->
    <div class="h-48 relative overflow-hidden bg-surface-900">
      <img 
        v-if="bird.photo_url" 
        :src="'/' + bird.photo_url" 
        :alt="bird.name || bird.ring_id" 
        class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
      >
      <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-surface-800 to-surface-900">
        <span class="text-6xl opacity-20">🐦</span>
      </div>
      
      <!-- Overlays -->
      <div class="absolute top-3 right-3">
        <Badge :variant="statusBadge.variant" :label="statusBadge.label" class="backdrop-blur-md bg-opacity-80" />
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent">
        <h3 class="text-lg font-bold text-white truncate drop-shadow-md">
          {{ bird.ring_id }}
        </h3>
      </div>
    </div>
    
    <!-- Body -->
    <div class="p-4 flex flex-col gap-2 flex-1">
      <div class="flex justify-between items-start">
        <div class="font-medium text-slate-200 truncate pr-2">
          {{ bird.category?.name || 'Uncategorized' }}
        </div>
        <div class="text-xl" title="Sex">
          <span v-if="bird.sex === 'male'" class="text-blue-400 drop-shadow-[0_0_4px_rgba(96,165,250,0.5)]">♂</span>
          <span v-else-if="bird.sex === 'female'" class="text-pink-400 drop-shadow-[0_0_4px_rgba(244,114,182,0.5)]">♀</span>
          <span v-else class="text-slate-400">?</span>
        </div>
      </div>
      
      <div class="text-sm text-primary-400 font-medium truncate">
        {{ bird.mutation || 'Standard Mutation' }}
      </div>
      
      <div class="mt-auto pt-3 flex items-center justify-between text-xs text-slate-400 border-t border-white/5">
        <div class="flex items-center gap-1 bg-surface-800 px-2 py-1 rounded-md">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="3" x2="21" y1="9" y2="9"/><line x1="9" x2="9" y1="21" y2="9"/></svg>
          Cage {{ bird.cage_number || 'N/A' }}
        </div>
        
        <span v-if="bird.name" class="px-2 py-1 bg-white/5 rounded-md truncate max-w-[100px]" :title="bird.name">
          {{ bird.name }}
        </span>
      </div>
    </div>
  </div>
</template>
