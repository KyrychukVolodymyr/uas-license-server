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
      max-width: 1300px;
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
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
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
    pre {
      background: #0f172a;
      color: #e5e7eb;
      padding: 12px;
      border-radius: 10px;
      overflow: auto;
      white-space: pre-wrap;
      font-size: 12px;
    }
    .small {
      font-size: 12px;
      color: #64748b;
    }
    .keycell {
      max-width: 260px;
      word-break: break-all;
      font-size: 11px;
    }
    .hidden {
      display: none;
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
      <button onclick="loadLicenses()">Load Licenses</button>
      <p class="small">The key is stored only in this browser local storage. Do not use this page on a shared computer.</p>
    </div>

    <div class="card">
      <h2>Dashboard Summary</h2>
      <button onclick="loadStats()">Refresh Summary</button>
      <div id="statsArea" class="small">Summary not loaded yet.</div>
    </div>

    <div class="card">
      <h2>Admin Audit Logs</h2>
      <button onclick="loadLogs()">Refresh Logs</button>
      <div id="logsArea" class="small">Logs not loaded yet.</div>
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
      <pre id="issueResult" class="hidden"></pre>
    </div>

    <div class="card">
      <h2>Licenses</h2>
      <div class="grid3">
        <div>
          <label>Search email / status / tier / key</label>
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

    <div class="card">
      <h2>Raw Output</h2>
      <pre id="rawOutput">Ready.</pre>
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

function showRaw(obj) {
  document.getElementById("rawOutput").textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
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
    document.getElementById("statsArea").textContent = String(err);
  }
}

function renderStats(stats) {
  const byStatus = stats.by_status || {};
  const byTier = stats.by_tier || {};

  let html = "";
  html += "<div class='grid'>";
  html += `<div><b>Total Customers</b><br>${stats.total_customers || 0}</div>`;
  html += `<div><b>Total Licenses</b><br>${stats.total_licenses || 0}</div>`;
  html += `<div><b>Total Devices</b><br>${stats.total_devices || 0}</div>`;
  html += `<div><b>Active</b><br>${byStatus.active || 0}</div>`;
  html += "</div>";

  html += "<h3>Status Breakdown</h3>";
  html += "<pre>" + JSON.stringify(byStatus, null, 2) + "</pre>";

  html += "<h3>Tier Breakdown</h3>";
  html += "<pre>" + JSON.stringify(byTier, null, 2) + "</pre>";

  document.getElementById("statsArea").innerHTML = html;
}

async function loadLogs() {
  const key = getAdminKey();
  if (!key) {
    alert("Enter admin key first.");
    return;
  }
  try {
    const data = await apiGet(`/admin/logs?admin_api_key=${encodeURIComponent(key)}&limit=100`);
    renderLogs(data.logs || []);
  } catch (err) {
    document.getElementById("logsArea").textContent = String(err);
  }
}

function renderLogs(logs) {
  if (!logs.length) {
    document.getElementById("logsArea").innerHTML = "<p class='small'>No logs found.</p>";
    return;
  }

  let html = "<table><thead><tr><th>ID</th><th>Action</th><th>Email</th><th>Details</th><th>Created</th></tr></thead><tbody>";
  for (const row of logs) {
    html += "<tr>";
    html += `<td>${row.id || ""}</td>`;
    html += `<td>${row.action || ""}</td>`;
    html += `<td>${row.customer_email || ""}</td>`;
    html += `<td>${row.details || ""}</td>`;
    html += `<td>${row.created_at || ""}</td>`;
    html += "</tr>";
  }
  html += "</tbody></table>";
  document.getElementById("logsArea").innerHTML = html;
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
    showRaw(data);
  } catch (err) {
    document.getElementById("historyArea").textContent = String(err);
  }
}

function renderHistory(activations, validations) {
  let html = "";

  html += "<h3>Activation History</h3>";
  if (!activations.length) {
    html += "<p class='small'>No activations found.</p>";
  } else {
    html += "<table><thead><tr><th>ID</th><th>Device ID</th><th>Hostname</th><th>App Version</th><th>Activated</th></tr></thead><tbody>";
    for (const row of activations) {
      html += "<tr>";
      html += `<td>${row.id || ""}</td>`;
      html += `<td>${row.device_id || ""}</td>`;
      html += `<td>${row.hostname || ""}</td>`;
      html += `<td>${row.app_version || ""}</td>`;
      html += `<td>${row.activated_at || ""}</td>`;
      html += "</tr>";
    }
    html += "</tbody></table>";
  }

  html += "<h3>Validation History</h3>";
  if (!validations.length) {
    html += "<p class='small'>No validations found.</p>";
  } else {
    html += "<table><thead><tr><th>ID</th><th>Device ID</th><th>Hostname</th><th>App Version</th><th>Validated</th></tr></thead><tbody>";
    for (const row of validations) {
      html += "<tr>";
      html += `<td>${row.id || ""}</td>`;
      html += `<td>${row.device_id || ""}</td>`;
      html += `<td>${row.hostname || ""}</td>`;
      html += `<td>${row.app_version || ""}</td>`;
      html += `<td>${row.validated_at || ""}</td>`;
      html += "</tr>";
    }
    html += "</tbody></table>";
  }

  document.getElementById("historyArea").innerHTML = html;
}


function statusBadge(status) {
  const s = String(status || "").toLowerCase();
  return `<span class="status ${s}">${s}</span>`;
}

async function apiGet(path) {
  const res = await fetch(path);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(JSON.stringify(data));
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
    throw new Error(JSON.stringify(data));
  }
  return data;
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
    showRaw(data);
    renderLicenses();
    await loadStats();
    await loadLogs();
  } catch (err) {
    showRaw(String(err));
    alert("Could not load licenses.");
  }
}

function renderLicenses() {
  const q = (document.getElementById("searchBox").value || "").toLowerCase();
  let filtered = licenses.filter(x => {
    const text = JSON.stringify(x).toLowerCase();
    return text.includes(q);
  });

  if (!filtered.length) {
    document.getElementById("licenseTable").innerHTML = "<p class='small'>No licenses found.</p>";
    return;
  }

  let html = "<table><thead><tr>";
  html += "<th>ID</th><th>Email</th><th>Tier</th><th>Status</th><th>Devices</th><th>Issued</th><th>Expires</th><th>License Key</th><th>Action</th>";
  html += "</tr></thead><tbody>";

  for (const lic of filtered) {
    html += "<tr>";
    html += `<td>${lic.id}</td>`;
    html += `<td>${lic.customer_email || ""}</td>`;
    html += `<td>${lic.tier || ""}</td>`;
    html += `<td>${statusBadge(lic.status)}</td>`;
    html += `<td>${lic.max_devices || ""}</td>`;
    html += `<td>${lic.issued_at || ""}</td>`;
    html += `<td>${lic.expires_at || ""}</td>`;
    html += `<td class="keycell">${lic.license_key || ""}</td>`;
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
    showRaw(data);
    renderDetail(data);
  } catch (err) {
    showRaw(String(err));
    alert("Could not load license detail.");
  }
}

function renderDetail(data) {
  const lic = data.license || {};
  const devices = data.devices || [];

  let html = "";
  html += `<h3>${lic.customer_email || ""}</h3>`;
  html += `<p>Status: ${statusBadge(lic.status)} | Tier: <b>${lic.tier || ""}</b> | Max devices: <b>${lic.max_devices || ""}</b></p>`;
  html += `<p class="small">Issued: ${lic.issued_at || ""} | Expires: ${lic.expires_at || ""}</p>`;
  html += `<p class="small keycell">License Key: ${lic.license_key || ""}</p>`;

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
    html += "<table><thead><tr><th>ID</th><th>Device ID</th><th>Hostname</th><th>App Version</th><th>First Seen</th><th>Last Seen</th></tr></thead><tbody>";
    for (const d of devices) {
      html += "<tr>";
      html += `<td>${d.id}</td>`;
      html += `<td>${d.device_id || ""}</td>`;
      html += `<td>${d.hostname || ""}</td>`;
      html += `<td>${d.app_version || ""}</td>`;
      html += `<td>${d.first_seen_at || ""}</td>`;
      html += `<td>${d.last_seen_at || ""}</td>`;
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
    const pre = document.getElementById("issueResult");
    pre.classList.remove("hidden");
    pre.textContent = JSON.stringify(data, null, 2);
    showRaw(data);
    await loadLicenses();
  } catch (err) {
    showRaw(String(err));
    alert("Could not issue license.");
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
    const data = await apiPost("/revoke-license", {
      admin_api_key: key,
      license_key: licenseKey,
      new_status: status
    });
    showRaw(data);
    await loadLicenses();
    await loadDetail(licenseKey);
  } catch (err) {
    showRaw(String(err));
    alert("Could not update status.");
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
    const data = await apiPost("/reset-devices", {
      admin_api_key: key,
      license_key: licenseKey
    });
    showRaw(data);
    await loadDetail(licenseKey);
  } catch (err) {
    showRaw(String(err));
    alert("Could not reset devices.");
  }
}

loadSavedKey();
</script>
</body>
</html>
"""
