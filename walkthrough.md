# Phase 8 — Google Drive Sync: Walkthrough

## Overview

Implemented the full Google Drive Sync feature, enabling multi-device synchronization of aviary data via Google Drive's `appDataFolder`. The sync uses an append-only transaction log pattern — local changes are recorded in `sync_log`, uploaded to Google Drive as a JSON file, and replayed on other devices.

---

## Changes Made

### Backend (Python FastAPI)

#### [NEW] [`sync_service.py`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/services/sync_service.py)
Core sync business logic:
- **`get_pending_entries()`** — Fetches unsynced `SyncLog` entries ordered by timestamp
- **`mark_entries_synced()`** — Marks entries as synced after successful upload
- **`replay_entries()`** — Replays remote transaction entries into local DB, dynamically resolving model classes and handling INSERT/UPDATE/DELETE operations with audit logging
- **`get_sync_status()`** — Returns total entries, unsynced count, and last sync timestamp
- **`create_sync_entry()`** — Creates new sync log entries

#### [NEW] [`sync.py` (router)](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/routers/sync.py)
Four REST endpoints:
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/sync/pending` | Get unsynced transaction entries |
| `POST` | `/api/sync/mark-synced` | Mark entries as synced |
| `POST` | `/api/sync/replay` | Replay remote entries into local DB |
| `GET` | `/api/sync/status` | Get sync status statistics |

#### [MODIFY] [`main.py`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/main.py)
- Added sync router import and registration

---

### Frontend Services

#### [NEW] [`authService.ts`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/services/authService.ts)
Google OAuth 2.0 PKCE flow:
- Generates code verifier/challenge pairs using Web Crypto API
- Initiates OAuth consent screen redirect
- Handles callback code-for-token exchange
- Auto-refreshes expired tokens (1-minute buffer)
- Manages token storage in `localStorage`

#### [NEW] [`GoogleDriveSyncService.ts`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/services/GoogleDriveSyncService.ts)
Google Drive `appDataFolder` REST API client:
- Finds/creates the `aviary_sync_log.json` file in the app's isolated Drive folder
- Downloads existing sync entries
- Uploads new entries with merge and deduplication
- Uses multipart upload for file creation, media upload for updates

---

### Frontend State & UI

#### [NEW] [`syncStore.ts`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/stores/syncStore.ts)
Pinia store managing:
- Authentication state (connected to Google)
- Sync state (syncing, pending count, errors)
- Auto-sync toggle (persisted to localStorage)
- Sync history log (last 10 operations)
- Full sync flow: fetch pending → upload to Drive → mark synced → download remote → filter foreign entries → replay locally
- Per-device UUID for distinguishing local vs remote entries

#### [NEW] [`useSync.ts`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/composables/useSync.ts)
Composable providing:
- Auto-sync interval management (5-minute default)
- Lifecycle-aware setup/teardown
- Reactive watch on autoSync toggle

#### [NEW] [`SyncSettingsView.vue`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/views/sync/SyncSettingsView.vue)
Premium sync settings page with:
- Google account connection card with status indicator
- Sync status card with last sync time, pending count, auto-sync toggle
- "Sync Now" button with animated spinner
- Sync history log table
- OAuth callback handling

#### [MODIFY] [`AppSidebar.vue`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/components/layout/AppSidebar.vue)
- Added "Cloud Sync" ☁️ nav item
- Added sync status indicator widget (green=synced, amber=pending, red=error, ping animation while syncing)
- Settings gear icon linking to sync page

#### [MODIFY] [`index.ts` (router)](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/router/index.ts)
- Added `/sync` route → SyncSettingsView
- Added `/auth/callback` route → SyncSettingsView (handles OAuth redirect)

#### [MODIFY] [`index.ts` (types)](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/types/index.ts)
Added interfaces: `SyncLogEntry`, `SyncStatus`, `GoogleDriveTokens`, `SyncState`

---

### Configuration

#### [NEW] [`.env.example`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/.env.example)
Template with:
- `VITE_GOOGLE_CLIENT_ID` — Google OAuth client ID
- `VITE_GOOGLE_REDIRECT_URI` — OAuth redirect URI

---

## Setup Required

To use Google Drive sync, you need to:

1. Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Google Drive API**
3. Create an **OAuth 2.0 Client ID** (type: Web application)
4. Add `http://localhost:1420/auth/callback` as an Authorized redirect URI
5. Copy `.env.example` to `.env` and fill in your Client ID

---

## Verification Results

| Check | Result |
|-------|--------|
| Backend imports | ✅ Pass |
| Sync API routes registered | ✅ 4 endpoints registered |
| TypeScript compilation | ✅ No new errors |
| API call pattern alignment | ✅ Fixed to match useApi return shape |
| AuditLog model compatibility | ✅ Fixed non-existent field |
