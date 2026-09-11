<script setup lang="ts">
import { computed } from 'vue'
import type { PairingDetail } from '@/types'

const props = defineProps<{
  pairing: PairingDetail
}>()

const stats = computed(() => {
  if (!props.pairing) return { total_clutches: 0, total_eggs: 0, total_chicks: 0, chicks_fledged: 0, promoted: 0, mortality: 0 }
  
  const clutches = props.pairing.clutches || []
  const chicks = clutches.flatMap(c => c.chicks || [])
  
  const total_clutches = clutches.length
  const total_eggs = clutches.reduce((sum, c) => sum + (c.total_eggs || 0), 0)
  const total_chicks = chicks.length
  const chicks_fledged = chicks.filter(c => c.status === 'fledged' || c.status === 'added_to_stock').length
  const promoted = chicks.filter(c => c.status === 'added_to_stock').length
  const deceased = chicks.filter(c => c.status === 'deceased').length
  
  const mortalityRate = total_chicks > 0 ? Math.round((deceased / total_chicks) * 100) : 0

  return {
    total_clutches,
    total_eggs,
    total_chicks,
    chicks_fledged,
    promoted,
    mortality: mortalityRate
  }
})
</script>

<template>
  <div class="glass-card p-4 flex flex-wrap gap-6 justify-between items-center">
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Clutches</span>
      <span class="text-2xl font-bold text-white">{{ stats.total_clutches }}</span>
    </div>
    
    <div class="w-px h-10 bg-white/10 hidden sm:block"></div>
    
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Total Eggs</span>
      <span class="text-2xl font-bold text-white">{{ stats.total_eggs }}</span>
    </div>
    
    <div class="w-px h-10 bg-white/10 hidden sm:block"></div>
    
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Hatched</span>
      <span class="text-2xl font-bold text-primary-400">{{ stats.total_chicks }}</span>
    </div>
    
    <div class="w-px h-10 bg-white/10 hidden sm:block"></div>
    
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Fledged</span>
      <span class="text-2xl font-bold text-green-400">{{ stats.chicks_fledged }}</span>
    </div>
    
    <div class="w-px h-10 bg-white/10 hidden md:block"></div>
    
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Promoted</span>
      <span class="text-2xl font-bold text-purple-400">{{ stats.promoted }}</span>
    </div>
    
    <div class="w-px h-10 bg-white/10 hidden lg:block"></div>
    
    <div class="flex flex-col">
      <span class="text-xs text-slate-400 uppercase tracking-wider">Mortality</span>
      <span class="text-2xl font-bold" :class="stats.mortality > 20 ? 'text-red-400' : 'text-slate-300'">{{ stats.mortality }}%</span>
    </div>
  </div>
</template>
