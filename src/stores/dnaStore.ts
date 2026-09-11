import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { DnaRecord } from '@/types'
import { Capacitor } from '@capacitor/core'
import { Filesystem, Directory } from '@capacitor/filesystem'

export const useDnaStore = defineStore('dna', () => {
  const { get, del, loading, error } = useApi()
  const dnaRecords = ref<DnaRecord[]>([])
  const searchResults = ref<DnaRecord[]>([])
  
  async function fetchDnaRecords(birdId: number) {
    try {
      const data = await get<DnaRecord[]>(`/dna/bird/${birdId}`)
      if (data) dnaRecords.value = data
    } catch (e) {
      console.error('Failed to fetch DNA records:', e)
    }
  }

  async function searchDna(query: string = '', categoryId?: string) {
    try {
      loading.value = true
      let url = `/dna/search?q=${encodeURIComponent(query)}`
      if (categoryId) {
        url += `&category_id=${categoryId}`
      }
      const data = await get<DnaRecord[]>(url)
      if (data) searchResults.value = data
    } catch (e) {
      console.error('Failed to search DNA records', e)
    } finally {
      loading.value = false
    }
  }

  async function uploadDna(birdId: number, file: File, fileType: string) {
    try {
      loading.value = true
      error.value = null
      
      if (Capacitor.isNativePlatform()) {
        const reader = new FileReader();
        const base64Data = await new Promise<string>((resolve, reject) => {
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });

        const fileName = `dna_${birdId}_${Date.now()}_${file.name}`;
        
        await Filesystem.writeFile({
          path: fileName,
          data: base64Data,
          directory: Directory.Data,
        });
        
        const uriResult = await Filesystem.getUri({
          directory: Directory.Data,
          path: fileName
        });
        
        const { post } = useApi();
        return await post(`/dna`, {
          bird_id: birdId,
          file_path: uriResult.uri,
          file_type: fileType
        });
      }

      const formData = new FormData()
      formData.append('file', file)
      formData.append('bird_id', String(birdId))
      formData.append('file_type', fileType)
      
      const response = await fetch(`/api/dna`, { 
        method: 'POST', 
        body: formData 
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || 'Failed to upload file')
      }
      
      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message || 'An error occurred during upload'
      console.error('Failed to upload DNA record:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteDnaRecord(id: number) {
    try {
      await del(`/dna/${id}`)
      dnaRecords.value = dnaRecords.value.filter(r => r.id !== id)
      searchResults.value = searchResults.value.filter(r => r.id !== id)
    } catch (e) {
      console.error('Failed to delete DNA record:', e)
      throw e
    }
  }

  return {
    dnaRecords,
    searchResults,
    loading,
    error,
    fetchDnaRecords,
    searchDna,
    uploadDna,
    deleteDnaRecord
  }
})
