/**
 * Update Service — checks for new app versions against a remote
 * JSON manifest hosted on GitHub Releases (or any static URL).
 *
 * The manifest URL is configured via VITE_UPDATE_CHECK_URL env var.
 * Expected manifest format (JSON):
 * {
 *   "version": "2.1.0",
 *   "download_url": "https://github.com/.../releases/latest",
 *   "changelog": "- Bug fixes\n- New features",
 *   "force_update": false
 * }
 */

import type { UpdateInfo } from '@/types'

const UPDATE_DISMISSED_KEY = 'update_dismissed_version'

/** Current app version — kept in sync with package.json */
const CURRENT_VERSION = __APP_VERSION__

/** How often to check for updates (ms) — every 6 hours */
const CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000

let lastCheckTime = 0

// ── Public API ─────────────────────────────────────────────

/**
 * Check for available updates. Returns UpdateInfo if a newer version
 * is available, or null if up to date (or on error).
 * Throttled to avoid excessive network calls.
 */
export async function checkForUpdate(): Promise<UpdateInfo | null> {
  // Throttle: skip if checked recently
  if (Date.now() - lastCheckTime < CHECK_INTERVAL_MS) {
    return null
  }

  const manifestUrl = getManifestUrl()
  if (!manifestUrl) return null

  try {
    lastCheckTime = Date.now()

    const response = await fetch(manifestUrl, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      cache: 'no-cache',
    })

    if (!response.ok) {
      console.warn('Update check failed:', response.status)
      return null
    }

    const data: UpdateInfo = await response.json()

    // Compare versions
    if (!isNewerVersion(data.version, CURRENT_VERSION)) {
      return null
    }

    return data
  } catch (err) {
    console.warn('Update check error:', err)
    return null
  }
}

/**
 * Returns the current app version string.
 */
export function getCurrentVersion(): string {
  return CURRENT_VERSION
}

/**
 * Returns true if the user has previously dismissed this version.
 */
export function isVersionDismissed(version: string): boolean {
  return localStorage.getItem(UPDATE_DISMISSED_KEY) === version
}

/**
 * Mark a version as dismissed so the banner won't show again for it.
 */
export function dismissVersion(version: string): void {
  localStorage.setItem(UPDATE_DISMISSED_KEY, version)
}

/**
 * Clear the dismissed version (e.g. on sign-out or reset).
 */
export function clearDismissed(): void {
  localStorage.removeItem(UPDATE_DISMISSED_KEY)
}

// ── Internal Helpers ──────────────────────────────────────

function getManifestUrl(): string | null {
  const url = import.meta.env.VITE_UPDATE_CHECK_URL as string | undefined
  return url || null
}

/**
 * Compares two semver-like version strings (e.g. "2.1.0" vs "2.0.0").
 * Returns true if `remote` is strictly newer than `current`.
 */
function isNewerVersion(remote: string, current: string): boolean {
  const r = remote.replace(/^v/, '').split('.').map(Number)
  const c = current.replace(/^v/, '').split('.').map(Number)

  for (let i = 0; i < Math.max(r.length, c.length); i++) {
    const rPart = r[i] ?? 0
    const cPart = c[i] ?? 0
    if (rPart > cPart) return true
    if (rPart < cPart) return false
  }

  return false
}
