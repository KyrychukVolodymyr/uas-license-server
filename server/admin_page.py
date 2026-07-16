ADMIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>UAS License Admin</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg: rgb(243, 246, 250);
      --panel: rgb(255, 255, 255);
      --ink: rgb(15, 23, 42);
      --muted: rgb(100, 116, 139);
      --line: rgb(226, 232, 240);
      --navy: rgb(15, 23, 42);
      --blue: rgb(37, 99, 235);
      --green: rgb(22, 163, 74);
      --red: rgb(220, 38, 38);
      --amber: rgb(217, 119, 6);
      --purple: rgb(124, 58, 237);
      --slate: rgb(71, 85, 105);
    }

    body {
      font-family: Arial, sans-serif;
      margin: 0;
      background: var(--bg);
      color: var(--ink);
    }

    header {
      background: linear-gradient(135deg, rgb(15, 23, 42), rgb(30, 41, 59));
      color: white;
      padding: 22px 28px;
      border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    header h1 {
      margin: 0;
      font-size: 24px;
      letter-spacing: -0.02em;
    }

    header p {
      margin: 6px 0 0 0;
      color: rgb(203, 213, 225);
      font-size: 13px;
    }

    main {
      padding: 24px;
      max-width: 1320px;
      margin: 0 auto;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 18px;
      margin-bottom: 18px;
      box-shadow: 0 10px 26px rgba(15,23,42,0.06);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }

    h2 {
      margin: 0;
      font-size: 18px;
    }

    h3 {
      margin: 14px 0 8px 0;
      font-size: 15px;
    }

    label {
      display: block;
      font-weight: 700;
      margin-top: 10px;
      margin-bottom: 4px;
      font-size: 12px;
      color: rgb(51, 65, 85);
    }

    input, select {
      width: 100%;
      box-sizing: border-box;
      padding: 10px;
      border: 1px solid rgb(203, 213, 225);
      border-radius: 10px;
      font-size: 14px;
      background: white;
    }


    textarea {
      width: 100%;
      box-sizing: border-box;
      padding: 10px;
      border: 1px solid rgb(203, 213, 225);
      border-radius: 10px;
      font-size: 14px;
      background: white;
      font-family: Arial, sans-serif;
      min-height: 90px;
      resize: vertical;
    }

    .result-list {
      max-height: 220px;
      overflow: auto;
      background: rgb(248, 250, 252);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px;
      margin-top: 10px;
      font-size: 12px;
    }

    button {
      padding: 9px 13px;
      border: 0;
      border-radius: 10px;
      background: var(--blue);
      color: white;
      cursor: pointer;
      font-weight: 700;
      margin-top: 8px;
      margin-right: 6px;
      font-size: 13px;
    }

    button:hover {
      opacity: 0.92;
    }

    button.secondary {
      background: var(--slate);
    }

    button.danger {
      background: var(--red);
    }

    button.warning {
      background: var(--amber);
    }

    button.success {
      background: var(--green);
    }

    button.purple {
      background: var(--purple);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }

    .grid3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .grid2 {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
    }

    .summary-box {
      background: rgb(248, 250, 252);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }

    .summary-title {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .summary-number {
      font-size: 28px;
      font-weight: 900;
      margin-top: 6px;
      color: var(--ink);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      background: white;
    }

    th, td {
      text-align: left;
      border-bottom: 1px solid rgb(229, 231, 235);
      padding: 10px;
      vertical-align: top;
    }

    th {
      background: rgb(248, 250, 252);
      font-weight: 800;
      color: rgb(51, 65, 85);
      position: sticky;
      top: 0;
      z-index: 1;
    }

    .table-wrap {
      max-height: 520px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 14px;
    }

    .pill {
      font-weight: 800;
      padding: 4px 9px;
      border-radius: 999px;
      display: inline-block;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .status-active {
      background: rgb(220, 252, 231);
      color: rgb(22, 101, 52);
    }

    .status-revoked {
      background: rgb(254, 226, 226);
      color: rgb(153, 27, 27);
    }

    .status-expired, .status-past_due {
      background: rgb(254, 243, 199);
      color: rgb(146, 64, 14);
    }

    .status-suspended {
      background: rgb(255, 237, 213);
      color: rgb(154, 52, 18);
    }

    .status-canceled, .status-cancelled, .status-blocked, .status-inactive, .status-missing {
      background: rgb(241, 245, 249);
      color: rgb(71, 85, 105);
    }

    .status-trial {
      background: rgb(219, 234, 254);
      color: rgb(30, 64, 175);
    }

    /* Status filter chips */
    .status-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 4px 0 12px 0;
    }

    .chip {
      border: 1px solid var(--line);
      background: white;
      color: var(--slate);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      margin: 0;
      line-height: 1;
    }

    .chip .chip-count {
      color: var(--muted);
      font-weight: 800;
      margin-left: 4px;
    }

    .chip.active {
      background: var(--navy);
      color: white;
      border-color: var(--navy);
    }

    .chip.active .chip-count {
      color: rgb(203, 213, 225);
    }

    /* Sortable headers, monospace keys, numeric alignment */
    th.sortable {
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }

    th.sortable .arrow {
      color: var(--blue);
      font-size: 11px;
    }

    td.num, th.num {
      text-align: right;
      font-variant-numeric: tabular-nums;
    }

    code.key {
      display: inline-block;
      max-width: 160px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      vertical-align: middle;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      background: rgb(248, 250, 252);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 2px 6px;
    }

    button.mini {
      padding: 5px 9px;
      font-size: 12px;
      margin: 0;
    }

    .tier-basic {
      background: rgb(241, 245, 249);
      color: rgb(51, 65, 85);
    }

    .tier-pro {
      background: rgb(237, 233, 254);
      color: rgb(91, 33, 182);
    }

    .tier-trial {
      background: rgb(219, 234, 254);
      color: rgb(30, 64, 175);
    }

    .tier-internal {
      background: rgb(224, 242, 254);
      color: rgb(3, 105, 161);
    }

    .small {
      font-size: 12px;
      color: var(--muted);
    }

    .message {
      background: rgb(248, 250, 252);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      margin-top: 12px;
      font-size: 13px;
    }

    .success-message {
      background: rgb(236, 253, 245);
      border: 1px solid rgb(187, 247, 208);
      color: rgb(20, 83, 45);
    }

    .error-message {
      background: rgb(254, 242, 242);
      border: 1px solid rgb(254, 202, 202);
      color: rgb(153, 27, 27);
    }

    .license-key-box {
      word-break: break-all;
      background: rgb(248, 250, 252);
      border: 1px solid rgb(203, 213, 225);
      border-radius: 12px;
      padding: 12px;
      margin-top: 10px;
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    .hidden {
      display: none;
    }

    .log-window {
      max-height: 245px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgb(248, 250, 252);
      padding: 8px 12px;
    }

    .log-window.expanded {
      max-height: 560px;
    }

    .log-line {
      padding: 9px 0;
      border-bottom: 1px solid rgb(226, 232, 240);
    }

    .log-line:last-child {
      border-bottom: 0;
    }

    .muted {
      color: var(--muted);
    }

    .detail-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }

    .detail-box {
      background: rgb(248, 250, 252);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }

    .row-actions {
      white-space: nowrap;
    }

    .filters {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr auto;
      gap: 10px;
      align-items: end;
      margin-bottom: 12px;
    }


    .key-actions {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
    }

    .key-hidden-box {
      margin-top: 8px;
      max-width: 360px;
      max-height: 90px;
      overflow: auto;
      word-break: break-all;
      background: rgb(248, 250, 252);
      border: 1px solid rgb(203, 213, 225);
      border-radius: 10px;
      padding: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 11px;
    }

    .compact-table td,
    .compact-table th {
      white-space: normal;
    }

    .actions-cell {
      min-width: 180px;
    }

    .key-cell {
      width: 230px;
      max-width: 230px;
    }

    .name-cell {
      min-width: 210px;
    }

    @media (max-width: 900px) {
      .grid, .grid2, .grid3, .summary, .detail-layout, .filters {
        grid-template-columns: 1fr;
      }
      main {
        padding: 14px;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>UAS License Admin Dashboard</h1>
    <p>Basic = 1 device. Pro = 2 devices. Standard is removed from the sales/admin flow.</p>
  </header>

  <main>
    <div class="card">
      <div class="card-header">
        <div>
          <h2>Admin Access</h2>
          <div class="small">Keep this key private. Use this dashboard only from your own computer.</div>
        </div>
        <button onclick="loadEverything()">Load Dashboard</button>
      </div>
      <label>Admin API Key</label>
      <input id="adminKey" type="password" placeholder="Paste admin key here">
      <button onclick="saveAdminKey()">Save Key in Browser</button>
      <button class="secondary" onclick="clearAdminKey()">Clear Key</button>
    </div>

    <div class="card">
      <div class="card-header">
        <h2>Dashboard Summary</h2>
        <button onclick="loadStats()">Refresh Summary</button>
      </div>
      <div id="statsArea" class="small">Summary not loaded yet.</div>
    </div>

    <div class="card">
      <h2>Issue New License</h2>
      <div class="grid">
        <div>
          <label>Email</label>
          <input id="issueEmail" placeholder="customer@email.com">
        </div>
        <div>
          <label>Full Name</label>
          <input id="issueName" placeholder="Customer Name">
        </div>
        <div>
          <label>Plan</label>
          <select id="issueTier" onchange="applyTierDefaults()">
            <option value="basic">Basic - 1 device</option>
            <option value="pro">Pro - 2 devices</option>
            <option value="trial">Trial - manual</option>
            <option value="internal">Internal - manual</option>
          </select>
        </div>
        <div>
          <label>Days Valid</label>
          <input id="issueDays" type="number" value="30">
        </div>
        <div>
          <label>Max Devices</label>
          <input id="issueMaxDevices" type="number" value="1">
        </div>
        <div>
          <label>Terms Version</label>
          <input id="issueTerms" value="2026-04-21-v2">
        </div>
      </div>
      <button class="success" onclick="issueLicense()">Issue License</button>
      <div id="issueResult"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <div>
          <h2>Licenses</h2>
          <div class="small">Search, filter, open details, renew, revoke, reset devices, or adjust device limit.</div>
        </div>
        <button onclick="loadLicenses()">Refresh Licenses</button>
      </div>

      <div class="filters">
        <div>
          <label>Search</label>
          <input id="licenseSearch" placeholder="email or license key" oninput="renderLicenses()">
        </div>
        <div>
          <label>Plan</label>
          <select id="tierFilter" onchange="renderLicenses()">
            <option value="">All plans</option>
            <option value="basic">Basic</option>
            <option value="pro">Pro</option>
            <option value="trial">Trial</option>
            <option value="internal">Internal</option>
          </select>
        </div>
        <button class="secondary" onclick="clearFilters()">Clear</button>
      </div>

      <label>Status</label>
      <div id="statusChips" class="status-chips"></div>

      <div id="licensesArea" class="small">Licenses not loaded yet.</div>
    </div>

    <div id="detailCard" class="card hidden">
      <div class="card-header">
        <div>
          <h2>License Detail</h2>
          <div class="small">Compact view with scrollable history.</div>
        </div>
        <button class="secondary" onclick="closeDetail()">Close Detail</button>
      </div>
      <div id="detailArea"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <div>
          <h2>Update Notifications</h2>
          <div class="small">Send a new-version email to all active license users. Always run Dry Run first.</div>
        </div>
      </div>

      <div class="grid2">
        <div>
          <label>Subject</label>
          <input id="updateSubject" value="New UAS Generator update is available">
        </div>
        <div>
          <label>Limit</label>
          <input id="updateLimit" type="number" value="500">
        </div>
      </div>

      <label>Message</label>
      <textarea id="updateMessage">A new UAS Generator version is available. Please download the correct version for your device and use your existing license key.</textarea>

      <button class="secondary" onclick="broadcastUpdate(true)">Dry Run — Preview Recipients</button>
      <button class="warning" onclick="broadcastUpdate(false)">Send Update Email to Active Users</button>

      <div id="updateResult"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <div>
          <h2>Recent Activity</h2>
          <div class="small">Shows latest 5 by default. Expand to review more.</div>
        </div>
        <div>
          <button onclick="loadLogs()">Refresh Activity</button>
          <button class="secondary" onclick="toggleLogs()">Expand / Collapse</button>
        </div>
      </div>
      <div id="logsArea" class="log-window small">Activity not loaded yet.</div>
    </div>

  </main>

<script>
let allLicenses = [];
let allLogs = [];
let logsExpanded = false;
let currentDetailLicenseKey = "";
let statusFilterValue = "";
let licenseSort = { key: "customer_email", dir: "asc" };

function adminKey() {
  return document.getElementById("adminKey").value.trim();
}

function apiKeyQuery() {
  return encodeURIComponent(adminKey());
}

function saveAdminKey() {
  localStorage.setItem("uas_admin_key", adminKey());
  showMessage("issueResult", "Admin key saved in this browser.", true);
}

function clearAdminKey() {
  localStorage.removeItem("uas_admin_key");
  document.getElementById("adminKey").value = "";
}

function loadSavedKey() {
  const saved = localStorage.getItem("uas_admin_key");
  if (saved) {
    document.getElementById("adminKey").value = saved;
  }
}

function showMessage(id, text, ok) {
  const el = document.getElementById(id);
  el.innerHTML = `<div class="message ${ok ? "success-message" : "error-message"}">${escapeHtml(text)}</div>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmt(value) {
  return escapeHtml(value || "");
}

function pill(value, kind) {
  const safe = String(value || "").toLowerCase();
  return `<span class="pill ${kind}-${safe}">${escapeHtml(value || "missing")}</span>`;
}

function applyTierDefaults() {
  const tier = document.getElementById("issueTier").value;
  const max = document.getElementById("issueMaxDevices");
  const days = document.getElementById("issueDays");
  if (tier === "basic") {
    max.value = 1;
    days.value = 30;
  } else if (tier === "pro") {
    max.value = 2;
    days.value = 30;
  } else if (tier === "trial") {
    max.value = 1;
    days.value = 7;
  } else if (tier === "internal") {
    max.value = 2;
    days.value = 3650;
  }
}

async function requestJson(url, options = {}) {
  const res = await fetch(url, options);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    throw new Error(data.detail || data.message || text || `HTTP ${res.status}`);
  }
  return data;
}

async function loadEverything() {
  await Promise.allSettled([loadStats(), loadLogs(), loadLicenses()]);
}

async function loadStats() {
  try {
    const data = await requestJson(`/admin/stats?admin_api_key=${apiKeyQuery()}`);
    const s = data.stats || {};
    const byStatus = s.by_status || {};
    document.getElementById("statsArea").innerHTML = `
      <div class="summary">
        <div class="summary-box">
          <div class="summary-title">Total Licenses</div>
          <div class="summary-number">${fmt(s.total_licenses ?? 0)}</div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Active Licenses</div>
          <div class="summary-number">${fmt(s.active_licenses ?? byStatus.active ?? 0)}</div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Active Subscriptions</div>
          <div class="summary-number">${fmt(s.active_subscriptions ?? 0)}</div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Devices</div>
          <div class="summary-number">${fmt(s.total_devices ?? 0)}</div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Activations</div>
          <div class="summary-number">${fmt(s.total_activations ?? 0)}</div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Validations</div>
          <div class="summary-number">${fmt(s.total_validations ?? 0)}</div>
        </div>
      </div>`;
  } catch (e) {
    document.getElementById("statsArea").innerHTML = `<div class="message error-message">${escapeHtml(e.message)}</div>`;
  }
}

async function loadLogs() {
  try {
    const data = await requestJson(`/admin/logs?admin_api_key=${apiKeyQuery()}&limit=200`);
    allLogs = data.logs || [];
    renderLogs();
  } catch (e) {
    document.getElementById("logsArea").innerHTML = `<div class="message error-message">${escapeHtml(e.message)}</div>`;
  }
}

function renderLogs() {
  const area = document.getElementById("logsArea");
  area.className = logsExpanded ? "log-window expanded small" : "log-window small";
  const rows = logsExpanded ? allLogs : allLogs.slice(0, 5);
  if (!rows.length) {
    area.innerHTML = "No activity found.";
    return;
  }
  area.innerHTML = rows.map(log => `
    <div class="log-line">
      <b>${fmt(log.action)}</b>
      <span class="muted">${fmt(log.created_at)}</span><br>
      <span>${fmt(log.customer_email)}</span><br>
      <span class="muted">${fmt(log.license_key)}</span><br>
      <span>${fmt(log.details)}</span>
    </div>`).join("");
}

function toggleLogs() {
  logsExpanded = !logsExpanded;
  renderLogs();
}

async function issueLicense() {
  try {
    const body = {
      admin_api_key: adminKey(),
      email: document.getElementById("issueEmail").value.trim(),
      full_name: document.getElementById("issueName").value.trim(),
      tier: document.getElementById("issueTier").value,
      days: Number(document.getElementById("issueDays").value || 30),
      days_valid: Number(document.getElementById("issueDays").value || 30),
      max_devices: Number(document.getElementById("issueMaxDevices").value || 1),
      terms_version: document.getElementById("issueTerms").value.trim()
    };
    const data = await requestJson("/issue-license", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });
    document.getElementById("issueResult").innerHTML = `
      <div class="message success-message">
        <b>License issued.</b>
        <div class="license-key-box" id="newLicenseKey">${escapeHtml(data.license_key)}</div>
        <button onclick="copyText('newLicenseKey')">Copy License Key</button>
        <div class="small">Plan: ${fmt(data.tier)} | Max devices: ${fmt(data.max_devices)} | Expires: ${fmt(data.expires_at)}</div>
      </div>`;
    await loadEverything();
  } catch (e) {
    showMessage("issueResult", e.message, false);
  }
}

function copyText(id) {
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.innerText);
}

async function loadLicenses() {
  try {
    const data = await requestJson(`/admin/licenses?admin_api_key=${apiKeyQuery()}&limit=500`);
    allLicenses = data.licenses || [];
    renderLicenses();
  } catch (e) {
    document.getElementById("licensesArea").innerHTML = `<div class="message error-message">${escapeHtml(e.message)}</div>`;
  }
}


function copyLicenseKeyValue(value) {
  navigator.clipboard.writeText(value || "");
  alert("License key copied.");
}

function clearFilters() {
  document.getElementById("licenseSearch").value = "";
  document.getElementById("tierFilter").value = "";
  statusFilterValue = "";
  renderLicenses();
}

function setStatusFilter(value) {
  statusFilterValue = value;
  renderLicenses();
}

function setSort(key) {
  if (licenseSort.key === key) {
    licenseSort.dir = licenseSort.dir === "asc" ? "desc" : "asc";
  } else {
    licenseSort.key = key;
    licenseSort.dir = "asc";
  }
  renderLicenses();
}

function sortArrow(key) {
  if (licenseSort.key !== key) return "";
  return `<span class="arrow">${licenseSort.dir === "asc" ? "\\u2191" : "\\u2193"}</span>`;
}

function compareBy(key, dir) {
  const mult = dir === "asc" ? 1 : -1;
  return (a, b) => {
    let av, bv;
    if (key === "devices") {
      av = Number(a.device_count ?? 0);
      bv = Number(b.device_count ?? 0);
    } else if (key === "expires_at") {
      av = String(a.expires_at || "");
      bv = String(b.expires_at || "");
    } else {
      av = String(a[key] || "").toLowerCase();
      bv = String(b[key] || "").toLowerCase();
    }
    if (av < bv) return -1 * mult;
    if (av > bv) return 1 * mult;
    return 0;
  };
}

function renderStatusChips(searchTierFiltered) {
  const counts = {};
  searchTierFiltered.forEach(l => {
    const s = String(l.status || "missing").toLowerCase();
    counts[s] = (counts[s] || 0) + 1;
  });
  const order = ["active", "expired", "revoked", "suspended", "trial", "canceled", "blocked"];
  const present = Object.keys(counts).sort((a, b) => {
    const ia = order.indexOf(a), ib = order.indexOf(b);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });
  const chip = (value, label, count) => {
    const cls = "chip" + (statusFilterValue === value ? " active" : "");
    return `<button class="${cls}" onclick="setStatusFilter('${value}')">${escapeHtml(label)}<span class="chip-count">${count}</span></button>`;
  };
  let html = chip("", "All", searchTierFiltered.length);
  present.forEach(s => {
    const label = s.charAt(0).toUpperCase() + s.slice(1);
    html += chip(s, label, counts[s]);
  });
  document.getElementById("statusChips").innerHTML = html;
}

function renderLicenses() {
  const search = document.getElementById("licenseSearch").value.trim().toLowerCase();
  const tier = document.getElementById("tierFilter").value;

  const searchTierFiltered = allLicenses.filter(l => {
    const text = `${l.customer_email || ""} ${l.customer_full_name || ""} ${l.license_key || ""}`.toLowerCase();
    if (search && !text.includes(search)) return false;
    if (tier && String(l.tier || "").toLowerCase() !== tier) return false;
    return true;
  });

  renderStatusChips(searchTierFiltered);

  let rows = searchTierFiltered.filter(l => {
    if (statusFilterValue && String(l.status || "").toLowerCase() !== statusFilterValue) return false;
    return true;
  });

  rows = rows.slice().sort(compareBy(licenseSort.key, licenseSort.dir));

  if (!rows.length) {
    document.getElementById("licensesArea").innerHTML = "No licenses found.";
    return;
  }

  document.getElementById("licensesArea").innerHTML = `
    <div class="table-wrap">
      <table class="compact-table">
        <thead>
          <tr>
            <th class="name-cell sortable" onclick="setSort('customer_email')">Customer ${sortArrow('customer_email')}</th>
            <th class="sortable" onclick="setSort('tier')">Plan ${sortArrow('tier')}</th>
            <th class="sortable" onclick="setSort('status')">Status ${sortArrow('status')}</th>
            <th class="num sortable" onclick="setSort('devices')">Devices ${sortArrow('devices')}</th>
            <th class="num sortable" onclick="setSort('expires_at')">Expires ${sortArrow('expires_at')}</th>
            <th class="key-cell">License Key</th>
            <th class="actions-cell">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map((l) => {
            const key = l.license_key || "";
            const deviceCount = l.device_count ?? 0;
            const maxDevices = l.max_devices ?? "";
            const email = l.customer_email || "";
            const fullName = l.customer_full_name || "";
            const keyJson = JSON.stringify(key);
            const openJson = JSON.stringify(key);
            return `
              <tr>
                <td class="name-cell">
                  <b>${fmt(email)}</b>
                  ${fullName ? `<br><span class="small">${fmt(fullName)}</span>` : ""}
                </td>
                <td>${pill(l.tier || "basic", "tier")}</td>
                <td>${pill(l.status || "missing", "status")}</td>
                <td class="num"><b>${fmt(deviceCount)}</b> / ${fmt(maxDevices)}</td>
                <td class="num">${fmt(l.expires_at)}</td>
                <td class="key-cell">
                  <code class="key" title="${fmt(key)}">${fmt(key)}</code>
                  <button class="mini" onclick='copyLicenseKeyValue(${keyJson})'>Copy</button>
                </td>
                <td class="actions-cell">
                  <button class="mini" onclick='openDetail(${openJson})'>Open</button>
                  <button class="mini success" onclick='quickRenew(${openJson}, 30)'>Renew 30d</button>
                </td>
              </tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>`;
}


async function openDetail(licenseKey) {
  currentDetailLicenseKey = licenseKey;
  document.getElementById("detailCard").classList.remove("hidden");
  document.getElementById("detailArea").innerHTML = "Loading detail...";
  try {
    const detail = await requestJson(`/admin/license?admin_api_key=${apiKeyQuery()}&license_key=${encodeURIComponent(licenseKey)}`);
    const history = await requestJson(`/admin/license-history?admin_api_key=${apiKeyQuery()}&license_key=${encodeURIComponent(licenseKey)}&limit=200`);
    renderDetail(detail, history);
    document.getElementById("detailCard").scrollIntoView({behavior: "smooth"});
  } catch (e) {
    document.getElementById("detailArea").innerHTML = `<div class="message error-message">${escapeHtml(e.message)}</div>`;
  }
}

function renderDetail(detail, history) {
  const l = detail.license || {};
  const devices = detail.devices || [];
  const activations = history.activations || [];
  const validations = history.validations || [];

  document.getElementById("detailArea").innerHTML = `
    <div class="detail-layout">
      <div class="detail-box">
        <h3>License</h3>
        <div><b>Email:</b> ${fmt(l.customer_email)}</div>
        <div><b>Plan:</b> ${pill(l.tier || "basic", "tier")}</div>
        <div><b>Status:</b> ${pill(l.status || "missing", "status")}</div>
        <div><b>Max Devices:</b> ${fmt(l.max_devices)}</div>
        <div><b>Issued:</b> ${fmt(l.issued_at)}</div>
        <div><b>Expires:</b> ${fmt(l.expires_at)}</div>
        <div class="license-key-box" id="detailLicenseKey">${fmt(l.license_key)}</div>
        <button onclick="copyText('detailLicenseKey')">Copy Key</button>

        <h3>Admin Controls</h3>
        <div class="grid2">
          <div>
            <label>Renew Days</label>
            <input id="renewDays" type="number" value="30">
            <button class="success" onclick="renewCurrent()">Renew Membership</button>
          </div>
          <div>
            <label>Max Devices</label>
            <input id="newMaxDevices" type="number" value="${fmt(l.max_devices || 1)}">
            <button class="purple" onclick="updateCurrentMaxDevices()">Update Max Devices</button>
          </div>
        </div>

        <button class="success" onclick="setStatus('${fmt(l.license_key)}', 'active')">Set Active</button>
        <button class="warning" onclick="setStatus('${fmt(l.license_key)}', 'suspended')">Suspend</button>
        <button class="danger" onclick="setStatus('${fmt(l.license_key)}', 'revoked')">Revoke</button>
        <button class="secondary" onclick="resetDevices('${fmt(l.license_key)}')">Reset Devices</button>
      </div>

      <div class="detail-box">
        <h3>Devices</h3>
        ${devices.length ? `
          <div class="table-wrap" style="max-height: 260px;">
            <table>
              <thead><tr><th>Device</th><th>Host</th><th>Last Seen</th><th>App</th></tr></thead>
              <tbody>
                ${devices.map(d => `
                  <tr>
                    <td>${fmt(d.device_id)}</td>
                    <td>${fmt(d.hostname)}</td>
                    <td>${fmt(d.last_seen_at)}</td>
                    <td>${fmt(d.app_version)}</td>
                  </tr>`).join("")}
              </tbody>
            </table>
          </div>` : `<div class="small">No devices activated yet.</div>`}
      </div>
    </div>

    <div class="detail-layout" style="margin-top: 14px;">
      <div class="detail-box">
        <h3>Recent Activations</h3>
        <div class="small">Latest 5 shown first. Scroll for more.</div>
        <div class="log-window">
          ${(activations.length ? activations : []).map(a => `
            <div class="log-line">
              <b>${fmt(a.activated_at)}</b><br>
              <span>${fmt(a.hostname)}</span><br>
              <span class="muted">${fmt(a.device_id)}</span>
            </div>`).join("") || "No activations found."}
        </div>
      </div>

      <div class="detail-box">
        <h3>Recent Validations</h3>
        <div class="small">Latest 5 visible first. Scroll for more.</div>
        <div class="log-window">
          ${(validations.length ? validations : []).map(v => `
            <div class="log-line">
              <b>${fmt(v.validated_at)}</b><br>
              <span>${fmt(v.hostname)}</span><br>
              <span class="muted">${fmt(v.device_id)}</span>
            </div>`).join("") || "No validations found."}
        </div>
      </div>
    </div>

    <div id="detailMessage"></div>`;
}

function closeDetail() {
  document.getElementById("detailCard").classList.add("hidden");
  currentDetailLicenseKey = "";
}

async function setStatus(licenseKey, newStatus) {
  if (!confirm(`Set license status to ${newStatus}?`)) return;
  try {
    await requestJson("/revoke-license", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({admin_api_key: adminKey(), license_key: licenseKey, new_status: newStatus})
    });
    await loadEverything();
    await openDetail(licenseKey);
  } catch (e) {
    showMessage("detailMessage", e.message, false);
  }
}

async function resetDevices(licenseKey) {
  if (!confirm("Reset all activated devices for this license? The user will need to activate again.")) return;
  try {
    await requestJson("/reset-devices", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({admin_api_key: adminKey(), license_key: licenseKey})
    });
    await loadEverything();
    await openDetail(licenseKey);
  } catch (e) {
    showMessage("detailMessage", e.message, false);
  }
}

async function quickRenew(licenseKey, days) {
  if (!confirm(`Renew this license for ${days} days?`)) return;
  try {
    await requestJson("/admin/renew-license", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({admin_api_key: adminKey(), license_key: licenseKey, days: days})
    });
    await loadEverything();
  } catch (e) {
    alert(e.message);
  }
}

async function renewCurrent() {
  const days = Number(document.getElementById("renewDays").value || 30);
  await quickRenew(currentDetailLicenseKey, days);
  await openDetail(currentDetailLicenseKey);
}

async function updateCurrentMaxDevices() {
  const maxDevices = Number(document.getElementById("newMaxDevices").value || 1);
  if (!confirm(`Set max devices to ${maxDevices}?`)) return;
  try {
    await requestJson("/admin/update-max-devices", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({admin_api_key: adminKey(), license_key: currentDetailLicenseKey, max_devices: maxDevices})
    });
    await loadEverything();
    await openDetail(currentDetailLicenseKey);
  } catch (e) {
    showMessage("detailMessage", e.message, false);
  }
}


async function broadcastUpdate(dryRun) {
  const subject = document.getElementById("updateSubject").value.trim();
  const message = document.getElementById("updateMessage").value.trim();
  const limit = Number(document.getElementById("updateLimit").value || 500);
  const result = document.getElementById("updateResult");

  if (!subject) {
    result.innerHTML = `<div class="message error-message">Subject is required.</div>`;
    return;
  }

  if (!message) {
    result.innerHTML = `<div class="message error-message">Message is required.</div>`;
    return;
  }

  if (!dryRun) {
    const ok = confirm("This will send update emails to all ACTIVE license users. Did you run Dry Run first?");
    if (!ok) return;
  }

  result.innerHTML = `<div class="message">Working...</div>`;

  try {
    const data = await requestJson("/admin/broadcast-update", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        admin_api_key: adminKey(),
        dry_run: dryRun,
        limit: limit,
        subject: subject,
        message: message
      })
    });

    const rows = data.results || [];
    const emails = rows.map(r => {
      const status = r.dry_run ? "dry-run" : (r.sent ? "sent" : "failed");
      return `<div>${escapeHtml(r.email || "")} — <b>${escapeHtml(status)}</b></div>`;
    }).join("");

    result.innerHTML = `
      <div class="message ${data.failed ? "error-message" : "success-message"}">
        <b>${dryRun ? "Dry Run Complete" : "Broadcast Complete"}</b><br>
        Recipients: ${escapeHtml(data.recipients ?? 0)}<br>
        Sent: ${escapeHtml(data.sent ?? 0)}<br>
        Failed: ${escapeHtml(data.failed ?? 0)}
        <div class="result-list">${emails || "No active recipients found."}</div>
      </div>
    `;

    await loadLogs();
  } catch (e) {
    result.innerHTML = `<div class="message error-message">${escapeHtml(e.message)}</div>`;
  }
}


loadSavedKey();
applyTierDefaults();
</script>
</body>
</html>
"""
