<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ClutchDetail } from '@/types'

const props = defineProps<{
  pairingId: number
  clutch?: ClutchDetail
}>()

const emit = defineEmits<{
  (e: 'saved', data: any): void
  (e: 'cancel'): void
}>()

const form = ref({
  clutch_date: new Date().toISOString().split('T')[0],
  total_eggs: 0,
  fertile_eggs: 0,
  hatched_eggs: 0,
  eggs_lost: 0,
  loss_reason: '',
  notes: ''
})

onMounted(() => {
  if (props.clutch) {
    form.value = {
      clutch_date: props.clutch.clutch_date ? props.clutch.clutch_date.split('T')[0] : new Date().toISOString().split('T')[0],
      total_eggs: props.clutch.total_eggs,
      fertile_eggs: props.clutch.fertile_eggs || 0,
      hatched_eggs: props.clutch.hatched_eggs || 0,
      eggs_lost: props.clutch.eggs_lost || 0,
      loss_reason: props.clutch.loss_reason || '',
      notes: props.clutch.notes || ''
    }
  }
})

const submit = () => {
  const payload: any = {
    pairing_id: props.pairingId,
    clutch_date: form.value.clutch_date,
    total_eggs: form.value.total_eggs,
    fertile_eggs: form.value.fertile_eggs,
    hatched_eggs: form.value.hatched_eggs,
    eggs_lost: form.value.eggs_lost,
    notes: form.value.notes
  }
  
  if (form.value.eggs_lost > 0) {
    payload.loss_reason = form.value.loss_reason
  }

  emit('saved', payload)
}
</script>

<template>
  <form @submit.prevent="submit" class="space-y-4">
    <div class="space-y-2">
      <label class="label">Clutch Date *</label>
      <input v-model="form.clutch_date" type="date" class="input-field" required>
    </div>
    
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="space-y-2">
        <label class="label">Total Eggs *</label>
        <input v-model.number="form.total_eggs" type="number" min="1" class="input-field" required>
      </div>
      <div class="space-y-2">
        <label class="label">Fertile</label>
        <input v-model.number="form.fertile_eggs" type="number" min="0" :max="form.total_eggs" class="input-field">
      </div>
      <div class="space-y-2">
        <label class="label">Hatched</label>
        <input v-model.number="form.hatched_eggs" type="number" min="0" :max="form.total_eggs" class="input-field">
      </div>
      <div class="space-y-2">
        <label class="label">Lost</label>
        <input v-model.number="form.eggs_lost" type="number" min="0" :max="form.total_eggs" class="input-field">
      </div>
    </div>
    
    <div v-if="form.eggs_lost > 0" class="space-y-2 animate-slide-up">
      <label class="label">Reason for Egg Loss</label>
      <input v-model="form.loss_reason" type="text" class="input-field" placeholder="e.g. Broken, Infertile, DIS">
    </div>
    
    <div class="space-y-2">
      <label class="label">Notes</label>
      <textarea v-model="form.notes" rows="2" class="input-field resize-none"></textarea>
    </div>
    
    <div class="flex justify-end gap-3 pt-4 border-t border-white/10 mt-6">
      <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
      <button type="submit" class="btn-primary">{{ props.clutch ? 'Save Changes' : 'Add Clutch' }}</button>
    </div>
  </form>
</template>
