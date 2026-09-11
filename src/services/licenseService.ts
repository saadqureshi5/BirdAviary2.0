/**
 * License Service — checks subscription status against the
 * Google Apps Script License API deployed in Phase 2.
 *
 * The Web App URL is stored in localStorage as `license_api_url`
 * (set from Settings or first-run setup). If a VITE_ env var is
 * provided it will be used as the default.
 */

import type { LicenseData } from '@/types'

const LICENSE_API_URL_KEY = 'license_api_url'
const LICENSE_CACHE_KEY = 'bird_aviary_license'

/** How long (ms) a cached license check is considered fresh — 1 hour */
const CACHE_TTL_MS = 60 * 60 * 1000

// ── Public API ─────────────────────────────────────────────

/**
 * Check the license for the given email.
 * Returns cached data when still fresh, otherwise calls the remote API.
 * On network failure, falls back to cached data if available.
 */
export async function checkLicense(email: string): Promise<LicenseData> {
  // Try cache first
  const cached = getCachedLicense()
  if (cached && Date.now() - cached.cached_at < CACHE_TTL_MS) {
    return cached
  }

  const apiUrl = getApiUrl()
  if (!apiUrl) {
    // No API URL configured — fall back to cache or return invalid
    return cached ?? createInvalidLicense()
  }

  try {
    const url = `${apiUrl}?action=check&email=${encodeURIComponent(email)}`
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    })

    if (!response.ok) {
      console.error('License API returned status', response.status)
      return cached ?? createInvalidLicense()
    }

    const data = await response.json()

    const license: LicenseData = {
      valid: data.valid === true,
      plan: data.plan || 'none',
      expires_at: data.expires_at || null,
      license_token: data.license_token || null,
      cached_at: Date.now(),
    }

    // Persist to cache
    cacheLicense(license)
    return license
  } catch (err) {
    console.error('License check failed:', err)
    // Network error — use stale cache if available
    return cached ?? createInvalidLicense()
  }
}

/**
 * Returns true if the given LicenseData represents a currently valid license.
 */
export function isLicenseValid(license: LicenseData | null): boolean {
  if (!license) return false
  if (!license.valid) return false
  if (license.expires_at) {
    return new Date(license.expires_at) > new Date()
  }
  // valid=true with no expires_at means lifetime
  return true
}

/**
 * Clear the cached license data (e.g. on sign-out).
 */
export function clearCachedLicense(): void {
  localStorage.removeItem(LICENSE_CACHE_KEY)
}

// ── API URL Management ────────────────────────────────────

/**
 * Get the configured License API URL.
 * Priority: localStorage > VITE_ env var
 */
export function getApiUrl(): string | null {
  const stored = localStorage.getItem(LICENSE_API_URL_KEY)
  if (stored) return stored

  // Fall back to env var if available
  const envUrl = import.meta.env.VITE_LICENSE_API_URL as string | undefined
  return envUrl || null
}

/**
 * Set the License API URL (persisted to localStorage).
 */
export function setApiUrl(url: string): void {
  localStorage.setItem(LICENSE_API_URL_KEY, url.replace(/\/+$/, ''))
}

// ── Internal Helpers ──────────────────────────────────────

function getCachedLicense(): LicenseData | null {
  const raw = localStorage.getItem(LICENSE_CACHE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as LicenseData
  } catch {
    return null
  }
}

function cacheLicense(license: LicenseData): void {
  localStorage.setItem(LICENSE_CACHE_KEY, JSON.stringify(license))
}

function createInvalidLicense(): LicenseData {
  return {
    valid: false,
    plan: 'none',
    expires_at: null,
    license_token: null,
    cached_at: Date.now(),
  }
}

// ── HMAC License Token Verification (Phase 5) ────────────

/**
 * Verify an HMAC-SHA256 signed license token offline.
 * Token format: base64url(payload) + "." + base64url(hmac)
 *
 * Returns the parsed payload if valid, or null if invalid.
 * Requires VITE_HMAC_SECRET to be set.
 */
export async function verifyLicenseToken(token: string): Promise<{
  email: string
  plan: string
  expires_at: string | null
  issued_at: string
} | null> {
  const secret = import.meta.env.VITE_HMAC_SECRET as string | undefined
  if (!secret || !token) return null

  const dotIndex = token.indexOf('.')
  if (dotIndex === -1) return null

  const payloadB64 = token.substring(0, dotIndex)
  const signatureB64 = token.substring(dotIndex + 1)

  try {
    // Import the HMAC key
    const encoder = new TextEncoder()
    const keyData = encoder.encode(secret)
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    )

    // Recompute the HMAC
    const payloadBytes = encoder.encode(payloadB64)
    const expectedSig = await crypto.subtle.sign('HMAC', cryptoKey, payloadBytes)
    const expectedB64 = base64UrlEncode(new Uint8Array(expectedSig))

    // Constant-time-ish comparison (not truly constant-time in JS, but
    // good enough for client-side — the real security is server-side)
    if (expectedB64 !== signatureB64) return null

    // Decode and parse the payload
    const payloadJson = base64UrlDecode(payloadB64)
    const payload = JSON.parse(payloadJson)

    return {
      email: payload.email,
      plan: payload.plan,
      expires_at: payload.expires_at || null,
      issued_at: payload.issued_at,
    }
  } catch {
    return null
  }
}

/**
 * Verify license validity using the signed token (offline).
 * Falls back to the standard valid + expires_at check if no token
 * or HMAC secret is available.
 */
export async function isLicenseValidOffline(license: LicenseData | null): Promise<boolean> {
  if (!license) return false

  // If we have a token and HMAC secret, do a cryptographic check
  if (license.license_token && import.meta.env.VITE_HMAC_SECRET) {
    const payload = await verifyLicenseToken(license.license_token)
    if (!payload) return false

    // Check expiry from the signed payload (tamper-proof)
    if (payload.expires_at) {
      return new Date(payload.expires_at) > new Date()
    }
    return true
  }

  // Fall back to basic check
  return isLicenseValid(license)
}

// ── Base64 URL helpers ────────────────────────────────────

function base64UrlEncode(bytes: Uint8Array): string {
  let binary = ''
  for (const byte of bytes) {
    binary += String.fromCharCode(byte)
  }
  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
}

function base64UrlDecode(str: string): string {
  // Restore standard base64 characters
  let b64 = str.replace(/-/g, '+').replace(/_/g, '/')
  // Add padding
  while (b64.length % 4) {
    b64 += '='
  }
  return atob(b64)
}

