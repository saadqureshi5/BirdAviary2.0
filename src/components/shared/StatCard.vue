<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  icon: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'primary' | 'success' | 'warning' | 'danger'
}>()

const getColorClass = (color: string = 'primary') => {
  switch (color) {
    case 'success': return 'from-green-500 to-green-400'
    case 'warning': return 'from-amber-500 to-amber-400'
    case 'danger': return 'from-red-500 to-red-400'
    case 'primary': 
    default: return 'from-primary-600 to-primary-400'
  }
}
</script>

<template>
  <div class="glass-card relative overflow-hidden group hover:scale-[1.02] transition-transform duration-300 cursor-pointer">
    <!-- Gradient accent line -->
    <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b opacity-80" :class="getColorClass(color)"></div>
    
    <div class="p-6 flex flex-col h-full relative z-10">
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-slate-400 font-medium text-sm uppercase tracking-wider">{{ title }}</h3>
        <span class="text-2xl drop-shadow-md opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all">{{ icon }}</span>
      </div>
      
      <div class="mt-auto">
        <div class="text-3xl font-bold text-white mb-2 animate-slide-up">{{ value }}</div>
        
        <div v-if="trend && trendValue" class="flex items-center text-sm font-medium">
          <span 
            class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-900/50"
            :class="{
              'text-green-400': trend === 'up',
              'text-red-400': trend === 'down',
              'text-slate-400': trend === 'neutral'
            }"
          >
            <svg v-if="trend === 'up'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>
            <svg v-else-if="trend === 'down'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="m19 12-7 7-7-7"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>
            {{ trendValue }}
          </span>
          <span class="ml-2 text-slate-500 text-xs">vs last month</span>
        </div>
      </div>
    </div>
    
    <!-- Background glow effect on hover -->
    <div class="absolute -right-10 -bottom-10 w-32 h-32 rounded-full blur-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-500" :class="getColorClass(color).replace('from-', 'bg-').split(' ')[0]"></div>
  </div>
</template>
