<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSoftFoodStore } from '@/stores/softFoodStore'
import { storeToRefs } from 'pinia'
import Modal from '@/components/shared/Modal.vue'
import StatCard from '@/components/shared/StatCard.vue'
import Badge from '@/components/shared/Badge.vue'
import type { SoftFoodLogCreate } from '@/types'

const softFoodStore = useSoftFoodStore()
const { softFoodLogs, loading } = storeToRefs(softFoodStore)

// Filters
const selectedYear = ref<number | 'all'>('all')
const selectedSeason = ref<string>('all')

const currentYear = new Date().getFullYear()
const availableYears = computed(() => {
  const years = new Set(softFoodLogs.value.map(log => log.year))
  years.add(currentYear)
  return Array.from(years).sort((a, b) => b - a)
})

const seasons = ['all', 'spring', 'summer', 'autumn', 'winter']

const fetchLogs = () => {
  const year = selectedYear.value === 'all' ? undefined : selectedYear.value
  const season = selectedSeason.value === 'all' ? undefined : selectedSeason.value
  softFoodStore.fetchLogs(year, season)
}

// Computed Stats
const totalRecipes = computed(() => softFoodLogs.value.length)
const thisYearRecipes = computed(() => softFoodLogs.value.filter(l => l.year === currentYear).length)
const seasonsCovered = computed(() => new Set(softFoodLogs.value.map(l => l.season)).size)

// Modal State
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const editingLogId = ref<number | null>(null)
const logToDelete = ref<number | null>(null)

const formData = ref({
  year: currentYear,
  season: 'spring' as 'spring' | 'summer' | 'autumn' | 'winter',
  recipe_name: '',
  ingredients: '',
  supplements: '',
  results: ''
})

const resetForm = () => {
  formData.value = {
    year: currentYear,
    season: 'spring',
    recipe_name: '',
    ingredients: '',
    supplements: '',
    results: ''
  }
  editingLogId.value = null
}

const openAddModal = () => {
  resetForm()
  isModalOpen.value = true
}

const openEditModal = (log: any) => {
  formData.value = {
    year: log.year,
    season: log.season,
    recipe_name: log.recipe_name,
    ingredients: log.ingredients,
    supplements: log.supplements || '',
    results: log.results || ''
  }
  editingLogId.value = log.id
  isModalOpen.value = true
}

const confirmDelete = (id: number) => {
  logToDelete.value = id
  isDeleteModalOpen.value = true
}

const handleSave = async () => {
  if (editingLogId.value) {
    await softFoodStore.updateLog(editingLogId.value, formData.value)
  } else {
    await softFoodStore.createLog(formData.value as SoftFoodLogCreate)
  }
  isModalOpen.value = false
  fetchLogs()
}

const handleDelete = async () => {
  if (logToDelete.value) {
    await softFoodStore.deleteLog(logToDelete.value)
    isDeleteModalOpen.value = false
    logToDelete.value = null
    fetchLogs()
  }
}

const getSeasonBadgeColor = (season: string) => {
  switch (season) {
    case 'spring': return 'success'
    case 'summer': return 'warning'
    case 'autumn': return 'danger'
    case 'winter': return 'info'
    default: return 'primary'
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Soft Food Log</h1>
        <p class="text-slate-400">Manage seasonal soft food recipes and results</p>
      </div>
      <button @click="openAddModal" class="btn-primary flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Add Recipe
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <StatCard
        title="Total Recipes"
        :value="totalRecipes"
        icon="📋"
      />
      <StatCard
        title="This Year"
        :value="thisYearRecipes"
        icon="📅"
      />
      <StatCard
        title="Seasons Covered"
        :value="seasonsCovered"
        icon="🌤️"
      />
    </div>

    <!-- Filters -->
    <div class="glass-panel p-4 flex flex-col sm:flex-row gap-4 items-center justify-between">
      <div class="flex items-center gap-2 w-full sm:w-auto">
        <label class="text-sm font-medium text-slate-300">Year:</label>
        <select v-model="selectedYear" @change="fetchLogs" class="input-field max-w-[120px]">
          <option value="all">All Years</option>
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
      
      <div class="flex flex-wrap gap-2 w-full sm:w-auto">
        <button 
          v-for="season in seasons" 
          :key="season"
          @click="selectedSeason = season; fetchLogs()"
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-colors"
          :class="selectedSeason === season ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'"
        >
          {{ season.charAt(0).toUpperCase() + season.slice(1) }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="softFoodLogs.length === 0" class="glass-panel py-16 text-center">
      <div class="text-5xl mb-4">🥗</div>
      <h3 class="text-xl font-semibold text-white mb-2">No recipes found</h3>
      <p class="text-slate-400 mb-6">Add your first soft food recipe to track bird diets.</p>
      <button @click="openAddModal" class="btn-primary">Add Recipe</button>
    </div>

    <!-- Recipes Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="log in softFoodLogs" :key="log.id" class="glass-card flex flex-col">
        <div class="p-5 flex-1">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-semibold text-white line-clamp-1">{{ log.recipe_name }}</h3>
            <Badge :variant="getSeasonBadgeColor(log.season)">
              {{ log.season.charAt(0).toUpperCase() + log.season.slice(1) }} {{ log.year }}
            </Badge>
          </div>
          
          <div class="space-y-3 text-sm">
            <div>
              <span class="text-slate-400 block mb-1">Ingredients:</span>
              <p class="text-slate-200 line-clamp-2">{{ log.ingredients }}</p>
            </div>
            
            <div v-if="log.supplements">
              <span class="text-slate-400 block mb-1">Supplements:</span>
              <p class="text-slate-200 line-clamp-1">{{ log.supplements }}</p>
            </div>
            
            <div v-if="log.results">
              <span class="text-slate-400 block mb-1">Results/Notes:</span>
              <p class="text-slate-200 line-clamp-2">{{ log.results }}</p>
            </div>
          </div>
        </div>
        
        <div class="px-5 py-3 border-t border-slate-700/50 flex justify-end gap-2 bg-slate-800/30 rounded-b-xl">
          <button @click="openEditModal(log)" class="btn-ghost text-sm py-1 px-3">
            Edit
          </button>
          <button @click="confirmDelete(log.id)" class="btn-ghost text-sm py-1 px-3 text-red-400 hover:text-red-300 hover:bg-red-500/10">
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal :show="isModalOpen" :title="editingLogId ? 'Edit Recipe' : 'Add Recipe'" @close="isModalOpen = false">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Year</label>
            <input v-model.number="formData.year" type="number" required class="input-field" />
          </div>
          <div>
            <label class="label">Season</label>
            <select v-model="formData.season" required class="input-field">
              <option value="spring">Spring</option>
              <option value="summer">Summer</option>
              <option value="autumn">Autumn</option>
              <option value="winter">Winter</option>
            </select>
          </div>
        </div>
        
        <div>
          <label class="label">Recipe Name</label>
          <input v-model="formData.recipe_name" type="text" required class="input-field" placeholder="e.g. Basic Egg Food" />
        </div>
        
        <div>
          <label class="label">Ingredients</label>
          <textarea v-model="formData.ingredients" required class="input-field min-h-[80px]" placeholder="List ingredients..."></textarea>
        </div>
        
        <div>
          <label class="label">Supplements (Optional)</label>
          <textarea v-model="formData.supplements" class="input-field min-h-[60px]" placeholder="Vitamins, minerals, etc."></textarea>
        </div>
        
        <div>
          <label class="label">Results & Notes (Optional)</label>
          <textarea v-model="formData.results" class="input-field min-h-[60px]" placeholder="How well was it eaten? Any breeding results?"></textarea>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="isModalOpen = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Recipe' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal :show="isDeleteModalOpen" title="Delete Recipe" @close="isDeleteModalOpen = false">
      <div class="p-2">
        <p class="text-slate-300 mb-6">Are you sure you want to delete this soft food recipe? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <button @click="isDeleteModalOpen = false" class="btn-secondary">Cancel</button>
          <button @click="handleDelete" class="btn-primary bg-red-600 hover:bg-red-700 text-white" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>
