# Mobile Distribution — Android APK + iOS IPA

Make the app fully self-contained on Android and iOS so it can be distributed to users who are controlled via the license system (Google Sheet).

## Background

Currently the app works as:
- **Desktop (Tauri)**: Frontend → Vite dev proxy → Python FastAPI backend → SQLite
- **Mobile (Capacitor)**: Partially set up — `useApi` already checks `Capacitor.isNativePlatform()` and diverts to `mobileDataLayer`, but only `birds` (GET/POST) and `categories` (GET) are implemented. All other endpoints return `null`.

### Key gaps to fix:
1. **SQLite schema** — only 2 of 12 tables are created on mobile
2. **Mobile data layer** — only handles 2 of ~40 API endpoints
3. **OAuth on mobile** — uses `window.location.href` redirect + local backend for token exchange; neither works in a WebView
4. **iOS project** — doesn't exist (`@capacitor/ios` not installed)
5. **Direct `fetch('/api')` calls** — `authService.ts`, `dnaStore.ts`, `AddBirdView.vue`, `EditBirdView.vue` bypass `useApi` entirely

## User Review Required

> [!IMPORTANT]
> **iPhone 7 Plus Compatibility**: iPhone 7 Plus maxes out at **iOS 15.8**. Capacitor 8.x requires iOS 14+, so it should work, but we should test early. If you hit issues, we may need to downgrade to Capacitor 6.

> [!WARNING]
> **Google Sign-In on mobile** will use the `@codetrix-studio/capacitor-google-auth` plugin, which handles the native Google Sign-In flow (no WebView redirect needed). This requires a **separate OAuth Client ID** in Google Cloud Console for each platform:
> - **Android**: Client ID with your app's SHA-1 signing key
> - **iOS**: Client ID with your app's Bundle ID
>
> You'll need to configure these in Google Cloud Console before the sign-in works on devices.

> [!IMPORTANT]
> **File uploads (photos, DNA certificates)** on mobile will be stored in the device's local filesystem via Capacitor Filesystem plugin instead of a backend `uploads/` directory. Photos taken via camera are already handled by `useCamera.ts`.

## Open Questions

> [!IMPORTANT]
> **Q1**: Do you want the app to work **100% offline** on mobile (all data in local SQLite, no backend needed at all), with Google Drive sync as the only cloud feature? Or do you want a hosted backend that mobile connects to over the internet?
> 
> **Recommendation**: 100% offline with local SQLite (the current architecture already points this direction). The Google Drive sync handles multi-device data sharing.

> [!IMPORTANT]
> **Q2**: For the iOS build, do you have a Mac available? iOS builds **require Xcode on macOS** — there's no way around this Apple restriction. You can develop and test the Android APK on Windows, but you'll need a Mac (or a CI service like GitHub Actions with macOS runners) for the iOS IPA.

## Proposed Changes

### Component 1: Complete Mobile SQLite Schema

#### [MODIFY] [sqliteService.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/services/sqliteService.ts)
Add all 12 tables matching the backend schema:
- `categories`, `birds` (already exist)
- Add: `pairing`, `clutch`, `chick`, `sale`, `dnarecord`, `reminder`, `soft_food_logs`, `expenses`, `synclog`, `auditlog`
- Include all columns, foreign keys, and defaults from the backend models

---

### Component 2: Complete Mobile Data Layer

#### [MODIFY] [mobileDataLayer.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/services/mobileDataLayer.ts)
Rewrite to handle all CRUD endpoints that the stores and views call:

| Resource | Operations | Used by |
|----------|-----------|---------|
| `/birds` | GET, GET/:id, POST, PUT, DELETE | birdsStore |
| `/birds/:id/photo` | POST (file) | AddBirdView, EditBirdView |
| `/birds/:id/siblings` | GET | BirdProfileView |
| `/birds/:id/pairings` | GET | BirdProfileView |
| `/birds/:id/ancestry/tree` | GET | GenerationalView |
| `/birds/:id/descendants/tree` | GET | GenerationalView |
| `/birds/search` | GET | useSearch |
| `/birds/stats/summary` | GET | DashboardView |
| `/categories` | GET, POST, PUT, DELETE | birdsStore |
| `/pairings` | GET, POST, PUT | breedingStore |
| `/pairings/:id` | GET (with clutches+chicks) | breedingStore |
| `/breeding/analytics` | GET | breedingStore |
| `/clutches` | POST, PUT | breedingStore |
| `/chicks` | POST, PUT | breedingStore |
| `/sales` | GET, POST, PUT, DELETE | salesStore |
| `/dna` | GET, POST, DELETE | dnaStore |
| `/reminders` | GET, POST, PUT, DELETE | remindersStore |
| `/soft-food` | GET, POST, PUT, DELETE | softFoodStore |
| `/expenses` | GET, POST, PUT, DELETE | accountingStore |
| `/activity` | GET | DashboardView |
| `/sync/*` | GET, POST | syncStore |

This is the largest single piece of work. The approach:
- Create a router-style dispatcher (`mobileDataLayer.ts`)
- Each resource gets a handler module in a new `src/services/mobile/` directory
- Each handler does raw SQL via `@capacitor-community/sqlite`

#### [NEW] `src/services/mobile/birdHandlers.ts`
#### [NEW] `src/services/mobile/categoryHandlers.ts`
#### [NEW] `src/services/mobile/breedingHandlers.ts`
#### [NEW] `src/services/mobile/salesHandlers.ts`
#### [NEW] `src/services/mobile/dnaHandlers.ts`
#### [NEW] `src/services/mobile/reminderHandlers.ts`
#### [NEW] `src/services/mobile/softFoodHandlers.ts`
#### [NEW] `src/services/mobile/expenseHandlers.ts`
#### [NEW] `src/services/mobile/activityHandlers.ts`
#### [NEW] `src/services/mobile/syncHandlers.ts`

---

### Component 3: Mobile Google Sign-In

#### Install `@codetrix-studio/capacitor-google-auth`
Native Google Sign-In plugin — handles the full OAuth flow natively on Android/iOS without WebView redirects.

#### [MODIFY] [authService.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/services/authService.ts)
Add platform detection:
- **Web/Tauri (desktop)**: Keep existing PKCE redirect flow via backend
- **Native (mobile)**: Use `GoogleAuth.signIn()` from the Capacitor plugin, which returns tokens + user profile directly — no backend needed

#### [MODIFY] [capacitor.config.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/capacitor.config.ts)
Add `GoogleAuth` plugin config with client IDs.

---

### Component 4: Fix Direct fetch('/api') Calls

#### [MODIFY] [dnaStore.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/stores/dnaStore.ts)
Add native platform check for DNA file upload — save to local filesystem instead of uploading to backend.

#### [MODIFY] [AddBirdView.vue](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/views/birds/AddBirdView.vue)
#### [MODIFY] [EditBirdView.vue](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/views/birds/EditBirdView.vue)
Add native platform check for photo upload — save to local filesystem instead of `fetch('/api/birds/{id}/photo')`.

---

### Component 5: Add iOS Platform

```bash
npm install @capacitor/ios
npx cap add ios
```

#### [MODIFY] [capacitor.config.ts](file:///c:/Users/saadq/Desktop/BirdAviary2.0/capacitor.config.ts)
Add iOS-specific plugin config.

#### [NEW] `ios/` directory (auto-generated by `npx cap add ios`)

---

### Component 6: Build Configuration

#### [NEW] `scripts/build-android.ps1`
Script to build the Android APK:
```
npm run build → npx cap sync android → Android Studio build
```

#### [NEW] `scripts/build-ios.sh`
Script to build the iOS IPA (requires macOS):
```
npm run build → npx cap sync ios → xcodebuild
```

---

## Verification Plan

### Automated Tests
- `npx vue-tsc --noEmit` — TypeScript compilation
- `npx cap sync android` — Capacitor Android sync
- `npx cap sync ios` — Capacitor iOS sync (if on macOS)

### Manual Verification
- Build APK and test on Android device/emulator
- Verify Google Sign-In flow on Android
- Verify license check works (hits Apps Script API)
- Test all CRUD operations (birds, breeding, sales, etc.) on mobile SQLite
- Test photo capture and DNA upload on mobile
- Test on iPhone 7 Plus (iOS 15.x) if Mac available

### Execution Order
1. Component 1 (SQLite schema) — foundation, everything depends on it
2. Component 2 (Data layer) — largest piece, enables all features
3. Component 3 (Mobile auth) — enables sign-in on devices
4. Component 4 (Fix direct fetches) — small patches
5. Component 5 (iOS platform) — add iOS project
6. Component 6 (Build scripts) — convenience
