<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSalesStore } from '@/stores/salesStore'
import { useBirdsStore } from '@/stores/birdsStore'
import StatCard from '@/components/shared/StatCard.vue'
import DataTable from '@/components/shared/DataTable.vue'
import Badge from '@/components/shared/Badge.vue'
import Modal from '@/components/shared/Modal.vue'
import type { SaleWithBird, SaleUpdate } from '@/types'

const router = useRouter()
const salesStore = useSalesStore()
const birdsStore = useBirdsStore()

const searchQuery = ref('')
const selectedCategory = ref('')
const showEditModal = ref(false)
const editingSale = ref<SaleWithBird | null>(null)
const editForm = ref<SaleUpdate>({})
const submitting = ref(false)

onMounted(async () => {
  await Promise.all([
    salesStore.fetchSales(),
    salesStore.fetchAnalytics(),
    birdsStore.fetchCategories()
  ])
})

// Debounced search
let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, (q) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!q.trim()) {
    salesStore.searchResults = []
    return
  }
  searchTimeout = setTimeout(() => {
    salesStore.searchSales(q.trim())
  }, 300)
})

const displayedSales = computed(() => {
  let list = salesStore.sales
  if (searchQuery.value.trim() && salesStore.searchResults.length > 0) {
    list = salesStore.searchResults
  }
  
  if (selectedCategory.value) {
    list = list.filter(s => String(s.bird?.category_id) === String(selectedCategory.value))
  }
  
  return list
})

const computedAnalytics = computed(() => {
  const totalSales = displayedSales.value.length
  const totalRevenue = displayedSales.value.reduce((sum, s) => sum + (s.sale_price || 0), 0)
  
  // Group by month
  const monthMap = new Map()
  displayedSales.value.forEach(s => {
    if (!s.date_sold) return
    const d = new Date(s.date_sold)
    const key = `${d.getFullYear()}-${d.getMonth() + 1}`
    if (!monthMap.has(key)) {
      monthMap.set(key, { year: d.getFullYear(), month: d.getMonth() + 1, count: 0, revenue: 0 })
    }
    const stat = monthMap.get(key)
    stat.count++
    stat.revenue += (s.sale_price || 0)
  })
  
  const salesByMonth = Array.from(monthMap.values()).sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year
    return a.month - b.month
  })
  
  return {
    total_sales: totalSales,
    total_revenue: totalRevenue,
    sales_by_month: salesByMonth,
    avg_price: totalSales > 0 ? totalRevenue / totalSales : 0
  }
})

const tableColumns = [
  { key: 'bird', label: 'Bird', sortable: false },
  { key: 'buyer_name', label: 'Buyer', sortable: true },
  { key: 'sale_price', label: 'Price', sortable: true },
  { key: 'date_sold', label: 'Date Sold', sortable: true },
  { key: 'notes', label: 'Notes', sortable: false },
  { key: 'actions', label: '', sortable: false }
]

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const openEditModal = (sale: SaleWithBird) => {
  editingSale.value = sale
  editForm.value = {
    date_sold: sale.date_sold?.split('T')[0] || '',
    sale_price: sale.sale_price,
    buyer_name: sale.buyer_name || '',
    notes: sale.notes || ''
  }
  showEditModal.value = true
}

const submitEdit = async () => {
  if (!editingSale.value || submitting.value) return

  try {
    submitting.value = true
    await salesStore.updateSale(editingSale.value.id, editForm.value)
    showEditModal.value = false
    editingSale.value = null
  } catch (e) {
    console.error('Error updating sale:', e)
  } finally {
    submitting.value = false
  }
}

const getMonthName = (month: number) => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months[month - 1] || ''
}

const deleteSaleRecord = async (sale: SaleWithBird) => {
  if (confirm("Are you sure you want to delete this sale? The bird will be returned to your inventory as 'In Stock'.")) {
    await salesStore.deleteSale(sale.id)
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
          Sales Management
          <span class="bg-emerald-500/20 text-emerald-400 text-sm py-1 px-3 rounded-full border border-emerald-500/30">
            {{ displayedSales.length }} records
          </span>
        </h2>
        <p class="text-slate-400 text-sm mt-1">Track sales, revenue, and buyer information</p>
      </div>
      
      <button @click="router.push('/sales/mark-sold')" class="btn-primary flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        Mark Bird as Sold
      </button>
    </div>

    <!-- Stats Area -->
    <div v-if="displayedSales.length >= 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard 
        title="Total Sales" 
        :value="computedAnalytics.total_sales" 
        icon="📊"
        color="primary"
      />
      <StatCard 
        title="Total Revenue" 
        :value="formatCurrency(computedAnalytics.total_revenue)" 
        icon="💰" 
        color="success"
      />
      <StatCard 
        title="This Month" 
        :value="computedAnalytics.sales_by_month.length > 0 ? computedAnalytics.sales_by_month[computedAnalytics.sales_by_month.length - 1].count : 0" 
        icon="📅" 
        color="warning"
      />
      <StatCard 
        title="Avg. Sale Price" 
        :value="computedAnalytics.total_sales > 0 ? formatCurrency(computedAnalytics.avg_price) : '$0'" 
        icon="📈" 
        color="primary"
      />
    </div>

    <!-- Search & Filters -->
    <div class="glass-card p-4 flex flex-col md:flex-row gap-4 justify-between items-center">
      <div class="flex flex-col sm:flex-row gap-4 w-full md:w-auto flex-1">
        <div class="relative w-full md:w-96">
          <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Search by ring ID, bird name, or buyer..." 
            class="input-field pl-9 text-sm py-1.5 h-10 w-full"
          >
        </div>
        
        <select v-model="selectedCategory" class="input-field sm:max-w-[200px] h-10 appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.5rem_center] bg-[length:1em_1em] pr-8">
          <option value="">All Categories</option>
          <option v-for="cat in birdsStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Content Area -->
    <div v-if="salesStore.loading && salesStore.sales.length === 0" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
    
    <div v-else-if="displayedSales.length === 0 && !searchQuery" class="glass-card py-20 flex flex-col items-center justify-center text-center">
      <div class="w-24 h-24 bg-surface-800 rounded-full flex items-center justify-center mb-6">
        <span class="text-4xl opacity-50">💰</span>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">No sales recorded</h3>
      <p class="text-slate-400 max-w-md mb-6">
        You haven't recorded any sales yet. Mark a bird as sold to start tracking your sales.
      </p>
      <button @click="router.push('/sales/mark-sold')" class="btn-primary">Mark Bird as Sold</button>
    </div>

    <div v-else-if="displayedSales.length === 0 && searchQuery" class="glass-card py-16 flex flex-col items-center justify-center text-center">
      <div class="w-20 h-20 bg-surface-800 rounded-full flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-slate-500"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      </div>
      <h3 class="text-lg font-medium text-white mb-2">No results found</h3>
      <p class="text-slate-400 text-sm">Try a different search term</p>
    </div>

    <template v-else>
      <DataTable 
        :columns="tableColumns" 
        :data="displayedSales"
      >
        <template #cell-bird="{ row }">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-surface-700 overflow-hidden shrink-0 border border-white/5">
              <img v-if="row.bird?.photo_url" :src="'/' + row.bird.photo_url" class="w-full h-full object-cover">
              <span v-else class="flex items-center justify-center w-full h-full text-sm">🐦</span>
            </div>
            <div>
              <div class="font-medium text-white">{{ row.bird?.name || 'Unnamed' }}</div>
              <div class="text-xs text-slate-400">{{ row.bird?.ring_id || 'No ring ID' }}</div>
            </div>
          </div>
        </template>
        
        <template #cell-buyer_name="{ row }">
          <span class="text-white">{{ row.buyer_name || '-' }}</span>
        </template>
        
        <template #cell-sale_price="{ row }">
          <span class="font-semibold text-emerald-400">{{ formatCurrency(row.sale_price) }}</span>
        </template>
        
        <template #cell-date_sold="{ row }">
          <span class="text-slate-300">{{ formatDate(row.date_sold) }}</span>
        </template>
        
        <template #cell-notes="{ row }">
          <span class="text-slate-400 text-sm truncate max-w-[200px] block">{{ row.notes || '-' }}</span>
        </template>
        
        <template #cell-actions="{ row }">
          <div class="flex justify-end gap-2">
            <button 
              v-if="row.bird"
              @click="router.push(`/birds/${row.bird.id}`)"
              class="text-primary-400 hover:text-primary-300 bg-primary-500/10 hover:bg-primary-500/20 px-3 py-1.5 rounded transition-colors text-sm"
            >
              View Bird
            </button>
            <button 
              @click="openEditModal(row)"
              class="text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 px-3 py-1.5 rounded transition-colors text-sm"
            >
              Edit
            </button>
            <button 
              @click="deleteSaleRecord(row)"
              class="text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded transition-colors text-sm"
            >
              Delete
            </button>
          </div>
        </template>
      </DataTable>
    </template>

    <!-- Monthly Revenue Breakdown -->
    <div v-if="salesStore.analytics && salesStore.analytics.sales_by_month.length > 0" class="glass-card p-6">
      <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
        Monthly Revenue
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div 
          v-for="item in salesStore.analytics.sales_by_month" 
          :key="`${item.year}-${item.month}`"
          class="bg-surface-800 rounded-xl p-4 border border-white/5 hover:border-primary-500/20 transition-colors"
        >
          <div class="text-xs text-slate-400 mb-1">{{ getMonthName(item.month) }} {{ item.year }}</div>
          <div class="text-lg font-bold text-white">{{ formatCurrency(item.revenue) }}</div>
          <div class="text-xs text-slate-500 mt-1">{{ item.count }} sale{{ item.count !== 1 ? 's' : '' }}</div>
        </div>
      </div>
    </div>

    <!-- Category Revenue Breakdown -->
    <div v-if="salesStore.analytics && salesStore.analytics.sales_by_category.length > 0" class="glass-card p-6">
      <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>
        Revenue by Category
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div 
          v-for="item in salesStore.analytics.sales_by_category" 
          :key="item.category_name"
          class="flex items-center justify-between bg-surface-800 rounded-xl p-4 border border-white/5"
        >
          <div>
            <div class="font-medium text-white">{{ item.category_name }}</div>
            <div class="text-xs text-slate-400 mt-1">{{ item.count }} sale{{ item.count !== 1 ? 's' : '' }}</div>
          </div>
          <div class="text-right">
            <div class="text-lg font-bold text-emerald-400">{{ formatCurrency(item.revenue) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Sale Modal -->
    <Modal :show="showEditModal" title="Edit Sale" @close="showEditModal = false">
      <form @submit.prevent="submitEdit" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="label">Sale Date</label>
            <input v-model="editForm.date_sold" type="date" class="input-field">
          </div>
          
          <div class="space-y-2">
            <label class="label">Sale Price</label>
            <input v-model.number="editForm.sale_price" type="number" step="0.01" min="0" class="input-field" placeholder="Enter amount">
          </div>
          
          <div class="space-y-2">
            <label class="label">Buyer Name</label>
            <input v-model="editForm.buyer_name" type="text" class="input-field" placeholder="Buyer name">
          </div>
          
          <div class="space-y-2 md:col-span-2">
            <label class="label">Notes</label>
            <textarea v-model="editForm.notes" rows="3" class="input-field resize-none" placeholder="Add any notes..."></textarea>
          </div>
        </div>
      </form>

      <template #footer>
        <button type="button" @click="showEditModal = false" class="btn-secondary">Cancel</button>
        <button 
          @click="submitEdit" 
          class="btn-primary" 
          :disabled="submitting"
          :class="{'opacity-50 cursor-not-allowed': submitting}"
        >
          <span v-if="submitting" class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full border-2 border-white/20 border-t-white animate-spin"></div>
            Saving...
          </span>
          <span v-else>Save Changes</span>
        </button>
      </template>
    </Modal>
  </div>
</template>
