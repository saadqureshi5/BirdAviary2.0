<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import PhotoUpload from '@/components/shared/PhotoUpload.vue'
import ParentSelector from '@/components/shared/ParentSelector.vue'
import type { BirdUpdate } from '@/types'
import { Capacitor } from '@capacitor/core'
import { Filesystem, Directory } from '@capacitor/filesystem'

const route = useRoute()
const router = useRouter()
const birdsStore = useBirdsStore()

const birdId = route.params.id as string
const isSubmitting = ref(false)
const errorMsg = ref('')
const photoFile = ref<File | null>(null)

const formData = ref<BirdUpdate>({
  ring_id: '',
  name: '',
  mutation: '',
  sex: 'unknown',
  category_id: undefined,
  cage_number: '',
  status: 'in_stock',
  notes: '',
  father_id: undefined,
  mother_id: undefined,
})

const currentPhotoUrl = ref<string | null>(null)

// Manual parent data (for parents not in aviary)
const manualFather = ref<{ ring_id: string; name: string; mutation: string; sex: string } | null>(null)
const manualMother = ref<{ ring_id: string; name: string; mutation: string; sex: string } | null>(null)

// Filter out the current bird from parent selections
const availableBirds = computed(() => birdsStore.birds.filter(b => String(b.id) !== birdId))

onMounted(async () => {
  await birdsStore.fetchCategories()
  await birdsStore.fetchBirds()
  const bird = await birdsStore.fetchBird(birdId)
  if (bird) {
    formData.value = {
      ring_id: bird.ring_id || '',
      name: bird.name || '',
      mutation: bird.mutation || '',
      sex: bird.sex || 'unknown',
      category_id: bird.category_id || undefined,
      cage_number: bird.cage_number || '',
      status: bird.status || 'in_stock',
      notes: bird.notes || '',
      father_id: bird.father_id || undefined,
      mother_id: bird.mother_id || undefined,
    }
    currentPhotoUrl.value = bird.photo_url ? `/${bird.photo_url}` : null
  }
})

const handlePhotoFile = (file: File) => {
  photoFile.value = file
}

const handleManualFather = (data: { ring_id: string; name: string; mutation: string; sex: string }) => {
  manualFather.value = data
}

const handleManualMother = (data: { ring_id: string; name: string; mutation: string; sex: string }) => {
  manualMother.value = data
}

const handleSubmit = async () => {
  isSubmitting.value = true
  errorMsg.value = ''

  try {
    // Create or update manual parent birds first if needed
    if (manualFather.value && manualFather.value.ring_id.trim()) {
      const ringId = manualFather.value.ring_id.trim()
      const existingFather = birdsStore.birds.find(b => b.ring_id === ringId)
      
      if (existingFather) {
        await birdsStore.updateBird(String(existingFather.id), {
          name: manualFather.value.name || undefined,
          mutation: manualFather.value.mutation || undefined,
          sex: 'male',
        })
        formData.value.father_id = String(existingFather.id)
      } else {
        const father = await birdsStore.createBird({
          ring_id: ringId,
          name: manualFather.value.name || undefined,
          mutation: manualFather.value.mutation || undefined,
          sex: 'male',
          category_id: formData.value.category_id ? String(formData.value.category_id) : undefined,
          status: 'external',
        })
        if (father) {
          formData.value.father_id = String(father.id)
        }
      }
    }

    if (manualMother.value && manualMother.value.ring_id.trim()) {
      const ringId = manualMother.value.ring_id.trim()
      const existingMother = birdsStore.birds.find(b => b.ring_id === ringId)
      
      if (existingMother) {
        await birdsStore.updateBird(String(existingMother.id), {
          name: manualMother.value.name || undefined,
          mutation: manualMother.value.mutation || undefined,
          sex: 'female',
        })
        formData.value.mother_id = String(existingMother.id)
      } else {
        const mother = await birdsStore.createBird({
          ring_id: ringId,
          name: manualMother.value.name || undefined,
          mutation: manualMother.value.mutation || undefined,
          sex: 'female',
          category_id: formData.value.category_id ? String(formData.value.category_id) : undefined,
          status: 'external',
        })
        if (mother) {
          formData.value.mother_id = String(mother.id)
        }
      }
    }

    await birdsStore.updateBird(birdId, formData.value)
    
    // Upload photo if a new one was selected
    if (photoFile.value) {
      if (Capacitor.isNativePlatform()) {
        const reader = new FileReader();
        const base64Data = await new Promise<string>((resolve, reject) => {
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(photoFile.value!);
        });

        const fileName = `bird_${birdId}_${Date.now()}_${photoFile.value.name}`;
        
        await Filesystem.writeFile({
          path: fileName,
          data: base64Data,
          directory: Directory.Data,
        });
        
        const uriResult = await Filesystem.getUri({
          directory: Directory.Data,
          path: fileName
        });
        
        await birdsStore.updateBird(birdId, { photo_url: uriResult.uri });
      } else {
        const fd = new FormData()
        fd.append('file', photoFile.value)
        await fetch(`/api/birds/${birdId}/photo`, {
          method: 'POST',
          body: fd,
        })
      }
    }
    
    router.push(`/birds/${birdId}`)
  } catch (e: any) {
    errorMsg.value = e.message || 'Failed to update bird'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in pb-12">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-white mb-1">Edit Bird</h2>
      <p class="text-slate-400">Update the details for this bird.</p>
    </div>

    <form @submit.prevent="handleSubmit" class="glass-card p-6 md:p-8">
      
      <div v-if="errorMsg" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl mb-8 flex items-start gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shrink-0 mt-0.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>{{ errorMsg }}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
        
        <!-- Left Column: Photo -->
        <div class="md:col-span-4">
          <PhotoUpload label="Bird Photo" :modelValue="currentPhotoUrl" @file="handlePhotoFile" />
        </div>
        
        <!-- Right Column: Form Fields -->
        <div class="md:col-span-8 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Ring ID -->
            <div>
              <label class="label">Ring ID <span class="text-red-400">*</span></label>
              <input 
                v-model="formData.ring_id" 
                type="text" 
                required
                class="input-field" 
                placeholder="e.g. RG-2023-001"
              >
            </div>
            
            <!-- Name -->
            <div>
              <label class="label">Name (Optional)</label>
              <input 
                v-model="formData.name" 
                type="text" 
                class="input-field" 
                placeholder="e.g. Charlie"
              >
            </div>

            <!-- Category -->
            <div>
              <label class="label">Category</label>
              <select v-model="formData.category_id" class="input-field appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_1rem_center] bg-[length:1.2em_1.2em]">
                <option value="">Select a category...</option>
                <option v-for="cat in birdsStore.categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <!-- Mutation -->
            <div>
              <label class="label">Mutation</label>
              <input 
                v-model="formData.mutation" 
                type="text" 
                class="input-field" 
                placeholder="e.g. Lutino, Normal"
              >
            </div>

            <!-- Sex -->
            <div>
              <label class="label">Sex</label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="formData.sex" value="male" class="text-primary-500 focus:ring-primary-500 bg-surface-900 border-white/20">
                  <span class="text-white">Male</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="formData.sex" value="female" class="text-primary-500 focus:ring-primary-500 bg-surface-900 border-white/20">
                  <span class="text-white">Female</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="formData.sex" value="unknown" class="text-primary-500 focus:ring-primary-500 bg-surface-900 border-white/20">
                  <span class="text-white">Unknown</span>
                </label>
              </div>
            </div>

            <!-- Cage Number -->
            <div>
              <label class="label">Cage Number</label>
              <input 
                v-model="formData.cage_number" 
                type="text" 
                class="input-field" 
                placeholder="e.g. C-12"
              >
            </div>
            
            <!-- Status -->
            <div class="md:col-span-2">
              <label class="label">Current Status</label>
              <select v-model="formData.status" class="input-field appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_1rem_center] bg-[length:1.2em_1.2em]">
                <option value="in_stock">In Stock</option>
                <option value="sold">Sold</option>
                <option value="deceased">Deceased</option>
              </select>
            </div>

            <!-- Parents Section -->
            <div class="md:col-span-2 border-t border-white/10 pt-6 mt-2">
              <h3 class="text-white font-semibold mb-4 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M17 18a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2"/><rect width="18" height="18" x="3" y="4" rx="2"/><circle cx="12" cy="10" r="2"/><line x1="8" x2="8" y1="2" y2="4"/><line x1="16" x2="16" y1="2" y2="4"/></svg>
                Parent Lineage
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ParentSelector
                  label="Sire (Father)"
                  sex="male"
                  :birds="availableBirds"
                  :categoryId="formData.category_id"
                  v-model="formData.father_id"
                  @manualParent="handleManualFather"
                />
                <ParentSelector
                  label="Dam (Mother)"
                  sex="female"
                  :birds="availableBirds"
                  :categoryId="formData.category_id"
                  v-model="formData.mother_id"
                  @manualParent="handleManualMother"
                />
              </div>
            </div>

            <!-- Notes -->
            <div class="md:col-span-2">
              <label class="label">Notes</label>
              <textarea 
                v-model="formData.notes" 
                rows="4" 
                class="input-field resize-none" 
                placeholder="Any additional information..."
              ></textarea>
            </div>
          </div>
          
          <div class="border-t border-white/10 pt-6 flex justify-end gap-4 mt-8">
            <button type="button" @click="router.back()" class="btn-ghost">Cancel</button>
            <button type="submit" class="btn-primary min-w-[120px]" :disabled="isSubmitting">
              {{ isSubmitting ? 'Updating...' : 'Update Bird' }}
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>
