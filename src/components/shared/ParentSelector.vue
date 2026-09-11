<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Bird } from '@/types'

const props = defineProps<{
  label: string
  sex: 'male' | 'female'
  birds: Bird[]
  categoryId?: string | number | null
  modelValue?: string | number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string | number | null): void
  (e: 'manualParent', data: { ring_id: string; name: string; mutation: string; sex: string }): void
}>()

const mode = ref<'aviary' | 'manual'>('aviary')
const searchQuery = ref('')
const isDropdownOpen = ref(false)

// Manual entry fields
const manualRingId = ref('')
const manualName = ref('')
const manualMutation = ref('')

// Filter birds by category and sex
const filteredBirds = computed(() => {
  let list = props.birds.filter(b => b.sex === props.sex)
  
  // Filter by category if set
  if (props.categoryId) {
    list = list.filter(b => String(b.category_id) === String(props.categoryId))
  }
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(b => 
      (b.ring_id && b.ring_id.toLowerCase().includes(q)) ||
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.mutation && b.mutation.toLowerCase().includes(q))
    )
  }
  
  return list
})

// Selected bird display
const selectedBird = computed(() => {
  if (!props.modelValue) return null
  return props.birds.find(b => String(b.id) === String(props.modelValue))
})

const selectedDisplay = computed(() => {
  if (!selectedBird.value) return ''
  const b = selectedBird.value
  let display = b.ring_id || ''
  if (b.mutation) display += ` — ${b.mutation}`
  if (b.name) display += ` (${b.name})`
  return display
})

const selectBird = (bird: Bird) => {
  emit('update:modelValue', bird.id)
  searchQuery.value = ''
  isDropdownOpen.value = false
}

const clearSelection = () => {
  emit('update:modelValue', null)
  searchQuery.value = ''
}

const switchToManual = () => {
  mode.value = 'manual'
  emit('update:modelValue', null)
  searchQuery.value = ''
  isDropdownOpen.value = false
}

const switchToAviary = () => {
  mode.value = 'aviary'
  manualRingId.value = ''
  manualName.value = ''
  manualMutation.value = ''
}

// Emit manual parent data whenever it changes
watch([manualRingId, manualName, manualMutation], () => {
  if (mode.value === 'manual' && manualRingId.value.trim()) {
    emit('manualParent', {
      ring_id: manualRingId.value,
      name: manualName.value,
      mutation: manualMutation.value,
      sex: props.sex,
    })
  }
})

// Close dropdown when clicking outside
const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest('.parent-selector-dropdown')) {
    isDropdownOpen.value = false
  }
}

// Attach listener
import { onMounted, onUnmounted } from 'vue'
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <label class="label flex items-center gap-1 mb-0">
        <span :class="sex === 'male' ? 'text-blue-400' : 'text-pink-400'">
          {{ sex === 'male' ? '♂' : '♀' }}
        </span>
        {{ label }}
      </label>
      <button 
        type="button"
        @click="mode === 'aviary' ? switchToManual() : switchToAviary()"
        class="text-xs text-primary-400 hover:text-primary-300 transition-colors"
      >
        {{ mode === 'aviary' ? 'Enter manually' : 'Select from aviary' }}
      </button>
    </div>

    <!-- Aviary Mode: Searchable select -->
    <template v-if="mode === 'aviary'">
      <!-- Selected bird display -->
      <div v-if="selectedBird" class="flex items-center justify-between p-3 rounded-xl bg-surface-800/50 border border-white/10">
        <div class="flex items-center gap-3">
          <div 
            class="w-8 h-8 rounded-md flex items-center justify-center text-sm"
            :class="sex === 'male' ? 'bg-blue-900/30 border border-blue-500/20 text-blue-400' : 'bg-pink-900/30 border border-pink-500/20 text-pink-400'"
          >
            {{ sex === 'male' ? '♂' : '♀' }}
          </div>
          <div>
            <div class="text-sm font-medium text-white">{{ selectedBird.ring_id }}</div>
            <div class="text-xs text-slate-400">
              {{ selectedBird.mutation || '' }}{{ selectedBird.name ? (selectedBird.mutation ? ' · ' : '') + selectedBird.name : '' }}
            </div>
          </div>
        </div>
        <button type="button" @click="clearSelection" class="text-slate-400 hover:text-red-400 transition-colors p-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <!-- Search input + dropdown -->
      <div v-else class="relative parent-selector-dropdown">
        <div class="relative">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input 
            v-model="searchQuery"
            type="text"
            class="input-field pl-10"
            :placeholder="`Search ${sex === 'male' ? 'sires' : 'dams'} by ring ID, name, or mutation...`"
            @focus="isDropdownOpen = true"
          >
        </div>

        <!-- Dropdown list -->
        <div 
          v-if="isDropdownOpen"
          class="absolute z-50 w-full mt-1 max-h-48 overflow-y-auto rounded-xl border border-white/10 bg-surface-800 shadow-xl backdrop-blur-sm"
        >
          <div v-if="filteredBirds.length === 0" class="p-3 text-sm text-slate-400 text-center">
            No {{ sex === 'male' ? 'males' : 'females' }} found{{ categoryId ? ' in this category' : '' }}
          </div>
          <button
            v-for="bird in filteredBirds"
            :key="bird.id"
            type="button"
            @click="selectBird(bird)"
            class="w-full flex items-center gap-3 p-3 hover:bg-surface-700 transition-colors text-left border-b border-white/5 last:border-0"
          >
            <div 
              class="w-7 h-7 rounded-md flex items-center justify-center text-xs shrink-0"
              :class="sex === 'male' ? 'bg-blue-900/30 border border-blue-500/20 text-blue-400' : 'bg-pink-900/30 border border-pink-500/20 text-pink-400'"
            >
              {{ sex === 'male' ? '♂' : '♀' }}
            </div>
            <div class="min-w-0">
              <div class="text-sm font-medium text-white truncate">{{ bird.ring_id }}</div>
              <div class="text-xs text-slate-400 truncate">
                {{ bird.mutation || 'No mutation' }}{{ bird.name ? ' · ' + bird.name : '' }}
              </div>
            </div>
          </button>
        </div>
      </div>
    </template>

    <!-- Manual Mode: Text inputs -->
    <template v-else>
      <div class="space-y-3 p-4 rounded-xl border border-dashed border-white/10 bg-surface-800/30">
        <div class="flex items-center gap-2 mb-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-400"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M3.6 15 12 3l8.4 12z"/></svg>
          <span class="text-xs text-amber-400">External parent (not in your aviary)</span>
        </div>
        <div class="text-[11px] text-slate-400 mb-2 mt-[-4px]">
          Enter manually information of bird which you have buy from outside. If its parents are present in the aviary choose it from the search bar.
        </div>
        <div>
          <label class="text-xs text-slate-400 mb-1 block">Ring ID</label>
          <input 
            v-model="manualRingId"
            type="text"
            class="input-field text-sm"
            placeholder="e.g. EXT-001"
          >
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Name</label>
            <input 
              v-model="manualName"
              type="text"
              class="input-field text-sm"
              placeholder="e.g. Apollo"
            >
          </div>
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Mutation</label>
            <input 
              v-model="manualMutation"
              type="text"
              class="input-field text-sm"
              placeholder="e.g. Normal Green"
            >
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
