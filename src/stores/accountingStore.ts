import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { Expense, ExpenseCreate, ExpenseUpdate, ExpenseAnalytics } from '@/types'

export const useAccountingStore = defineStore('accounting', () => {
  const { get, post, put, del, loading, error } = useApi()
  const expenses = ref<Expense[]>([])
  const analytics = ref<ExpenseAnalytics | null>(null)

  async function fetchExpenses(year?: number, month?: number) {
    try {
      const params = new URLSearchParams()
      if (year) params.append('year', year.toString())
      if (month) params.append('month', month.toString())
      
      const queryString = params.toString()
      const url = queryString ? `/expenses?${queryString}` : '/expenses'
      
      const data = await get<Expense[]>(url)
      if (data) expenses.value = data
    } catch (e) {
      console.error('Failed to fetch expenses:', e)
    }
  }

  async function createExpense(expenseData: ExpenseCreate) {
    try {
      const newExpense = await post<Expense>('/expenses', expenseData)
      if (newExpense) {
        expenses.value.unshift(newExpense)
        // Refresh analytics when data changes
        await fetchAnalytics()
      }
      return newExpense
    } catch (e) {
      console.error('Failed to create expense:', e)
      return null
    }
  }

  async function updateExpense(id: number, expenseData: ExpenseUpdate) {
    try {
      const updatedExpense = await put<Expense>(`/expenses/${id}`, expenseData)
      if (updatedExpense) {
        const index = expenses.value.findIndex(e => e.id === id)
        if (index !== -1) {
          expenses.value[index] = updatedExpense
        }
        await fetchAnalytics()
      }
      return updatedExpense
    } catch (e) {
      console.error('Failed to update expense:', e)
      return null
    }
  }

  async function deleteExpense(id: number) {
    try {
      await del(`/expenses/${id}`)
      expenses.value = expenses.value.filter(e => e.id !== id)
      await fetchAnalytics()
      return true
    } catch (e) {
      console.error('Failed to delete expense:', e)
      return false
    }
  }

  async function fetchAnalytics() {
    try {
      const data = await get<ExpenseAnalytics>('/expenses/analytics')
      if (data) analytics.value = data
    } catch (e) {
      console.error('Failed to fetch expense analytics:', e)
    }
  }

  return {
    expenses,
    analytics,
    loading,
    error,
    fetchExpenses,
    createExpense,
    updateExpense,
    deleteExpense,
    fetchAnalytics
  }
})
