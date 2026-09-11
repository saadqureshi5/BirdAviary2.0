import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authService from '@/services/authService'
import * as licenseService from '@/services/licenseService'
import type { UserProfile, LicenseData } from '@/types'

const USER_PROFILE_KEY = 'user_profile'
const LICENSE_CACHE_KEY = 'bird_aviary_license'

export const useAuthStore = defineStore('auth', () => {
  // State
  const userProfile = ref<UserProfile | null>(loadStoredProfile())
  const licenseData = ref<LicenseData | null>(loadStoredLicense())
  const isCheckingLicense = ref(false)
  const loginError = ref<string | null>(null)

  // Getters
  const isLoggedIn = computed(() => {
    return !!userProfile.value && authService.isAuthenticated()
  })

  const userEmail = computed(() => userProfile.value?.email ?? null)
  const userName = computed(() => userProfile.value?.name ?? 'User')
  const userAvatar = computed(() => userProfile.value?.avatar_url ?? '')

  const hasValidLicense = computed(() => {
    if (!licenseData.value) return false
    if (!licenseData.value.valid) return false
    if (licenseData.value.expires_at) {
      return new Date(licenseData.value.expires_at) > new Date()
    }
    return false
  })

  // Actions
  async function signIn() {
    loginError.value = null
    try {
      await authService.startOAuthFlow()
    } catch (e: any) {
      loginError.value = e.message || 'Failed to start sign in'
    }
  }

  async function handleCallback(code: string): Promise<boolean> {
    loginError.value = null
    try {
      // Exchange code for tokens
      await authService.handleOAuthCallback(code)

      // Fetch user profile from Google
      const token = await authService.getValidAccessToken()
      if (!token) throw new Error('Failed to get access token')

      const profile = await authService.fetchUserProfile(token)
      userProfile.value = profile
      localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(profile))

      return true
    } catch (e: any) {
      loginError.value = e.message || 'Authentication failed'
      console.error('OAuth callback failed:', e)
      return false
    }
  }

  function signOut() {
    authService.clearTokens()
    userProfile.value = null
    licenseData.value = null
    localStorage.removeItem(USER_PROFILE_KEY)
    localStorage.removeItem(LICENSE_CACHE_KEY)
    licenseService.clearCachedLicense()
    loginError.value = null
  }

  function setLicense(data: LicenseData) {
    licenseData.value = data
    localStorage.setItem(LICENSE_CACHE_KEY, JSON.stringify(data))
  }

  function clearLicense() {
    licenseData.value = null
    localStorage.removeItem(LICENSE_CACHE_KEY)
  }

  /**
   * Verify the current user's license against the remote API.
   * Updates licenseData and returns the result.
   */
  async function verifyLicense(): Promise<LicenseData | null> {
    const email = userProfile.value?.email
    if (!email) return null

    isCheckingLicense.value = true
    try {
      const data = await licenseService.checkLicense(email)
      setLicense(data)
      return data
    } catch (e) {
      console.error('License verification failed:', e)
      return licenseData.value
    } finally {
      isCheckingLicense.value = false
    }
  }

  return {
    // State
    userProfile,
    licenseData,
    isCheckingLicense,
    loginError,
    // Getters
    isLoggedIn,
    userEmail,
    userName,
    userAvatar,
    hasValidLicense,
    // Actions
    signIn,
    handleCallback,
    signOut,
    setLicense,
    clearLicense,
    verifyLicense,
  }
})

// Helper functions
function loadStoredProfile(): UserProfile | null {
  const stored = localStorage.getItem(USER_PROFILE_KEY)
  if (!stored) return null
  try {
    return JSON.parse(stored) as UserProfile
  } catch {
    return null
  }
}

function loadStoredLicense(): LicenseData | null {
  const stored = localStorage.getItem(LICENSE_CACHE_KEY)
  if (!stored) return null
  try {
    return JSON.parse(stored) as LicenseData
  } catch {
    return null
  }
}
