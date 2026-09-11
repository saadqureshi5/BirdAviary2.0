<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
  label: string
}>()

const badgeClass = computed(() => {
  switch (props.variant) {
    case 'success': return 'badge-success shadow-[0_0_10px_rgba(34,197,94,0.2)]'
    case 'warning': return 'badge-warning shadow-[0_0_10px_rgba(245,158,11,0.2)]'
    case 'danger': return 'badge-danger shadow-[0_0_10px_rgba(239,68,68,0.2)]'
    case 'info': return 'badge-info shadow-[0_0_10px_rgba(59,130,246,0.2)]'
    case 'neutral': 
    default: return 'badge-neutral'
  }
})
</script>

<template>
  <span class="badge" :class="badgeClass">
    <slot>{{ label }}</slot>
  </span>
</template>
