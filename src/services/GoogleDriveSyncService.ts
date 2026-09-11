// Manages sync file in Google Drive's appDataFolder
// The sync file stores the append-only transaction log as JSON
// File is named 'aviary_sync_log.json'

import { getValidAccessToken } from './authService'
import type { SyncLogEntry } from '@/types'

const DRIVE_API = 'https://www.googleapis.com/drive/v3'
const DRIVE_UPLOAD_API = 'https://www.googleapis.com/upload/drive/v3'
const SYNC_FILENAME = 'aviary_sync_log.json'

export class GoogleDriveSyncService {
  // Helper to make authenticated Drive API requests
  private async driveRequest(url: string, options?: RequestInit): Promise<Response> {
    const token = await getValidAccessToken()
    if (!token) throw new Error('Not authenticated')
    
    const headers = new Headers(options?.headers)
    headers.set('Authorization', `Bearer ${token}`)
    
    const response = await fetch(url, { ...options, headers })
    if (response.status === 401) {
      throw new Error('Authentication expired')
    }
    return response
  }

  // Find the sync file in appDataFolder
  async findSyncFile(): Promise<string | null> {
    const query = new URLSearchParams({
      spaces: 'appDataFolder',
      q: `name='${SYNC_FILENAME}'`,
      fields: 'files(id)'
    })
    
    const response = await this.driveRequest(`${DRIVE_API}/files?${query.toString()}`)
    if (!response.ok) throw new Error('Failed to query drive files')
    
    const data = await response.json()
    if (data.files && data.files.length > 0) {
      return data.files[0].id
    }
    return null
  }
  
  // Download sync entries from Drive
  async downloadEntries(): Promise<SyncLogEntry[]> {
    const fileId = await this.findSyncFile()
    if (!fileId) return []
    
    const response = await this.driveRequest(`${DRIVE_API}/files/${fileId}?alt=media`)
    if (!response.ok) {
      if (response.status === 404) return []
      throw new Error('Failed to download sync file')
    }
    
    try {
      const text = await response.text()
      return text ? JSON.parse(text) : []
    } catch (e) {
      console.error('Error parsing sync file:', e)
      return []
    }
  }
  
  // Upload new entries to Drive (append to existing)
  async uploadEntries(entries: SyncLogEntry[]): Promise<void> {
    if (!entries.length) return
    
    const fileId = await this.findSyncFile()
    const existingEntries = await this.downloadEntries()
    
    // Merge and deduplicate by id
    const entryMap = new Map<number, SyncLogEntry>()
    for (const e of existingEntries) entryMap.set(e.id, e)
    for (const e of entries) entryMap.set(e.id, e)
      
    const mergedEntries = Array.from(entryMap.values()).sort((a, b) => a.id - b.id)
    
    if (fileId) {
      await this.updateSyncFile(fileId, mergedEntries)
    } else {
      await this.createSyncFile(mergedEntries)
    }
  }
  
  // Create the sync file if it doesn't exist
  private async createSyncFile(entries: SyncLogEntry[]): Promise<string> {
    const boundary = '-------314159265358979323846'
    const delimiter = `\r\n--${boundary}\r\n`
    const closeDelimiter = `\r\n--${boundary}--`
    
    const metadata = {
      name: SYNC_FILENAME,
      parents: ['appDataFolder'],
      mimeType: 'application/json'
    }
    
    const body = delimiter +
      'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
      JSON.stringify(metadata) +
      delimiter +
      'Content-Type: application/json\r\n\r\n' +
      JSON.stringify(entries) +
      closeDelimiter

    const response = await this.driveRequest(`${DRIVE_UPLOAD_API}/files?uploadType=multipart`, {
      method: 'POST',
      headers: {
        'Content-Type': `multipart/related; boundary="${boundary}"`
      },
      body
    })
    
    if (!response.ok) throw new Error('Failed to create sync file')
    const data = await response.json()
    return data.id
  }
  
  // Update existing sync file with merged entries
  private async updateSyncFile(fileId: string, entries: SyncLogEntry[]): Promise<void> {
    const response = await this.driveRequest(`${DRIVE_UPLOAD_API}/files/${fileId}?uploadType=media`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(entries)
    })
    
    if (!response.ok) throw new Error('Failed to update sync file')
  }
}

export const driveSyncService = new GoogleDriveSyncService()
