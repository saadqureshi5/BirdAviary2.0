<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import CategoryFilter from '@/components/birds/CategoryFilter.vue'
import BirdCard from '@/components/birds/BirdCard.vue'
import DataTable from '@/components/shared/DataTable.vue'
import Badge from '@/components/shared/Badge.vue'

const router = useRouter()
const route = useRoute()
const birdsStore = useBirdsStore()

const viewMode = ref<'grid' | 'list'>('grid')
const selectedCategory = ref<string | null>(route.query.category as string || null)
const selectedStatus = ref<string>('in_stock')
const searchQuery = ref('')

onMounted(async () => {
  await Promise.all([
    birdsStore.fetchBirds(),
    birdsStore.fetchCategories()
  ])
})

const filteredBirds = computed(() => {
  let result = birdsStore.birds
  
  if (selectedStatus.value) {
    result = result.filter(b => b.status === selectedStatus.value)
  }
  
  if (selectedCategory.value) {
    result = result.filter(b => String(b.category_id) === String(selectedCategory.value))
  }
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(b => 
      b.ring_id.toLowerCase().includes(q) || 
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.mutation && b.mutation.toLowerCase().includes(q))
    )
  }
  
  return result
})

const statusBadgeLabel = computed(() => {
  if (!selectedStatus.value) return `${filteredBirds.value.length} total`
  return `${filteredBirds.value.length} ${selectedStatus.value.replace('_', ' ')}`
})

const tableColumns = [
  { key: 'ring_id', label: 'Ring ID', sortable: true },
  { key: 'name', label: 'Category', sortable: true },
  { key: 'mutation', label: 'Mutation', sortable: true },
  { key: 'sex', label: 'Sex', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'cage_number', label: 'Cage', sortable: true }
]

const getStatusVariant = (status: string) => {
  switch(status) {
    case 'in_stock': return 'success'
    case 'sold': return 'warning'
    case 'deceased': return 'danger'
    default: return 'neutral'
  }
}

const handleCreateCategory = async (data: { name: string, description?: string }) => {
  try {
    await birdsStore.createCategory(data)
  } catch (e) {
    console.error('Failed to create category', e)
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
          Birds Inventory
          <span class="bg-primary-500/20 text-primary-400 text-sm py-1 px-3 rounded-full border border-primary-500/30">
            {{ statusBadgeLabel }}
          </span>
        </h2>
      </div>
      
      <button @click="router.push('/birds/add')" class="btn-primary flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Add Bird
      </button>
    </div>

    <!-- Filters Area -->
    <div class="glass-card p-4 flex flex-col md:flex-row gap-4 justify-between items-center relative z-20 overflow-visible">
      <div class="w-full md:w-auto overflow-visible flex items-center gap-3">
        <div class="flex bg-surface-900 rounded-lg p-1 border border-white/10 shrink-0">
          <button 
            @click="selectedStatus = ''" 
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="!selectedStatus ? 'bg-surface-700 text-white shadow' : 'text-slate-400 hover:text-white'"
          >All</button>
          <button 
            @click="selectedStatus = 'in_stock'" 
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="selectedStatus === 'in_stock' ? 'bg-emerald-500/20 text-emerald-400 shadow' : 'text-slate-400 hover:text-white'"
          >In Stock</button>
          <button 
            @click="selectedStatus = 'sold'" 
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="selectedStatus === 'sold' ? 'bg-amber-500/20 text-amber-400 shadow' : 'text-slate-400 hover:text-white'"
          >Sold</button>
          <button 
            @click="selectedStatus = 'deceased'" 
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="selectedStatus === 'deceased' ? 'bg-red-500/20 text-red-400 shadow' : 'text-slate-400 hover:text-white'"
          >Deceased</button>
        </div>
        <CategoryFilter 
          :categories="birdsStore.categories" 
          :birds="birdsStore.birds"
          :selected-status="selectedStatus"
          v-model="selectedCategory"
          @create="handleCreateCategory" 
        />
      </div>
      
      <div class="flex items-center gap-4 w-full md:w-auto">
        <div class="relative w-full md:w-64">
          <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Filter birds..." 
            class="w-full bg-surface-900/50 border border-white/10 rounded-lg pl-10 pr-4 py-1.5 h-10 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all duration-200"
          >
        </div>
        
        <div class="flex bg-surface-900 rounded-lg p-1 border border-white/10 shrink-0">
          <button 
            @click="viewMode = 'grid'" 
            class="p-1.5 rounded-md transition-colors"
            :class="viewMode === 'grid' ? 'bg-surface-700 text-white shadow' : 'text-slate-400 hover:text-white'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
          </button>
          <button 
            @click="viewMode = 'list'" 
            class="p-1.5 rounded-md transition-colors"
            :class="viewMode === 'list' ? 'bg-surface-700 text-white shadow' : 'text-slate-400 hover:text-white'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Content Area -->
    <div v-if="birdsStore.loading && birdsStore.birds.length === 0" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="filteredBirds.length === 0" class="glass-card py-20 flex flex-col items-center justify-center text-center">
      <div class="w-24 h-24 bg-surface-800 rounded-full flex items-center justify-center mb-6">
        <span class="text-4xl opacity-50">🦜</span>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">No birds found</h3>
      <p class="text-slate-400 max-w-md mb-6">
        We couldn't find any birds matching your current filters. Try adjusting your search or add a new bird.
      </p>
      <button @click="router.push('/birds/add')" class="btn-primary">Add New Bird</button>
    </div>

    <template v-else>
      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <BirdCard 
          v-for="bird in filteredBirds" 
          :key="bird.id" 
          :bird="bird" 
        />
      </div>
      
      <!-- List View -->
      <DataTable 
        v-else 
        :columns="tableColumns" 
        :data="filteredBirds"
      >
        <template #cell-name="{ row }">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded bg-surface-700 overflow-hidden shrink-0">
              <img v-if="row.photo_url" :src="'/' + row.photo_url" class="w-full h-full object-contain">
              <span v-else class="flex items-center justify-center w-full h-full text-xs">🐦</span>
            </div>
            <span class="font-medium text-white">{{ row.category?.name || 'Uncategorized' }}</span>
          </div>
        </template>
        
        <template #cell-sex="{ row }">
          <span v-if="row.sex === 'male'" class="text-blue-400 flex items-center gap-1"><span class="text-lg">♂</span> Male</span>
          <span v-else-if="row.sex === 'female'" class="text-pink-400 flex items-center gap-1"><span class="text-lg">♀</span> Female</span>
          <span v-else class="text-slate-400">Unknown</span>
        </template>
        
        <template #cell-status="{ row }">
          <Badge :variant="getStatusVariant(row.status)" :label="row.status.replace('_', ' ')" />
        </template>
        
      </DataTable>
    </template>
  </div>
</template>
