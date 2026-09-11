import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import type { Sale, SaleWithBird, SaleCreate, SaleUpdate, SaleAnalytics } from '@/types'

export const useSalesStore = defineStore('sales', () => {
  const { get, post, put, del, loading, error } = useApi()

  // State
  const sales = ref<SaleWithBird[]>([])
  const analytics = ref<SaleAnalytics | null>(null)
  const searchResults = ref<SaleWithBird[]>([])

  // Getters
  const totalSales = computed(() => sales.value.length)
  const totalRevenue = computed(() =>
    sales.value.reduce((sum, s) => sum + (s.sale_price || 0), 0)
  )

  // Actions
  async function fetchSales(skip = 0, limit = 100) {
    try {
      const data = await get<SaleWithBird[]>(`/sales?skip=${skip}&limit=${limit}`)
      if (data) sales.value = data
    } catch (e) {
      console.error('Failed to fetch sales', e)
    }
  }

  async function createSale(saleData: SaleCreate) {
    try {
      const data = await post<Sale>('/sales', saleData)
      if (data) {
        // Refetch to get bird details
        await fetchSales()
        return data
      }
    } catch (e) {
      console.error('Failed to create sale', e)
      throw e
    }
  }

  async function updateSale(id: number, saleData: SaleUpdate) {
    try {
      const data = await put<Sale>(`/sales/${id}`, saleData)
      if (data) {
        await fetchSales()
        return data
      }
    } catch (e) {
      console.error(`Failed to update sale ${id}`, e)
      throw e
    }
  }

  async function searchSales(query: string) {
    try {
      const data = await get<SaleWithBird[]>(`/sales/search?q=${encodeURIComponent(query)}`)
      if (data) searchResults.value = data
      return data
    } catch (e) {
      console.error('Failed to search sales', e)
      return []
    }
  }

  async function fetchAnalytics() {
    try {
      const data = await get<SaleAnalytics>('/sales/analytics')
      if (data) analytics.value = data
    } catch (e) {
      console.error('Failed to fetch sales analytics', e)
    }
  }

  async function deleteSale(id: number) {
    try {
      loading.value = true
      await del(`/sales/${id}`)
      sales.value = sales.value.filter(s => s.id !== id)
      await fetchAnalytics()
    } catch (e) {
      console.error(`Failed to delete sale ${id}`, e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    sales,
    analytics,
    searchResults,
    loading,
    error,

    // Getters
    totalSales,
    totalRevenue,

    // Actions
    fetchSales,
    createSale,
    updateSale,
    deleteSale,
    searchSales,
    fetchAnalytics,
  }
})
