<script setup lang="ts">
import { ref, computed } from 'vue'

export interface Column {
  key: string
  label: string
  sortable?: boolean
}

const props = defineProps<{
  columns: Column[]
  data: any[]
  loading?: boolean
}>()

const sortKey = ref('')
const sortAsc = ref(true)

const sortBy = (key: string) => {
  const col = props.columns.find(c => c.key === key)
  if (!col?.sortable) return

  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const sortedData = computed(() => {
  if (!sortKey.value) return props.data
  
  return [...props.data].sort((a, b) => {
    let valA = a[sortKey.value]
    let valB = b[sortKey.value]
    
    // Handle nested properties if needed, simple implementation for now
    
    if (valA < valB) return sortAsc.value ? -1 : 1
    if (valA > valB) return sortAsc.value ? 1 : -1
    return 0
  })
})
</script>

<template>
  <div class="glass-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-surface-900/50 border-b border-white/10">
            <th 
              v-for="col in columns" 
              :key="col.key"
              class="px-6 py-4 text-sm font-medium text-slate-300 uppercase tracking-wider"
              :class="{ 'cursor-pointer hover:text-white transition-colors': col.sortable }"
              @click="sortBy(col.key)"
            >
              <div class="flex items-center gap-2">
                {{ col.label }}
                <span v-if="col.sortable" class="text-slate-500">
                  <template v-if="sortKey === col.key">
                    {{ sortAsc ? '↑' : '↓' }}
                  </template>
                  <template v-else>↕</template>
                </span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" v-for="i in 5" :key="`skeleton-${i}`" class="border-b border-white/5 animate-pulse">
            <td v-for="col in columns" :key="`skel-${col.key}`" class="px-6 py-4">
              <div class="h-4 bg-surface-700 rounded w-3/4"></div>
            </td>
          </tr>
          
          <template v-else-if="sortedData.length">
            <tr 
              v-for="(row, idx) in sortedData" 
              :key="idx"
              class="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
            >
              <td v-for="col in columns" :key="col.key" class="px-6 py-4 whitespace-nowrap">
                <slot :name="`cell-${col.key}`" :row="row">
                  {{ row[col.key] }}
                </slot>
              </td>
            </tr>
          </template>
          
          <tr v-else>
            <td :colspan="columns.length" class="px-6 py-12 text-center text-slate-400">
              <div class="flex flex-col items-center justify-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="opacity-50"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="3" x2="21" y1="9" y2="9"/><line x1="9" x2="9" y1="21" y2="9"/></svg>
                <p>No data available</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
