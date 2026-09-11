<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBreedingStore } from '@/stores/breedingStore'
import type { Chick, ChickCreate } from '@/types'
import Badge from '@/components/shared/Badge.vue'
import Modal from '@/components/shared/Modal.vue'

const props = defineProps<{
  clutchId: number
  chicks: Chick[]
}>()

const emit = defineEmits<{
  (e: 'updated'): void
}>()

const router = useRouter()
const breedingStore = useBreedingStore()

const showAddModal = ref(false)
const showDeceasedModal = ref(false)
const submitting = ref(false)
const selectedChick = ref<Chick | null>(null)
const isEditing = ref(false)
const mortalityReason = ref('')

const chickForm = ref<ChickCreate>({
  ring_id: '',
  mutation: '',
  sex: 'unknown',
  hatch_date: new Date().toISOString().split('T')[0]
})

const resetForm = () => {
  chickForm.value = {
    ring_id: '',
    mutation: '',
    sex: 'unknown',
    hatch_date: new Date().toISOString().split('T')[0]
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showAddModal.value = true
}

const openEditModal = (chick: Chick) => {
  selectedChick.value = chick
  isEditing.value = true
  chickForm.value = {
    ring_id: chick.ring_id || '',
    mutation: chick.mutation || '',
    sex: chick.sex || 'unknown',
    hatch_date: chick.hatch_date ? (chick.hatch_date as string).split('T')[0] : ''
  }
  showAddModal.value = true
}

const saveChick = async () => {
  try {
    submitting.value = true
    const payload = {
      clutch_id: props.clutchId,
      ring_id: chickForm.value.ring_id || undefined,
      mutation: chickForm.value.mutation || undefined,
      sex: chickForm.value.sex,
      hatch_date: chickForm.value.hatch_date || undefined
    }
    
    if (isEditing.value && selectedChick.value) {
      await breedingStore.updateChick(selectedChick.value.id, payload)
    } else {
      await breedingStore.createChick(props.clutchId, payload)
    }
    
    showAddModal.value = false
    resetForm()
    emit('updated')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const markFledged = async (chick: Chick) => {
  try {
    await breedingStore.updateChick(chick.id, { 
      status: 'fledged',
      fledge_date: new Date().toISOString().split('T')[0]
    })
    emit('updated')
  } catch (e) {
    console.error(e)
  }
}

const promoteChick = async (chick: Chick) => {
  if (!chick.ring_id) {
    if (!confirm("This bird doesn't have a Ring ID yet. Please ring the bird before promoting it to the flock.\n\nDo you want to promote without a ring anyway?")) {
      return
    }
  }

  try {
    await breedingStore.promoteChick(chick.id)
    emit('updated')
  } catch (e) {
    console.error(e)
  }
}

const openDeceasedModal = (chick: Chick) => {
  selectedChick.value = chick
  mortalityReason.value = chick.status === 'deceased' ? (chick.mortality_reason || '') : ''
  showDeceasedModal.value = true
}

const markDeceased = async () => {
  if (!selectedChick.value) return
  
  try {
    submitting.value = true
    await breedingStore.updateChick(selectedChick.value.id, { 
      status: 'deceased',
      mortality_reason: mortalityReason.value
    })
    showDeceasedModal.value = false
    selectedChick.value = null
    emit('updated')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const removeDeceasedStatus = async () => {
  if (!selectedChick.value) return
  
  try {
    submitting.value = true
    const newStatus = selectedChick.value.fledge_date ? 'fledged' : 'hatched'
    await breedingStore.updateChick(selectedChick.value.id, { 
      status: newStatus,
      mortality_reason: null
    })
    showDeceasedModal.value = false
    selectedChick.value = null
    emit('updated')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'info' | 'neutral' => {
  switch (status) {
    case 'hatched': return 'info'
    case 'fledged': return 'success'
    case 'added_to_stock': return 'success'
    case 'deceased': return 'danger'
    default: return 'neutral'
  }
}

const getSexIcon = (sex: string) => {
  switch (sex) {
    case 'male': return { text: '♂', color: 'text-blue-400' }
    case 'female': return { text: '♀', color: 'text-pink-400' }
    default: return { text: '?', color: 'text-slate-400' }
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Action Bar -->
    <div class="flex justify-between items-center">
      <h4 class="text-sm font-medium text-slate-300 uppercase tracking-wider">Chicks ({{ chicks.length }})</h4>
      <button @click="openAddModal" class="btn-ghost text-primary-400 hover:text-primary-300 flex items-center gap-1 text-sm py-1 px-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Add Chick
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="chicks.length === 0" class="text-center py-6 border border-dashed border-white/10 rounded-lg">
      <p class="text-slate-500 text-sm">No chicks recorded yet.</p>
    </div>

    <!-- Chicks List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="chick in chicks" 
        :key="chick.id"
        class="bg-surface-900 border border-white/5 rounded-lg p-4 flex flex-col transition-all hover:border-white/10"
        :class="{'opacity-75': chick.status === 'deceased'}"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl font-bold" :class="getSexIcon(chick.sex).color">{{ getSexIcon(chick.sex).text }}</span>
            <span class="font-medium text-white">{{ chick.ring_id || 'Unringed' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button v-if="chick.status !== 'deceased'" @click="openEditModal(chick)" class="text-slate-400 hover:text-white bg-surface-800 hover:bg-surface-700 p-1 rounded-md transition-colors border border-white/5" title="Edit Chick">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
            </button>
            <button v-else @click="openDeceasedModal(chick)" class="text-slate-400 hover:text-white bg-surface-800 hover:bg-surface-700 p-1 rounded-md transition-colors border border-white/5" title="Edit Deceased Info">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
            </button>
            <Badge :variant="getStatusVariant(chick.status)" :label="chick.status.replace(/_/g, ' ')" />
          </div>
        </div>
        
        <div class="text-sm text-slate-400 mb-4 flex-grow">
          <div>Mutation: <span class="text-slate-300">{{ chick.mutation || 'Unknown' }}</span></div>
          <div v-if="chick.hatch_date">Hatched: <span class="text-slate-300">{{ new Date(chick.hatch_date).toLocaleDateString() }}</span></div>
          <div v-if="chick.status === 'deceased' && chick.mortality_reason" class="text-red-400 mt-1">
            Reason: {{ chick.mortality_reason }}
          </div>
        </div>
        
        <!-- Action Buttons based on status -->
        <div class="flex gap-2 pt-3 border-t border-white/5 mt-auto">
          <template v-if="chick.status === 'hatched'">
            <button @click="markFledged(chick)" class="btn-primary flex-1 py-1.5 text-xs">Mark Fledged</button>
            <button @click="openDeceasedModal(chick)" class="btn-secondary text-red-400 hover:text-red-300 hover:bg-red-900/20 py-1.5 px-3 text-xs">Deceased</button>
          </template>
          
          <template v-else-if="chick.status === 'fledged'">
            <button @click="promoteChick(chick)" class="bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded px-3 py-1.5 text-xs font-medium flex-1 transition-colors border border-green-500/30">
              Promote to Stock
            </button>
            <button @click="openDeceasedModal(chick)" class="btn-secondary text-red-400 hover:text-red-300 hover:bg-red-900/20 py-1.5 px-3 text-xs">Deceased</button>
          </template>
          
          <template v-else-if="chick.status === 'added_to_stock' && chick.promoted_bird_id">
            <button @click="router.push(`/birds/${chick.promoted_bird_id}`)" class="btn-secondary flex-1 py-1.5 text-xs flex items-center justify-center gap-1">
              View Bird Profile
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Add/Edit Chick Modal -->
    <Modal :show="showAddModal" :title="isEditing ? 'Edit Chick' : 'Record New Chick'" @close="showAddModal = false">
      <form @submit.prevent="saveChick" class="space-y-4">
        <div class="space-y-2">
          <label class="label">Ring ID (if ringed)</label>
          <input v-model="chickForm.ring_id" type="text" class="input-field" placeholder="e.g. 2026-001">
        </div>
        
        <div class="space-y-2">
          <label class="label">Mutation</label>
          <input v-model="chickForm.mutation" type="text" class="input-field" placeholder="e.g. Lutino, Normal">
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="label">Sex</label>
            <select v-model="chickForm.sex" class="input-field">
              <option value="unknown">Unknown</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          
          <div class="space-y-2">
            <label class="label">Hatch Date</label>
            <input v-model="chickForm.hatch_date" type="date" class="input-field">
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-4 border-t border-white/10 mt-6">
          <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            {{ submitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Add Chick') }}
          </button>
        </div>
      </form>
    </Modal>
    
    <!-- Deceased Modal -->
    <Modal :show="showDeceasedModal" :title="selectedChick?.status === 'deceased' ? 'Edit Deceased Info' : 'Mark Chick Deceased'" @close="showDeceasedModal = false">
      <form @submit.prevent="markDeceased" class="space-y-4">
        <p v-if="selectedChick?.status !== 'deceased'" class="text-slate-300 text-sm">
          You are marking chick <strong class="text-white">{{ selectedChick?.ring_id || 'Unringed' }}</strong> as deceased.
        </p>
        
        <div class="space-y-2 mt-4">
          <label class="label">Reason (Optional)</label>
          <input v-model="mortalityReason" type="text" class="input-field" placeholder="e.g. Unknown, Weak">
        </div>
        
        <div class="flex justify-between gap-3 pt-4 border-t border-white/10 mt-6">
          <div>
            <button v-if="selectedChick?.status === 'deceased'" type="button" @click="removeDeceasedStatus" class="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10 px-3 py-2 text-sm font-medium transition-colors" :disabled="submitting">
              Remove Deceased Status
            </button>
          </div>
          <div class="flex gap-3">
            <button type="button" @click="showDeceasedModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors" :disabled="submitting">
              {{ selectedChick?.status === 'deceased' ? 'Save Changes' : 'Confirm' }}
            </button>
          </div>
        </div>
      </form>
    </Modal>
  </div>
</template>
