<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { CategoryWithCount, Bird } from '@/types'

const props = defineProps<{
  categories: CategoryWithCount[]
  birds: Bird[]
  selectedStatus: string
  modelValue: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string | null): void
  (e: 'create', val: { name: string, description?: string }): void
}>()

const isOpen = ref(false)
const showAddForm = ref(false)
const newCategoryName = ref('')
const newCategoryDescription = ref('')
const dropdownRef = ref<HTMLElement | null>(null)

const selectedLabel = computed(() => {
  if (!props.modelValue) return 'All Birds'
  const cat = props.categories.find(c => c.id === props.modelValue)
  return cat ? cat.name : 'All Birds'
})

const statusFilteredBirds = computed(() => {
  if (!props.selectedStatus) return props.birds
  return props.birds.filter(b => b.status === props.selectedStatus)
})

const totalBirdCount = computed(() => {
  return statusFilteredBirds.value.length
})

const categoryCounts = computed(() => {
  const counts = new Map<string, number>()
  for (const bird of statusFilteredBirds.value) {
    const catId = String(bird.category_id || '')
    counts.set(catId, (counts.get(catId) || 0) + 1)
  }
  return counts
})

function getCategoryCount(categoryId: string): number {
  return categoryCounts.value.get(String(categoryId)) || 0
}

function selectCategory(id: string | null) {
  emit('update:modelValue', id)
  isOpen.value = false
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    showAddForm.value = false
  }
}

function handleCreate() {
  if (!newCategoryName.value.trim()) return
  emit('create', {
    name: newCategoryName.value.trim(),
    description: newCategoryDescription.value.trim() || undefined
  })
  newCategoryName.value = ''
  newCategoryDescription.value = ''
  showAddForm.value = false
}

function handleCancelAdd() {
  newCategoryName.value = ''
  newCategoryDescription.value = ''
  showAddForm.value = false
}

// Close on outside click
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
    showAddForm.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- Trigger Button -->
    <button
      @click="toggleDropdown"
      class="flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-200"
      :class="isOpen
        ? 'bg-primary-600 border-primary-500 text-white shadow-[0_0_15px_rgba(20,184,166,0.3)]'
        : modelValue
          ? 'bg-primary-600/80 border-primary-500/60 text-white'
          : 'bg-surface-800 border-white/10 text-slate-300 hover:border-white/20 hover:bg-surface-700'"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-60">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
        <line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
      <span class="whitespace-nowrap text-sm font-medium">{{ selectedLabel }}</span>
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50 transition-transform" :class="isOpen ? 'rotate-180' : ''">
        <path d="m6 9 6 6 6-6"/>
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <transition name="dropdown">
      <div
        v-if="isOpen"
        class="absolute top-full left-0 mt-2 w-64 bg-surface-800 border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden"
      >
        <!-- All Birds option -->
        <button
          @click="selectCategory(null)"
          class="w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-white/5"
          :class="!modelValue ? 'text-primary-400 bg-primary-500/10' : 'text-slate-300'"
        >
          <span class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="!modelValue ? 'bg-primary-400' : 'bg-transparent'"></span>
            All Birds
          </span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-surface-900 text-slate-400">{{ totalBirdCount }}</span>
        </button>

        <!-- Divider -->
        <div class="border-t border-white/5"></div>

        <!-- Category list -->
        <div class="max-h-48 overflow-y-auto py-1">
          <button
            v-for="cat in categories"
            :key="cat.id"
            @click="selectCategory(cat.id)"
            class="w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-white/5"
            :class="modelValue === cat.id ? 'text-primary-400 bg-primary-500/10' : 'text-slate-300'"
          >
            <span class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full" :class="modelValue === cat.id ? 'bg-primary-400' : 'bg-transparent'"></span>
              {{ cat.name }}
            </span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-surface-900 text-slate-400">{{ getCategoryCount(cat.id) }}</span>
          </button>

          <div v-if="categories.length === 0" class="px-4 py-3 text-sm text-slate-500 text-center">
            No categories yet
          </div>
        </div>

        <!-- Divider -->
        <div class="border-t border-white/5"></div>

        <!-- Add Category -->
        <div v-if="!showAddForm">
          <button
            @click.stop="showAddForm = true"
            class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="M12 5v14"/>
            </svg>
            Add Category
          </button>
        </div>

        <!-- Add Category Form -->
        <div v-else class="p-3 space-y-2 bg-surface-900/50">
          <input
            v-model="newCategoryName"
            type="text"
            placeholder="Category name"
            class="w-full bg-surface-900 border border-white/10 rounded-md px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            @keyup.enter="handleCreate"
            @click.stop
          >
          <input
            v-model="newCategoryDescription"
            type="text"
            placeholder="Description (optional)"
            class="w-full bg-surface-900 border border-white/10 rounded-md px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            @keyup.enter="handleCreate"
            @click.stop
          >
          <div class="flex items-center gap-2">
            <button
              @click.stop="handleCreate"
              class="px-3 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-sm rounded-md transition-colors"
            >
              Create
            </button>
            <button
              @click.stop="handleCancelAdd"
              class="px-3 py-1.5 bg-surface-700 hover:bg-surface-600 text-slate-300 text-sm rounded-md transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
