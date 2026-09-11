<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSearch } from '@/composables/useSearch'
import SearchInput from '@/components/shared/SearchInput.vue'
import Badge from '@/components/shared/Badge.vue'

const router = useRouter()
const query = ref('')
const { results, loading } = useSearch(query)

const isOpen = ref(false)
const searchContainer = ref<HTMLElement | null>(null)

const handleInput = () => {
  isOpen.value = true
}

const selectResult = (id: string) => {
  router.push(`/birds/${id}`)
  isOpen.value = false
  query.value = ''
}

// Close when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (searchContainer.value && !searchContainer.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="searchContainer" class="relative w-full z-50">
    <SearchInput 
      v-model="query" 
      placeholder="Search birds by ring ID, name, mutation..." 
      :loading="loading"
      @input="handleInput"
      @focus="isOpen = true"
    />
    
    <!-- Results Dropdown -->
    <transition name="slide-up">
      <div 
        v-if="isOpen && query.length > 0" 
        class="absolute top-full left-0 right-0 mt-2 glass-card max-h-[400px] overflow-y-auto shadow-2xl py-2 divide-y divide-white/5 border border-white/10"
      >
        <div v-if="loading" class="p-4 text-center text-slate-400">
          Searching...
        </div>
        
        <div v-else-if="results.length === 0" class="p-4 text-center text-slate-400">
          No birds found for "{{ query }}"
        </div>
        
        <div 
          v-else 
          v-for="bird in results" 
          :key="bird.id"
          @click="selectResult(bird.id)"
          class="p-3 hover:bg-white/5 cursor-pointer flex items-center gap-4 transition-colors"
        >
          <div class="w-12 h-12 rounded-lg bg-surface-700 overflow-hidden shrink-0">
            <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-xl">🐦</div>
          </div>
          
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <h4 class="font-medium text-white truncate">{{ bird.ring_id }}</h4>
              <Badge 
                :variant="bird.status === 'in_stock' ? 'success' : bird.status === 'sold' ? 'warning' : 'danger'" 
                :label="bird.status.replace('_', ' ')" 
              />
            </div>
            <div class="text-sm text-slate-400 truncate mt-0.5">
              {{ bird.name ? `${bird.name} • ` : '' }}{{ bird.mutation }}
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
