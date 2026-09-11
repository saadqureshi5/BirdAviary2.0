<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBreedingStore } from '@/stores/breedingStore'
import { useBirdsStore } from '@/stores/birdsStore'
import StatCard from '@/components/shared/StatCard.vue'

const router = useRouter()
const breedingStore = useBreedingStore()
const birdsStore = useBirdsStore()

const selectedCategory = ref<number | null>(null)

onMounted(async () => {
  await birdsStore.fetchCategories()
  await breedingStore.fetchAnalytics()
})

watch(selectedCategory, async (newVal) => {
  await breedingStore.fetchAnalytics(newVal)
})

const getRankColor = (index: number) => {
  switch (index) {
    case 0: return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'
    case 1: return 'text-slate-300 bg-slate-300/10 border-slate-300/30'
    case 2: return 'text-amber-600 bg-amber-600/10 border-amber-600/30'
    default: return 'text-slate-400 bg-surface-700 border-white/5'
  }
}
</script>

<template>
  <div class="space-y-8 animate-fade-in max-w-6xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
      <div class="flex items-center gap-4">
        <button @click="router.push('/breeding')" class="p-2 bg-surface-800 hover:bg-surface-700 text-slate-300 rounded-lg transition-colors border border-white/5">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <h2 class="text-2xl font-bold text-white">Breeding Analytics</h2>
          <p class="text-slate-400 text-sm mt-1">Overview of breeding performance and productivity</p>
        </div>
      </div>
      
      <div class="w-full sm:w-64">
        <select v-model="selectedCategory" class="input-field w-full">
          <option :value="null">All Categories</option>
          <option v-for="cat in birdsStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="breedingStore.loading && !breedingStore.analytics" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>

    <template v-else-if="breedingStore.analytics">
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <StatCard 
          title="Total Pairs" 
          :value="breedingStore.analytics.total_pairings" 
          icon="👩‍❤️‍👨"
        />
        <StatCard 
          title="Total Clutches" 
          :value="breedingStore.analytics.total_clutches" 
          icon="🪺"
        />
        <StatCard 
          title="Total Eggs" 
          :value="breedingStore.analytics.total_eggs" 
          icon="🥚"
        />
        <StatCard 
          title="Chicks Hatched" 
          :value="breedingStore.analytics.total_chicks_hatched" 
          icon="🐣"
        />
        <StatCard 
          title="Chicks Fledged" 
          :value="breedingStore.analytics.total_chicks_fledged" 
          icon="🕊️"
          valueClass="text-green-400"
        />
        <StatCard 
          title="Promoted to Stock" 
          :value="breedingStore.analytics.total_promoted_to_stock" 
          icon="📈"
          valueClass="text-purple-400"
        />
        <StatCard 
          title="Mortality" 
          :value="breedingStore.analytics.total_deceased" 
          icon="⚠️"
          valueClass="text-red-400"
        />
        <StatCard 
          title="Success Rate" 
          :value="(breedingStore.analytics.total_eggs > 0 ? Math.round((breedingStore.analytics.total_chicks_fledged / breedingStore.analytics.total_eggs) * 100) : 0) + '%'" 
          icon="🎯"
          valueClass="text-primary-400"
        />
      </div>

      <!-- Best Performing Pairs -->
      <div>
        <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" class="text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>
          Top Producing Pairs
        </h3>
        
        <div v-if="!breedingStore.analytics.best_pairs || breedingStore.analytics.best_pairs.length === 0" class="glass-card py-12 text-center">
          <p class="text-slate-400">Not enough data to determine top pairs yet.</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="(pair, index) in breedingStore.analytics.best_pairs" 
            :key="pair.id"
            class="glass-card p-5 relative overflow-hidden group cursor-pointer hover:border-primary-500/30 transition-colors"
            @click="router.push(`/breeding/${pair.id}`)"
          >
            <!-- Rank Badge -->
            <div class="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center font-bold border" :class="getRankColor(index)">
              #{{ index + 1 }}
            </div>
            
            <div class="flex items-center gap-4 mb-6 pr-10">
              <div class="flex -space-x-2">
                <div class="w-14 h-14 rounded-full border-2 border-surface-800 bg-surface-700 overflow-hidden z-10">
                  <img v-if="pair.bird_a?.photo_url" :src="pair.bird_a.photo_url" class="w-full h-full object-cover">
                  <span v-else class="flex items-center justify-center w-full h-full text-sm">♂</span>
                </div>
                <div class="w-14 h-14 rounded-full border-2 border-surface-800 bg-surface-700 overflow-hidden z-0 opacity-90">
                  <img v-if="pair.bird_b?.photo_url" :src="pair.bird_b.photo_url" class="w-full h-full object-cover">
                  <span v-else class="flex items-center justify-center w-full h-full text-sm">♀</span>
                </div>
              </div>
              <div>
                <div class="font-bold text-white text-lg">Pair #{{ pair.id }}</div>
                <div class="text-sm text-slate-400">{{ pair.bird_a?.ring_id }} × {{ pair.bird_b?.ring_id }}</div>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-surface-900/50 rounded-lg p-3 border border-white/5">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Clutches</div>
                <div class="text-xl font-bold text-white">{{ pair.total_clutches }}</div>
              </div>
              <div class="bg-surface-900/50 rounded-lg p-3 border border-white/5">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Fledged</div>
                <div class="text-xl font-bold text-green-400">{{ pair.chicks_fledged }}</div>
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-white/5 text-sm flex justify-between items-center text-slate-400">
              <span>View Record</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="group-hover:translate-x-1 transition-transform"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
