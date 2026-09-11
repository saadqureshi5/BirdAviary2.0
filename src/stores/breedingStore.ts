import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { 
  PairingWithStats, 
  PairingDetail, 
  PairingCreate,
  ClutchDetail,
  ClutchCreate,
  Chick,
  ChickCreate,
  BreedingAnalytics 
} from '@/types'

export const useBreedingStore = defineStore('breeding', () => {
  const { get, post, put, loading, error } = useApi()
  
  // State
  const pairings = ref<PairingWithStats[]>([])
  const selectedPairing = ref<PairingDetail | null>(null)
  const analytics = ref<BreedingAnalytics | null>(null)

  // Actions
  async function fetchPairings() {
    try {
      const data = await get<PairingWithStats[]>('/pairings')
      if (data) pairings.value = data
    } catch (e) {
      console.error('Failed to fetch pairings', e)
    }
  }

  async function fetchPairing(id: number) {
    try {
      const data = await get<PairingDetail>(`/pairings/${id}`)
      if (data) selectedPairing.value = data
      return data
    } catch (e) {
      console.error(`Failed to fetch pairing ${id}`, e)
      return null
    }
  }

  async function createPairing(pairingData: PairingCreate) {
    try {
      const data = await post<PairingDetail>('/pairings', pairingData)
      return data
    } catch (e) {
      console.error('Failed to create pairing', e)
      throw e
    }
  }

  async function updatePairing(id: number, pairingData: { end_date?: string, cage_number?: string, notes?: string }) {
    try {
      const data = await put<PairingDetail>(`/pairings/${id}`, pairingData)
      if (data && selectedPairing.value?.id === id) {
        selectedPairing.value = data
      }
      return data
    } catch (e) {
      console.error(`Failed to update pairing ${id}`, e)
      throw e
    }
  }

  async function createClutch(pairingId: number, clutchData: ClutchCreate) {
    try {
      const data = await post<ClutchDetail>(`/breeding/pairings/${pairingId}/clutches`, clutchData)
      if (data && selectedPairing.value?.id === pairingId) {
        // Refetch the pairing to get the updated clutches list
        await fetchPairing(pairingId)
      }
      return data
    } catch (e) {
      console.error('Failed to create clutch', e)
      throw e
    }
  }

  async function updateClutch(clutchId: number, clutchData: Partial<ClutchCreate>) {
    try {
      const data = await put<ClutchDetail>(`/breeding/clutches/${clutchId}`, clutchData)
      if (selectedPairing.value) {
        await fetchPairing(selectedPairing.value.id)
      }
      return data
    } catch (e) {
      console.error(`Failed to update clutch ${clutchId}`, e)
      throw e
    }
  }

  async function createChick(clutchId: number, chickData: ChickCreate) {
    try {
      const data = await post<Chick>(`/breeding/clutches/${clutchId}/chicks`, chickData)
      if (selectedPairing.value) {
        await fetchPairing(selectedPairing.value.id)
      }
      return data
    } catch (e) {
      console.error('Failed to create chick', e)
      throw e
    }
  }

  async function updateChick(chickId: number, chickData: Partial<ChickCreate & { status: string, mortality_reason: string, fledge_date: string }>) {
    try {
      const data = await put<Chick>(`/breeding/chicks/${chickId}`, chickData)
      if (selectedPairing.value) {
        await fetchPairing(selectedPairing.value.id)
      }
      return data
    } catch (e) {
      console.error(`Failed to update chick ${chickId}`, e)
      throw e
    }
  }

  async function promoteChick(chickId: number) {
    try {
      const data = await post<any>(`/breeding/chicks/${chickId}/promote`, {})
      if (selectedPairing.value) {
        await fetchPairing(selectedPairing.value.id)
      }
      return data
    } catch (e) {
      console.error(`Failed to promote chick ${chickId}`, e)
      throw e
    }
  }

  async function fetchAnalytics(categoryId?: number | null) {
    try {
      const url = categoryId ? `/breeding/analytics?category_id=${categoryId}` : '/breeding/analytics'
      const data = await get<BreedingAnalytics>(url)
      if (data) analytics.value = data
      return data
    } catch (e) {
      console.error('Failed to fetch analytics', e)
      return null
    }
  }

  return {
    pairings,
    selectedPairing,
    analytics,
    loading,
    error,
    fetchPairings,
    fetchPairing,
    createPairing,
    updatePairing,
    createClutch,
    updateClutch,
    createChick,
    updateChick,
    promoteChick,
    fetchAnalytics
  }
})
