<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import { useDnaStore } from '@/stores/dnaStore'
import Badge from '@/components/shared/Badge.vue'

const route = useRoute()
const router = useRouter()
const birdsStore = useBirdsStore()
const dnaStore = useDnaStore()

const loading = ref(true)
const viewingDna = ref(false)
const birdId = computed(() => route.params.id as string)

onMounted(async () => {
  loading.value = true
  await birdsStore.fetchBird(birdId.value)
  loading.value = false
})

const bird = computed(() => birdsStore.selectedBird)

const statusBadge = computed(() => {
  if (!bird.value) return { label: 'Unknown', variant: 'neutral' as const }
  switch (bird.value.status) {
    case 'in_stock': return { label: 'In Stock', variant: 'success' as const }
    case 'sold': return { label: 'Sold', variant: 'warning' as const }
    case 'deceased': return { label: 'Deceased', variant: 'danger' as const }
    default: return { label: 'Unknown', variant: 'neutral' as const }
  }
})

const formatDate = (dateString?: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}

const handleViewDna = async () => {
  viewingDna.value = true
  try {
    await dnaStore.fetchDnaRecords(Number(birdId.value))
    if (dnaStore.dnaRecords && dnaStore.dnaRecords.length > 0) {
      const record = dnaStore.dnaRecords[0]
      window.open(`/${record.file_path}`, '_blank')
    } else {
      alert("No DNA record found for this bird.")
    }
  } catch (e) {
    alert("Error fetching DNA record.")
  } finally {
    viewingDna.value = false
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in pb-10">
    <!-- Breadcrumb -->
    <nav class="flex text-sm text-slate-400 mb-4">
      <router-link to="/birds" class="hover:text-white transition-colors">Birds</router-link>
      <span class="mx-2">/</span>
      <span class="text-white">{{ bird?.ring_id || 'Loading...' }}</span>
    </nav>

    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="!bird" class="glass-card p-10 text-center">
      <div class="text-6xl mb-4">😢</div>
      <h3 class="text-xl font-bold text-white mb-2">Bird Not Found</h3>
      <p class="text-slate-400 mb-6">The bird you're looking for doesn't exist or has been deleted.</p>
      <button @click="router.push('/birds')" class="btn-primary">Back to Inventory</button>
    </div>

    <template v-else>
      <!-- Hero Profile Section -->
      <div class="glass-card overflow-hidden relative">
        <div class="absolute inset-0 bg-gradient-to-r from-surface-900/90 to-surface-900/40 z-10"></div>
        
        <!-- Background Image Blur -->
        <div 
          v-if="bird.photo_url"
          class="absolute inset-0 bg-cover bg-center blur-xl opacity-30"
          :style="{ backgroundImage: `url(/${bird.photo_url})` }"
        ></div>
        
        <div class="relative z-20 flex flex-col md:flex-row p-6 md:p-10 gap-8 items-center md:items-stretch">
          <!-- Profile Photo -->
          <div class="w-48 md:w-72 rounded-2xl overflow-hidden border-4 border-white/10 shadow-2xl shrink-0 bg-surface-800 flex items-center justify-center">
            <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-auto max-h-72 object-contain">
            <div v-else class="w-full h-48 md:h-64 flex items-center justify-center bg-gradient-to-br from-surface-700 to-surface-800">
              <span class="text-6xl opacity-30">🐦</span>
            </div>
          </div>
          
          <!-- Key Info -->
          <div class="flex-1 flex flex-col justify-center text-center md:text-left">
            <div class="flex flex-col md:flex-row items-center gap-3 mb-2">
              <h1 class="text-4xl font-bold text-white drop-shadow-md">{{ bird.ring_id }}</h1>
              <Badge :variant="statusBadge.variant" :label="statusBadge.label" class="text-sm px-3 py-1" />
            </div>
            
            <h2 class="text-2xl text-slate-300 font-medium mb-4">{{ bird.mutation || 'Unknown Mutation' }}</h2>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-auto w-full max-w-2xl">
              <div class="bg-surface-900/50 p-3 rounded-xl border border-white/5 backdrop-blur-sm">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Sex</div>
                <div class="font-medium text-white flex items-center justify-center md:justify-start gap-1">
                  <span v-if="bird.sex === 'male'" class="text-blue-400 text-lg">♂</span>
                  <span v-else-if="bird.sex === 'female'" class="text-pink-400 text-lg">♀</span>
                  {{ bird.sex.charAt(0).toUpperCase() + bird.sex.slice(1) }}
                </div>
              </div>
              <div class="bg-surface-900/50 p-3 rounded-xl border border-white/5 backdrop-blur-sm">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Name</div>
                <div class="font-medium text-white truncate" :title="bird.name || 'N/A'">{{ bird.name || 'N/A' }}</div>
              </div>
              <div class="bg-surface-900/50 p-3 rounded-xl border border-white/5 backdrop-blur-sm">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Category</div>
                <div class="font-medium text-white truncate">{{ bird.category?.name || 'N/A' }}</div>
              </div>
              <div class="bg-surface-900/50 p-3 rounded-xl border border-white/5 backdrop-blur-sm">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-1">Cage</div>
                <div class="font-medium text-white">{{ bird.cage_number || 'N/A' }}</div>
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex flex-col gap-3 justify-center w-full md:w-auto shrink-0 mt-4 md:mt-0">
            <button @click="router.push(`/birds/${bird.id}/edit`)" class="btn-primary w-full shadow-[0_0_15px_rgba(20,184,166,0.3)]">Edit Profile</button>
            <button @click="handleViewDna" :disabled="viewingDna" class="btn-secondary w-full">
              {{ viewingDna ? 'Loading...' : 'View DNA Cert' }}
            </button>
            <router-link :to="`/birds/${bird.id}/pedigree`" class="btn-secondary w-full flex items-center justify-center gap-2 no-underline">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v16"/><path d="M8 8h8"/><path d="M8 16h8"/></svg>
              Ancestry Tree
            </router-link>
          </div>
        </div>
      </div>

      <!-- Details Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Parent Lineage -->
        <div class="lg:col-span-1 space-y-6">
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white border-b border-white/10 pb-3 mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M17 18a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2"/><rect width="18" height="18" x="3" y="4" rx="2"/><circle cx="12" cy="10" r="2"/><line x1="8" x2="8" y1="2" y2="4"/><line x1="16" x2="16" y1="2" y2="4"/></svg>
              Lineage
            </h3>
            
            <div class="space-y-4">
              <!-- Father -->
              <div>
                <div class="text-xs text-slate-400 mb-2 uppercase tracking-wider font-medium">Sire (Father)</div>
                <div 
                  v-if="bird.father"
                  @click="router.push(`/birds/${bird.father?.id}`)"
                  class="flex items-center gap-3 p-3 rounded-lg bg-surface-800/50 border border-white/5 hover:border-blue-500/30 hover:bg-surface-800 cursor-pointer transition-all group"
                >
                  <div class="w-10 h-10 rounded-md bg-blue-900/30 border border-blue-500/20 flex items-center justify-center text-blue-400 text-lg">♂</div>
                  <div>
                    <div class="font-medium text-white group-hover:text-blue-400 transition-colors">{{ bird.father.ring_id }}</div>
                    <div class="text-xs text-slate-400">{{ bird.father.name || bird.father.mutation }}</div>
                  </div>
                </div>
                <div v-else class="p-3 rounded-lg border border-dashed border-white/10 text-slate-500 text-sm flex items-center justify-center">
                  Unknown Sire
                </div>
              </div>
              
              <!-- Mother -->
              <div>
                <div class="text-xs text-slate-400 mb-2 uppercase tracking-wider font-medium">Dam (Mother)</div>
                <div 
                  v-if="bird.mother"
                  @click="router.push(`/birds/${bird.mother?.id}`)"
                  class="flex items-center gap-3 p-3 rounded-lg bg-surface-800/50 border border-white/5 hover:border-pink-500/30 hover:bg-surface-800 cursor-pointer transition-all group"
                >
                  <div class="w-10 h-10 rounded-md bg-pink-900/30 border border-pink-500/20 flex items-center justify-center text-pink-400 text-lg">♀</div>
                  <div>
                    <div class="font-medium text-white group-hover:text-pink-400 transition-colors">{{ bird.mother.ring_id }}</div>
                    <div class="text-xs text-slate-400">{{ bird.mother.name || bird.mother.mutation }}</div>
                  </div>
                </div>
                <div v-else class="p-3 rounded-lg border border-dashed border-white/10 text-slate-500 text-sm flex items-center justify-center">
                  Unknown Dam
                </div>
              </div>
            </div>
          </div>
          
          <!-- Notes -->
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white border-b border-white/10 pb-3 mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              Notes
            </h3>
            <p v-if="bird.notes" class="text-slate-300 text-sm whitespace-pre-line leading-relaxed">
              {{ bird.notes }}
            </p>
            <p v-else class="text-slate-500 text-sm italic">No notes recorded for this bird.</p>
          </div>
        </div>
        
        <!-- Main Info Tabs -->
        <div class="lg:col-span-2 space-y-6">
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white border-b border-white/10 pb-3 mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/></svg>
              System Information
            </h3>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8">
              <div class="flex justify-between py-2 border-b border-white/5">
                <span class="text-slate-400">Database ID</span>
                <span class="text-slate-200 font-mono text-sm">{{ bird.id }}</span>
              </div>
              <div class="flex justify-between py-2 border-b border-white/5">
                <span class="text-slate-400">Created At</span>
                <span class="text-slate-200">{{ formatDate(bird.created_at) }}</span>
              </div>
              <div class="flex justify-between py-2 border-b border-white/5">
                <span class="text-slate-400">Last Updated</span>
                <span class="text-slate-200">{{ formatDate(bird.updated_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="glass-card p-6 min-h-[300px] flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-full bg-surface-800 flex items-center justify-center mb-4 border border-white/10">
              <span class="text-2xl">🥚</span>
            </div>
            <h3 class="text-xl font-medium text-white mb-2">Breeding History</h3>
            <p class="text-slate-400 max-w-md">Detailed breeding history, pairings, and offspring will be displayed here in a future update.</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
