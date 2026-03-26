let activeDataset = null;
let datasets = {};
let monacoEditor = null;

const api = {
  async upload(formData) {
    const r = await fetch("/api/upload", { method: "POST", body: formData });
    return r.json();
  },
  async getDataset(filename) {
    const r = await fetch(`/api/dataset/${encodeURIComponent(filename)}`);
    return r.json();
  },
  async transform(payload) {
    const r = await fetch("/api/transform", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return r.json();
  },
  async reset(filename) {
    const r = await fetch(`/api/reset/${encodeURIComponent(filename)}`, { method: "POST" });
    return r.json();
  },
  async deleteDataset(filename) {
    const r = await fetch(`/api/delete/${encodeURIComponent(filename)}`, { method: "DELETE" });
    return r.json();
  },
  async loadToDb(filename) {
    const r = await fetch(`/api/load-to-db/${encodeURIComponent(filename)}`, { method: "POST" });
    return r.json();
  },
  async runQuery(query) {
    const r = await fetch("/api/run-query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    return r.json();
  },
  async getTables() {
    const r = await fetch("/api/tables");
    return r.json();
  }
};

function buildTable(columns, rows) {
  if (!rows || rows.length === 0) return "<p style='padding:14px;color:var(--text-muted);font-size:13px'>No rows to display</p>";
  let html = "<table class='data-table'><thead><tr>";
  columns.forEach(c => { html += `<th>${escHtml(String(c))}</th>`; });
  html += "</tr></thead><tbody>";
  rows.forEach(row => {
    html += "<tr>";
    columns.forEach(c => {
      const val = row[c] !== undefined && row[c] !== null ? String(row[c]) : "";
      html += `<td title="${escHtml(val)}">${escHtml(val)}</td>`;
    });
    html += "</tr>";
  });
  html += "</tbody></table>";
  return html;
}

function buildPreviewTable(columns, rows) {
  if (!rows || rows.length === 0) return "<p style='padding:14px;color:var(--text-muted);font-size:13px'>No rows to display</p>";
  let html = "<table class='data-table'><thead><tr>";
  columns.forEach(c => { html += `<th>${escHtml(c)}</th>`; });
  html += "</tr></thead><tbody>";
  rows.forEach(row => {
    html += "<tr>";
    columns.forEach(c => {
      const val = row[c] !== undefined && row[c] !== null ? String(row[c]) : "";
      html += `<td title="${escHtml(val)}">${escHtml(val)}</td>`;
    });
    html += "</tr>";
  });
  html += "</tbody></table>";
  return html;
}

function escHtml(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function renderStats(data) {
  const quality = data.quality_score;
  document.getElementById("statsRow").innerHTML = `
    <div class="stat-card">
      <div class="stat-label">Rows</div>
      <div class="stat-value">${data.rows.toLocaleString()}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Columns</div>
      <div class="stat-value">${data.columns.length}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Steps Applied</div>
      <div class="stat-value">${(data.history || []).length}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Quality Score</div>
      <div class="stat-value">${quality}</div>
      <div class="quality-bar-wrap">
        <div class="quality-bar-bg"><div class="quality-bar-fill" style="width:${quality}%"></div></div>
      </div>
    </div>
  `;
}

function renderProfile(profile) {
  const grid = document.getElementById("profileGrid");
  grid.innerHTML = profile.map(p => `
    <div class="profile-card">
      <div class="profile-col-name" title="${escHtml(p.column)}">${escHtml(p.column)}</div>
      <div class="profile-col-type">${p.dtype}</div>
      <div class="profile-stats">
        <div class="profile-stat">Nulls: <span>${p.null_count} (${p.null_pct}%)</span></div>
        <div class="profile-stat">Unique: <span>${p.unique_count}</span></div>
      </div>
    </div>
  `).join("");
}

function renderHistory(history) {
  const list = document.getElementById("historyList");
  if (!history || history.length === 0) {
    list.innerHTML = "<div class='empty-state-small'>No steps yet</div>";
    return;
  }
  list.innerHTML = history.map(s => `
    <div class="history-step">
      <div class="history-step-num">Step ${s.step}</div>
      <div class="history-step-label">${escHtml(s.label)}</div>
      <div class="history-step-stat">${s.rows_before.toLocaleString()} → ${s.rows_after.toLocaleString()} rows (${s.rows_affected >= 0 ? "-" : "+"}${Math.abs(s.rows_affected)} affected)</div>
    </div>
  `).join("");
}

function loadDatasetIntoUI(data) {
  activeDataset = data.filename;
  datasets[data.filename] = data;

  document.getElementById("activeLabel").textContent = data.filename;
  document.getElementById("emptyWorkspace").classList.add("hidden");
  document.getElementById("previewContent").classList.remove("hidden");

  renderStats(data);
  renderProfile(data.profile);

  const cols = data.columns;
  const preview = data.preview;
  document.getElementById("previewTable").innerHTML = buildPreviewTable(cols, preview);

  const colSelect = document.getElementById("transformColumn");
  colSelect.innerHTML = cols.map(c => `<option value="${escHtml(c)}">${escHtml(c)}</option>`).join("");

  renderHistory(data.history);

  document.getElementById("transformPreviewWrap").style.display = "none";
  document.getElementById("transformFeedback").classList.add("hidden");
  document.getElementById("loadFeedback").classList.add("hidden");
  document.getElementById("loadResult").classList.add("hidden");

  document.querySelectorAll(".dataset-item").forEach(el => {
    el.classList.toggle("active", el.dataset.filename === data.filename);
  });
}

function renderSidebar() {
  const list = document.getElementById("datasetList");
  const keys = Object.keys(datasets);
  if (keys.length === 0) {
    list.innerHTML = "<div class='empty-state-small'>No datasets yet</div>";
    return;
  }
  list.innerHTML = keys.map(name => {
    const d = datasets[name];
    return `
      <div class="dataset-item ${name === activeDataset ? "active" : ""}" data-filename="${escHtml(name)}" onclick="selectDataset('${escHtml(name)}')">
        <div style="flex:1;min-width:0">
          <div class="dataset-name" title="${escHtml(name)}">${escHtml(name)}</div>
          <div class="dataset-meta">${d.rows ? d.rows.toLocaleString() : "?"} rows</div>
        </div>
        <button class="dataset-delete" onclick="event.stopPropagation();deleteDataset('${escHtml(name)}')" title="Remove">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    `;
  }).join("");
}

async function selectDataset(filename) {
  if (filename === activeDataset) return;
  const data = await api.getDataset(filename);
  if (data.error) return;
  datasets[filename] = data;
  loadDatasetIntoUI(data);
  renderSidebar();
}

async function deleteDataset(filename) {
  await api.deleteDataset(filename);
  delete datasets[filename];
  if (activeDataset === filename) {
    activeDataset = null;
    const remaining = Object.keys(datasets);
    if (remaining.length > 0) {
      const data = await api.getDataset(remaining[0]);
      loadDatasetIntoUI(data);
    } else {
      document.getElementById("activeLabel").textContent = "No dataset selected";
      document.getElementById("previewContent").classList.add("hidden");
      document.getElementById("emptyWorkspace").classList.remove("hidden");
    }
  }
  renderSidebar();
}

async function handleUpload(files) {
  if (!files || files.length === 0) return;
  const status = document.getElementById("uploadStatus");
  status.textContent = "Uploading…";
  status.classList.remove("hidden");

  const formData = new FormData();
  Array.from(files).forEach(f => formData.append("file", f));

  const result = await api.upload(formData);
  let added = 0;

  result.results.forEach(r => {
    if (r.error) {
      status.textContent = `Error: ${r.error}`;
    } else {
      datasets[r.filename] = r;
      added++;
    }
  });

  if (added > 0) {
    status.textContent = `${added} file${added > 1 ? "s" : ""} uploaded`;
    const firstName = result.results.find(r => !r.error)?.filename;
    if (firstName) {
      loadDatasetIntoUI(datasets[firstName]);
    }
    renderSidebar();
  }

  setTimeout(() => { status.textContent = ""; status.classList.add("hidden"); }, 3000);
}

function setupUploadZone() {
  const zone = document.getElementById("uploadZone");
  const input = document.getElementById("fileInput");

  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", () => handleUpload(input.files));

  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("dragover");
    handleUpload(e.dataTransfer.files);
  });
}

function setupTabs() {
  document.querySelectorAll(".step-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".step-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.add("hidden"));
      tab.classList.add("active");
      document.getElementById(`tab-${tab.dataset.tab}`).classList.remove("hidden");
      if (tab.dataset.tab === "sql") initMonaco();
    });
  });
}

function showFeedback(el, msg, type) {
  el.textContent = msg;
  el.className = `feedback ${type}`;
}

function setupTransform() {
  document.getElementById("applyBtn").addEventListener("click", async () => {
    if (!activeDataset) return;
    const column = document.getElementById("transformColumn").value;
    const action = document.getElementById("transformAction").value;
    const fb = document.getElementById("transformFeedback");
    fb.className = "feedback hidden";

    const data = await api.transform({ filename: activeDataset, column, action });
    if (data.error) {
      showFeedback(fb, data.error, "error");
      return;
    }

    datasets[activeDataset] = data;
    renderStats(data);
    renderProfile(data.profile);
    renderHistory(data.history);

    document.getElementById("transformPreviewWrap").style.display = "block";
    document.getElementById("transformPreview").innerHTML = buildPreviewTable(data.columns, data.preview);

    const colSelect = document.getElementById("transformColumn");
    const currentVal = colSelect.value;
    colSelect.innerHTML = data.columns.map(c => `<option value="${escHtml(c)}">${escHtml(c)}</option>`).join("");
    if (data.columns.includes(currentVal)) colSelect.value = currentVal;

    showFeedback(fb, `✓ ${data.step.label} — ${Math.abs(data.rows_affected)} row${Math.abs(data.rows_affected) !== 1 ? "s" : ""} affected`, "success");
    renderSidebar();
  });

  document.getElementById("skipBtn").addEventListener("click", () => {
    document.querySelectorAll(".step-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.add("hidden"));
    document.querySelector('[data-tab="sql"]').classList.add("active");
    document.getElementById("tab-sql").classList.remove("hidden");
    initMonaco();
  });

  document.getElementById("resetBtn").addEventListener("click", async () => {
    if (!activeDataset) return;
    const data = await api.reset(activeDataset);
    if (data.error) return;
    datasets[activeDataset] = data;
    loadDatasetIntoUI(data);
    renderSidebar();
    showFeedback(document.getElementById("transformFeedback"), "✓ Dataset reset to original", "success");
  });
}

function initMonaco() {
  if (monacoEditor) return;
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  require.config({ paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.55.1/min/vs" } });
  require(["vs/editor/editor.main"], function () {
    monacoEditor = monaco.editor.create(document.getElementById("monacoEditor"), {
      value: "SELECT * FROM your_table LIMIT 50;",
      language: "sql",
      theme: isDark ? "vs-dark" : "vs",
      automaticLayout: true,
      fontSize: 13,
      fontFamily: "JetBrains Mono, monospace",
      minimap: { enabled: false },
      lineNumbers: "on",
      scrollBeyondLastLine: false,
      padding: { top: 12 }
    });
  });
}

function updateMonacoTheme(dark) {
  if (monacoEditor) {
    monaco.editor.setTheme(dark ? "vs-dark" : "vs");
  }
}

async function setupSQL() {
  await loadTables();

  document.getElementById("refreshTablesBtn").addEventListener("click", loadTables);

  document.getElementById("sqlTableSelect").addEventListener("change", function () {
    if (!this.value || !monacoEditor) return;
    monacoEditor.setValue(`SELECT * FROM "${this.value}" LIMIT 50;`);
  });

  document.getElementById("runQueryBtn").addEventListener("click", async () => {
    if (!monacoEditor) return;
    const query = monacoEditor.getValue().trim();
    if (!query) return;
    const fb = document.getElementById("sqlFeedback");
    fb.className = "feedback hidden";

    const data = await api.runQuery(query);
    const resultWrap = document.getElementById("sqlResultWrap");
    const resultTable = document.getElementById("sqlResultTable");
    const resultFooter = document.getElementById("sqlResultFooter");
    const resultTitle = document.getElementById("sqlResultTitle");

    if (data.error) {
      showFeedback(fb, data.error, "error");
      resultWrap.style.display = "none";
      return;
    }

    resultTitle.style.display = "block";
    resultWrap.style.display = "block";
    resultTable.innerHTML = buildTable(data.columns, data.rows);
    resultFooter.textContent = `${data.row_count} row${data.row_count !== 1 ? "s" : ""} returned`;

    if (data.message) {
      showFeedback(fb, `✓ ${data.message}`, "success");
    }
  });

  document.getElementById("clearQueryBtn").addEventListener("click", () => {
    if (monacoEditor) monacoEditor.setValue("");
  });
}

async function loadTables() {
  const data = await api.getTables();
  const select = document.getElementById("sqlTableSelect");
  if (!data.tables || data.tables.length === 0) {
    select.innerHTML = "<option value=''>No tables loaded yet</option>";
    return;
  }
  select.innerHTML = "<option value=''>Select a table</option>" +
    data.tables.map(t => `<option value="${escHtml(t)}">${escHtml(t)}</option>`).join("");
}

function setupLoad() {
  document.getElementById("loadDbBtn").addEventListener("click", async () => {
    if (!activeDataset) {
      showFeedback(document.getElementById("loadFeedback"), "Select a dataset first", "error");
      return;
    }
    const btn = document.getElementById("loadDbBtn");
    btn.disabled = true;
    btn.textContent = "Uploading…";
    const fb = document.getElementById("loadFeedback");
    fb.className = "feedback hidden";

    const data = await api.loadToDb(activeDataset);
    btn.disabled = false;
    btn.textContent = "Upload to Database";

    if (data.error) {
      showFeedback(fb, data.error, "error");
      return;
    }

    showFeedback(fb, `✓ Successfully loaded into database`, "success");

    const result = data.result;
    const loadResult = document.getElementById("loadResult");
    loadResult.classList.remove("hidden");
    loadResult.innerHTML = `
      <div class="load-result-title">Upload Summary</div>
      <div class="load-result-grid">
        <div class="load-stat"><div class="load-stat-label">Table Name</div><div class="load-stat-val" style="font-size:14px">${escHtml(result.table_name)}</div></div>
        <div class="load-stat"><div class="load-stat-label">Rows Inserted</div><div class="load-stat-val">${result.rows.toLocaleString()}</div></div>
        <div class="load-stat"><div class="load-stat-label">Columns</div><div class="load-stat-val">${result.columns}</div></div>
      </div>
      <div class="section-title" style="margin-bottom:8px">Schema</div>
      <div class="schema-list">${result.schema.map(s => `<div class="schema-pill">${escHtml(s.column)}: ${s.type}</div>`).join("")}</div>
    `;
    loadTables();
  });

  document.getElementById("downloadCsvBtn").addEventListener("click", () => {
    if (!activeDataset) return;
    window.location.href = `/api/download/${encodeURIComponent(activeDataset)}?format=csv`;
  });

  document.getElementById("downloadJsonBtn").addEventListener("click", () => {
    if (!activeDataset) return;
    window.location.href = `/api/download/${encodeURIComponent(activeDataset)}?format=json`;
  });
}

function setupTheme() {
  const toggle = document.getElementById("themeToggle");
  const sun = document.getElementById("sunIcon");
  const moon = document.getElementById("moonIcon");
  const saved = localStorage.getItem("etl-theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  if (saved === "dark") { sun.style.display = "none"; moon.style.display = "block"; }

  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("etl-theme", next);
    sun.style.display = next === "dark" ? "none" : "block";
    moon.style.display = next === "dark" ? "block" : "none";
    updateMonacoTheme(next === "dark");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupTheme();
  setupUploadZone();
  setupTabs();
  setupTransform();
  setupSQL();
  setupLoad();
});
