<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useDnaStore } from '@/stores/dnaStore'
import { useBirdsStore } from '@/stores/birdsStore'
import { useApi } from '@/composables/useApi'
import Modal from '@/components/shared/Modal.vue'
import Badge from '@/components/shared/Badge.vue'
import type { Bird } from '@/types'

const dnaStore = useDnaStore()
const birdsStore = useBirdsStore()
const { get } = useApi()

onMounted(async () => {
  await birdsStore.fetchCategories()
  // Load all DNA records on initial page load
  dnaStore.searchDna('', undefined)
})

// UI State
const searchQuery = ref('')
const selectedCategory = ref('')
const showUploadModal = ref(false)
const showDeleteConfirm = ref(false)
const dnaToDelete = ref<number | null>(null)
const uploadLoading = ref(false)

// Form State
const uploadForm = ref({
  birdId: null as number | null,
  file: null as File | null
})

// Bird Search
const birdSearchQuery = ref('')
const birdSearchResults = ref<Bird[]>([])
const isSearchingBirds = ref(false)
const selectedBird = ref<Bird | null>(null)

let searchTimeout: ReturnType<typeof setTimeout>

// Methods
const handleSearch = () => {
  dnaStore.searchDna(searchQuery.value, selectedCategory.value || undefined)
}

watch(searchQuery, (newVal) => {
  if (newVal === '') {
    handleSearch()
  }
})

watch(selectedCategory, () => {
  handleSearch()
})

watch(birdSearchQuery, (newVal) => {
  clearTimeout(searchTimeout)
  if (!newVal.trim()) {
    birdSearchResults.value = []
    return
  }
  
  isSearchingBirds.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const data = await get<Bird[]>(`/birds/search?q=${encodeURIComponent(newVal)}`)
      if (data) {
        birdSearchResults.value = data
      } else {
        birdSearchResults.value = []
      }
    } catch (e) {
      console.error(e)
    } finally {
      isSearchingBirds.value = false
    }
  }, 300)
})

const selectBird = (bird: Bird) => {
  selectedBird.value = bird
  uploadForm.value.birdId = parseInt(bird.id)
  birdSearchQuery.value = ''
  birdSearchResults.value = []
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadForm.value.file = target.files[0]
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.birdId || !uploadForm.value.file) return
  
  uploadLoading.value = true
  try {
    const file = uploadForm.value.file
    const fileType = file.type.startsWith('image/') ? 'image' : 'pdf'
    await dnaStore.uploadDna(uploadForm.value.birdId, file, fileType)
    closeModal()
    if (searchQuery.value.trim()) {
      handleSearch()
    }
  } catch (e: any) {
    alert('Upload failed: ' + (e?.message || 'Unknown error'))
  } finally {
    uploadLoading.value = false
  }
}

const closeModal = () => {
  showUploadModal.value = false
  uploadForm.value = { birdId: null, file: null }
  selectedBird.value = null
  birdSearchQuery.value = ''
  birdSearchResults.value = []
}

const confirmDelete = (id: number) => {
  dnaToDelete.value = id
  showDeleteConfirm.value = true
}

const executeDelete = async () => {
  if (dnaToDelete.value) {
    await dnaStore.deleteDnaRecord(dnaToDelete.value)
    showDeleteConfirm.value = false
    dnaToDelete.value = null
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">DNA Records</h1>
        <p class="text-slate-400 mt-1">Manage DNA certificates and test results</p>
      </div>
      <button class="btn-primary" @click="showUploadModal = true">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
        </svg>
        Upload Record
      </button>
    </div>

    <!-- Search Section -->
    <div class="glass-card p-6">
      <div class="max-w-3xl">
        <label class="label block mb-2">Search DNA Records</label>
        <div class="flex flex-col sm:flex-row gap-4">
          <input 
            v-model="searchQuery" 
            type="text" 
            class="input-field flex-1" 
            placeholder="Search by Ring ID, name, or mutation..."
            @keyup.enter="handleSearch"
          />
          <select v-model="selectedCategory" class="input-field sm:max-w-[200px] appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.5rem_center] bg-[length:1em_1em] pr-8">
            <option value="">All Categories</option>
            <option v-for="cat in birdsStore.categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <button class="btn-secondary" @click="handleSearch">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Results Grid -->
    <div v-if="dnaStore.loading" class="flex justify-center items-center p-12">
      <svg class="animate-spin h-8 w-8 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    
    <div v-else-if="dnaStore.searchResults.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-slide-up">
      <div v-for="record in dnaStore.searchResults" :key="record.id" class="glass-card overflow-hidden hover:border-slate-700 transition-colors">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-semibold text-white">
                {{ record.bird?.name ? (record.bird?.mutation ? record.bird.name + ' (' + record.bird.mutation + ')' : record.bird.name) : (record.bird?.mutation || 'Unknown Bird') }}
              </h3>
              <p class="text-sm text-slate-400 font-mono">{{ record.bird?.ring_id || 'Unknown Ring ID' }}</p>
            </div>
            <Badge :variant="record.file_type === 'pdf' ? 'danger' : 'info'">
              {{ record.file_type.toUpperCase() }}
            </Badge>
          </div>
          
          <div class="text-sm text-slate-400 mb-6">
            Uploaded on {{ formatDate(record.created_at) }}
          </div>

          <div class="flex gap-3">
            <a :href="`/${record.file_path}`" target="_blank" class="btn-secondary flex-1 text-center flex items-center justify-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              View
            </a>
            <button class="btn-secondary text-red-400 hover:text-red-300 border-red-900/30 hover:bg-red-900/20" @click="confirmDelete(record.id)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="searchQuery" class="glass-card p-12 text-center animate-fade-in">
      <div class="w-16 h-16 mx-auto mb-4 bg-surface-800 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">No Records Found</h3>
      <p class="text-slate-400 max-w-md mx-auto">We couldn't find any DNA records for "{{ searchQuery }}". Try a different search term or upload a new record.</p>
    </div>

    <!-- Initial State -->
    <div v-else class="glass-card p-12 text-center">
      <div class="w-16 h-16 mx-auto mb-4 bg-surface-800 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">Search DNA Records</h3>
      <p class="text-slate-400 max-w-md mx-auto">Enter a bird's Ring ID, name, or mutation above to view its DNA records, or upload a new certificate.</p>
    </div>

    <!-- Upload Modal -->
    <Modal :show="showUploadModal" title="Upload DNA Record" @close="closeModal">
      <div class="space-y-6">
        <div>
          <label class="label block mb-2">Select Bird</label>
          <div v-if="!selectedBird" class="relative">
            <input 
              v-model="birdSearchQuery" 
              type="text" 
              class="input-field w-full" 
              placeholder="Search by Ring ID, name, mutation, or category..."
            />
            <div v-if="isSearchingBirds" class="absolute right-3 top-3">
              <svg class="animate-spin h-5 w-5 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            
            <!-- Search Results Dropdown -->
            <div v-if="birdSearchResults.length > 0" class="absolute z-10 w-full mt-1 bg-surface-800 border border-surface-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              <div 
                v-for="bird in birdSearchResults" 
                :key="bird.id"
                class="p-3 hover:bg-surface-700 cursor-pointer flex justify-between items-center border-b border-surface-700 last:border-0"
                @click="selectBird(bird)"
              >
                <div>
                  <div class="font-medium text-white">
                    {{ bird.name ? (bird.mutation ? bird.name + ' (' + bird.mutation + ')' : bird.name) : (bird.mutation || 'Unknown Bird') }}
                  </div>
                  <div class="text-xs text-slate-400">{{ bird.ring_id }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Selected Bird display -->
          <div v-else class="flex justify-between items-center p-3 bg-surface-800 border border-surface-700 rounded-lg">
            <div>
              <div class="font-medium text-white">
                {{ selectedBird.name ? (selectedBird.mutation ? selectedBird.name + ' (' + selectedBird.mutation + ')' : selectedBird.name) : (selectedBird.mutation || 'Unknown Bird') }}
              </div>
              <div class="text-xs text-slate-400">{{ selectedBird.ring_id }}</div>
            </div>
            <button class="text-slate-400 hover:text-white" @click="selectedBird = null">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="label block mb-2">DNA Certificate / Results File (PDF/Image)</label>
          <input 
            type="file" 
            accept="image/*,.pdf" 
            class="input-field w-full py-2" 
            @change="handleFileChange"
          />
        </div>
      </div>
      <template #footer>
        <button class="btn-ghost mr-3" @click="closeModal">Cancel</button>
        <button 
          class="btn-primary" 
          :disabled="!uploadForm.birdId || !uploadForm.file || uploadLoading" 
          @click="handleUpload"
        >
          <svg v-if="uploadLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ uploadLoading ? 'Uploading...' : 'Upload' }}
        </button>
      </template>
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal :show="showDeleteConfirm" title="Confirm Deletion" @close="showDeleteConfirm = false">
      <p class="text-slate-300">Are you sure you want to delete this DNA record? This action cannot be undone.</p>
      <template #footer>
        <button class="btn-ghost mr-3" @click="showDeleteConfirm = false">Cancel</button>
        <button class="btn-primary bg-red-600 hover:bg-red-700 text-white shadow-red-500/20" @click="executeDelete">Delete</button>
      </template>
    </Modal>
  </div>
</template>
