<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBirdsStore } from '@/stores/birdsStore'
import StatCard from '@/components/shared/StatCard.vue'

const router = useRouter()
const birdsStore = useBirdsStore()
const userName = ref('Admin')

const formatTimeAgo = (timestamp: string) => {
  const now = new Date()
  const date = new Date(timestamp)
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  return date.toLocaleDateString()
}

onMounted(() => {
  const storedName = localStorage.getItem('userName')
  if (storedName) {
    userName.value = storedName
  }
  
  birdsStore.fetchBirdStats()
  birdsStore.fetchCategories()
  birdsStore.fetchRecentActivity()
})
</script>

<template>
  <div class="space-y-8 pb-8 animate-fade-in">
    <!-- Welcome Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface-800/40 p-6 rounded-2xl border border-white/5 backdrop-blur-sm relative overflow-hidden">
      <!-- Decorative gradient -->
      <div class="absolute right-0 top-0 w-64 h-64 bg-primary-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none"></div>
      
      <div>
        <h2 class="text-2xl font-bold text-white mb-1">Welcome back, {{ userName }}! 👋</h2>
        <p class="text-slate-400">Here's what's happening in your aviary today.</p>
      </div>
      
      <div class="flex gap-3 relative z-10">
        <button @click="router.push('/birds/add')" class="btn-primary flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          Add Bird
        </button>
        <button @click="router.push('/breeding')" class="btn-secondary flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21a9 9 0 0 0 9-9c0-5-4-9-9-9s-9 4-9 9a9 9 0 0 0 9 9z"/><path d="M9 12a3 3 0 1 0 6 0 3 3 0 1 0-6 0z"/></svg>
          Create Pair
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Total Birds"
        :value="birdsStore.birdStats.total_birds"
        icon="🐦"
        trend="up"
        trendValue="12%"
        color="primary"
      />
      <StatCard
        title="In Stock"
        :value="birdsStore.birdStats.in_stock"
        icon="✨"
        trend="up"
        trendValue="5%"
        color="success"
      />
      <StatCard
        title="Birds Sold"
        :value="birdsStore.birdStats.sold"
        icon="💰"
        trend="neutral"
        trendValue="0%"
        color="warning"
      />
      <StatCard
        title="Active Pairs"
        :value="birdsStore.birdStats.active_pairs"
        icon="❤️"
        trend="up"
        trendValue="2%"
        color="danger"
      />
    </div>

    <!-- Main Content Area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Category Breakdown -->
      <div class="lg:col-span-2 glass-card p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-white flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
            Category Breakdown
          </h3>
          <button @click="router.push('/birds')" class="text-sm text-primary-400 hover:text-primary-300 transition-colors">View All Birds &rarr;</button>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div 
            v-for="cat in birdsStore.categories" 
            :key="cat.id"
            class="bg-surface-800/50 p-4 rounded-xl border border-white/5 hover:bg-surface-800 transition-colors flex justify-between items-center group cursor-pointer"
            @click="router.push({ path: '/birds', query: { category: cat.id } })"
          >
            <div>
              <div class="font-medium text-white group-hover:text-primary-400 transition-colors">{{ cat.name }}</div>
              <div class="text-xs text-slate-400 mt-1">{{ cat.description || 'No description' }}</div>
            </div>
            <div class="w-10 h-10 rounded-full bg-surface-900 border border-white/10 flex items-center justify-center text-lg font-bold text-slate-300 shadow-inner">
              {{ cat.bird_count }}
            </div>
          </div>
          
          <div v-if="birdsStore.categories.length === 0 && !birdsStore.loading" class="col-span-2 text-center py-8 text-slate-400">
            No categories found. Start by adding a bird!
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-400"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          Recent Activity
        </h3>
        
        <div v-if="birdsStore.recentActivity.length === 0 && !birdsStore.loading" class="text-center py-8 text-slate-400">
          No recent activity yet.
        </div>
        
        <div v-else class="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent max-h-96 overflow-y-auto pr-2 custom-scrollbar">
          <div 
            v-for="(item, index) in birdsStore.recentActivity" 
            :key="item.id"
            class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group"
            :class="{ 'is-active': index === 0 }"
          >
            <!-- Timeline circle icon -->
            <div 
              class="flex items-center justify-center w-10 h-10 rounded-full border border-white/10 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10"
              :class="{
                'bg-primary-500/20 text-primary-400': item.icon === 'add',
                'bg-amber-500/20 text-amber-400': item.icon === 'sale' || item.icon === 'expense',
                'bg-pink-500/20 text-pink-400': item.icon === 'pair' || item.icon === 'egg' || item.icon === 'chick',
                'bg-red-500/20 text-red-400': item.icon === 'remove',
                'bg-blue-500/20 text-blue-400': item.icon === 'update' || item.icon === 'dna',
                'bg-purple-500/20 text-purple-400': item.icon === 'reminder',
                'bg-green-500/20 text-green-400': item.icon === 'food',
                'bg-surface-900': !['add','sale','expense','pair','egg','chick','remove','update','dna','reminder','food'].includes(item.icon),
              }"
            >
              <!-- Add icon -->
              <svg v-if="item.icon === 'add'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
              <!-- Sale icon -->
              <svg v-else-if="item.icon === 'sale' || item.icon === 'expense'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              <!-- Pair/egg/chick icon -->
              <svg v-else-if="item.icon === 'pair' || item.icon === 'egg' || item.icon === 'chick'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
              <!-- Remove icon -->
              <svg v-else-if="item.icon === 'remove'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
              <!-- Update/dna icon -->
              <svg v-else-if="item.icon === 'update' || item.icon === 'dna'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
              <!-- Reminder icon -->
              <svg v-else-if="item.icon === 'reminder'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
              <!-- Food icon -->
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
            </div>
            <!-- Content card -->
            <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-white/5 bg-surface-800/50">
              <div class="flex items-center justify-between mb-1">
                <div class="font-medium text-white text-sm">{{ item.title }}</div>
                <div class="text-xs text-slate-500">{{ formatTimeAgo(item.timestamp) }}</div>
              </div>
              <div class="text-xs text-slate-400">{{ item.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
