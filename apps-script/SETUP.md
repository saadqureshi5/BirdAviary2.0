# BirdAviary 2.0 — Apps Script License API Setup Guide

This guide walks you through deploying the Google Apps Script license API that BirdAviary 2.0 uses to validate subscriptions.

---

## Overview

The license system uses:
- **Google Sheet** → acts as the license database (one row per user)
- **Google Apps Script** → deployed as a Web App that reads/writes the Sheet
- **Desktop App** → calls the Web App URL to check license status

```
┌──────────────┐     GET ?action=check     ┌─────────────────┐     read/write     ┌──────────────┐
│  BirdAviary  │  ──────────────────────►  │  Apps Script    │  ───────────────►  │ Google Sheet │
│  Desktop App │  ◄──────────────────────  │  Web App        │  ◄───────────────  │ (Licenses)   │
└──────────────┘     { valid, plan, … }    └─────────────────┘                    └──────────────┘
```

---

## Step 1 — Create the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Name it **"BirdAviary Licenses"** (or any name you prefer).
3. Copy the **Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/COPY_THIS_PART/edit
   ```
4. You do **not** need to manually create headers — the script will create them automatically on first run.

---

## Step 2 — Create the Apps Script Project

1. Go to [Google Apps Script](https://script.google.com) and click **New project**.
2. Name the project **"BirdAviary License API"**.
3. Delete any default code in `Code.gs`.
4. Copy the entire contents of [`apps-script/Code.gs`](file:///c:/Users/saadq/Desktop/BirdAviary2.0/apps-script/Code.gs) and paste it into the editor.
5. Press **Ctrl+S** to save.

---

## Step 3 — Configure Script Properties

1. In the Apps Script editor, click the **⚙️ gear icon** (Project Settings) in the left sidebar.
2. Scroll down to **Script Properties** and click **Edit script properties**.
3. Add the following properties:

| Property      | Value                            | Required |
|---------------|----------------------------------|----------|
| `SHEET_ID`    | Your Google Sheet ID from Step 1 | ✅ Yes    |
| `ADMIN_KEY`   | A strong random string (e.g. generate with `openssl rand -hex 32`) | ✅ Yes |
| `HMAC_SECRET` | Another strong random string for signing license tokens | ⚠️ Recommended |

> **Generating secure keys (PowerShell):**
> ```powershell
> # Admin key
> -join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
>
> # HMAC secret
> -join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
> ```

4. Click **Save script properties**.

---

## Step 4 — Run Initial Setup

1. In the Apps Script editor, select the function **`setupLicenseSheet`** from the function dropdown (top bar).
2. Click **▶ Run**.
3. You will be prompted to **authorize** the script — review the permissions and click **Allow**.
4. Check the **Execution log** at the bottom — you should see:
   ```
   ✅ Licenses sheet ready: Licenses
      Rows (including header): 1
   ```

---

## Step 5 — Deploy as Web App

1. Click **Deploy → New deployment** (top right).
2. Click the **⚙️ gear icon** next to "Select type" and choose **Web app**.
3. Configure:

| Setting              | Value                                |
|----------------------|--------------------------------------|
| Description          | BirdAviary License API v1            |
| Execute as           | **Me** (your Google account)         |
| Who has access       | **Anyone**                           |

4. Click **Deploy**.
5. **Copy the Web App URL** — it will look like:
   ```
   https://script.google.com/macros/s/AKfycb.../exec
   ```
6. **Save this URL** — you'll need it in Phase 3 when creating `licenseService.ts`.

> [!IMPORTANT]
> Every time you edit the script code, you must create a **new deployment version** for changes to take effect. Go to **Deploy → Manage deployments → ✏️ Edit → New version → Deploy**.

---

## Step 6 — Add the Web App URL to Your Environment

Add the following to your `.env` file in the project root:

```env
# License API — Apps Script Web App URL (from Step 5)
LICENSE_API_URL=https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec
```

This URL will be used by `licenseService.ts` in Phase 3.

---

## API Reference

### Check License (used by the desktop app)

```
GET <WEB_APP_URL>?action=check&email=user@example.com
```

**Response:**
```json
{
  "valid": true,
  "plan": "yearly",
  "expires_at": "2027-01-15T00:00:00.000Z",
  "license_token": "eyJlbWFpbCI6InVzZXJAZXhhbXBsZ...",
  "status": 200
}
```

### Add / Update License (admin only)

```
POST <WEB_APP_URL>?action=add
Content-Type: application/json

{
  "email": "user@example.com",
  "plan": "yearly",
  "expires_at": "2027-01-15T00:00:00.000Z",
  "admin_key": "YOUR_ADMIN_KEY"
}
```

**Response:**
```json
{
  "success": true,
  "message": "License created for user@example.com",
  "status": 200
}
```

### Revoke License (admin only)

```
POST <WEB_APP_URL>?action=revoke
Content-Type: application/json

{
  "email": "user@example.com",
  "admin_key": "YOUR_ADMIN_KEY"
}
```

**Response:**
```json
{
  "success": true,
  "message": "License revoked for user@example.com",
  "status": 200
}
```

---

## Managing Licenses

You can manage licenses in **two ways**:

### Option A: Directly in the Google Sheet
Open the Google Sheet and manually add/edit rows:

| email              | plan     | expires_at                 | is_active | created_at                 | notes         |
|--------------------|----------|----------------------------|-----------|----------------------------|---------------|
| user@gmail.com     | yearly   | 2027-01-15T00:00:00.000Z  | TRUE      | 2026-09-10T12:00:00.000Z  | Paid via PayPal |
| another@gmail.com  | lifetime |                            | TRUE      | 2026-09-10T12:00:00.000Z  |               |

> For **lifetime** plans, leave `expires_at` empty.

### Option B: Using the API
Use `curl` or any HTTP client to call the admin endpoints (see API Reference above).

```bash
# Add a yearly license
curl -X POST "YOUR_WEB_APP_URL?action=add" \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@gmail.com","plan":"yearly","expires_at":"2027-09-10T00:00:00.000Z","admin_key":"YOUR_ADMIN_KEY"}'
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Internal error: Cannot call SpreadsheetApp.openById" | Verify `SHEET_ID` is correct in Script Properties |
| 403 Unauthorized on add/revoke | Check that `admin_key` in request matches `ADMIN_KEY` in Script Properties |
| Changes to code not reflected | Create a new deployment version (Deploy → Manage deployments → Edit) |
| CORS errors from the desktop app | Apps Script Web Apps handle CORS automatically — ensure you're using the `/exec` URL, not `/dev` |
| License shows invalid after renewal | Make sure `is_active` is `TRUE` and `expires_at` is a future date |

---

## What's Next

After completing this setup, proceed to **Phase 3** which will:
- Create `src/services/licenseService.ts` to call your deployed Web App URL
- Create the `SubscriptionExpiredView.vue` page
- Add license checking to the router guard and auth store
