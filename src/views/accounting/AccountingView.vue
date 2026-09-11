<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAccountingStore } from '@/stores/accountingStore'
import { storeToRefs } from 'pinia'
import Modal from '@/components/shared/Modal.vue'
import StatCard from '@/components/shared/StatCard.vue'
import Badge from '@/components/shared/Badge.vue'
import DataTable from '@/components/shared/DataTable.vue'
import type { ExpenseCreate } from '@/types'

const accountingStore = useAccountingStore()
const { expenses, analytics, loading } = storeToRefs(accountingStore)

// Filters
const currentDate = new Date()
const selectedYear = ref<number>(currentDate.getFullYear())
const selectedMonth = ref<number | 'all'>('all')

const currentYear = currentDate.getFullYear()
const availableYears = computed(() => {
  const years = new Set(expenses.value.map(e => e.year))
  years.add(currentYear)
  if (analytics.value) {
    analytics.value.yearly_totals.forEach(yt => years.add(yt.year))
  }
  return Array.from(years).sort((a, b) => b - a)
})

const months = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
]

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchData = () => {
  const month = selectedMonth.value === 'all' ? undefined : selectedMonth.value
  accountingStore.fetchExpenses(selectedYear.value, month)
  accountingStore.fetchAnalytics()
}

// Computed Stats
const totalExpenses = computed(() => analytics.value?.total_expenses || 0)
const thisMonthExpenses = computed(() => {
  if (!analytics.value) return 0
  const monthData = analytics.value.monthly_totals.find(
    m => m.year === currentYear && m.month === currentDate.getMonth() + 1
  )
  return monthData?.total || 0
})
const thisYearExpenses = computed(() => {
  if (!analytics.value) return 0
  const yearData = analytics.value.yearly_totals.find(y => y.year === currentYear)
  return yearData?.total || 0
})
const avgMonthlyExpenses = computed(() => {
  if (!analytics.value || analytics.value.monthly_totals.length === 0) return 0
  return totalExpenses.value / analytics.value.monthly_totals.length
})

// Table Columns
const tableColumns = [
  { key: 'date', label: 'Date', sortable: true },
  { key: 'description', label: 'Description', sortable: true },
  { key: 'amount', label: 'Amount', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false }
]

// Modal State
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const editingExpenseId = ref<number | null>(null)
const expenseToDelete = ref<number | null>(null)

const getTodayDateString = () => {
  const d = new Date()
  return d.toISOString().split('T')[0]
}

const formData = ref({
  date: getTodayDateString(),
  description: '',
  amount: 0
})

const resetForm = () => {
  formData.value = {
    date: getTodayDateString(),
    description: '',
    amount: 0
  }
  editingExpenseId.value = null
}

const openAddModal = () => {
  resetForm()
  isModalOpen.value = true
}

const openEditModal = (expense: any) => {
  formData.value = {
    date: expense.date,
    description: expense.description,
    amount: expense.amount
  }
  editingExpenseId.value = expense.id
  isModalOpen.value = true
}

const confirmDelete = (id: number) => {
  expenseToDelete.value = id
  isDeleteModalOpen.value = true
}

const handleSave = async () => {
  // Parse year and month from the date string
  const dateObj = new Date(formData.value.date)
  const payload: ExpenseCreate = {
    ...formData.value,
    year: dateObj.getFullYear(),
    month: dateObj.getMonth() + 1
  }
  
  if (editingExpenseId.value) {
    await accountingStore.updateExpense(editingExpenseId.value, payload)
  } else {
    await accountingStore.createExpense(payload)
  }
  isModalOpen.value = false
  fetchData()
}

const handleDelete = async () => {
  if (expenseToDelete.value) {
    await accountingStore.deleteExpense(expenseToDelete.value)
    isDeleteModalOpen.value = false
    expenseToDelete.value = null
    fetchData()
  }
}

// Chart Helpers
const monthlyChartData = computed(() => {
  if (!analytics.value) return []
  // Get data for selected year
  const yearData = analytics.value.monthly_totals.filter(m => m.year === selectedYear.value)
  
  // Fill in missing months with 0
  const fullYear = months.map(m => {
    const existing = yearData.find(d => d.month === m.value)
    return {
      month: m.label.substring(0, 3),
      total: existing ? existing.total : 0
    }
  })
  
  return fullYear
})

const maxMonthlyTotal = computed(() => {
  if (monthlyChartData.value.length === 0) return 1
  return Math.max(...monthlyChartData.value.map(d => d.total), 1)
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Accounting</h1>
        <p class="text-slate-400">Track and manage aviary expenses</p>
      </div>
      <button @click="openAddModal" class="btn-primary flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Add Expense
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total All Time"
        :value="formatCurrency(totalExpenses)"
        icon="💰"
      />
      <StatCard
        title="This Month"
        :value="formatCurrency(thisMonthExpenses)"
        icon="📅"
      />
      <StatCard
        title="This Year"
        :value="formatCurrency(thisYearExpenses)"
        icon="📊"
      />
      <StatCard
        title="Avg Monthly"
        :value="formatCurrency(avgMonthlyExpenses)"
        icon="📈"
      />
    </div>

    <!-- Monthly Summary Chart (CSS-based) -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-semibold text-white mb-6">Monthly Expenses ({{ selectedYear }})</h3>
      
      <div v-if="loading && expenses.length === 0" class="h-48 flex justify-center items-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
      
      <div v-else class="flex items-end h-48 gap-2 sm:gap-4">
        <div v-for="data in monthlyChartData" :key="data.month" class="flex-1 flex flex-col items-center justify-end h-full group relative">
          <!-- Tooltip -->
          <div class="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-xs text-white p-2 rounded shadow-lg whitespace-nowrap pointer-events-none z-10">
            {{ formatCurrency(data.total) }}
          </div>
          
          <!-- Bar -->
          <div 
            class="w-full max-w-[40px] bg-indigo-500/80 hover:bg-indigo-400 rounded-t-md transition-all duration-300"
            :style="{ height: `${(data.total / maxMonthlyTotal) * 100}%`, minHeight: data.total > 0 ? '4px' : '0' }"
          ></div>
          
          <!-- Label -->
          <span class="text-xs text-slate-400 mt-2">{{ data.month }}</span>
        </div>
      </div>
    </div>

    <!-- Filters and Data Table -->
    <div class="glass-card overflow-hidden flex flex-col">
      <!-- Filters header -->
      <div class="p-4 border-b border-slate-700/50 flex flex-col sm:flex-row gap-4 justify-between items-center bg-slate-800/30">
        <h3 class="text-lg font-semibold text-white">Expense Records</h3>
        
        <div class="flex items-center gap-3 w-full sm:w-auto">
          <select v-model="selectedYear" @change="fetchData" class="input-field py-1.5 min-w-[100px]">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
          
          <select v-model="selectedMonth" @change="fetchData" class="input-field py-1.5 min-w-[120px]">
            <option value="all">All Months</option>
            <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
          </select>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="expenses.length === 0" class="py-16 text-center">
        <div class="text-5xl mb-4">💸</div>
        <h3 class="text-xl font-semibold text-white mb-2">No expenses found</h3>
        <p class="text-slate-400 mb-6">Record your first expense to start tracking.</p>
        <button @click="openAddModal" class="btn-primary">Add Expense</button>
      </div>

      <!-- DataTable -->
      <div v-else class="p-0">
        <DataTable :columns="tableColumns" :data="expenses">
          <template #cell-date="{ row }">
            <span class="text-slate-300">{{ formatDate(row.date) }}</span>
          </template>
          
          <template #cell-description="{ row }">
            <span class="text-white font-medium">{{ row.description }}</span>
          </template>
          
          <template #cell-amount="{ row }">
            <span class="text-rose-400 font-medium">{{ formatCurrency(row.amount) }}</span>
          </template>
          
          <template #cell-actions="{ row }">
            <div class="flex gap-2">
              <button @click="openEditModal(row)" class="text-indigo-400 hover:text-indigo-300 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
              <button @click="confirmDelete(row.id)" class="text-red-400 hover:text-red-300 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal :show="isModalOpen" :title="editingExpenseId ? 'Edit Expense' : 'Add Expense'" @close="isModalOpen = false">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="label">Date</label>
          <input v-model="formData.date" type="date" required class="input-field" />
        </div>
        
        <div>
          <label class="label">Description</label>
          <input v-model="formData.description" type="text" required class="input-field" placeholder="What was this expense for?" />
        </div>
        
        <div>
          <label class="label">Amount ($)</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="text-slate-400">$</span>
            </div>
            <input 
              v-model.number="formData.amount" 
              type="number" 
              step="0.01" 
              min="0" 
              required 
              class="input-field pl-8" 
              placeholder="0.00" 
            />
          </div>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="isModalOpen = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Expense' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal :show="isDeleteModalOpen" title="Delete Expense" @close="isDeleteModalOpen = false">
      <div class="p-2">
        <p class="text-slate-300 mb-6">Are you sure you want to delete this expense record? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <button @click="isDeleteModalOpen = false" class="btn-secondary">Cancel</button>
          <button @click="handleDelete" class="btn-primary bg-red-600 hover:bg-red-700 text-white" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>
