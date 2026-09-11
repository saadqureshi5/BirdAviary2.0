import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import type { Reminder, ReminderCreate, ReminderUpdate } from '@/types'

export const useRemindersStore = defineStore('reminders', () => {
  const { get, post, put, del, loading, error } = useApi()
  const reminders = ref<Reminder[]>([])

  // Getters
  const activeReminders = computed(() =>
    reminders.value.filter(r => r.is_active)
  )

  const dueReminders = computed(() => {
    const now = new Date()
    return reminders.value.filter(r => r.is_active && new Date(r.due_date) <= now)
  })

  const upcomingReminders = computed(() => {
    const now = new Date()
    const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
    return reminders.value.filter(r =>
      r.is_active && new Date(r.due_date) > now && new Date(r.due_date) <= weekFromNow
    )
  })

  const completedReminders = computed(() =>
    reminders.value.filter(r => !r.is_active)
  )

  // Actions
  async function fetchReminders(activeOnly?: boolean) {
    try {
      const url = activeOnly ? '/reminders?active_only=true' : '/reminders'
      const data = await get<Reminder[]>(url)
      if (data) reminders.value = data
    } catch (e) {
      console.error('Failed to fetch reminders:', e)
    }
  }

  async function fetchDueReminders() {
    try {
      const data = await get<Reminder[]>('/reminders/due')
      return data
    } catch (e) {
      console.error('Failed to fetch due reminders:', e)
      return []
    }
  }

  async function createReminder(reminderData: ReminderCreate) {
    try {
      const data = await post<Reminder>('/reminders', reminderData)
      if (data) {
        await fetchReminders()
        return data
      }
    } catch (e) {
      console.error('Failed to create reminder:', e)
      throw e
    }
  }

  async function updateReminder(id: number, reminderData: ReminderUpdate) {
    try {
      const data = await put<Reminder>(`/reminders/${id}`, reminderData)
      if (data) {
        await fetchReminders()
        return data
      }
    } catch (e) {
      console.error('Failed to update reminder:', e)
      throw e
    }
  }

  async function deleteReminder(id: number) {
    try {
      await del(`/reminders/${id}`)
      reminders.value = reminders.value.filter(r => r.id !== id)
    } catch (e) {
      console.error('Failed to delete reminder:', e)
      throw e
    }
  }

  async function markNotificationSent(id: number) {
    try {
      const data = await post<Reminder>(`/reminders/${id}/mark-sent`, {})
      if (data) {
        const index = reminders.value.findIndex(r => r.id === id)
        if (index !== -1) {
          reminders.value[index] = data
        }
      }
      return data
    } catch (e) {
      console.error('Failed to mark reminder notification sent:', e)
      throw e
    }
  }

  return {
    // State
    reminders,
    loading,
    error,

    // Getters
    activeReminders,
    dueReminders,
    upcomingReminders,
    completedReminders,

    // Actions
    fetchReminders,
    fetchDueReminders,
    createReminder,
    updateReminder,
    deleteReminder,
    markNotificationSent
  }
})
