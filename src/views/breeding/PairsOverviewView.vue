<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBreedingStore } from '@/stores/breedingStore'
import { useBirdsStore } from '@/stores/birdsStore'
import { ref } from 'vue'
import StatCard from '@/components/shared/StatCard.vue'
import DataTable from '@/components/shared/DataTable.vue'
import Badge from '@/components/shared/Badge.vue'

const router = useRouter()
const breedingStore = useBreedingStore()
const birdsStore = useBirdsStore()

const selectedCategory = ref('')

onMounted(async () => {
  await Promise.all([
    breedingStore.fetchPairings(),
    breedingStore.fetchAnalytics(),
    birdsStore.fetchCategories()
  ])
})

const tableColumns = [
  { key: 'bird_a', label: 'Male (♂)', sortable: false },
  { key: 'bird_b', label: 'Female (♀)', sortable: false },
  { key: 'cage_number', label: 'Cage', sortable: true },
  { key: 'start_date', label: 'Start Date', sortable: true },
  { key: 'status', label: 'Status', sortable: false },
  { key: 'total_clutches', label: 'Clutches', sortable: true },
  { key: 'chicks_fledged', label: 'Fledged', sortable: true },
  { key: 'actions', label: '', sortable: false }
]

const getStatusVariant = (endDate: string | null) => {
  return endDate ? 'neutral' : 'success'
}

const filteredPairings = computed(() => {
  let list = breedingStore.pairings
  if (selectedCategory.value) {
    list = list.filter(p => String(p.bird_a?.category_id) === String(selectedCategory.value) || String(p.bird_b?.category_id) === String(selectedCategory.value))
  }
  return list
})

const computedAnalytics = computed(() => {
  return {
    active_pairs: filteredPairings.value.filter(p => !p.end_date).length,
    total_clutches: filteredPairings.value.reduce((sum, p) => sum + (p.total_clutches || 0), 0),
    total_chicks_fledged: filteredPairings.value.reduce((sum, p) => sum + (p.chicks_fledged || 0), 0),
    total_promoted_to_stock: filteredPairings.value.reduce((sum, p) => sum + (p.chicks_added_to_stock || 0), 0)
  }
})

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
          Breeding Pairs
          <span class="bg-primary-500/20 text-primary-400 text-sm py-1 px-3 rounded-full border border-primary-500/30">
            {{ filteredPairings.length }} total
          </span>
        </h2>
      </div>
      
      <div class="flex flex-wrap gap-3 items-center">
        <!-- Category Filter -->
        <select v-model="selectedCategory" class="input-field max-w-[200px] py-1.5 appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.5rem_center] bg-[length:1em_1em] pr-8">
          <option value="">All Categories</option>
          <option v-for="cat in birdsStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
        
        <button @click="router.push('/breeding/analytics')" class="btn-secondary flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
          Analytics
        </button>
        <button @click="router.push('/breeding/create')" class="btn-primary flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          Create Pair
        </button>
      </div>
    </div>

    <!-- Stats Area -->
    <div v-if="filteredPairings.length >= 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard 
        title="Active Pairs" 
        :value="computedAnalytics.active_pairs" 
        icon="🐦"
        color="primary"
      />
      <StatCard 
        title="Total Clutches" 
        :value="computedAnalytics.total_clutches" 
        icon="🥚" 
        color="warning"
      />
      <StatCard 
        title="Chicks Fledged" 
        :value="computedAnalytics.total_chicks_fledged" 
        icon="🐣" 
        color="success"
      />
      <StatCard 
        title="Promoted to Stock" 
        :value="computedAnalytics.total_promoted_to_stock" 
        icon="📈" 
        color="success"
      />
    </div>

    <!-- Content Area -->
    <div v-if="breedingStore.loading && breedingStore.pairings.length === 0" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="breedingStore.pairings.length === 0" class="glass-card py-20 flex flex-col items-center justify-center text-center">
      <div class="w-24 h-24 bg-surface-800 rounded-full flex items-center justify-center mb-6">
        <span class="text-4xl opacity-50">👩‍❤️‍👨</span>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">No breeding pairs found</h3>
      <p class="text-slate-400 max-w-md mb-6">
        You haven't set up any breeding pairs yet. Create your first pair to start tracking clutches and chicks.
      </p>
      <button @click="router.push('/breeding/create')" class="btn-primary">Create Pair</button>
    </div>

    <template v-else>
      <DataTable 
        :columns="tableColumns" 
        :data="filteredPairings"
      >
        <template #cell-bird_a="{ row }">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded bg-surface-700 overflow-hidden shrink-0">
              <img v-if="row.bird_a?.photo_url" :src="'/' + row.bird_a.photo_url" class="w-full h-full object-contain">
              <span v-else class="flex items-center justify-center w-full h-full text-xs">🐦</span>
            </div>
            <div>
              <div class="font-medium text-blue-400 flex items-center gap-1">
                {{ row.bird_a?.mutation || 'Unknown Mutation' }} <span class="text-lg">♂</span>
              </div>
              <div class="text-xs text-slate-400">{{ row.bird_a?.ring_id }}</div>
            </div>
          </div>
        </template>
        
        <template #cell-bird_b="{ row }">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded bg-surface-700 overflow-hidden shrink-0">
              <img v-if="row.bird_b?.photo_url" :src="'/' + row.bird_b.photo_url" class="w-full h-full object-contain">
              <span v-else class="flex items-center justify-center w-full h-full text-xs">🐦</span>
            </div>
            <div>
              <div class="font-medium text-pink-400 flex items-center gap-1">
                {{ row.bird_b?.mutation || 'Unknown Mutation' }} <span class="text-lg">♀</span>
              </div>
              <div class="text-xs text-slate-400">{{ row.bird_b?.ring_id }}</div>
            </div>
          </div>
        </template>
        
        <template #cell-start_date="{ row }">
          {{ formatDate(row.start_date) }}
        </template>

        <template #cell-status="{ row }">
          <Badge :variant="getStatusVariant(row.end_date)" :label="row.end_date ? 'Ended' : 'Active'" />
        </template>
        
        <template #cell-actions="{ row }">
          <div class="flex justify-end">
            <button 
              @click="router.push(`/breeding/${row.id}`)"
              class="text-primary-400 hover:text-primary-300 bg-primary-500/10 hover:bg-primary-500/20 px-3 py-1.5 rounded transition-colors text-sm"
            >
              View Record
            </button>
          </div>
        </template>
      </DataTable>
    </template>
  </div>
</template>
