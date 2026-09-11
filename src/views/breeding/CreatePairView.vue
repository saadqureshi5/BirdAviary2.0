<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBreedingStore } from '@/stores/breedingStore'
import { useBirdsStore } from '@/stores/birdsStore'
import type { Bird } from '@/types'

const router = useRouter()
const breedingStore = useBreedingStore()
const birdsStore = useBirdsStore()

const maleSearch = ref('')
const femaleSearch = ref('')
const selectedMale = ref<Bird | null>(null)
const selectedFemale = ref<Bird | null>(null)

const form = ref({
  start_date: new Date().toISOString().split('T')[0],
  cage_number: '',
  notes: ''
})

const submitting = ref(false)

onMounted(async () => {
  await birdsStore.fetchBirds()
})

const availableMales = computed(() => {
  return birdsStore.inStockBirds
    .filter(b => b.sex === 'male')
    .filter(b => {
      if (!maleSearch.value) return true
      const q = maleSearch.value.toLowerCase()
      return b.ring_id.toLowerCase().includes(q) || 
             (b.name && b.name.toLowerCase().includes(q))
    })
})

const availableFemales = computed(() => {
  return birdsStore.inStockBirds
    .filter(b => b.sex === 'female')
    .filter(b => {
      if (!femaleSearch.value) return true
      const q = femaleSearch.value.toLowerCase()
      return b.ring_id.toLowerCase().includes(q) || 
             (b.name && b.name.toLowerCase().includes(q))
    })
})

const isFormValid = computed(() => {
  return selectedMale.value && selectedFemale.value && form.value.start_date
})

const submitForm = async () => {
  if (!isFormValid.value || submitting.value) return
  
  try {
    submitting.value = true
    const pair = await breedingStore.createPairing({
      bird_a_id: parseInt(selectedMale.value!.id),
      bird_b_id: parseInt(selectedFemale.value!.id),
      start_date: new Date(form.value.start_date).toISOString(),
      cage_number: form.value.cage_number || undefined,
      notes: form.value.notes || undefined
    })
    
    if (pair) {
      router.push(`/breeding/${pair.id}`)
    }
  } catch (e) {
    console.error('Error creating pair:', e)
  } finally {
    submitting.value = false
  }
}

const unselectMale = () => {
  selectedMale.value = null
  maleSearch.value = ''
}

const unselectFemale = () => {
  selectedFemale.value = null
  femaleSearch.value = ''
}
</script>

<template>
  <div class="space-y-6 animate-fade-in max-w-4xl mx-auto">
    <!-- Header Area -->
    <div class="flex items-center gap-4 mb-6">
      <button @click="router.back()" class="p-2 bg-surface-800 hover:bg-surface-700 text-slate-300 rounded-lg transition-colors border border-white/5">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="text-2xl font-bold text-white">Create Breeding Pair</h2>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      
      <!-- Bird Selection Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Male Selector -->
        <div class="glass-card p-6">
          <h3 class="text-lg font-medium text-blue-400 mb-4 flex items-center gap-2">
            <span class="text-2xl">♂</span> Select Male
          </h3>
          
          <div v-if="!selectedMale">
            <div class="relative mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              <input 
                v-model="maleSearch"
                type="text" 
                placeholder="Search males by ring or name..." 
                class="input-field pl-9"
              >
            </div>
            
            <div class="max-h-60 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
              <div v-if="availableMales.length === 0" class="text-slate-400 text-sm py-4 text-center">
                No males found
              </div>
              <div 
                v-for="bird in availableMales" 
                :key="bird.id"
                @click="selectedMale = bird"
                class="flex items-center gap-3 p-3 rounded-lg bg-surface-800 border border-white/5 hover:border-primary-500/30 cursor-pointer transition-colors"
              >
                <div class="w-10 h-10 rounded bg-surface-700 overflow-hidden shrink-0">
                  <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-full object-cover">
                  <span v-else class="flex items-center justify-center w-full h-full text-xs">🐦</span>
                </div>
                <div>
                  <div class="font-medium text-white">{{ bird.name || 'Unnamed' }}</div>
                  <div class="text-xs text-slate-400">{{ bird.ring_id }} • {{ bird.mutation || 'No mutation' }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="flex items-start gap-4 p-4 rounded-xl bg-blue-900/10 border border-blue-500/20 relative">
            <button @click.prevent="unselectMale" class="absolute top-2 right-2 text-slate-400 hover:text-white p-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
            <div class="w-16 h-16 rounded-lg bg-surface-800 overflow-hidden shrink-0 border border-blue-500/30">
              <img v-if="selectedMale.photo_url" :src="'/' + selectedMale.photo_url" class="w-full h-full object-cover">
              <span v-else class="flex items-center justify-center w-full h-full text-2xl">🐦</span>
            </div>
            <div>
              <div class="font-bold text-white text-lg">{{ selectedMale.name || 'Unnamed' }}</div>
              <div class="text-sm text-slate-300">{{ selectedMale.ring_id }}</div>
              <div class="text-sm text-blue-300 mt-1">{{ selectedMale.mutation || 'No mutation' }}</div>
            </div>
          </div>
        </div>
        
        <!-- Female Selector -->
        <div class="glass-card p-6">
          <h3 class="text-lg font-medium text-pink-400 mb-4 flex items-center gap-2">
            <span class="text-2xl">♀</span> Select Female
          </h3>
          
          <div v-if="!selectedFemale">
            <div class="relative mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              <input 
                v-model="femaleSearch"
                type="text" 
                placeholder="Search females by ring or name..." 
                class="input-field pl-9"
              >
            </div>
            
            <div class="max-h-60 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
              <div v-if="availableFemales.length === 0" class="text-slate-400 text-sm py-4 text-center">
                No females found
              </div>
              <div 
                v-for="bird in availableFemales" 
                :key="bird.id"
                @click="selectedFemale = bird"
                class="flex items-center gap-3 p-3 rounded-lg bg-surface-800 border border-white/5 hover:border-pink-500/30 cursor-pointer transition-colors"
              >
                <div class="w-10 h-10 rounded bg-surface-700 overflow-hidden shrink-0">
                  <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-full object-cover">
                  <span v-else class="flex items-center justify-center w-full h-full text-xs">🐦</span>
                </div>
                <div>
                  <div class="font-medium text-white">{{ bird.name || 'Unnamed' }}</div>
                  <div class="text-xs text-slate-400">{{ bird.ring_id }} • {{ bird.mutation || 'No mutation' }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="flex items-start gap-4 p-4 rounded-xl bg-pink-900/10 border border-pink-500/20 relative">
            <button @click.prevent="unselectFemale" class="absolute top-2 right-2 text-slate-400 hover:text-white p-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
            <div class="w-16 h-16 rounded-lg bg-surface-800 overflow-hidden shrink-0 border border-pink-500/30">
              <img v-if="selectedFemale.photo_url" :src="'/' + selectedFemale.photo_url" class="w-full h-full object-cover">
              <span v-else class="flex items-center justify-center w-full h-full text-2xl">🐦</span>
            </div>
            <div>
              <div class="font-bold text-white text-lg">{{ selectedFemale.name || 'Unnamed' }}</div>
              <div class="text-sm text-slate-300">{{ selectedFemale.ring_id }}</div>
              <div class="text-sm text-pink-300 mt-1">{{ selectedFemale.mutation || 'No mutation' }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Pairing Details -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-medium text-white mb-4">Pairing Details</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="label">Start Date *</label>
            <input v-model="form.start_date" type="date" class="input-field" required>
          </div>
          
          <div class="space-y-2">
            <label class="label">Cage Number</label>
            <input v-model="form.cage_number" type="text" class="input-field" placeholder="e.g. C-12">
          </div>
          
          <div class="space-y-2 md:col-span-2">
            <label class="label">Notes</label>
            <textarea v-model="form.notes" rows="3" class="input-field resize-none" placeholder="Add any notes about this pairing..."></textarea>
          </div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4 border-t border-white/10">
        <button type="button" @click="router.back()" class="btn-secondary">Cancel</button>
        <button 
          type="submit" 
          class="btn-primary" 
          :disabled="!isFormValid || submitting"
          :class="{'opacity-50 cursor-not-allowed': !isFormValid || submitting}"
        >
          <span v-if="submitting" class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full border-2 border-white/20 border-t-white animate-spin"></div>
            Creating...
          </span>
          <span v-else>Create Pair</span>
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
