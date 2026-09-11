import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { SoftFoodLog, SoftFoodLogCreate, SoftFoodLogUpdate } from '@/types'

export const useSoftFoodStore = defineStore('softFood', () => {
  const { get, post, put, del, loading, error } = useApi()
  const softFoodLogs = ref<SoftFoodLog[]>([])

  async function fetchLogs(year?: number, season?: string) {
    try {
      const params = new URLSearchParams()
      if (year) params.append('year', year.toString())
      if (season && season !== 'all') params.append('season', season)
      
      const queryString = params.toString()
      const url = queryString ? `/soft-food?${queryString}` : '/soft-food'
      
      const data = await get<SoftFoodLog[]>(url)
      if (data) softFoodLogs.value = data
    } catch (e) {
      console.error('Failed to fetch soft food logs:', e)
    }
  }

  async function createLog(logData: SoftFoodLogCreate) {
    try {
      const newLog = await post<SoftFoodLog>('/soft-food', logData)
      if (newLog) {
        softFoodLogs.value.push(newLog)
      }
      return newLog
    } catch (e) {
      console.error('Failed to create soft food log:', e)
      return null
    }
  }

  async function updateLog(id: number, logData: SoftFoodLogUpdate) {
    try {
      const updatedLog = await put<SoftFoodLog>(`/soft-food/${id}`, logData)
      if (updatedLog) {
        const index = softFoodLogs.value.findIndex(l => l.id === id)
        if (index !== -1) {
          softFoodLogs.value[index] = updatedLog
        }
      }
      return updatedLog
    } catch (e) {
      console.error('Failed to update soft food log:', e)
      return null
    }
  }

  async function deleteLog(id: number) {
    try {
      await del(`/soft-food/${id}`)
      softFoodLogs.value = softFoodLogs.value.filter(l => l.id !== id)
      return true
    } catch (e) {
      console.error('Failed to delete soft food log:', e)
      return false
    }
  }

  return {
    softFoodLogs,
    loading,
    error,
    fetchLogs,
    createLog,
    updateLog,
    deleteLog
  }
})
