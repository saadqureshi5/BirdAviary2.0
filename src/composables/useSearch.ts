import { ref, watch, type Ref } from 'vue'
import { useApi } from './useApi'
import type { Bird } from '@/types'

export function useSearch(query: Ref<string>, debounceMs = 300) {
  const { get, loading, error } = useApi()
  const results = ref<Bird[]>([])
  
  let timeoutId: number | null = null

  const performSearch = async (q: string) => {
    if (!q.trim()) {
      results.value = []
      return
    }
    
    try {
      // Adjusted based on typical FastAPI search endpoint
      const response = await get<Bird[]>(`/birds/search?q=${encodeURIComponent(q)}`)
      results.value = response || []
    } catch (e) {
      console.error('Search failed:', e)
      results.value = []
    }
  }

  watch(query, (newVal) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    timeoutId = window.setTimeout(() => {
      performSearch(newVal)
    }, debounceMs)
  })

  return {
    results,
    loading,
    error,
    performSearch // expose for manual trigger if needed
  }
}
