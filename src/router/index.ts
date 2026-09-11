import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- Auth Routes (no layout) ---
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { title: 'Sign In', public: true }
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/views/auth/AuthCallbackView.vue'),
      meta: { title: 'Authenticating...', public: true }
    },
    {
      path: '/subscription-expired',
      name: 'subscription-expired',
      component: () => import('@/views/auth/SubscriptionExpiredView.vue'),
      meta: { title: 'Subscription Expired', public: true }
    },
    // --- App Routes (with layout, require auth) ---
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: '/birds',
      name: 'birds',
      component: () => import('@/views/birds/BirdsListView.vue'),
      meta: { title: 'Birds Inventory' }
    },
    {
      path: '/birds/add',
      name: 'add-bird',
      component: () => import('@/views/birds/AddBirdView.vue'),
      meta: { title: 'Add New Bird' }
    },
    {
      path: '/birds/:id/pedigree',
      name: 'bird-pedigree',
      component: () => import('@/views/birds/GenerationalView.vue'),
      meta: { title: 'Pedigree Tree' }
    },
    {
      path: '/birds/:id/edit',
      name: 'edit-bird',
      component: () => import('@/views/birds/EditBirdView.vue'),
      meta: { title: 'Edit Bird' }
    },
    {
      path: '/birds/:id',
      name: 'bird-profile',
      component: () => import('@/views/birds/BirdProfileView.vue'),
      meta: { title: 'Bird Profile' }
    },
    {
      path: '/breeding',
      name: 'breeding',
      component: () => import('@/views/breeding/PairsOverviewView.vue'),
      meta: { title: 'Breeding Pairs' }
    },
    {
      path: '/breeding/create',
      name: 'breeding-create',
      component: () => import('@/views/breeding/CreatePairView.vue'),
      meta: { title: 'Create Breeding Pair' }
    },
    {
      path: '/breeding/analytics',
      name: 'breeding-analytics',
      component: () => import('@/views/breeding/BreedingAnalyticsView.vue'),
      meta: { title: 'Breeding Analytics' }
    },
    {
      path: '/breeding/:id',
      name: 'breeding-record',
      component: () => import('@/views/breeding/BreedingRecordView.vue'),
      meta: { title: 'Breeding Record' }
    },
    {
      path: '/sales',
      name: 'sales',
      component: () => import('@/views/sales/SalesListView.vue'),
      meta: { title: 'Sales Management' }
    },
    {
      path: '/sales/mark-sold',
      name: 'mark-sold',
      component: () => import('@/views/sales/MarkSoldView.vue'),
      meta: { title: 'Mark Bird as Sold' }
    },
    {
      path: '/dna',
      name: 'dna',
      component: () => import('@/views/dna/DnaRecordsView.vue'),
      meta: { title: 'DNA Records' }
    },
    {
      path: '/reminders',
      name: 'reminders',
      component: () => import('@/views/reminders/RemindersView.vue'),
      meta: { title: 'Reminders' }
    },
    {
      path: '/soft-food',
      name: 'soft-food',
      component: () => import('@/views/softfood/SoftFoodView.vue'),
      meta: { title: 'Soft Food Log' }
    },
    {
      path: '/accounting',
      name: 'accounting',
      component: () => import('@/views/accounting/AccountingView.vue'),
      meta: { title: 'Accounting' }
    },
    {
      path: '/sync',
      name: 'sync',
      component: () => import('@/views/sync/SyncSettingsView.vue'),
      meta: { title: 'Cloud Sync' }
    },
  ]
})

// Navigation guard — require authentication + valid license
router.beforeEach(async (to, _from, next) => {
  // Update page title
  document.title = `${to.meta.title || 'App'} | Bird Aviary`

  // Allow public routes (login, callback, expired page)
  if (to.meta.public) {
    return next()
  }

  // Check if user is logged in (has profile + tokens in localStorage)
  const hasProfile = !!localStorage.getItem('user_profile')
  const hasTokens = !!localStorage.getItem('gdrive_tokens')

  if (!hasProfile || !hasTokens) {
    return next({ name: 'login' })
  }

  // Check license — import store lazily to avoid circular deps
  const { useAuthStore } = await import('@/stores/authStore')
  const { isLicenseValid } = await import('@/services/licenseService')
  const authStore = useAuthStore()

  // If we haven't checked the license yet this session, do it now
  if (!authStore.licenseData) {
    await authStore.verifyLicense()
  }

  // Block access if license is invalid / expired
  if (!isLicenseValid(authStore.licenseData)) {
    return next({ name: 'subscription-expired' })
  }

  next()
})

export default router

