# BirdAviary 2.0 — Implementation Tasks

## Phase 1: Google Login (Mandatory Sign-In) ✅
- [x] Add `UserProfile` and `LicenseData` types to `src/types/index.ts`
- [x] Create `src/stores/authStore.ts` (user auth state)
- [x] Modify `src/services/authService.ts` (add email/profile scopes + fetch user info)
- [x] Create `src/views/auth/LoginView.vue` (Sign in with Google screen)
- [x] Create `src/views/auth/AuthCallbackView.vue` (OAuth callback handler)
- [x] Modify `src/router/index.ts` (add login route + auth guard)
- [x] Update `src/App.vue` (conditional layout for public vs auth routes)
- [x] Update `src/components/layout/AppHeader.vue` (use Google profile data + sign out)
- [x] Update `src/views/sync/SyncSettingsView.vue` (remove separate sign-in, use login state)

## Phase 2: Google Apps Script License API ✅
- [x] Create Apps Script code file for user to deploy
- [x] Create setup instructions document

## Phase 3: License Service + Subscription Guard ✅
- [x] Create `src/services/licenseService.ts`
- [x] Create `src/views/auth/SubscriptionExpiredView.vue`
- [x] Modify router guard to check license after auth
- [x] Integrate license check into `authStore.ts`

## Phase 4: Update Checker ✅
- [x] Create `src/services/updateService.ts`
- [x] Create `src/components/shared/UpdateBanner.vue`
- [x] Add update banner to `src/components/layout/AppLayout.vue`

## Phase 5: Security Hardening ✅
- [x] Install `vite-plugin-obfuscator`
- [x] Configure obfuscation in `vite.config.ts`
- [x] Add HMAC license token verification in `licenseService.ts`
