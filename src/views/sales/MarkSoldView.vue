<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import { useSalesStore } from '@/stores/salesStore'
import type { Bird, SaleCreate } from '@/types'

const router = useRouter()
const birdsStore = useBirdsStore()
const salesStore = useSalesStore()

const searchQuery = ref('')
const selectedBird = ref<Bird | null>(null)
const submitting = ref(false)
const submitError = ref<string | null>(null)

const form = ref({
  date_sold: new Date().toISOString().split('T')[0],
  sale_price: 0,
  buyer_name: '',
  notes: ''
})

onMounted(async () => {
  await birdsStore.fetchBirds()
})

const availableBirds = computed(() => {
  let result = birdsStore.birds.filter(b => b.status === 'in_stock')
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(b =>
      (b.ring_id && b.ring_id.toLowerCase().includes(q)) ||
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.mutation && b.mutation.toLowerCase().includes(q))
    )
  }
  
  return result
})

const isFormValid = computed(() => {
  return selectedBird.value && form.value.date_sold && form.value.sale_price > 0
})

const selectBird = (bird: Bird) => {
  selectedBird.value = bird
  searchQuery.value = ''
}

const unselectBird = () => {
  selectedBird.value = null
  searchQuery.value = ''
}

const submitForm = async () => {
  if (!isFormValid.value || submitting.value || !selectedBird.value) return

  try {
    submitting.value = true
    submitError.value = null
    
    const saleData: SaleCreate = {
      bird_id: parseInt(selectedBird.value.id as string),
      date_sold: new Date(form.value.date_sold).toISOString(),
      sale_price: form.value.sale_price,
      buyer_name: form.value.buyer_name || undefined,
      notes: form.value.notes || undefined
    }

    await salesStore.createSale(saleData)
    router.push('/sales')
  } catch (e: any) {
    submitError.value = e.message || 'Failed to record sale'
    console.error('Error creating sale:', e)
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}
</script>

<template>
  <div class="space-y-6 animate-fade-in max-w-4xl mx-auto">
    <!-- Header Area -->
    <div class="flex items-center gap-4 mb-6">
      <button @click="router.back()" class="p-2 bg-surface-800 hover:bg-surface-700 text-slate-300 rounded-lg transition-colors border border-white/5">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <div>
        <h2 class="text-2xl font-bold text-white">Mark Bird as Sold</h2>
        <p class="text-slate-400 text-sm mt-0.5">Select a bird from your stock and record the sale details</p>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="submitError" class="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 flex items-center gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-400 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
      <span class="text-red-300 text-sm">{{ submitError }}</span>
      <button @click="submitError = null" class="ml-auto text-red-400 hover:text-red-300 p-1">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      
      <!-- Bird Selection -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-medium text-white mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          Select Bird to Sell
        </h3>
        
        <div v-if="!selectedBird">
          <div class="relative mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Search birds by ring ID, name, or mutation..." 
              class="input-field pl-9"
            >
          </div>
          
          <div class="max-h-72 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            <div v-if="birdsStore.loading" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
            
            <div v-else-if="availableBirds.length === 0" class="text-center py-8">
              <div class="w-16 h-16 bg-surface-800 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl opacity-50">🐦</span>
              </div>
              <p class="text-slate-400 text-sm">No birds available in stock</p>
            </div>
            
            <div 
              v-for="bird in availableBirds" 
              :key="bird.id"
              @click="selectBird(bird)"
              class="flex items-center gap-4 p-3 rounded-lg bg-surface-800 border border-white/5 hover:border-emerald-500/30 cursor-pointer transition-all hover:bg-surface-700/80 group"
            >
              <div class="w-12 h-12 rounded-lg bg-surface-700 overflow-hidden shrink-0 border border-white/5 group-hover:border-emerald-500/20">
                <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-full object-cover">
                <span v-else class="flex items-center justify-center w-full h-full text-lg">🐦</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-medium text-white flex items-center gap-2">
                  {{ bird.name || 'Unnamed' }}
                  <span v-if="bird.sex === 'male'" class="text-blue-400 text-lg">♂</span>
                  <span v-else-if="bird.sex === 'female'" class="text-pink-400 text-lg">♀</span>
                </div>
                <div class="text-xs text-slate-400 flex items-center gap-2">
                  <span>{{ bird.ring_id || 'No ring ID' }}</span>
                  <span v-if="bird.mutation" class="text-slate-500">•</span>
                  <span v-if="bird.mutation">{{ bird.mutation }}</span>
                </div>
              </div>
              <div class="text-xs text-slate-500 shrink-0">
                {{ bird.cage_number ? `Cage ${bird.cage_number}` : '' }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Selected bird display -->
        <div v-else class="flex items-start gap-4 p-4 rounded-xl bg-emerald-900/10 border border-emerald-500/20 relative animate-fade-in">
          <button @click.prevent="unselectBird" class="absolute top-3 right-3 text-slate-400 hover:text-white p-1 rounded-md hover:bg-white/10 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
          <div class="w-20 h-20 rounded-xl bg-surface-800 overflow-hidden shrink-0 border border-emerald-500/30">
            <img v-if="selectedBird.photo_url" :src="'/' + selectedBird.photo_url" class="w-full h-full object-cover">
            <span v-else class="flex items-center justify-center w-full h-full text-3xl">🐦</span>
          </div>
          <div>
            <div class="font-bold text-white text-lg flex items-center gap-2">
              {{ selectedBird.name || 'Unnamed' }}
              <span v-if="selectedBird.sex === 'male'" class="text-blue-400 text-xl">♂</span>
              <span v-else-if="selectedBird.sex === 'female'" class="text-pink-400 text-xl">♀</span>
            </div>
            <div class="text-sm text-slate-300 mt-0.5">{{ selectedBird.ring_id || 'No ring ID' }}</div>
            <div class="text-sm text-emerald-300 mt-1">{{ selectedBird.mutation || 'No mutation' }}</div>
            <div v-if="selectedBird.cage_number" class="text-xs text-slate-400 mt-1">Cage {{ selectedBird.cage_number }}</div>
          </div>
        </div>
      </div>
      
      <!-- Sale Details -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-medium text-white mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-400"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          Sale Details
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="label">Sale Date *</label>
            <input v-model="form.date_sold" type="date" class="input-field" required>
          </div>
          
          <div class="space-y-2">
            <label class="label">Sale Price *</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
              <input 
                v-model.number="form.sale_price" 
                type="number" 
                step="0.01" 
                min="0" 
                class="input-field pl-7" 
                placeholder="0.00"
                required
              >
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="label">Buyer Name</label>
            <input v-model="form.buyer_name" type="text" class="input-field" placeholder="Enter buyer's name">
          </div>
          
          <div class="space-y-2 md:col-span-2">
            <label class="label">Notes</label>
            <textarea v-model="form.notes" rows="3" class="input-field resize-none" placeholder="Any additional details about the sale..."></textarea>
          </div>
        </div>
      </div>
      
      <!-- Summary card (shows when bird is selected) -->
      <div v-if="selectedBird && form.sale_price > 0" class="glass-card p-4 border-emerald-500/20 animate-fade-in">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-400"><path d="M20 6 9 17l-5-5"/></svg>
            </div>
            <div>
              <div class="text-sm text-slate-400">Selling <span class="text-white font-medium">{{ selectedBird.name || selectedBird.ring_id || 'Unnamed' }}</span></div>
              <div class="text-xs text-slate-500">{{ form.buyer_name ? `To ${form.buyer_name}` : 'Buyer not specified' }} • {{ formatDate(form.date_sold) }}</div>
            </div>
          </div>
          <div class="text-2xl font-bold text-emerald-400">
            {{ formatCurrency(form.sale_price) }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4 border-t border-white/10">
        <button type="button" @click="router.back()" class="btn-secondary">Cancel</button>
        <button 
          type="submit" 
          class="btn-primary flex items-center gap-2" 
          :disabled="!isFormValid || submitting"
          :class="{'opacity-50 cursor-not-allowed': !isFormValid || submitting}"
        >
          <span v-if="submitting" class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full border-2 border-white/20 border-t-white animate-spin"></div>
            Recording Sale...
          </span>
          <span v-else class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            Confirm Sale
          </span>
        </button>
      </div>
      
    </form>
  </div>
</template>


<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
