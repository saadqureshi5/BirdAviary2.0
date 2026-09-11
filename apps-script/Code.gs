/**
 * BirdAviary 2.0 — License API (Google Apps Script)
 *
 * This script runs as a deployed Google Apps Script Web App.
 * It uses a Google Sheet as the license database.
 *
 * Sheet columns (row 1 = headers):
 *   A: email
 *   B: plan          (e.g. "monthly", "yearly", "lifetime")
 *   C: expires_at    (ISO 8601 date string, empty for lifetime)
 *   D: is_active     (TRUE / FALSE)
 *   E: created_at    (ISO 8601 date string)
 *   F: notes         (optional admin notes)
 *
 * ── Endpoints ──────────────────────────────────────────────
 *
 *   GET  ?action=check&email=<email>
 *        → Returns license status for the given email.
 *
 *   POST ?action=add
 *        body: { email, plan, expires_at?, admin_key }
 *        → Adds or updates a license row.
 *
 *   POST ?action=revoke
 *        body: { email, admin_key }
 *        → Deactivates a license.
 *
 * ── Security ───────────────────────────────────────────────
 *
 *   • The web app is deployed as "Execute as: Me" and
 *     "Who has access: Anyone" so the frontend can call it
 *     without OAuth.
 *   • Admin-write endpoints require an ADMIN_KEY match.
 *   • License responses include an HMAC-SHA256 token that
 *     the desktop app can verify offline (Phase 5).
 */

// ═══════════════════════════════════════════════════════════
// Configuration — update these after creating your Sheet
// ═══════════════════════════════════════════════════════════

/**
 * The ID of the Google Sheet used as the license database.
 * Find it in the Sheet URL: https://docs.google.com/spreadsheets/d/<THIS_PART>/edit
 */
const SHEET_ID = PropertiesService.getScriptProperties().getProperty('SHEET_ID') || '';

/**
 * Secret key for admin endpoints (add / revoke).
 * Set this in Script Properties → ADMIN_KEY
 */
const ADMIN_KEY = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY') || '';

/**
 * HMAC secret used to sign license tokens.
 * Set this in Script Properties → HMAC_SECRET
 * Must match the secret configured in the desktop app (Phase 5).
 */
const HMAC_SECRET = PropertiesService.getScriptProperties().getProperty('HMAC_SECRET') || '';

/** Name of the sheet tab containing license data */
const SHEET_NAME = 'Licenses';

// ═══════════════════════════════════════════════════════════
// HTTP Handlers
// ═══════════════════════════════════════════════════════════

/**
 * Handles GET requests.
 * Supported actions: check
 */
function doGet(e) {
  try {
    const action = (e.parameter.action || '').toLowerCase();

    if (action === 'check') {
      const email = (e.parameter.email || '').toLowerCase().trim();
      if (!email) return jsonResponse({ error: 'Missing email parameter' }, 400);
      return checkLicense(email);
    }

    return jsonResponse({ error: 'Unknown action. Use ?action=check&email=...' }, 400);
  } catch (err) {
    return jsonResponse({ error: 'Internal error: ' + err.message }, 500);
  }
}

/**
 * Handles POST requests.
 * Supported actions: add, revoke
 */
function doPost(e) {
  try {
    const action = (e.parameter.action || '').toLowerCase();
    const body = JSON.parse(e.postData.contents || '{}');

    // Verify admin key for write operations
    if (!body.admin_key || body.admin_key !== ADMIN_KEY) {
      return jsonResponse({ error: 'Unauthorized' }, 403);
    }

    if (action === 'add') {
      return addOrUpdateLicense(body);
    }

    if (action === 'revoke') {
      return revokeLicense(body);
    }

    return jsonResponse({ error: 'Unknown action. Use ?action=add or ?action=revoke' }, 400);
  } catch (err) {
    return jsonResponse({ error: 'Internal error: ' + err.message }, 500);
  }
}

// ═══════════════════════════════════════════════════════════
// Core Functions
// ═══════════════════════════════════════════════════════════

/**
 * Checks whether a given email has a valid, active license.
 * Returns a response matching the LicenseData interface.
 */
function checkLicense(email) {
  const row = findLicenseRow(email);

  if (!row) {
    return jsonResponse({
      valid: false,
      plan: 'none',
      expires_at: null,
      license_token: null,
    });
  }

  const plan = row.plan;
  const expiresAt = row.expires_at;
  const isActive = row.is_active;

  // Determine validity
  let valid = isActive;
  if (valid && expiresAt) {
    valid = new Date(expiresAt) > new Date();
  }

  // Generate HMAC token for offline verification
  const licenseToken = valid ? generateLicenseToken(email, plan, expiresAt) : null;

  return jsonResponse({
    valid: valid,
    plan: plan,
    expires_at: expiresAt || null,
    license_token: licenseToken,
  });
}

/**
 * Adds a new license or updates an existing one.
 */
function addOrUpdateLicense(body) {
  const email = (body.email || '').toLowerCase().trim();
  if (!email) return jsonResponse({ error: 'Missing email' }, 400);

  const plan = body.plan || 'monthly';
  const expiresAt = body.expires_at || null;

  const sheet = getSheet();
  const existingRowIndex = findLicenseRowIndex(email);

  if (existingRowIndex > 0) {
    // Update existing row
    const row = existingRowIndex + 1; // 1-indexed (header is row 1)
    sheet.getRange(row, 2).setValue(plan);
    sheet.getRange(row, 3).setValue(expiresAt || '');
    sheet.getRange(row, 4).setValue(true);
    return jsonResponse({ success: true, message: 'License updated for ' + email });
  }

  // Add new row
  sheet.appendRow([
    email,
    plan,
    expiresAt || '',
    true,
    new Date().toISOString(),
    '',
  ]);

  return jsonResponse({ success: true, message: 'License created for ' + email });
}

/**
 * Deactivates a license (sets is_active = FALSE).
 */
function revokeLicense(body) {
  const email = (body.email || '').toLowerCase().trim();
  if (!email) return jsonResponse({ error: 'Missing email' }, 400);

  const sheet = getSheet();
  const rowIndex = findLicenseRowIndex(email);

  if (rowIndex <= 0) {
    return jsonResponse({ error: 'No license found for ' + email }, 404);
  }

  sheet.getRange(rowIndex + 1, 4).setValue(false);
  return jsonResponse({ success: true, message: 'License revoked for ' + email });
}

// ═══════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════

/**
 * Returns the Licenses sheet, creating it with headers if it doesn't exist.
 */
function getSheet() {
  const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
  let sheet = spreadsheet.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = spreadsheet.insertSheet(SHEET_NAME);
    sheet.appendRow(['email', 'plan', 'expires_at', 'is_active', 'created_at', 'notes']);
    sheet.getRange(1, 1, 1, 6).setFontWeight('bold');
  }

  return sheet;
}

/**
 * Finds a license row by email and returns its data, or null.
 */
function findLicenseRow(email) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).toLowerCase().trim() === email) {
      return {
        email: data[i][0],
        plan: data[i][1],
        expires_at: data[i][2] ? String(data[i][2]) : null,
        is_active: data[i][3] === true || data[i][3] === 'TRUE',
        created_at: data[i][4] ? String(data[i][4]) : null,
        notes: data[i][5] || '',
      };
    }
  }

  return null;
}

/**
 * Returns the 0-based data-array index of the row for the given email,
 * or -1 if not found. (Add 1 to get the sheet row number, since row 1 = headers.)
 */
function findLicenseRowIndex(email) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).toLowerCase().trim() === email) {
      return i;
    }
  }

  return -1;
}

/**
 * Generates an HMAC-SHA256 signed license token.
 * The token payload includes email, plan, and expiry so the
 * desktop app can verify it offline without calling the API.
 *
 * Token format: base64(payload) + "." + base64(hmac)
 */
function generateLicenseToken(email, plan, expiresAt) {
  if (!HMAC_SECRET) {
    // If no HMAC secret configured, return a simple unsigned token
    return null;
  }

  const payload = JSON.stringify({
    email: email,
    plan: plan,
    expires_at: expiresAt,
    issued_at: new Date().toISOString(),
  });

  const payloadB64 = Utilities.base64EncodeWebSafe(payload);
  const signature = Utilities.computeHmacSha256Signature(payloadB64, HMAC_SECRET);
  const signatureB64 = Utilities.base64EncodeWebSafe(signature);

  return payloadB64 + '.' + signatureB64;
}

/**
 * Utility: return a JSON response with CORS headers.
 */
function jsonResponse(data, statusCode) {
  // Note: Apps Script doGet/doPost always return 200 at the HTTP level.
  // We embed the logical status in the response body.
  const output = ContentService.createTextOutput(
    JSON.stringify({ ...data, status: statusCode || 200 })
  );
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}

// ═══════════════════════════════════════════════════════════
// Utility: First-time setup
// ═══════════════════════════════════════════════════════════

/**
 * Run this function once from the Apps Script editor to:
 * 1. Create the Licenses sheet (if missing)
 * 2. Verify Script Properties are set
 *
 * Go to: Run → setupLicenseSheet
 */
function setupLicenseSheet() {
  // Verify required properties
  const props = PropertiesService.getScriptProperties();
  const sheetId = props.getProperty('SHEET_ID');
  const adminKey = props.getProperty('ADMIN_KEY');
  const hmacSecret = props.getProperty('HMAC_SECRET');

  const issues = [];
  if (!sheetId) issues.push('SHEET_ID is not set');
  if (!adminKey) issues.push('ADMIN_KEY is not set');
  if (!hmacSecret) issues.push('HMAC_SECRET (optional but recommended) is not set');

  if (issues.length > 0) {
    Logger.log('⚠️  Configuration issues:\n  • ' + issues.join('\n  • '));
    Logger.log('\nSet these in: Project Settings → Script Properties');
  }

  if (sheetId) {
    const sheet = getSheet();
    Logger.log('✅ Licenses sheet ready: ' + sheet.getName());
    Logger.log('   Rows (including header): ' + sheet.getLastRow());
  }

  Logger.log('\n📋 Setup complete. Review the logs above for any warnings.');
}
