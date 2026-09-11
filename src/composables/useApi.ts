import { ref } from 'vue'
import { Capacitor } from '@capacitor/core'
import { processMobileRequest } from '@/services/mobileDataLayer'

export function useApi() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const request = async <T>(url: string, options: RequestInit = {}): Promise<T | null> => {
    loading.value = true
    error.value = null
    
    try {
      if (Capacitor.isNativePlatform()) {
        const data = await processMobileRequest(options.method || 'GET', url, options.body)
        return data as T
      }

      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      }
      
      const response = await fetch(`/api${url}`, { ...options, headers })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.message || errorData?.detail || `HTTP error! status: ${response.status}`)
      }
      
      // Some endpoints might return 204 No Content
      if (response.status === 204) {
        return null
      }
      
      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message || 'An unexpected error occurred'
      console.error(`API Error [${options.method || 'GET'} ${url}]:`, e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    get: <T>(url: string) => request<T>(url, { method: 'GET' }),
    post: <T>(url: string, body: any) => request<T>(url, { method: 'POST', body: JSON.stringify(body) }),
    put: <T>(url: string, body: any) => request<T>(url, { method: 'PUT', body: JSON.stringify(body) }),
    del: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
  }
}
