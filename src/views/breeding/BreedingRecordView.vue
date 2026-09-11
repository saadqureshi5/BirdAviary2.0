<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBreedingStore } from '@/stores/breedingStore'
import PairStats from '@/components/breeding/PairStats.vue'
import ClutchForm from '@/components/breeding/ClutchForm.vue'
import ChickList from '@/components/breeding/ChickList.vue'
import Badge from '@/components/shared/Badge.vue'
import Modal from '@/components/shared/Modal.vue'

const route = useRoute()
const router = useRouter()
const breedingStore = useBreedingStore()

const showAddClutchModal = ref(false)
const showEditClutchModal = ref(false)
const editingClutch = ref<any>(null)

const pairingId = computed(() => parseInt(route.params.id as string))
const pairing = computed(() => breedingStore.selectedPairing)

onMounted(async () => {
  if (pairingId.value) {
    await breedingStore.fetchPairing(pairingId.value)
  }
})

const refreshPairing = async () => {
  await breedingStore.fetchPairing(pairingId.value)
}

const handleAddClutch = async (data: any) => {
  try {
    await breedingStore.createClutch(pairingId.value, data)
    showAddClutchModal.value = false
  } catch (e) {
    console.error(e)
  }
}

const handleEditClutch = async (data: any) => {
  if (!editingClutch.value) return
  try {
    await breedingStore.updateClutch(editingClutch.value.id, data)
    showEditClutchModal.value = false
    editingClutch.value = null
  } catch (e) {
    console.error(e)
  }
}

const openEditClutch = (clutch: any) => {
  editingClutch.value = clutch
  showEditClutchModal.value = true
}

const getStatusVariant = (endDate: string | null) => {
  return endDate ? 'neutral' : 'success'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const endPairing = async () => {
  if (confirm('Are you sure you want to end this pairing?')) {
    try {
      await breedingStore.updatePairing(pairingId.value, { 
        end_date: new Date().toISOString().split('T')[0] 
      })
    } catch (e) {
      console.error(e)
    }
  }
}

const reactivatePairing = async () => {
  if (confirm('Are you sure you want to reactivate this pairing?')) {
    try {
      await breedingStore.updatePairing(pairingId.value, { 
        end_date: null 
      })
    } catch (e) {
      console.error(e)
    }
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in max-w-5xl mx-auto">
    
    <div v-if="breedingStore.loading && !pairing" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
    
    <template v-else-if="pairing">
      <!-- Header / Pair Info -->
      <div class="glass-card p-6">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-6">
          <div class="flex items-center gap-4">
            <button @click="router.back()" class="p-2 bg-surface-800 hover:bg-surface-700 text-slate-300 rounded-lg transition-colors border border-white/5">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            </button>
            
            <div>
              <h2 class="text-2xl font-bold text-white flex items-center gap-2">
                Breeding Record #{{ pairing.id }}
                <Badge :variant="getStatusVariant(pairing.end_date)" :label="pairing.end_date ? 'Ended' : 'Active'" />
              </h2>
              <div class="text-slate-400 text-sm mt-1 flex items-center gap-4">
                <span class="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                  {{ formatDate(pairing.start_date) }} 
                  <template v-if="pairing.end_date"> - {{ formatDate(pairing.end_date) }}</template>
                </span>
                <span v-if="pairing.cage_number" class="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
                  Cage {{ pairing.cage_number }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="flex gap-3">
            <button v-if="!pairing.end_date" @click="endPairing" class="btn-secondary text-orange-400 hover:text-orange-300">
              End Pairing
            </button>
            <button v-else @click="reactivatePairing" class="btn-secondary text-green-400 hover:text-green-300">
              Reactivate Pairing
            </button>
            <button @click="showAddClutchModal = true" class="btn-primary flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
              Add Clutch
            </button>
          </div>
        </div>
        
        <!-- Parents visualization -->
        <div class="flex justify-center items-center gap-4 md:gap-10 py-6 border-y border-white/10 bg-surface-900/30 rounded-lg">
          <!-- Male -->
          <div class="flex flex-col items-center cursor-pointer hover:opacity-80 transition-opacity" @click="router.push(`/birds/${pairing.bird_a_id}`)">
            <div class="w-20 h-20 md:w-24 md:h-24 rounded-full bg-blue-900/20 border-2 border-blue-500/40 p-1 mb-3">
              <div class="w-full h-full rounded-full overflow-hidden bg-surface-800">
                <img v-if="pairing.bird_a?.photo_url" :src="'/' + pairing.bird_a.photo_url" class="w-full h-full object-contain">
                <span v-else class="flex items-center justify-center w-full h-full text-3xl">🐦</span>
              </div>
            </div>
            <div class="font-bold text-blue-400 flex items-center gap-1">
              {{ pairing.bird_a?.mutation || 'Unknown Mutation' }} <span class="text-xl">♂</span>
            </div>
            <div class="text-sm text-slate-400">{{ pairing.bird_a?.ring_id }}</div>
          </div>
          
          <div class="text-3xl text-white/20 px-2 font-light">×</div>
          
          <!-- Female -->
          <div class="flex flex-col items-center cursor-pointer hover:opacity-80 transition-opacity" @click="router.push(`/birds/${pairing.bird_b_id}`)">
            <div class="w-20 h-20 md:w-24 md:h-24 rounded-full bg-pink-900/20 border-2 border-pink-500/40 p-1 mb-3">
              <div class="w-full h-full rounded-full overflow-hidden bg-surface-800">
                <img v-if="pairing.bird_b?.photo_url" :src="'/' + pairing.bird_b.photo_url" class="w-full h-full object-contain">
                <span v-else class="flex items-center justify-center w-full h-full text-3xl">🐦</span>
              </div>
            </div>
            <div class="font-bold text-pink-400 flex items-center gap-1">
              {{ pairing.bird_b?.mutation || 'Unknown Mutation' }} <span class="text-xl">♀</span>
            </div>
            <div class="text-sm text-slate-400">{{ pairing.bird_b?.ring_id }}</div>
          </div>
        </div>
        
        <div v-if="pairing.notes" class="mt-6 text-slate-300 text-sm bg-surface-900/50 p-4 rounded-lg border border-white/5">
          <span class="text-slate-400 block mb-1 uppercase tracking-wider text-xs">Notes</span>
          {{ pairing.notes }}
        </div>
      </div>
      
      <!-- Stats -->
      <PairStats :pairing="pairing" />
      
      <!-- Clutches Timeline -->
      <div class="mt-8">
        <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" class="text-primary-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
          Clutch Timeline
        </h3>
        
        <div v-if="!pairing.clutches || pairing.clutches.length === 0" class="glass-card py-16 text-center border-dashed">
          <div class="w-16 h-16 bg-surface-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl opacity-50">🥚</span>
          </div>
          <h4 class="text-lg font-medium text-white mb-2">No clutches recorded</h4>
          <p class="text-slate-400 max-w-md mx-auto mb-6">Record the first clutch for this pair when eggs are laid.</p>
          <button @click="showAddClutchModal = true" class="btn-primary">Add First Clutch</button>
        </div>
        
        <div v-else class="space-y-6">
          <div v-for="(clutch, index) in pairing.clutches" :key="clutch.id" class="glass-card overflow-hidden">
            <!-- Clutch Header -->
            <div class="bg-surface-900/50 p-4 md:p-5 border-b border-white/5 flex flex-col sm:flex-row justify-between sm:items-center gap-4">
              <div>
                <h4 class="text-lg font-bold text-white flex items-center gap-2">
                  Clutch #{{ pairing.clutches.length - index }} 
                  <span class="text-sm font-normal text-slate-400 bg-surface-800 px-2 py-0.5 rounded-full border border-white/5">
                    {{ formatDate(clutch.clutch_date) }}
                  </span>
                </h4>
                <div class="flex flex-wrap gap-x-6 gap-y-2 mt-2 text-sm">
                  <div class="flex items-center gap-1 text-slate-300">
                    <span class="text-slate-500">Total Eggs:</span> <span class="font-bold text-white">{{ clutch.total_eggs }}</span>
                  </div>
                  <div v-if="clutch.fertile_eggs > 0" class="flex items-center gap-1 text-slate-300">
                    <span class="text-slate-500">Fertile:</span> <span class="font-bold text-green-400">{{ clutch.fertile_eggs }}</span>
                  </div>
                  <div v-if="clutch.hatched_eggs > 0" class="flex items-center gap-1 text-slate-300">
                    <span class="text-slate-500">Hatched:</span> <span class="font-bold text-emerald-400">{{ clutch.hatched_eggs }}</span>
                  </div>
                  <div v-if="clutch.eggs_lost > 0" class="flex items-center gap-1 text-slate-300">
                    <span class="text-slate-500">Lost:</span> <span class="font-bold text-red-400">{{ clutch.eggs_lost }}</span>
                    <span v-if="clutch.loss_reason" class="text-xs text-red-400/70 ml-1">({{ clutch.loss_reason }})</span>
                  </div>
                </div>
              </div>
              
              <button @click="openEditClutch(clutch)" class="btn-secondary text-sm py-1.5 px-3 whitespace-nowrap">
                Edit Details
              </button>
            </div>
            
            <div v-if="clutch.notes" class="px-5 pt-4 text-sm text-slate-400">
              <span class="text-slate-500 mr-2">Notes:</span>{{ clutch.notes }}
            </div>
            
            <!-- Chicks -->
            <div class="p-4 md:p-5">
              <ChickList 
                :clutchId="clutch.id" 
                :chicks="clutch.chicks || []" 
                @updated="refreshPairing"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <div v-else class="glass-card py-20 text-center">
      <h3 class="text-xl text-white mb-2">Pairing not found</h3>
      <button @click="router.push('/breeding')" class="btn-primary mt-4">Back to List</button>
    </div>

    <!-- Modals -->
    <Modal :show="showAddClutchModal" title="Add New Clutch" @close="showAddClutchModal = false">
      <ClutchForm 
        :pairingId="pairingId"
        @saved="handleAddClutch"
        @cancel="showAddClutchModal = false"
      />
    </Modal>
    
    <Modal :show="showEditClutchModal" title="Edit Clutch" @close="showEditClutchModal = false">
      <ClutchForm 
        v-if="editingClutch"
        :pairingId="pairingId"
        :clutch="editingClutch"
        @saved="handleEditClutch"
        @cancel="showEditClutchModal = false"
      />
    </Modal>
    
  </div>
</template>
