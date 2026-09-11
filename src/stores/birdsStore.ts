import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import type { Bird, BirdCreate, BirdUpdate, Category, CategoryWithCount, BirdStats, AncestryTreeNode, DescendantsTreeNode, ActivityItem } from '@/types'

export const useBirdsStore = defineStore('birds', () => {
  const { get, post, put, del, loading, error } = useApi()
  
  // State
  const birds = ref<Bird[]>([])
  const categories = ref<CategoryWithCount[]>([])
  const selectedBird = ref<Bird | null>(null)
  const birdStats = ref<BirdStats>({
    total_birds: 0,
    in_stock: 0,
    sold: 0,
    deceased: 0,
    active_pairs: 0
  })
  const recentActivity = ref<ActivityItem[]>([])

  // Getters
  const birdsByCategory = computed(() => {
    const grouped = new Map<string, Bird[]>()
    birds.value.forEach(bird => {
      const catId = bird.category_id || 'uncategorized'
      if (!grouped.has(catId)) grouped.set(catId, [])
      grouped.get(catId)!.push(bird)
    })
    return grouped
  })

  const inStockBirds = computed(() => birds.value.filter(b => b.status === 'in_stock'))
  const soldBirds = computed(() => birds.value.filter(b => b.status === 'sold'))
  const totalCount = computed(() => birds.value.length)

  // Actions
  async function fetchBirds() {
    try {
      const data = await get<Bird[]>('/birds')
      if (data) birds.value = data
    } catch (e) {
      console.error('Failed to fetch birds', e)
    }
  }

  async function fetchBird(id: string) {
    try {
      const data = await get<Bird>(`/birds/${id}`)
      if (data) selectedBird.value = data
      return data
    } catch (e) {
      console.error(`Failed to fetch bird ${id}`, e)
      return null
    }
  }

  async function createBird(birdData: BirdCreate) {
    try {
      const data = await post<Bird>('/birds', birdData)
      if (data) {
        birds.value.push(data)
        return data
      }
    } catch (e) {
      console.error('Failed to create bird', e)
      throw e
    }
  }

  async function updateBird(id: string, birdData: BirdUpdate) {
    try {
      const data = await put<Bird>(`/birds/${id}`, birdData)
      if (data) {
        const index = birds.value.findIndex(b => b.id === id)
        if (index !== -1) birds.value[index] = data
        if (selectedBird.value?.id === id) selectedBird.value = data
        return data
      }
    } catch (e) {
      console.error(`Failed to update bird ${id}`, e)
      throw e
    }
  }

  async function deleteBird(id: string) {
    try {
      await del(`/birds/${id}`)
      birds.value = birds.value.filter(b => b.id !== id)
      if (selectedBird.value?.id === id) selectedBird.value = null
    } catch (e) {
      console.error(`Failed to delete bird ${id}`, e)
      throw e
    }
  }

  async function fetchCategories() {
    try {
      const data = await get<CategoryWithCount[]>('/categories')
      if (data) categories.value = data
    } catch (e) {
      console.error('Failed to fetch categories', e)
    }
  }

  async function createCategory(data: { name: string, description?: string }) {
    try {
      const newCategory = await post<CategoryWithCount>('/categories', data)
      if (newCategory) {
        await fetchCategories()
        return newCategory
      }
    } catch (e) {
      console.error('Failed to create category', e)
      throw e
    }
  }

  async function fetchBirdStats() {
    try {
      const data = await get<BirdStats>('/birds/stats/summary')
      if (data) birdStats.value = data
    } catch (e) {
      console.error('Failed to fetch bird stats', e)
    }
  }

  async function fetchRecentActivity() {
    try {
      const data = await get<ActivityItem[]>('/activity?limit=10')
      if (data) recentActivity.value = data
    } catch (e) {
      console.error('Failed to fetch recent activity', e)
    }
  }

  async function fetchAncestryTree(id: string, depth: number = 5) {
    try {
      return await get<AncestryTreeNode>(`/birds/${id}/ancestry/tree?depth=${depth}`)
    } catch (e) {
      console.error(`Failed to fetch ancestry tree for bird ${id}`, e)
      return null
    }
  }

  async function fetchDescendantsTree(id: string, depth: number = 5) {
    try {
      return await get<DescendantsTreeNode>(`/birds/${id}/descendants/tree?depth=${depth}`)
    } catch (e) {
      console.error(`Failed to fetch descendants tree for bird ${id}`, e)
      return null
    }
  }

  return {
    // State
    birds,
    categories,
    selectedBird,
    birdStats,
    recentActivity,
    loading,
    error,
    
    // Getters
    birdsByCategory,
    inStockBirds,
    soldBirds,
    totalCount,
    
    // Actions
    fetchBirds,
    fetchBird,
    createBird,
    updateBird,
    deleteBird,
    fetchCategories,
    createCategory,
    fetchBirdStats,
    fetchRecentActivity,
    fetchAncestryTree,
    fetchDescendantsTree
  }
})
