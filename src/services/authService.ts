// Google OAuth 2.0 PKCE flow for desktop/SPA applications
// Token exchange happens via the backend (client_secret stays server-side)
// Stores tokens in localStorage

import type { GoogleDriveTokens } from '@/types'
import { Capacitor } from '@capacitor/core'
import { GoogleAuth } from '@codetrix-studio/capacitor-google-auth'

const GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
const SCOPES = 'email profile https://www.googleapis.com/auth/drive.appdata'
const TOKENS_KEY = 'gdrive_tokens'

// Fetch the client ID from the backend (no secrets in the frontend)
let _cachedClientId: string | null = null

async function getClientId(): Promise<string> {
  if (_cachedClientId) return _cachedClientId

  const response = await fetch('/api/auth/client-id')
  if (!response.ok) throw new Error('Failed to fetch Google Client ID from server')
  const data = await response.json()
  _cachedClientId = data.client_id
  return data.client_id
}

function getRedirectUri(): string {
  return `${window.location.origin}/auth/callback`
}

// Generate PKCE code verifier and challenge
async function generatePKCE() {
  const array = new Uint32Array(56 / 2)
  window.crypto.getRandomValues(array)
  const codeVerifier = Array.from(array, dec => ('0' + dec.toString(16)).substr(-2)).join('')
  
  const encoder = new TextEncoder()
  const data = encoder.encode(codeVerifier)
  const hash = await window.crypto.subtle.digest('SHA-256', data)
  
  const base64Digest = btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
    
  return { codeVerifier, codeChallenge: base64Digest }
}

// Initiate OAuth flow - opens Google consent screen
export async function startOAuthFlow() {
  if (Capacitor.isNativePlatform()) {
    try {
      const user = await GoogleAuth.signIn();
      if (user.authentication) {
        const tokens: GoogleDriveTokens = {
          access_token: user.authentication.accessToken,
          refresh_token: user.serverAuthCode || '',
          expires_at: Date.now() + 3600000,
          token_type: 'Bearer'
        };
        storeTokens(tokens);
      }
      return;
    } catch (e) {
      console.error('Native Google Sign-In error:', e);
      throw e;
    }
  }

  const clientId = await getClientId()
  const { codeVerifier, codeChallenge } = await generatePKCE()
  sessionStorage.setItem('pkce_verifier', codeVerifier)
  
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: getRedirectUri(),
    response_type: 'code',
    scope: SCOPES,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    access_type: 'offline',
    prompt: 'consent'
  })
  
  window.location.href = `${GOOGLE_AUTH_URL}?${params.toString()}`
}

// Handle OAuth callback - exchange code for tokens via backend
export async function handleOAuthCallback(code: string): Promise<GoogleDriveTokens> {
  const codeVerifier = sessionStorage.getItem('pkce_verifier')
  if (!codeVerifier) throw new Error('No PKCE verifier found')
  
  const response = await fetch('/api/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      code_verifier: codeVerifier,
      redirect_uri: getRedirectUri()
    })
  })
  
  if (!response.ok) {
    throw new Error('Failed to exchange code for tokens')
  }
  
  const data = await response.json()
  const tokens: GoogleDriveTokens = {
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: Date.now() + (data.expires_in * 1000),
    token_type: data.token_type
  }
  
  storeTokens(tokens)
  sessionStorage.removeItem('pkce_verifier')
  return tokens
}

// Refresh expired access token via backend
export async function refreshAccessToken(refreshToken: string): Promise<GoogleDriveTokens> {
  if (Capacitor.isNativePlatform()) {
    const auth = await GoogleAuth.refresh();
    const oldTokens = getStoredTokens();
    const tokens: GoogleDriveTokens = {
      access_token: auth.accessToken,
      refresh_token: oldTokens?.refresh_token || '',
      expires_at: Date.now() + 3600000,
      token_type: 'Bearer'
    };
    storeTokens(tokens);
    return tokens;
  }

  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  })
  
  if (!response.ok) {
    throw new Error('Failed to refresh token')
  }
  
  const data = await response.json()
  const oldTokens = getStoredTokens()
  
  const tokens: GoogleDriveTokens = {
    access_token: data.access_token,
    refresh_token: data.refresh_token || (oldTokens?.refresh_token ?? ''),
    expires_at: Date.now() + (data.expires_in * 1000),
    token_type: data.token_type
  }
  
  storeTokens(tokens)
  return tokens
}

// Get current valid access token (auto-refresh if expired)
export async function getValidAccessToken(): Promise<string | null> {
  const tokens = getStoredTokens()
  if (!tokens) return null
  
  if (Date.now() > tokens.expires_at - 60000) { // Refresh if within 1 minute of expiring
    if (!tokens.refresh_token && !Capacitor.isNativePlatform()) {
      clearTokens()
      return null
    }
    try {
      if (Capacitor.isNativePlatform()) {
         const newTokens = await refreshAccessToken('');
         return newTokens.access_token;
      }
      const newTokens = await refreshAccessToken(tokens.refresh_token)
      return newTokens.access_token
    } catch (e) {
      clearTokens()
      return null
    }
  }
  
  return tokens.access_token
}

// Store/retrieve tokens from localStorage
export function storeTokens(tokens: GoogleDriveTokens): void {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
}

export function getStoredTokens(): GoogleDriveTokens | null {
  const stored = localStorage.getItem(TOKENS_KEY)
  if (!stored) return null
  try {
    return JSON.parse(stored) as GoogleDriveTokens
  } catch (e) {
    return null
  }
}

export function clearTokens(): void {
  localStorage.removeItem(TOKENS_KEY)
  if (Capacitor.isNativePlatform()) {
     GoogleAuth.signOut().catch(console.error);
  }
}

export function isAuthenticated(): boolean {
  return !!getStoredTokens()
}

// Fetch user profile from Google (name, email, avatar)
export async function fetchUserProfile(accessToken: string): Promise<{ email: string; name: string; avatar_url: string; google_id: string }> {
  const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
    headers: { Authorization: `Bearer ${accessToken}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user profile')
  const data = await response.json()
  return {
    email: data.email,
    name: data.name || data.email.split('@')[0],
    avatar_url: data.picture || '',
    google_id: data.id
  }
}
