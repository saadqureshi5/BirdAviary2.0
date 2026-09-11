<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRemindersStore } from '@/stores/remindersStore'
import Modal from '@/components/shared/Modal.vue'
import Badge from '@/components/shared/Badge.vue'
import StatCard from '@/components/shared/StatCard.vue'
import type { Reminder, ReminderCreate, ReminderUpdate } from '@/types'

const remindersStore = useRemindersStore()

// State
const filter = ref<'all' | 'active' | 'due' | 'completed'>('active')
const showAddEditModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const reminderToEdit = ref<number | null>(null)
const reminderToDelete = ref<number | null>(null)
const loading = ref(false)

const form = ref<ReminderCreate & { is_active?: boolean }>({
  title: '',
  description: '',
  due_date: '',
  recurrence_pattern: ''
})

onMounted(async () => {
  await remindersStore.fetchReminders()
})

// Computed
const filteredReminders = computed(() => {
  const now = new Date()
  return remindersStore.reminders.filter(r => {
    if (filter.value === 'active') return r.is_active
    if (filter.value === 'completed') return !r.is_active
    if (filter.value === 'due') return r.is_active && new Date(r.due_date) <= now
    return true
  }).sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
})

const stats = computed(() => {
  const now = new Date()
  const next7Days = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  
  return {
    active: remindersStore.reminders.filter(r => r.is_active).length,
    dueToday: remindersStore.reminders.filter(r => {
      if (!r.is_active) return false
      const due = new Date(r.due_date)
      return due.toDateString() === now.toDateString() || due < now
    }).length,
    upcoming: remindersStore.reminders.filter(r => {
      if (!r.is_active) return false
      const due = new Date(r.due_date)
      return due > now && due <= next7Days
    }).length,
    completed: remindersStore.reminders.filter(r => !r.is_active).length
  }
})

// Methods
const openAddModal = () => {
  isEditing.value = false
  reminderToEdit.value = null
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  form.value = {
    title: '',
    description: '',
    due_date: now.toISOString().slice(0, 16),
    recurrence_pattern: ''
  }
  showAddEditModal.value = true
}

const openEditModal = (reminder: Reminder) => {
  isEditing.value = true
  reminderToEdit.value = reminder.id
  
  // Format due_date for datetime-local input
  const dateObj = new Date(reminder.due_date)
  const tzOffset = dateObj.getTimezoneOffset() * 60000
  const localIsoTime = (new Date(dateObj.getTime() - tzOffset)).toISOString().slice(0,16)
  
  form.value = {
    title: reminder.title,
    description: reminder.description || '',
    due_date: localIsoTime,
    recurrence_pattern: reminder.recurrence_pattern || '',
    is_active: reminder.is_active
  }
  showAddEditModal.value = true
}

const saveReminder = async () => {
  loading.value = true
  try {
    const formattedData = {
      ...form.value,
      // Ensure strict UTC standard if needed, or rely on backend to parse it
      due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : new Date().toISOString(),
      recurrence_pattern: form.value.recurrence_pattern || null
    }

    if (isEditing.value && reminderToEdit.value) {
      await remindersStore.updateReminder(reminderToEdit.value, formattedData as ReminderUpdate)
    } else {
      await remindersStore.createReminder(formattedData as ReminderCreate)
    }
    showAddEditModal.value = false
  } catch (e: any) {
    alert(e.message || 'An error occurred while saving the reminder.')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const confirmDelete = (id: number) => {
  reminderToDelete.value = id
  showDeleteModal.value = true
}

const executeDelete = async () => {
  if (reminderToDelete.value) {
    loading.value = true
    try {
      await remindersStore.deleteReminder(reminderToDelete.value)
      showDeleteModal.value = false
    } finally {
      loading.value = false
    }
  }
}

const toggleStatus = async (reminder: Reminder) => {
  await remindersStore.updateReminder(reminder.id, {
    is_active: !reminder.is_active
  })
}

const getStatusDetails = (reminder: Reminder) => {
  if (!reminder.is_active) {
    return { label: 'Completed', variant: 'neutral' as const }
  }
  const now = new Date()
  const due = new Date(reminder.due_date)
  if (due < now) {
    return { label: 'Overdue', variant: 'danger' as const }
  }
  
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(23, 59, 59, 999)
  
  if (due <= tomorrow) {
    return { label: 'Due Soon', variant: 'warning' as const }
  }
  return { label: 'Active', variant: 'success' as const }
}

const formatDate = (dateStr: string) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  }).format(new Date(dateStr))
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-bold text-white">Reminders</h1>
        <Badge variant="info">{{ remindersStore.reminders.length }} Total</Badge>
      </div>
      <button class="btn-primary" @click="openAddModal">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add Reminder
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard 
        title="Active Reminders" 
        :value="stats.active" 
        icon="🔔" 
        color="primary" 
      />
      <StatCard 
        title="Due Today / Overdue" 
        :value="stats.dueToday" 
        icon="⚠️" 
        color="danger" 
      />
      <StatCard 
        title="Upcoming (7 Days)" 
        :value="stats.upcoming" 
        icon="📅" 
        color="warning" 
      />
      <StatCard 
        title="Completed" 
        :value="stats.completed" 
        icon="✅" 
        color="success" 
      />
    </div>

    <!-- Main Content -->
    <div class="glass-card flex flex-col min-h-[500px]">
      <!-- Filters -->
      <div class="p-4 border-b border-surface-700/50 flex gap-2 overflow-x-auto hide-scrollbar">
        <button 
          v-for="f in ['all', 'active', 'due', 'completed']" 
          :key="f"
          @click="filter = f as any"
          class="px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all"
          :class="filter === f ? 'bg-surface-700 text-white shadow-sm' : 'text-slate-400 hover:text-white hover:bg-surface-800'"
        >
          {{ f.charAt(0).toUpperCase() + f.slice(1) }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="remindersStore.loading && remindersStore.reminders.length === 0" class="flex-1 flex justify-center items-center p-12">
        <svg class="animate-spin h-8 w-8 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredReminders.length === 0" class="flex-1 flex flex-col items-center justify-center p-12">
        <div class="w-16 h-16 bg-surface-800 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
        </div>
        <h3 class="text-xl font-medium text-white mb-2">No Reminders Found</h3>
        <p class="text-slate-400">
          {{ filter === 'all' ? 'You have no reminders yet. Create one to get started!' : `You have no ${filter} reminders.` }}
        </p>
        <button v-if="filter === 'all'" class="btn-primary mt-6" @click="openAddModal">Add Reminder</button>
      </div>

      <!-- Reminder List -->
      <div v-else class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="reminder in filteredReminders" 
          :key="reminder.id" 
          class="glass-card p-5 relative overflow-hidden group transition-all"
          :class="{'opacity-60': !reminder.is_active}"
        >
          <!-- Status Line Indicator -->
          <div 
            class="absolute left-0 top-0 bottom-0 w-1" 
            :class="{
              'bg-emerald-500': getStatusDetails(reminder).variant === 'success',
              'bg-red-500': getStatusDetails(reminder).variant === 'danger',
              'bg-amber-500': getStatusDetails(reminder).variant === 'warning',
              'bg-slate-600': getStatusDetails(reminder).variant === 'neutral'
            }"
          ></div>
          
          <div class="pl-2">
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-semibold text-lg text-white" :class="{'line-through text-slate-400': !reminder.is_active}">
                {{ reminder.title }}
              </h3>
              <Badge :variant="getStatusDetails(reminder).variant">
                {{ getStatusDetails(reminder).label }}
              </Badge>
            </div>
            
            <p v-if="reminder.description" class="text-slate-400 text-sm mb-4 line-clamp-2">
              {{ reminder.description }}
            </p>
            
            <div class="space-y-2 mb-6">
              <div class="flex items-center text-sm text-slate-300">
                <svg class="w-4 h-4 mr-2 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span :class="{'text-red-400 font-medium': getStatusDetails(reminder).variant === 'danger'}">
                  {{ formatDate(reminder.due_date) }}
                </span>
              </div>
              
              <div v-if="reminder.recurrence_pattern" class="flex items-center text-sm text-slate-300">
                <svg class="w-4 h-4 mr-2 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Repeats: <span class="capitalize ml-1">{{ reminder.recurrence_pattern }}</span>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex gap-2 pt-4 border-t border-surface-700/50">
              <button 
                class="flex-1 btn-secondary py-1.5 text-sm flex justify-center items-center"
                @click="toggleStatus(reminder)"
              >
                <svg v-if="reminder.is_active" class="w-4 h-4 mr-1 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-1 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                {{ reminder.is_active ? 'Complete' : 'Reactivate' }}
              </button>
              
              <button class="btn-secondary py-1.5 px-3 text-slate-300 hover:text-white" @click="openEditModal(reminder)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              
              <button class="btn-secondary py-1.5 px-3 text-red-400 hover:text-red-300 border-red-900/30 hover:bg-red-900/20" @click="confirmDelete(reminder.id)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal :show="showAddEditModal" :title="isEditing ? 'Edit Reminder' : 'Add Reminder'" @close="showAddEditModal = false">
      <div class="space-y-4">
        <div>
          <label class="label block mb-2">Title *</label>
          <input v-model="form.title" type="text" class="input-field w-full" placeholder="e.g. Check eggs in nest box #4" required />
        </div>
        
        <div>
          <label class="label block mb-2">Description</label>
          <textarea v-model="form.description" class="input-field w-full h-24 resize-none" placeholder="Optional details..."></textarea>
        </div>
        
        <div>
          <label class="label block mb-2">Due Date & Time *</label>
          <input v-model="form.due_date" type="datetime-local" class="input-field w-full" required />
        </div>
        
        <div>
          <label class="label block mb-2">Recurrence Pattern</label>
          <select v-model="form.recurrence_pattern" class="input-field w-full">
            <option value="">None (One-time)</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
      </div>
      
      <template #footer>
        <button class="btn-ghost mr-3" @click="showAddEditModal = false" :disabled="loading">Cancel</button>
        <button class="btn-primary" @click="saveReminder" :disabled="!form.title || !form.due_date || loading">
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isEditing ? 'Update' : 'Create' }}
        </button>
      </template>
    </Modal>

    <!-- Delete Modal -->
    <Modal :show="showDeleteModal" title="Delete Reminder" @close="showDeleteModal = false">
      <p class="text-slate-300">Are you sure you want to delete this reminder? This action cannot be undone.</p>
      <template #footer>
        <button class="btn-ghost mr-3" @click="showDeleteModal = false" :disabled="loading">Cancel</button>
        <button class="btn-primary bg-red-600 hover:bg-red-700 text-white shadow-red-500/20" @click="executeDelete" :disabled="loading">
          Delete
        </button>
      </template>
    </Modal>
  </div>
</template>
