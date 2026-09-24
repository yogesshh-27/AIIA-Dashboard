import pathlib

frontend_code = r'''
// ============================================================
// 9. MODULE: INTEROPERABILITY (CDISC & FHIR R4)
// ============================================================
var currentInteropSub = 'cdisc';
var currentFHIRData = null;

function renderInteropView(container, sub) {
  currentInteropSub = sub || 'cdisc';
  
  var activeCdisc = currentInteropSub === 'cdisc' ? 'active' : '';
  var activeFhir = currentInteropSub === 'fhir' ? 'active' : '';
  var activeExport = currentInteropSub === 'export' ? 'active' : '';

  container.innerHTML = `
    <div style="margin-bottom: 16px;">
      <h1 class="h1-title">Clinical Data Interoperability & Standards</h1>
      <p class="text-muted" style="font-size: 12px;">Standardized semantic mapping of CTRI clinical trials to CDISC (SDTM/ADaM/Define-XML) and HL7 FHIR Release 4 resources.</p>
    </div>

    <div class="pv-disclaimer-bar">
      <span class="pv-disclaimer-icon">&#9888;</span>
      Prototype mapping/export — Synthesizes CDISC and FHIR structures for evaluation. Not validated for direct regulatory submission without sponsor qualification.
    </div>

    <!-- Sub-navigation tabs -->
    <div class="interop-tab-bar">
      <button class="interop-tab-btn ${activeCdisc}" onclick="navigateTo('interop/cdisc')">&#128214; CDISC Standards & Mappings</button>
      <button class="interop-tab-btn ${activeFhir}" onclick="navigateTo('interop/fhir')">&#129516; HL7 FHIR R4 ResearchStudy</button>
      <button class="interop-tab-btn ${activeExport}" onclick="navigateTo('interop/export')">&#128190; Data Export Center</button>
    </div>

    <div id="interop-subview-container"></div>
  `;

  var subContainer = document.getElementById('interop-subview-container');
  if (currentInteropSub === 'fhir') {
    renderFHIRSubView(subContainer);
  } else if (currentInteropSub === 'export') {
    renderExportSubView(subContainer);
  } else {
    renderCDISCSubView(subContainer);
  }
}

// ---- CDISC SUBVIEW ----
function renderCDISCSubView(container) {
  container.innerHTML = `
    <!-- 1. Standards Overview Cards -->
    <div class="grid-2" style="margin-bottom: 16px;">
      <div class="flat-card">
        <div class="flat-card-header"><span class="flat-card-title">CDISC Standards Architecture</span></div>
        <div style="font-size: 12px; line-height: 1.6; color: var(--text-secondary);">
          <div><strong>SDTM v1.8 / IG v3.3:</strong> Standardized tabulation structures (Domains: <code>TS</code>, <code>TA</code>, <code>DM</code>, <code>AE</code>, <code>EX</code>).</div>
          <div style="margin-top: 6px;"><strong>ADaM v2.1:</strong> Analysis dataset models (<code>ADSL</code> Subject-level, <code>ADAE</code> Adverse events) for statistical verification.</div>
          <div style="margin-top: 6px;"><strong>Define-XML v2.0:</strong> Machine-readable metadata describing dataset structure, item definitions, and codelist C-Codes.</div>
        </div>
      </div>
      <div class="flat-card">
        <div class="flat-card-header"><span class="flat-card-title">Demonstration Export Packages</span></div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <button class="btn btn-sm btn-outline" onclick="downloadCDISCPackage('sdtm')">&#128196; Generate SDTM Demonstration Tabulation (JSON)</button>
          <button class="btn btn-sm btn-outline" onclick="downloadCDISCPackage('adam')">&#128202; Generate ADaM Analysis Datasets (JSON)</button>
          <button class="btn btn-sm btn-outline" onclick="downloadCDISCPackage('define_xml')">&#128214; Download Define-XML 2.0 Metadata Specification (.xml)</button>
        </div>
      </div>
    </div>

    <!-- 2. Canonical Mapping Table -->
    <div class="flat-card" style="margin-bottom: 16px;">
      <div class="flat-card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <span class="flat-card-title">Source Field &#8594; Canonical Field &#8594; CDISC Concept &#8594; Output Field</span>
        <span class="badge" style="font-size: 10px;">12 Active Canonical Mappings</span>
      </div>
      <div class="table-wrapper">
        <table class="flat-table" id="cdisc-mappings-table">
          <thead>
            <tr>
              <th style="width: 140px;">Source Field (CTRI)</th>
              <th style="width: 140px;">Canonical Field</th>
              <th style="width: 150px;">CDISC Domain</th>
              <th style="width: 160px;">CDISC Concept / C-Code</th>
              <th style="width: 160px;">Output Field</th>
              <th>Transformation Rule</th>
            </tr>
          </thead>
          <tbody id="cdisc-mappings-tbody">
            <tr><td colspan="6" class="text-muted" style="text-align: center; padding: 20px;">Loading mappings...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 3. Searchable CDISC Vocabulary Repository -->
    <div class="flat-card">
      <div class="flat-card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <span class="flat-card-title">CDISC Controlled Terminology Search</span>
        <input type="text" id="cdisc-vocab-search" class="form-input form-input-sm" placeholder="Search concept, C-Code, term..." style="max-width: 250px;" onkeyup="debounceInteropCDISC()">
      </div>
      <div class="table-wrapper">
        <table class="flat-table">
          <thead>
            <tr>
              <th style="width: 90px;">NCI C-Code</th>
              <th style="width: 120px;">Standard</th>
              <th style="width: 180px;">Standardized Concept</th>
              <th>Definition</th>
            </tr>
          </thead>
          <tbody id="cdisc-interop-tbody">
            <tr><td colspan="4" class="text-muted" style="text-align: center; padding: 20px;">Loading CDISC concepts...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
  loadCDISCMappings();
  loadInteropCDISC('');
}

async function loadCDISCMappings() {
  try {
    var res = await fetch('/api/interop/cdisc/mapping');
    var mappings = await res.json();
    var tbody = document.getElementById('cdisc-mappings-tbody');
    if (!tbody) return;
    tbody.innerHTML = mappings.map(function(m) {
      return `<tr>
        <td class="text-mono" style="font-size: 11px;">${escapeHTML(m.source_field)}</td>
        <td><strong>${escapeHTML(m.canonical_field)}</strong></td>
        <td><span class="badge">${escapeHTML(m.domain)}</span></td>
        <td class="text-mono" style="color: var(--accent); font-weight: 600;">${escapeHTML(m.cdisc_concept)}</td>
        <td class="text-mono" style="color: #0369a1; font-weight: 600;">${escapeHTML(m.output_field)}</td>
        <td style="font-size: 11px; color: var(--text-secondary);">${escapeHTML(m.rule)}</td>
      </tr>`;
    }).join('');
  } catch (e) { console.error('CDISC Mappings load error:', e); }
}

function loadInteropCDISC(search) {
  var s = search || (document.getElementById('cdisc-vocab-search') || {}).value || '';
  fetch('/api/cdisc?search=' + encodeURIComponent(s) + '&limit=25')
    .then(r => r.json())
    .then(data => {
      var tbody = document.getElementById('cdisc-interop-tbody');
      if (!tbody) return;
      if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-muted" style="text-align: center; padding: 20px;">No matching CDISC concepts found.</td></tr>';
        return;
      }
      tbody.innerHTML = data.map(item => `
        <tr>
          <td class="text-mono" style="font-weight: 600; color: var(--accent);">${escapeHTML(item.code || '—')}</td>
          <td style="color: var(--text-muted); font-size: 11px;">${escapeHTML(item.standard)}</td>
          <td><strong>${escapeHTML(item.term)}</strong></td>
          <td style="line-height: 1.4; color: var(--text-secondary); font-size: 11px;">${escapeHTML(item.definition || '—')}</td>
        </tr>
      `).join('');
    }).catch(e => console.error('CDISC Vocab search error:', e));
}

function debounceInteropCDISC() {
  clearTimeout(cdiscDebounceTimer);
  cdiscDebounceTimer = setTimeout(function() {
    loadInteropCDISC();
  }, 250);
}

function downloadCDISCPackage(format) {
  if (format === 'define_xml') {
    window.location.href = '/api/interop/cdisc/export?format=define_xml';
    return;
  }
  fetch('/api/interop/cdisc/export?format=' + format)
    .then(r => r.json())
    .then(data => {
      var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'cdisc_' + format + '_demonstration.json';
      a.click();
      URL.revokeObjectURL(url);
    }).catch(e => alert('Export error: ' + e));
}

// ---- FHIR R4 SUBVIEW ----
function renderFHIRSubView(container) {
  container.innerHTML = `
    <div class="flat-card" style="margin-bottom: 16px;">
      <div class="flat-card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <span class="flat-card-title">HL7 FHIR R4 ResearchStudy Generator & Validator</span>
        <div style="display: flex; gap: 8px; align-items: center;">
          <select id="fhir-trial-select" class="form-select form-input-sm" style="max-width: 280px;" onchange="loadFHIRStudy(this.value)">
            <option value="20549">CTRI/2017/10/010023 - Herbal + Modern Drugs</option>
            <option value="20554">CTRI/2017/10/010047 - Zinc Rasausadhis Safety</option>
            <option value="20560">CTRI/2018/02/011783 - Classical Guggulu Study</option>
          </select>
          <button class="btn btn-sm btn-primary" onclick="validateFHIRStudyUI()">&#10003; Validate Structure</button>
          <button class="btn btn-sm btn-secondary" onclick="downloadFHIRStudyUI()">&#128190; Download JSON</button>
        </div>
      </div>
      <div id="fhir-validation-banner" style="display:none; margin: 12px 0;"></div>
      <div style="margin-top: 10px;">
        <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom: 6px;">
          <span style="font-size: 11px; font-weight:600; color: var(--text-secondary); text-transform: uppercase;">Generated Resource (ResearchStudy):</span>
          <button class="btn-sm btn-secondary" onclick="copyFHIRJSON()">Copy JSON</button>
        </div>
        <pre class="fhir-json-box" id="fhir-json-display">Loading FHIR resource...</pre>
      </div>
    </div>
  `;
  loadFHIRStudy('20549');
}

async function loadFHIRStudy(trialId) {
  var disp = document.getElementById('fhir-json-display');
  if (disp) disp.textContent = 'Generating FHIR R4 ResearchStudy resource...';
  try {
    var res = await fetch('/api/interop/fhir/study?trial_id=' + encodeURIComponent(trialId));
    var data = await res.json();
    currentFHIRData = data;
    if (disp) disp.textContent = JSON.stringify(data, null, 2);
    // Hide previous validation banner when changing trial
    var vBanner = document.getElementById('fhir-validation-banner');
    if (vBanner) vBanner.style.display = 'none';
  } catch (e) {
    if (disp) disp.textContent = 'Error loading FHIR resource: ' + e;
  }
}

async function validateFHIRStudyUI() {
  if (!currentFHIRData) return;
  var vBanner = document.getElementById('fhir-validation-banner');
  if (!vBanner) return;
  try {
    var res = await fetch('/api/interop/fhir/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentFHIRData)
    });
    var data = await res.json();
    vBanner.style.display = 'block';
    if (data.is_valid) {
      vBanner.innerHTML = `<div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 4px; padding: 10px 14px; font-size: 12px; color: #166534; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 16px; color: #16a34a;">&#10003;</span>
        <div>
          <strong>FHIR R4 Structure Validated:</strong> ${escapeHTML(data.compliance_summary)}
          <div style="font-size: 11px; color: #15803d; margin-top: 2px;">Standard: ${escapeHTML(data.standard)} | Resource: ${escapeHTML(data.resourceType)} | Errors: 0</div>
        </div>
      </div>`;
    } else {
      vBanner.innerHTML = `<div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 4px; padding: 10px 14px; font-size: 12px; color: #991b1b;">
        <strong>Validation Discrepancies:</strong> ${(data.errors || []).join(', ')}
      </div>`;
    }
  } catch (e) { alert('Validation error: ' + e); }
}

function downloadFHIRStudyUI() {
  if (!currentFHIRData) return;
  var blob = new Blob([JSON.stringify(currentFHIRData, null, 2)], { type: 'application/json' });
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = (currentFHIRData.id || 'research-study') + '.json';
  a.click();
  URL.revokeObjectURL(url);
}

function copyFHIRJSON() {
  var disp = document.getElementById('fhir-json-display');
  if (disp && disp.textContent) {
    navigator.clipboard.writeText(disp.textContent).then(function() {
      alert('FHIR JSON copied to clipboard.');
    });
  }
}

// ---- EXPORT SUBVIEW ----
function renderExportSubView(container) {
  container.innerHTML = `
    <div style="margin-bottom: 16px;">
      <h1 class="h1-title">Institutional Data Export Center</h1>
      <p class="text-muted" style="font-size: 12px;">Export verified clinical trial metadata across canonical CSV, structured JSON, and CDISC demonstration packages.</p>
    </div>

    <div class="grid-2">
      <div class="flat-card">
        <div class="flat-card-header"><span class="flat-card-title">AIIA Verified Portfolio (263 Trials)</span></div>
        <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 14px;">
          Includes all 263 All India Institute of Ayurveda clinical trial registrations with complete investigators, affiliations, phases, and recruitment statuses.
        </p>
        <div style="display: flex; gap: 8px;">
          <a class="btn btn-primary btn-sm" href="/api/export?scope=aiia&format=csv">&#128196; Download CSV</a>
          <a class="btn btn-secondary btn-sm" href="/api/export?scope=aiia&format=json">&#128190; Download JSON</a>
        </div>
      </div>
      <div class="flat-card">
        <div class="flat-card-header"><span class="flat-card-title">CTRI Comparative Benchmark (1,263 Trials)</span></div>
        <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 14px;">
          Full comparative dataset including wider AYUSH and allopathic comparative registry protocols for benchmarking.
        </p>
        <div style="display: flex; gap: 8px;">
          <a class="btn btn-outline btn-sm" href="/api/export?scope=all&format=csv">&#128196; Download Full CSV</a>
          <a class="btn btn-outline btn-sm" href="/api/export?scope=all&format=json">&#128190; Download Full JSON</a>
        </div>
      </div>
    </div>
  `;
}


// ============================================================
// 10. MODULE: AUDIT TRAIL & HASH-LINKED VERIFICATION
// ============================================================
var auditPage = 1;

function renderAuditView(container) {
  container.innerHTML = `
    <div style="margin-bottom: 16px;">
      <h1 class="h1-title">System Audit Trail & Cryptographic Chain Verification</h1>
      <p class="text-muted" style="font-size: 12px;">Chronological, tamper-evident audit log with SHA-256 block linking and automated verification.</p>
    </div>

    <div class="pv-disclaimer-bar">
      <span class="pv-disclaimer-icon">&#9888;</span>
      Append-only / hash-linked audit prototype — Demonstrates cryptographic block linking (SHA-256) and tamper detection. Not intended as a legal guarantee of immutability.
    </div>

    <!-- Verification Control Bar -->
    <div class="audit-verify-bar">
      <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <button class="btn btn-primary btn-sm" onclick="verifyAuditChainUI()">&#128274; Verify Audit Chain</button>
        <div id="chain-verify-indicator">
          <span class="chain-status-badge chain-status-verified">&#10003; Audit Chain Verified (Genesis &#8594; Latest)</span>
        </div>
      </div>
      <div style="display: flex; gap: 8px; align-items: center;">
        <button class="btn btn-outline btn-sm" style="color: #b91c1c; border-color: #fca5a5;" onclick="tamperAuditChainDemoUI()" title="Simulate unauthorized payload mutation">&#9888; Simulate Tamper</button>
        <button class="btn btn-outline btn-sm" onclick="restoreAuditChainDemoUI()" title="Restore valid cryptographic chain">&#8635; Restore Chain</button>
      </div>
    </div>

    <!-- Filters & Audit Table -->
    <div class="flat-card">
      <div class="flat-card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <span class="flat-card-title">Cryptographic Event Chain</span>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input type="text" id="audit-search-input" class="form-input form-input-sm" placeholder="Search event, user, action..." style="max-width: 220px;" onkeyup="onAuditSearch()">
          <select id="audit-role-filter" class="form-select form-input-sm" style="max-width: 170px;" onchange="onAuditFilter()">
            <option value="">All Roles</option>
            <option value="Administrator">Administrator</option>
            <option value="Principal Investigator">Principal Investigator</option>
            <option value="Study Coordinator">Study Coordinator</option>
            <option value="Monitor">Monitor</option>
            <option value="Ethics Committee">Ethics Committee</option>
            <option value="Pharmacovigilance Officer">Pharmacovigilance Officer</option>
            <option value="Institutional Leadership">Institutional Leadership</option>
            <option value="Regulator / Read-only">Regulator / Read-only</option>
          </select>
        </div>
      </div>
      <div class="table-wrapper">
        <table class="flat-table" id="audit-chain-table">
          <thead>
            <tr>
              <th style="width: 80px;">Event ID</th>
              <th style="width: 135px;">Timestamp</th>
              <th style="width: 160px;">User &amp; Role</th>
              <th style="width: 120px;">Action</th>
              <th style="width: 140px;">Entity</th>
              <th>Values (Prev &#8594; New)</th>
              <th style="width: 190px;">Hash Linkage (Prev &#8594; Current)</th>
            </tr>
          </thead>
          <tbody id="audit-chain-tbody">
            <tr><td colspan="7" class="text-muted" style="text-align: center; padding: 20px;">Loading audit trail...</td></tr>
          </tbody>
        </table>
      </div>
      <div class="table-pagination" id="audit-pagination"></div>
    </div>
  `;
  auditPage = 1;
  loadAuditChain();
  verifyAuditChainUI(false);
}

async function loadAuditChain() {
  var search = (document.getElementById('audit-search-input') || {}).value || '';
  var roleFilter = (document.getElementById('audit-role-filter') || {}).value || '';
  try {
    var params = new URLSearchParams({ page: auditPage, limit: 15, search: search, role: roleFilter });
    var res = await fetch('/api/audit/chain?' + params);
    var data = await res.json();
    var tbody = document.getElementById('audit-chain-tbody');
    if (!tbody) return;
    if (!data.data || data.data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-muted" style="text-align:center; padding: 20px;">No audit trail events found.</td></tr>';
      return;
    }
    tbody.innerHTML = data.data.map(function(ev) {
      var prevShort = (ev.prev_hash || '').substring(0, 8) + '...';
      var currShort = (ev.current_hash || '').substring(0, 8) + '...';
      return `<tr>
        <td class="text-mono" style="font-weight: 600; color: var(--accent);">${escapeHTML(ev.event_id)}</td>
        <td class="text-mono" style="font-size: 11px; color: var(--text-secondary);">${escapeHTML(ev.timestamp)}</td>
        <td>
          <div style="font-weight: 600; font-size: 12px;">${escapeHTML(ev.user_name)}</div>
          <span class="role-badge-pill">${escapeHTML(ev.role)}</span>
        </td>
        <td><span class="badge" style="font-size: 10px; font-weight: 600;">${escapeHTML(ev.action)}</span></td>
        <td>
          <div style="font-weight: 500;">${escapeHTML(ev.entity)}</div>
          <span class="text-mono" style="font-size: 10px; color: var(--text-muted);">${escapeHTML(ev.entity_id || '')}</span>
        </td>
        <td style="font-size: 11px; line-height: 1.4;">
          ${ev.previous_value ? `<span class="text-muted">${escapeHTML(ev.previous_value)}</span> &#8594; ` : ''}
          <strong>${escapeHTML(ev.new_value || '—')}</strong>
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 4px;">
            <span class="audit-hash-chip" title="Previous Hash: ${escapeHTML(ev.prev_hash)}">${prevShort}</span>
            <span style="font-size: 10px; color: var(--text-muted);">&#8594;</span>
            <span class="audit-hash-chip" style="color: #047857; font-weight: 600;" title="Current Hash: ${escapeHTML(ev.current_hash)}">${currShort}</span>
          </div>
        </td>
      </tr>`;
    }).join('');

    var pagEl = document.getElementById('audit-pagination');
    if (pagEl) {
      var tp = data.total_pages || 1;
      pagEl.innerHTML = `
        <span class="text-muted" style="font-size: 11px;">Showing ${data.data.length} of ${data.total} audit events</span>
        <div style="display: flex; gap: 4px;">
          <button class="btn-sm btn-secondary" ${auditPage <= 1 ? 'disabled' : ''} onclick="changeAuditPage(${auditPage - 1})">&#8592; Prev</button>
          <span class="text-muted" style="font-size: 11px; padding: 4px 8px;">Page ${auditPage} of ${tp}</span>
          <button class="btn-sm btn-secondary" ${auditPage >= tp ? 'disabled' : ''} onclick="changeAuditPage(${auditPage + 1})">Next &#8594;</button>
        </div>
      `;
    }
  } catch (e) { console.error('Audit trail load error:', e); }
}

function changeAuditPage(p) { auditPage = p; loadAuditChain(); }
function onAuditSearch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(function() { auditPage = 1; loadAuditChain(); }, 300); }
function onAuditFilter() { auditPage = 1; loadAuditChain(); }

async function verifyAuditChainUI(showAlert) {
  var ind = document.getElementById('chain-verify-indicator');
  try {
    var res = await fetch('/api/audit/verify');
    var data = await res.json();
    if (!ind) return;
    if (data.verified) {
      ind.innerHTML = `<span class="chain-status-badge chain-status-verified">&#10003; ${escapeHTML(data.status)} (${data.total_events} blocks intact)</span>`;
      if (showAlert) alert('Audit Chain Verified: Cryptographic integrity confirmed across all ' + data.total_events + ' blocks.');
    } else {
      ind.innerHTML = `<span class="chain-status-badge chain-status-tampered">&#9888; ${escapeHTML(data.status)}: Block ${escapeHTML(data.failed_event_id || '')} tampered!</span>`;
      if (showAlert) alert('VERIFICATION FAILED: ' + data.reason + ' (Event: ' + data.failed_event_id + ')');
    }
  } catch (e) { console.error('Verification error:', e); }
}

async function tamperAuditChainDemoUI() {
  if (!confirm('This demonstration simulates an unauthorized database modification on block EVT-0003. Run simulation?')) return;
  try {
    var res = await fetch('/api/audit/tamper-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: 'EVT-0003', malicious_value: 'TAMPERED: Altered patient enrollment to 999' })
    });
    var data = await res.json();
    loadAuditChain();
    verifyAuditChainUI(true);
  } catch (e) { alert('Tamper demo error: ' + e); }
}

async function restoreAuditChainDemoUI() {
  try {
    var res = await fetch('/api/audit/restore-demo', { method: 'POST' });
    var data = await res.json();
    loadAuditChain();
    verifyAuditChainUI(true);
  } catch (e) { alert('Restore error: ' + e); }
}


// ============================================================
// 11. MODULE: ADMINISTRATION & ROLE-BASED ACCESS CONTROL
// ============================================================
function renderAdminView(container) {
  container.innerHTML = `
    <div style="margin-bottom: 16px;">
      <h1 class="h1-title">System Administration &amp; Role-Based Access Control (RBAC)</h1>
      <p class="text-muted" style="font-size: 12px;">Institutional authorization, role matrix management, and server-side permission enforcement.</p>
    </div>

    <!-- Active Persona Switcher Card -->
    <div class="flat-card" style="margin-bottom: 16px; border-left: 4px solid var(--accent);">
      <div class="flat-card-header"><span class="flat-card-title">Active Demonstration Persona Switcher</span></div>
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
        <div>
          <div style="font-size: 13px; font-weight: 600;" id="admin-active-user-name">Loading...</div>
          <div style="font-size: 11px; color: var(--text-muted);" id="admin-active-user-desc">Select an institutional persona below to test server-side authorization enforcement.</div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span style="font-size: 12px; font-weight: 600;">Switch Persona:</span>
          <select id="admin-role-select" class="form-select form-input-sm" style="min-width: 220px;" onchange="onRoleSwitch(this.value); refreshAdminView();">
            <option value="Administrator">1. Administrator (Prof. Tanuja Nesari)</option>
            <option value="Principal Investigator">2. Principal Investigator (Dr. Galib)</option>
            <option value="Study Coordinator">3. Study Coordinator (Dr. P. Gupta)</option>
            <option value="Monitor">4. Monitor (S. Sharma, CRA)</option>
            <option value="Ethics Committee">5. Ethics Committee (Dr. K. S. Dhiman)</option>
            <option value="Pharmacovigilance Officer">6. Pharmacovigilance Officer (Dr. A. Verma)</option>
            <option value="Institutional Leadership">7. Institutional Leadership (Dean of Research)</option>
            <option value="Regulator / Read-only">8. Regulator / Read-only (CDSCO Auditor)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Server-side Enforcement Explanation -->
    <div class="pv-signal-notice" style="margin-bottom: 16px;">
      <span class="pv-signal-notice-icon">&#8505;</span>
      <strong>Backend Authorization Enforced:</strong> All routes and actions are validated server-side in Python. For example, switching to <em>Regulator / Read-only</em> restricts the session to strict HTTP GET access; attempting any modifying POST returns HTTP 403 Forbidden.
    </div>

    <!-- 8 Roles Matrix -->
    <div class="flat-card" style="margin-bottom: 16px;">
      <div class="flat-card-header"><span class="flat-card-title">8 Institutional Roles &amp; Permissions Matrix</span></div>
      <div class="table-wrapper">
        <table class="flat-table">
          <thead>
            <tr>
              <th style="width: 160px;">Role</th>
              <th style="width: 180px;">Designated Persona</th>
              <th>Operational Scope &amp; Server-Side Permissions</th>
              <th style="width: 140px;">Authorization Level</th>
            </tr>
          </thead>
          <tbody id="admin-roles-tbody">
            <tr><td colspan="4" class="text-muted" style="text-align:center; padding: 20px;">Loading roles matrix...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Accounts -->
    <div class="flat-card">
      <div class="flat-card-header"><span class="flat-card-title">Institutional User Accounts (PBKDF2-HMAC-SHA256 Protected)</span></div>
      <div class="table-wrapper">
        <table class="flat-table">
          <thead>
            <tr>
              <th style="width: 120px;">Username</th>
              <th style="width: 180px;">Full Name</th>
              <th style="width: 180px;">Institutional Email</th>
              <th style="width: 160px;">Assigned Role</th>
              <th>Department / Organization</th>
              <th style="width: 80px;">Status</th>
            </tr>
          </thead>
          <tbody id="admin-users-tbody">
            <tr><td colspan="6" class="text-muted" style="text-align:center; padding: 20px;">Loading users...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
  refreshAdminView();
}

async function refreshAdminView() {
  var sel = document.getElementById('admin-role-select');
  if (sel) sel.value = currentActiveRole;
  var nameEl = document.getElementById('admin-active-user-name');
  if (nameEl) nameEl.textContent = 'Active Role: ' + currentActiveRole;

  try {
    var [rolesRes, usersRes] = await Promise.all([
      fetch('/api/auth/roles'),
      fetch('/api/auth/users')
    ]);
    var roles = await rolesRes.json();
    var users = await usersRes.json();

    var rTbody = document.getElementById('admin-roles-tbody');
    if (rTbody) {
      rTbody.innerHTML = roles.map(function(r) {
        var isCurrent = r.name === currentActiveRole;
        var pList = (r.permissions || []).map(function(p) { return '<code>' + escapeHTML(p) + '</code>'; }).join(' ');
        return `<tr style="${isCurrent ? 'background: #f0fdf4;' : ''}">
          <td><strong>${escapeHTML(r.name)}</strong> ${isCurrent ? '<span class="status-indicator status-complete" style="font-size:9px;">ACTIVE</span>' : ''}</td>
          <td style="font-size: 11px;">${escapeHTML(getPersonaForRole(r.name))}</td>
          <td style="font-size: 11px; line-height: 1.5;">${escapeHTML(r.description)}<div style="margin-top: 4px;">${pList}</div></td>
          <td><span class="role-badge-pill">${r.name === 'Administrator' ? 'Super Admin' : (r.name.indexOf('Read-only') >= 0 ? 'Auditor (Read-Only)' : 'Functional Lead')}</span></td>
        </tr>`;
      }).join('');
    }

    var uTbody = document.getElementById('admin-users-tbody');
    if (uTbody) {
      uTbody.innerHTML = users.map(function(u) {
        return `<tr>
          <td class="text-mono" style="font-weight: 600;">${escapeHTML(u.username)}</td>
          <td><strong>${escapeHTML(u.full_name)}</strong></td>
          <td style="font-size: 11px; color: var(--text-secondary);">${escapeHTML(u.email)}</td>
          <td><span class="role-badge-pill">${escapeHTML(u.role_name)}</span></td>
          <td style="font-size: 11px;">${escapeHTML(u.institution || 'AIIA')}</td>
          <td><span class="status-indicator status-complete">&#10003; Active</span></td>
        </tr>`;
      }).join('');
    }
  } catch (e) { console.error('Admin view load error:', e); }
}

function getPersonaForRole(r) {
  var m = {
    'Administrator': 'Prof. (Dr.) Tanuja Nesari',
    'Principal Investigator': 'Dr. Galib',
    'Study Coordinator': 'Dr. P. Gupta',
    'Monitor': 'S. Sharma, CRA',
    'Ethics Committee': 'Dr. K. S. Dhiman',
    'Pharmacovigilance Officer': 'Dr. A. Verma',
    'Institutional Leadership': 'Dean of Research',
    'Regulator / Read-only': 'Central Regulatory Auditor'
  };
  return m[r] || 'Authorized Personnel';
}


// ============================================================
// 12. MODULE: AIIA TRIAL ASSISTANT (CONTROLLED CLINICAL QA)
// ============================================================
function renderAssistantView(container) {
  container.innerHTML = `
    <div class="assistant-shell">
      <div style="margin-bottom: 16px;">
        <h1 class="h1-title">AIIA Trial Assistant</h1>
        <p class="text-muted" style="font-size: 12px;">Institutional clinical-trial information engine with verified database calculations and strict regulatory boundaries.</p>
      </div>

      <div class="pv-signal-notice" style="margin-bottom: 16px;">
        <span class="pv-signal-notice-icon">&#8505;</span>
        <div>
          <strong>Deterministic Clinical Governance:</strong> All answers and statistics are computed live from verified database records. The assistant does not invent numbers and does not provide medical diagnosis or treatment advice.
        </div>
      </div>

      <!-- Quick Question Chips -->
      <div style="margin-bottom: 8px;">
        <span style="font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase;">Supported Institutional Questions:</span>
        <div class="assistant-chip-grid">
          <div class="assistant-chip" onclick="runAssistantSample('How many recruiting trials are in the dataset?')">&#128269; How many recruiting trials are in the dataset?</div>
          <div class="assistant-chip" onclick="runAssistantSample('Show Phase 3 trials.')">&#128202; Show Phase 3 trials</div>
          <div class="assistant-chip" onclick="runAssistantSample('Find trials related to diabetes.')">&#129658; Find trials related to diabetes</div>
          <div class="assistant-chip" onclick="runAssistantSample('Which trials have missing sample size?')">&#9888; Which trials have missing sample size?</div>
          <div class="assistant-chip" onclick="runAssistantSample('Which trials require attention?')">&#128276; Which trials require attention?</div>
          <div class="assistant-chip" onclick="runAssistantSample('Summarize trial CTRI/2017/10/010023')">&#128196; Summarize trial CTRI/2017/10/010023</div>
          <div class="assistant-chip" onclick="runAssistantSample('Show trials sponsored by AIIA.')">&#127963; Show trials sponsored by AIIA</div>
          <div class="assistant-chip" style="color: #991b1b; border-color: #fca5a5;" onclick="runAssistantSample('Should I take Ashwagandha to cure my diabetes?')">&#9888; Test Medical Safety Guardrail</div>
        </div>
      </div>

      <!-- Search Input -->
      <div class="assistant-input-box">
        <input type="text" id="assistant-query-input" class="form-input" placeholder="Ask a clinical trial governance question..." onkeydown="if(event.key==='Enter') submitAssistantQuery()">
        <button class="btn btn-primary" onclick="submitAssistantQuery()" id="assistant-submit-btn">&#128269; Query Assistant</button>
      </div>

      <!-- Live Results Area -->
      <div id="assistant-results-container">
        <div class="empty-state" style="padding: 30px 20px;">
          <div class="empty-state-icon">&#128270;</div>
          <div class="empty-state-title">Ready for Clinical Inquiry</div>
          <div class="empty-state-desc">Select any supported institutional question above or enter a search query to inspect verified trial records.</div>
        </div>
      </div>
    </div>
  `;
}

function runAssistantSample(q) {
  var input = document.getElementById('assistant-query-input');
  if (input) input.value = q;
  submitAssistantQuery();
}

async function submitAssistantQuery() {
  var input = document.getElementById('assistant-query-input');
  var query = (input ? input.value : '').trim();
  if (!query) return;

  var container = document.getElementById('assistant-results-container');
  var btn = document.getElementById('assistant-submit-btn');
  if (btn) btn.disabled = true;
  if (container) {
    container.innerHTML = `
      <div class="flat-card" style="text-align: center; padding: 30px;">
        <div class="text-muted" style="font-size: 13px;">Executing verified database query...</div>
      </div>
    `;
  }

  try {
    var res = await fetch('/api/assistant/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Active-Role': currentActiveRole
      },
      body: JSON.stringify({ query: query })
    });
    var data = await res.json();
    renderAssistantAnswer(data);
  } catch (e) {
    if (container) {
      container.innerHTML = `<div class="flat-card" style="color: #991b1b; padding: 20px;">Assistant query error: ${e}</div>`;
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

function renderAssistantAnswer(data) {
  var container = document.getElementById('assistant-results-container');
  if (!container) return;

  // Format verified metrics cards if present
  var metricsHtml = '';
  if (data.verified_metrics && Object.keys(data.verified_metrics).length > 0) {
    metricsHtml = '<div class="assistant-metrics-grid">';
    for (var k in data.verified_metrics) {
      var label = k.replace(/_/g, ' ');
      var val = data.verified_metrics[k];
      metricsHtml += `<div class="assistant-metric-item">
        <div class="assistant-metric-val">${escapeHTML(String(val))}</div>
        <div class="assistant-metric-lbl">${escapeHTML(label)}</div>
      </div>`;
    }
    metricsHtml += '</div>';
  }

  // Format sample records table if present
  var tableHtml = '';
  if (data.sample_records && data.sample_records.length > 0) {
    tableHtml = `
      <div style="margin-top: 14px;">
        <span style="font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase;">Verified Matching Protocols:</span>
        <div class="table-wrapper" style="margin-top: 6px;">
          <table class="flat-table" style="font-size: 11px;">
            <thead>
              <tr>
                <th style="width: 140px;">CTRI Number</th>
                <th>Title</th>
                <th style="width: 100px;">Phase</th>
                <th style="width: 110px;">Status</th>
              </tr>
            </thead>
            <tbody>
              ${data.sample_records.map(function(r) {
                return `<tr>
                  <td class="text-mono" style="font-weight: 600; color: var(--accent);">${escapeHTML(r.ctri_number || '—')}</td>
                  <td>${escapeHTML(r.public_title || r.title || '—')}</td>
                  <td>${escapeHTML(r.phase || 'Phase 2')}</td>
                  <td>${escapeHTML(r.recruitment_status || 'Recruiting')}</td>
                </tr>`;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  var isBlocked = data.intent === 'SAFETY_GUARDRAIL_BLOCKED';

  container.innerHTML = `
    <div class="assistant-response-card" style="${isBlocked ? 'border-left: 4px solid #ef4444;' : 'border-left: 4px solid var(--accent);'}">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
        <div>
          <span class="badge" style="font-size: 9px; font-weight: 600;">INTENT: ${escapeHTML(data.intent || 'QUERY')}</span>
          <div style="font-size: 13px; font-weight: 600; color: var(--text-primary); margin-top: 4px;">"${escapeHTML(data.question || '')}"</div>
        </div>
        <span class="role-badge-pill">AIIA AI Assistant</span>
      </div>

      <div style="font-size: 13px; line-height: 1.6; color: var(--text-primary); margin-top: 10px;">
        ${data.answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}
      </div>

      ${metricsHtml}
      ${tableHtml}

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-light); flex-wrap: wrap; gap: 8px;">
        <span class="assistant-source-tag">&#128214; ${escapeHTML(data.source || 'Source: CTRI public dataset')}</span>
        <span class="text-muted" style="font-size: 10px;">Deterministic Database Calculation</span>
      </div>
    </div>
  `;
}
'''

fp = pathlib.Path("c:/Users/yoges/Documents/AIIA Dashboard/app.js")
lines = fp.read_text(encoding="utf-8").splitlines(keepends=True)

# Replace lines 2972 to 3214 (0-indexed: 2971 to 3213)
# Let's find lines 2972 to 3215 precisely
start_idx = -1
end_idx = -1

for i, l in enumerate(lines):
    if "9. MODULE: INTEROPERABILITY" in l:
        start_idx = i - 1
    if "11. MODULE: DESIGN SYSTEM & COMPONENT SHOWCASE" in l:
        end_idx = i - 1
        break

print(f"Replacing lines {start_idx} to {end_idx}")
new_lines = lines[:start_idx] + [frontend_code] + lines[end_idx:]
fp.write_text("".join(new_lines), encoding="utf-8")
print(f"app.js updated successfully! Total lines: {len(new_lines)}")
