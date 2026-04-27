ADMIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>UAS License Admin</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      background: #f6f7f9;
      color: #1f2933;
    }
    header {
      background: #111827;
      color: white;
      padding: 18px 24px;
    }
    header h1 {
      margin: 0;
      font-size: 22px;
    }
    main {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }
    .card {
      background: white;
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 18px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    label {
      display: block;
      font-weight: 600;
      margin-top: 10px;
      margin-bottom: 4px;
      font-size: 13px;
    }
    input, select {
      width: 100%;
      box-sizing: border-box;
      padding: 9px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 14px;
    }
    button {
      padding: 9px 13px;
      border: 0;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      cursor: pointer;
      font-weight: 600;
      margin-top: 10px;
      margin-right: 6px;
    }
    button.secondary {
      background: #475569;
    }
    button.danger {
      background: #dc2626;
    }
    button.warning {
      background: #d97706;
    }
    button.success {
      background: #16a34a;
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
    .summary {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
    }
    .summary-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 14px;
    }
    .summary-number {
      font-size: 26px;
      font-weight: 800;
      margin-top: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      background: white;
    }
    th, td {
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
      padding: 9px;
      vertical-align: top;
    }
    th {
      background: #f1f5f9;
      font-weight: 700;
    }
    .status {
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 999px;
      display: inline-block;
    }
    .active {
      background: #dcfce7;
      color: #166534;
    }
    .revoked, .canceled {
      background: #fee2e2;
      color: #991b1b;
    }
    .suspended, .expired {
      background: #fef3c7;
      color: #92400e;
    }
    .trial {
      background: #dbeafe;
      color: #1e40af;
    }
    .small {
      font-size: 12px;
      color: #64748b;
    }
    .message {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 12px;
      margin-top: 12px;
      font-size: 13px;
    }
    .success-message {
      background: #ecfdf5;
      border: 1px solid #bbf7d0;
      color: #14532d;
    }
    .error-message {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #991b1b;
    }
    .license-key-box {
      word-break: break-all;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 12px;
      margin-top: 10px;
      font-size: 12px;
    }
    .hidden {
      display: none;
    }
    .log-line {
      padding: 8px 0;
      border-bottom: 1px solid #e5e7eb;
    }
    .muted {
      color: #64748b;
    }
  </style>
</head>
<body>
  <header>
    <h1>UAS License Admin Dashboard</h1>
  </header>

  <main>
    <div class="card">
      <h2>Admin Access</h2>
      <label>Admin API Key</label>
      <input id="adminKey" type="password" placeholder="Paste admin key here">
      <button onclick="saveAdminKey()">Save Key in Browser</button>
      <button class="secondary" onclick="clearAdminKey()">Clear Key</button>
      <button onclick="loadEverything()">Load Dashboard</button>
      <p class="small">Use this only on your own computer.</p>
    </div>

    <div class="card">
      <h2>Dashboard Summary</h2>
      <button onclick="loadStats()">Refresh Summary</button>
      <div id="statsArea" class="small">Summary not loaded yet.</div>
    </div>

    <div class="card">
      <h2>Recent Activity</h2>
      <button onclick="loadLogs()">Refresh Activity</button>
      <div id="logsArea" class="small">Activity not loaded yet.</div>
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
          <label>Tier</label>
          <select id="issueTier">
            <option value="basic">Basic</option>
            <option value="standard">Standard</option>
            <option value="pro">Pro</option>
            <option value="trial">Trial</option>
          </select>
        </div>
        <div>
          <label>Days Valid</label>
          <input id="issueDays" type="number" value="30">
        </div>
      </div>
      <div class="grid3">
        <div>
          <label>Max Devices</label>
          <input id="issueMaxDevices" type="number" value="1">
        </div>
        <div>
          <label>Terms Version</label>
          <input id="issueTerms" value="2026-04-21-v2">
        </div>
        <div>
          <label>&nbsp;</label>
          <button onclick="issueLicense()">Issue License</button>
        </div>
      </div>
      <div id="issueResult" class="hidden"></div>
    </div>

    <div class="card">
      <h2>Licenses</h2>
      <div class="grid3">
        <div>
          <label>Search email / status / tier</label>
          <input id="searchBox" oninput="renderLicenses()" placeholder="Type to filter">
        </div>
        <div>
          <label>Limit</label>
          <input id="limitBox" type="number" value="200">
        </div>
        <div>
          <label>&nbsp;</label>
          <button onclick="loadLicenses()">Refresh</button>
        </div>
      </div>
      <div id="licenseTable"></div>
    </div>

    <div class="card">
      <h2>License Detail</h2>
      <div id="detailArea">
        <p class="small">Select a license to view details.</p>
      </div>
    </div>
  </main>

<script>
let licenses = [];

function getAdminKey() {
  return document.getElementById("adminKey").value.trim();
}

function saveAdminKey() {
  const key = getAdminKey();
  if (!key) {
    alert("Paste admin key first.");
    return;
  }
  localStorage.setItem("uas_admin_key", key);
  alert("Admin key saved in this browser.");
}

function clearAdminKey() {
  localStorage.removeItem("uas_admin_key");
  document.getElementById("adminKey").value = "";
  alert("Admin key cleared.");
}

function loadSavedKey() {
  const key = localStorage.getItem("uas_admin_key") || "";
  document.getElementById("adminKey").value = key;
}

function showMessage(elementId, text, type="normal") {
  const el = document.getElementById(elementId);
  el.classList.remove("hidden");
  el.className = "message";
  if (type === "success") el.classList.add("success-message");
  if (type === "error") el.classList.add("error-message");
  el.innerHTML = text;
}

function statusBadge(status) {
  const s = String(status || "").toLowerCase();
  return `<span class="status ${s}">${s}</span>`;
}

function shortDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (isNaN(d.getTime())) return String(value).split("T")[0] || value;
  return d.toLocaleDateString(undefined, {year: "numeric", month: "short", day: "numeric"});
}

function simpleAction(action) {
  const map = {
    "issue_license": "License issued",
    "activate_license": "Device activated",
    "set_license_status": "License status changed",
    "reset_devices": "Devices reset"
  };
  return map[action] || action || "Activity";
}

function simpleDetails(details) {
  if (!details) return "";
  return String(details)
    .replace("tier=", "tier: ")
    .replace("max_devices=", "devices: ")
    .replace("device_id=", "device: ")
    .replace("new_status=", "new status: ")
    .replace("deleted_devices=", "deleted devices: ");
}

async function apiGet(path) {
  const res = await fetch(path);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

async function loadEverything() {
  await loadStats();
  await loadLogs();
  await loadLicenses();
}

async function loadStats() {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }
  try {
    const data = await apiGet(`/admin/stats?admin_api_key=${encodeURIComponent(key)}`);
    renderStats(data.stats || {});
  } catch (err) {
    document.getElementById("statsArea").textContent = String(err.message || err);
  }
}

function renderStats(stats) {
  const byStatus = stats.by_status || {};
  let html = "";
  html += "<div class='summary'>";
  html += `<div class='summary-box'><b>Customers</b><div class='summary-number'>${stats.total_customers || 0}</div></div>`;
  html += `<div class='summary-box'><b>Licenses</b><div class='summary-number'>${stats.total_licenses || 0}</div></div>`;
  html += `<div class='summary-box'><b>Devices</b><div class='summary-number'>${stats.total_devices || 0}</div></div>`;
  html += `<div class='summary-box'><b>Active</b><div class='summary-number'>${byStatus.active || 0}</div></div>`;
  html += `<div class='summary-box'><b>Suspended / Revoked</b><div class='summary-number'>${(byStatus.suspended || 0) + (byStatus.revoked || 0)}</div></div>`;
  html += "</div>";
  document.getElementById("statsArea").innerHTML = html;
}

async function loadLogs() {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }
  try {
    const data = await apiGet(`/admin/logs?admin_api_key=${encodeURIComponent(key)}&limit=50`);
    renderLogs(data.logs || []);
  } catch (err) {
    document.getElementById("logsArea").textContent = String(err.message || err);
  }
}

function renderLogs(logs) {
  if (!logs.length) {
    document.getElementById("logsArea").innerHTML = "<p class='small'>No activity yet.</p>";
    return;
  }

  let html = "";
  for (const row of logs) {
    html += "<div class='log-line'>";
    html += `<b>${shortDate(row.created_at)}</b> — ${simpleAction(row.action)}`;
    if (row.customer_email) html += ` for <b>${row.customer_email}</b>`;
    if (row.details) html += ` <span class='muted'>(${simpleDetails(row.details)})</span>`;
    html += "</div>";
  }
  document.getElementById("logsArea").innerHTML = html;
}

async function loadLicenses() {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }
  const limit = document.getElementById("limitBox").value || 200;
  try {
    const data = await apiGet(`/admin/licenses?admin_api_key=${encodeURIComponent(key)}&limit=${encodeURIComponent(limit)}`);
    licenses = data.licenses || [];
    renderLicenses();
    await loadStats();
    await loadLogs();
  } catch (err) {
    alert("Could not load licenses: " + String(err.message || err));
  }
}

function renderLicenses() {
  const q = (document.getElementById("searchBox").value || "").toLowerCase();
  let filtered = licenses.filter(x => {
    const text = [
      x.customer_email,
      x.status,
      x.tier,
      x.issued_at,
      x.expires_at
    ].join(" ").toLowerCase();
    return text.includes(q);
  });

  if (!filtered.length) {
    document.getElementById("licenseTable").innerHTML = "<p class='small'>No licenses found.</p>";
    return;
  }

  let html = "<table><thead><tr>";
  html += "<th>ID</th><th>Email</th><th>Tier</th><th>Status</th><th>Allowed Devices</th><th>Issued</th><th>Expires</th><th>Action</th>";
  html += "</tr></thead><tbody>";

  for (const lic of filtered) {
    html += "<tr>";
    html += `<td>${lic.id}</td>`;
    html += `<td>${lic.customer_email || ""}</td>`;
    html += `<td>${lic.tier || ""}</td>`;
    html += `<td>${statusBadge(lic.status)}</td>`;
    html += `<td>${lic.max_devices || ""}</td>`;
    html += `<td>${shortDate(lic.issued_at)}</td>`;
    html += `<td>${shortDate(lic.expires_at)}</td>`;
    html += `<td><button onclick='loadDetail(${JSON.stringify(lic.license_key)})'>Open</button></td>`;
    html += "</tr>";
  }

  html += "</tbody></table>";
  document.getElementById("licenseTable").innerHTML = html;
}

async function loadDetail(licenseKey) {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }

  try {
    const data = await apiGet(`/admin/license?admin_api_key=${encodeURIComponent(key)}&license_key=${encodeURIComponent(licenseKey)}`);
    renderDetail(data);
  } catch (err) {
    alert("Could not load license detail: " + String(err.message || err));
  }
}

function renderDetail(data) {
  const lic = data.license || {};
  const devices = data.devices || [];

  let html = "";
  html += `<h3>${lic.customer_email || ""}</h3>`;
  html += `<p>Status: ${statusBadge(lic.status)} | Tier: <b>${lic.tier || ""}</b> | Allowed devices: <b>${lic.max_devices || ""}</b></p>`;
  html += `<p class="small">Issued: ${shortDate(lic.issued_at)} | Expires: ${shortDate(lic.expires_at)}</p>`;

  html += `<button onclick='copyText(${JSON.stringify(lic.license_key)})'>Copy License Key</button>`;
  html += `<button class="success" onclick='setStatus(${JSON.stringify(lic.license_key)}, "active")'>Set Active</button>`;
  html += `<button class="warning" onclick='setStatus(${JSON.stringify(lic.license_key)}, "suspended")'>Suspend</button>`;
  html += `<button class="danger" onclick='setStatus(${JSON.stringify(lic.license_key)}, "revoked")'>Revoke</button>`;
  html += `<button class="secondary" onclick='resetDevices(${JSON.stringify(lic.license_key)})'>Reset Devices</button>`;
  html += `<button onclick='loadHistory(${JSON.stringify(lic.license_key)})'>Load History</button>`;

  html += `<div id="historyArea" class="small" style="margin-top:12px;">History not loaded yet.</div>`;

  html += "<h3>Devices</h3>";
  if (!devices.length) {
    html += "<p class='small'>No devices activated.</p>";
  } else {
    html += "<table><thead><tr><th>Device</th><th>Computer Name</th><th>App Version</th><th>First Seen</th><th>Last Seen</th></tr></thead><tbody>";
    for (const d of devices) {
      html += "<tr>";
      html += `<td>${d.device_id || ""}</td>`;
      html += `<td>${d.hostname || ""}</td>`;
      html += `<td>${d.app_version || ""}</td>`;
      html += `<td>${shortDate(d.first_seen_at)}</td>`;
      html += `<td>${shortDate(d.last_seen_at)}</td>`;
      html += "</tr>";
    }
    html += "</tbody></table>";
  }

  document.getElementById("detailArea").innerHTML = html;
}

async function issueLicense() {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }

  const body = {
    admin_api_key: key,
    email: document.getElementById("issueEmail").value.trim(),
    full_name: document.getElementById("issueName").value.trim(),
    tier: document.getElementById("issueTier").value,
    days: parseInt(document.getElementById("issueDays").value || "30", 10),
    max_devices: parseInt(document.getElementById("issueMaxDevices").value || "1", 10),
    terms_version: document.getElementById("issueTerms").value.trim()
  };

  try {
    const data = await apiPost("/issue-license", body);
    let html = "";
    html += "<b>License created successfully.</b>";
    html += `<div class="license-key-box" id="newLicenseKey">${data.license_key}</div>`;
    html += `<button onclick='copyText(${JSON.stringify(data.license_key)})'>Copy License Key</button>`;
    showMessage("issueResult", html, "success");
    await loadLicenses();
  } catch (err) {
    showMessage("issueResult", "Could not issue license: " + String(err.message || err), "error");
  }
}

async function setStatus(licenseKey, status) {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }

  if (!confirm(`Set license status to ${status}?`)) {
    return;
  }

  try {
    await apiPost("/revoke-license", {
      admin_api_key: key,
      license_key: licenseKey,
      new_status: status
    });
    await loadLicenses();
    await loadDetail(licenseKey);
  } catch (err) {
    alert("Could not update status: " + String(err.message || err));
  }
}

async function resetDevices(licenseKey) {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }

  if (!confirm("Reset devices for this license? Customer will need to activate again.")) {
    return;
  }

  try {
    await apiPost("/reset-devices", {
      admin_api_key: key,
      license_key: licenseKey
    });
    await loadDetail(licenseKey);
    await loadStats();
    await loadLogs();
  } catch (err) {
    alert("Could not reset devices: " + String(err.message || err));
  }
}

async function loadHistory(licenseKey) {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }
  try {
    const data = await apiGet(`/admin/license-history?admin_api_key=${encodeURIComponent(key)}&license_key=${encodeURIComponent(licenseKey)}&limit=100`);
    renderHistory(data.activations || [], data.validations || []);
  } catch (err) {
    document.getElementById("historyArea").textContent = String(err.message || err);
  }
}

function renderHistory(activations, validations) {
  let html = "";

  html += "<h3>Activation History</h3>";
  if (!activations.length) {
    html += "<p class='small'>No activations found.</p>";
  } else {
    for (const row of activations) {
      html += `<div class='log-line'><b>${shortDate(row.activated_at)}</b> — Device activated`;
      if (row.hostname) html += ` on <b>${row.hostname}</b>`;
      if (row.app_version) html += ` <span class='muted'>(${row.app_version})</span>`;
      html += "</div>";
    }
  }

  html += "<h3>Validation History</h3>";
  if (!validations.length) {
    html += "<p class='small'>No validations found.</p>";
  } else {
    for (const row of validations) {
      html += `<div class='log-line'><b>${shortDate(row.validated_at)}</b> — License checked`;
      if (row.hostname) html += ` on <b>${row.hostname}</b>`;
      if (row.app_version) html += ` <span class='muted'>(${row.app_version})</span>`;
      html += "</div>";
    }
  }

  document.getElementById("historyArea").innerHTML = html;
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert("Copied.");
  }).catch(() => {
    alert("Could not copy automatically. Select and copy manually.");
  });
}

loadSavedKey();
</script>
</body>
</html>
"""
