/**
 * AYURCTMS - AIIA Clinical Trial Management & Research Portal
 * Smart India Hackathon Problem Statement 26046
 * Full Frontend Application Logic
 */

// ============================================================
// STATE STORE
// ============================================================
const STATE = {
  currentView: 'gate', // 'gate' | 'patient' | 'staff'
  currentStaffTab: 'dashboard',
  currentUser: null,
  sidebarCollapsed: false,
  stats: null,
  trials: [],
  sites: [],
  doctors: [],
  patients: [],
  approvals: [],
  gcp: null,
  pvSummary: null,
  pvEvents: [],
  pvSignals: [],
  notifications: [],
  auditTrail: []
};

// ============================================================
// TOAST SYSTEM
// ============================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:transparent; border:none; color:#fff; cursor:pointer; font-size:14px;" onclick="this.parentElement.remove()">✕</button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // Check if session exists
  const savedUser = localStorage.getItem('ayur_staff_user');
  if (savedUser) {
    try {
      STATE.currentUser = JSON.parse(savedUser);
    } catch (e) {
      STATE.currentUser = null;
    }
  }

  // Handle hash routing if available
  const hash = window.location.hash.replace('#', '');
  if (hash === 'patient') {
    showPatientPortal();
  } else if (hash && STATE.currentUser) {
    showStaffPortal();
    switchStaffTab(hash);
  } else {
    showLandingGate();
  }
});

// ============================================================
// 1. TOP-LEVEL VIEW SWITCHING
// ============================================================
function showLandingGate() {
  STATE.currentView = 'gate';
  document.getElementById('landing-gate').style.display = 'flex';
  document.getElementById('patient-portal').style.display = 'none';
  document.getElementById('staff-portal').style.display = 'none';
  hideStaffLoginModal();
  window.location.hash = '';
}

function showPatientPortal() {
  STATE.currentView = 'patient';
  document.getElementById('landing-gate').style.display = 'none';
  document.getElementById('patient-portal').style.display = 'block';
  document.getElementById('staff-portal').style.display = 'none';
  hideStaffLoginModal();
  window.location.hash = 'patient';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function returnToGate() {
  showLandingGate();
}

function showStaffLoginModal() {
  document.getElementById('staff-login-modal').style.display = 'flex';
  document.getElementById('login-error-msg').style.display = 'none';
}

function hideStaffLoginModal() {
  document.getElementById('staff-login-modal').style.display = 'none';
}

function autofillDemoLogin() {
  document.getElementById('login-staff-id').value = 'AIIA001';
  document.getElementById('login-password').value = 'AIIA@123';
}

async function handleStaffLogin(e) {
  if (e && e.preventDefault) e.preventDefault();
  const staffIdInput = document.getElementById('login-staff-id');
  const passwordInput = document.getElementById('login-password');
  const staffId = staffIdInput ? staffIdInput.value.trim() : 'AIIA001';
  const password = passwordInput ? passwordInput.value.trim() : 'AIIA@123';
  const errorEl = document.getElementById('login-error-msg');

  if (errorEl) errorEl.style.display = 'none';

  const isDemoMatch = (staffId.toUpperCase() === 'AIIA001' && password === 'AIIA@123') ||
                      (staffId.toLowerCase() === 'admin' && password === 'admin123');

  try {
    const res = await fetch('/api/ayur/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ staff_id: staffId, password })
    });
    
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        STATE.currentUser = data.user;
        localStorage.setItem('ayur_staff_user', JSON.stringify(data.user));
        hideStaffLoginModal();
        showToast(`Welcome, ${data.user.full_name}`, 'success');
        showStaffPortal();
        return;
      }
    }
  } catch (err) {
    console.warn('Network login check fallback...', err);
  }

  if (isDemoMatch) {
    const fallbackUser = {
      staff_id: 'AIIA001',
      full_name: 'Dr. Research Admin',
      role: 'AIIA Authorized Staff',
      designation: 'Clinical Research Coordinator / Admin',
      institution: 'All India Institute of Ayurveda (AIIA), New Delhi'
    };
    STATE.currentUser = fallbackUser;
    localStorage.setItem('ayur_staff_user', JSON.stringify(fallbackUser));
    hideStaffLoginModal();
    showToast('Welcome, Dr. Research Admin', 'success');
    showStaffPortal();
    return;
  }

  if (errorEl) {
    errorEl.textContent = 'Invalid Staff ID or Password. Demo: AIIA001 / AIIA@123';
    errorEl.style.display = 'block';
  }
}

function logoutStaff() {
  STATE.currentUser = null;
  localStorage.removeItem('ayur_staff_user');
  showToast('Logged out of AIIA Staff Portal', 'info');
  showLandingGate();
}

function showStaffPortal() {
  STATE.currentView = 'staff';
  document.getElementById('landing-gate').style.display = 'none';
  document.getElementById('patient-portal').style.display = 'none';
  document.getElementById('staff-portal').style.display = 'flex';

  if (STATE.currentUser) {
    document.getElementById('staff-display-name').textContent = STATE.currentUser.full_name;
  }

  loadInitialStaffData();
  switchStaffTab(STATE.currentStaffTab || 'dashboard');
}

function toggleSidebar() {
  const sidebar = document.getElementById('staff-sidebar');
  sidebar.classList.toggle('collapsed');
  STATE.sidebarCollapsed = sidebar.classList.contains('collapsed');
}

// ============================================================
// 2. PATIENT INTAKE & TRIAL MATCHING
// ============================================================
function onConditionSelectChange(val) {
  // Helpful hint
}

function resetPatientForm() {
  document.getElementById('patient-matching-form').reset();
  document.getElementById('patient-results-area').style.display = 'none';
}

function scrollToForm() {
  document.querySelector('.patient-intake-section').scrollIntoView({ behavior: 'smooth' });
}

async function handlePatientMatchingSubmit(e) {
  e.preventDefault();

  const fullName = document.getElementById('p-fullname').value.trim();
  const age = document.getElementById('p-age').value;
  const gender = document.getElementById('p-gender').value;
  const condition = document.getElementById('p-condition').value;
  const city = document.getElementById('p-city').value.trim();
  const distancePref = document.getElementById('p-distance').value;

  // Collect multi-select accessible locations
  const locCheckboxes = document.querySelectorAll('input[name="accessible_loc"]:checked');
  const accessibleLocations = Array.from(locCheckboxes).map(cb => cb.value);

  const resultsArea = document.getElementById('patient-results-area');
  const cardsContainer = document.getElementById('patient-trial-cards-container');
  const resultsTitle = document.getElementById('patient-results-title');
  const resultsCount = document.getElementById('patient-results-count');

  resultsArea.style.display = 'block';
  resultsTitle.textContent = 'Finding suitable clinical trial locations...';
  resultsCount.textContent = 'Analyzing condition matching and multi-center location accessibility...';
  cardsContainer.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 30px;"><div class="badge badge-info">Searching AIIA Active Clinical Trials...</div></div>';

  resultsArea.scrollIntoView({ behavior: 'smooth' });

  try {
    const res = await fetch('/api/ayur/patient/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        condition,
        accessible_locations: accessibleLocations,
        distance_pref: distancePref,
        age,
        gender
      })
    });
    const data = await res.json();

    if (data.success && data.results && data.results.length > 0) {
      resultsTitle.textContent = `Recommended Clinical Trial Locations for "${condition === 'All' ? 'All Conditions' : condition}"`;
      resultsCount.textContent = `Identified ${data.results.length} potentially relevant trial site(s) matching your location accessibility.`;

      cardsContainer.innerHTML = data.results.map(t => `
        <div class="trial-recommendation-card">
          <div class="trial-card-header">
            <span class="trial-id-badge">${t.trial_id}</span>
            <span class="badge ${t.status === 'Recruiting' ? 'badge-success' : 'badge-info'}">${t.status}</span>
          </div>

          <h4 class="trial-condition-title">${t.condition}</h4>
          <p style="font-size: 13px; font-weight:600; color: var(--ayur-primary); margin-bottom: 8px;">${t.trial_name}</p>

          <div class="trial-meta-grid">
            <div class="trial-meta-item">
              <span class="meta-label">Location</span>
              <span class="meta-value">${t.location}, ${t.state}</span>
            </div>
            <div class="trial-meta-item">
              <span class="meta-label">Hospital / Site</span>
              <span class="meta-value">${t.hospital}</span>
            </div>
            <div class="trial-meta-item">
              <span class="meta-label">Duration</span>
              <span class="meta-value">${t.duration}</span>
            </div>
            <div class="trial-meta-item">
              <span class="meta-label">Available Slots</span>
              <span class="meta-value" style="color: #047857; font-weight: 700;">${t.available_slots} Slots</span>
            </div>
          </div>

          <div class="distance-info-tag">
            📍 <strong>Accessibility:</strong> ${t.distance_context}
          </div>

          <button class="btn btn-primary btn-sm btn-block" onclick="openPatientTrialDetailModal('${t.trial_id}')">
            VIEW DETAILS
          </button>
        </div>
      `).join('');

      showToast(`Found ${data.results.length} matching trial locations.`, 'success');
    } else {
      resultsTitle.textContent = 'No Direct Matches Found';
      resultsCount.textContent = 'No actively recruiting trials matched all criteria in the selected cities.';
      cardsContainer.innerHTML = `
        <div style="grid-column: 1/-1; background:#fff; padding: 30px; border-radius: 8px; text-align:center; border: 1px dashed var(--border-medium);">
          <p style="font-size: 14px; color: var(--text-secondary); margin-bottom: 12px;">We currently do not have open trial slots for this specific combination.</p>
          <button class="btn btn-outline btn-sm" onclick="document.getElementById('p-condition').value='All'; handlePatientMatchingSubmit(new Event('submit'))">
            View All Active Ayurveda Trials
          </button>
        </div>
      `;
    }
  } catch (err) {
    resultsTitle.textContent = 'Error Searching Trials';
    cardsContainer.innerHTML = '<div style="color: red; padding: 20px;">Could not connect to matching server.</div>';
  }
}

async function openPatientTrialDetailModal(trialId) {
  try {
    const res = await fetch(`/api/ayur/trials/${trialId}`);
    const data = await res.json();
    if (!data.success) return;
    const t = data.trial;

    const modalContent = document.getElementById('dynamic-modal-content');
    modalContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="trial-id-badge">${t.trial_id}</span>
          <h3 style="margin-top: 6px; font-size: 18px;">${t.trial_name}</h3>
        </div>
        <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
      </div>

      <div class="disclaimer-banner" style="margin-bottom: 16px;">
        <div class="disclaimer-icon">ℹ️</div>
        <div class="disclaimer-content">
          <strong>Potentially Relevant Trial Information</strong>
          <p>Final eligibility will be determined by the authorized clinical research team.</p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13px;">
        <div><strong>Condition Being Studied:</strong> ${t.condition}</div>
        <div><strong>Ayurvedic Intervention:</strong> ${t.intervention}</div>
        <div><strong>Clinical Site:</strong> ${t.hospital_name} (${t.city}, ${t.state})</div>
        <div><strong>Principal Investigator:</strong> ${t.pi_name}</div>
        <div><strong>Trial Duration:</strong> ${t.duration_weeks} Weeks</div>
        <div><strong>Current Recruitment Status:</strong> <span class="badge badge-success">${t.recruitment_status}</span></div>

        <div style="background: var(--bg-canvas); padding: 12px; border-radius: 6px; border: 1px solid var(--border-light);">
          <strong>Public Eligibility Information:</strong>
          <p style="margin-top: 4px; font-size: 12.5px; color: var(--text-secondary);">${t.eligibility_criteria || 'Adult participants meeting condition diagnosis.'}</p>
        </div>

        <div style="background: var(--bg-canvas); padding: 12px; border-radius: 6px; border: 1px solid var(--border-light);">
          <strong>Exclusion Criteria:</strong>
          <p style="margin-top: 4px; font-size: 12.5px; color: var(--text-secondary);">${t.exclusion_criteria || 'Severe uncontrolled systemic illness.'}</p>
        </div>

        <div>
          <strong>Trial Description:</strong>
          <p style="margin-top: 4px; color: var(--text-secondary);">${t.description}</p>
        </div>

        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 6px; font-size: 12px; color: #166534;">
          📞 <strong>Clinical Trial Coordinator Contact:</strong> Contact AIIA Research Desk at <strong>research@aiia.gov.in</strong> or visit the hospital clinical desk with ID <strong>${t.trial_id}</strong>.
        </div>
      </div>

      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <button class="btn btn-outline" onclick="closeDynamicModal()">Close</button>
      </div>
    `;

    document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  } catch (e) {
    showToast('Could not load trial details', 'danger');
  }
}

// ============================================================
// 3. STAFF PORTAL: INITIAL DATA LOADER & TAB ROUTING
// ============================================================
async function loadInitialStaffData() {
  try {
    const [statsRes, notifsRes] = await Promise.all([
      fetch('/api/ayur/dashboard/stats'),
      fetch('/api/ayur/notifications')
    ]);
    STATE.stats = await statsRes.json();
    const notifs = await notifsRes.json();
    STATE.notifications = notifs.notifications || [];

    // Update badges
    if (STATE.stats) {
      const gcpPct = STATE.stats.gcp_compliance.percentage;
      document.getElementById('badge-gcp-pct').textContent = `${gcpPct}%`;
      document.getElementById('badge-active-trials').textContent = STATE.stats.active_trials_summary.ongoing;
    }

    renderNotificationsDrawer();
  } catch (e) {
    console.error('Error loading staff initial data', e);
  }
}

function renderNotificationsDrawer() {
  const countEl = document.getElementById('notification-unread-count');
  const listEl = document.getElementById('notif-items-list');
  const totalBadge = document.getElementById('notif-total-badge');

  const unread = STATE.notifications.filter(n => !n.is_read);
  countEl.textContent = unread.length;
  totalBadge.textContent = `${STATE.notifications.length} Total`;

  listEl.innerHTML = STATE.notifications.map(n => `
    <div class="notif-item ${!n.is_read ? 'notif-unread' : ''}" onclick="handleNotificationClick(${n.id}, '${n.link_route}')">
      <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-bottom: 2px;">
        <span>${n.category}</span>
        <span>${n.created_at}</span>
      </div>
      <div style="font-weight: 600; color: var(--text-primary); font-size: 12px;">${n.title}</div>
      <div style="font-size: 11.5px; color: var(--text-secondary); margin-top: 2px;">${n.message}</div>
    </div>
  `).join('');
}

function toggleNotificationsDrawer() {
  const drawer = document.getElementById('notifications-drawer');
  drawer.style.display = drawer.style.display === 'none' ? 'block' : 'none';
}

async function handleNotificationClick(notifId, route) {
  try {
    await fetch('/api/ayur/notifications/read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notification_id: notifId })
    });
    const notif = STATE.notifications.find(n => n.id === notifId);
    if (notif) notif.is_read = 1;
    renderNotificationsDrawer();
    toggleNotificationsDrawer();
    if (route) switchStaffTab(route);
  } catch (e) {
    console.error(e);
  }
}

function switchStaffTab(tabName) {
  STATE.currentStaffTab = tabName;
  window.location.hash = tabName;

  // Update active sidebar link
  document.querySelectorAll('.sidebar-nav-item').forEach(el => {
    if (el.getAttribute('data-nav') === tabName) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });

  const viewport = document.getElementById('staff-main-content');
  viewport.innerHTML = '<div style="padding: 40px; text-align:center;"><div class="badge badge-info">Loading clinical module...</div></div>';

  switch (tabName) {
    case 'dashboard':
      renderDashboardView(viewport);
      break;
    case 'active-trials':
      renderActiveTrialsView(viewport);
      break;
    case 'sites':
      renderSitesView(viewport);
      break;
    case 'trial-info':
      renderTrialInfoView(viewport);
      break;
    case 'approvals':
      renderApprovalsView(viewport);
      break;
    case 'gcp':
      renderGCPView(viewport);
      break;
    case 'doctors':
      renderDoctorsView(viewport);
      break;
    case 'patients':
      renderPatientsView(viewport);
      break;
    case 'pv':
      renderPVView(viewport);
      break;
    case 'reports':
      renderReportsView(viewport);
      break;
    case 'interop':
      renderInteropView(viewport);
      break;
    default:
      renderDashboardView(viewport);
  }
}

// ============================================================
// 4. MODULE 1: DASHBOARD (MATCHING HAND-DRAWN SKETCH)
// ============================================================
async function renderDashboardView(container) {
  const res = await fetch('/api/ayur/dashboard/stats');
  const data = await res.json();
  STATE.stats = data;

  const kpis = data.kpi_cards;
  const trialsSum = data.active_trials_summary;

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>AIIA Clinical Trials Executive Dashboard</h2>
        <p>Real-time clinical trial oversight, doctor rosters, patient flow, and pharmacovigilance</p>
      </div>
      <div style="display: flex; gap: 10px;">
        <button class="btn btn-outline btn-sm" onclick="switchStaffTab('gcp')">🛡️ GCP Status: ${data.gcp_compliance.percentage}%</button>
        <button class="btn btn-primary btn-sm" onclick="openCreateTrialModal()">+ CREATE NEW TRIAL</button>
      </div>
    </div>

    <!-- 3 MAJOR TOP KPI CARDS (MATCHING THE SKETCH) -->
    <div class="sketch-kpi-grid">
      <!-- CARD 1: DOCTOR INFORMATION -->
      <div class="sketch-kpi-card kpi-doctor">
        <div class="kpi-card-header">
          <span class="kpi-card-title">${kpis.doctors.title}</span>
          <span class="kpi-card-icon">👨‍⚕️</span>
        </div>
        <div class="kpi-stats-row">
          <div class="kpi-stat-col">
            <span class="kpi-stat-number">${kpis.doctors.total_doctors}</span>
            <span class="kpi-stat-label">Total Doctors</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number" style="color: #0b4f49;">${kpis.doctors.active_investigators}</span>
            <span class="kpi-stat-label">Active PIs</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number">${kpis.doctors.trial_sites}</span>
            <span class="kpi-stat-label">Trial Sites</span>
          </div>
        </div>
        <button class="btn btn-outline btn-sm kpi-card-btn" onclick="switchStaffTab('doctors')">
          ${kpis.doctors.button_text}
        </button>
      </div>

      <!-- CARD 2: PATIENT INFORMATION -->
      <div class="sketch-kpi-card kpi-patient">
        <div class="kpi-card-header">
          <span class="kpi-card-title">${kpis.patients.title}</span>
          <span class="kpi-card-icon">👥</span>
        </div>
        <div class="kpi-stats-row">
          <div class="kpi-stat-col">
            <span class="kpi-stat-number">${kpis.patients.total_patients}</span>
            <span class="kpi-stat-label">Registered</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number" style="color: #0284c7;">${kpis.patients.active_participants}</span>
            <span class="kpi-stat-label">Active Flow</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number" style="color: #059669;">${kpis.patients.completed_participants}</span>
            <span class="kpi-stat-label">Completed</span>
          </div>
        </div>
        <button class="btn btn-outline btn-sm kpi-card-btn" onclick="switchStaffTab('patients')">
          ${kpis.patients.button_text}
        </button>
      </div>

      <!-- CARD 3: PHARMACOVIGILANCE -->
      <div class="sketch-kpi-card kpi-pv">
        <div class="kpi-card-header">
          <span class="kpi-card-title">${kpis.pharmacovigilance.title}</span>
          <span class="kpi-card-icon">⚠️</span>
        </div>
        <div class="kpi-stats-row">
          <div class="kpi-stat-col">
            <span class="kpi-stat-number">${kpis.pharmacovigilance.total_adverse_events}</span>
            <span class="kpi-stat-label">Total AE</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number" style="color: #dc2626;">${kpis.pharmacovigilance.serious_adverse_events}</span>
            <span class="kpi-stat-label">Serious (SAE)</span>
          </div>
          <div class="kpi-stat-col">
            <span class="kpi-stat-number" style="color: #d97706;">${kpis.pharmacovigilance.cases_under_review}</span>
            <span class="kpi-stat-label">Under Review</span>
          </div>
        </div>
        <button class="btn btn-outline btn-sm kpi-card-btn" onclick="switchStaffTab('pv')">
          ${kpis.pharmacovigilance.button_text}
        </button>
      </div>
    </div>

    <!-- SECTION A: ACTIVE TRIALS BREAKDOWN & PROGRESS BARS -->
    <div class="active-trials-section-card">
      <div class="section-card-header">
        <span class="section-card-title">Active Clinical Trials & Milestone Progress</span>
        <button class="btn btn-ghost btn-sm" onclick="switchStaffTab('active-trials')">View All Trials →</button>
      </div>

      <div class="trials-summary-counters">
        <div class="trial-counter-pill">
          <span>🟢 Ongoing:</span>
          <strong>${trialsSum.ongoing}</strong>
        </div>
        <div class="trial-counter-pill">
          <span>🔵 Completed:</span>
          <strong>${trialsSum.completed}</strong>
        </div>
        <div class="trial-counter-pill">
          <span>🟡 Upcoming / Pending:</span>
          <strong>${trialsSum.upcoming}</strong>
        </div>
      </div>

      <div class="trial-progress-list">
        ${trialsSum.trials_progress.map(t => `
          <div class="trial-progress-row" onclick="openStaffTrialDetailModal('${t.trial_id}')">
            <div class="trial-progress-header">
              <div>
                <span class="trial-progress-id">${t.trial_id}</span>: 
                <strong>${t.trial_name}</strong> (${t.condition} • ${t.city})
              </div>
              <div>
                <span style="font-weight: 700; color: var(--ayur-primary);">${t.progress_pct}%</span>
                <span class="text-muted" style="font-size: 11px;">(${t.enrolled_participants}/${t.target_participants} Enrolled)</span>
              </div>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${t.progress_pct}%;"></div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- QUICK SITES MATRIX SHORTCUT -->
    <div class="active-trials-section-card">
      <div class="section-card-header">
        <span class="section-card-title">National Ayurveda Clinical Trial Sites (9 Participating Centers)</span>
        <button class="btn btn-ghost btn-sm" onclick="switchStaffTab('sites')">Full Sites Center →</button>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px;">
        ${['Mumbai', 'Delhi', 'Kolkata', 'Kerala', 'Lucknow', 'Noida', 'Jaipur', 'Hyderabad', 'Bengaluru'].map(c => `
          <button class="btn btn-outline btn-sm" onclick="openSiteDetailModal('${c}')" style="font-weight: 600;">
            📍 ${c}
          </button>
        `).join('')}
      </div>
    </div>
  `;
}

// ============================================================
// 5. MODULE 2: ACTIVE TRIALS
// ============================================================
async function renderActiveTrialsView(container) {
  const res = await fetch('/api/ayur/trials');
  const data = await res.json();
  const trials = data.trials || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Active Clinical Trials Directory</h2>
        <p>Multi-center Ayurveda clinical trials across India with live enrollment tracking</p>
      </div>
      <button class="btn btn-primary btn-sm" onclick="openCreateTrialModal()">+ CREATE NEW TRIAL</button>
    </div>

    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Trial ID</th>
            <th>Title & Condition</th>
            <th>Location & Site</th>
            <th>Principal Investigator</th>
            <th>Duration</th>
            <th>Enrolled / Target</th>
            <th>Progress</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${trials.map(t => `
            <tr>
              <td><span class="trial-id-badge">${t.trial_id}</span></td>
              <td>
                <div style="font-weight: 700;">${t.condition}</div>
                <div style="font-size: 11.5px; color: var(--text-muted);">${t.trial_name}</div>
              </td>
              <td>
                <div style="font-weight: 600;">${t.city}</div>
                <div style="font-size: 11px; color: var(--text-muted);">${t.hospital_name}</div>
              </td>
              <td>${t.pi_name}</td>
              <td>${t.duration_weeks} Wks</td>
              <td><strong>${t.enrolled_participants}</strong> / ${t.target_participants}</td>
              <td>
                <div style="width: 80px;">
                  <div style="font-size: 11px; font-weight:700; margin-bottom: 2px;">${t.progress_pct}%</div>
                  <div class="progress-bar-container" style="height: 6px;">
                    <div class="progress-bar-fill" style="width: ${t.progress_pct}%;"></div>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge ${t.trial_status === 'Ongoing' ? 'badge-success' : t.trial_status === 'Completed' ? 'badge-info' : 'badge-warning'}">
                  ${t.trial_status}
                </span>
              </td>
              <td>
                <button class="btn btn-outline btn-xs" onclick="openStaffTrialDetailModal('${t.trial_id}')">Details</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ============================================================
// 6. MODULE 3: SITES / LOCATIONS (9 CITIES MATRIX)
// ============================================================
async function renderSitesView(container) {
  const res = await fetch('/api/ayur/sites');
  const data = await res.json();
  const sites = data.sites || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>AIIA Participating Clinical Trial Sites Across India</h2>
        <p>Interactive location nodes with live protocol tracking and recorded outcome trends</p>
      </div>
    </div>

    <div class="sites-grid">
      ${sites.map(s => `
        <div class="site-card" onclick="openSiteDetailModal('${s.city}')">
          <div class="site-card-header">
            <span class="site-city-title">📍 ${s.city}</span>
            <span class="badge ${s.status === 'Ongoing' ? 'badge-success' : 'badge-warning'}">${s.status}</span>
          </div>
          <div class="site-hospital-name">${s.hospital_name}</div>
          
          <div style="margin-bottom: 10px; font-size: 12.5px;">
            <strong>Condition:</strong> ${s.condition}
          </div>

          <div class="site-stats-row">
            <div>
              <span class="meta-label">Enrolled</span>
              <div style="font-weight: 700;">${s.participants_enrolled} / ${s.participants_target}</div>
            </div>
            <div>
              <span class="meta-label">Duration</span>
              <div style="font-weight: 700;">${s.duration_weeks} Weeks</div>
            </div>
            <div>
              <span class="meta-label">Progress</span>
              <div style="font-weight: 700; color: var(--ayur-primary);">${s.progress_pct}%</div>
            </div>
          </div>

          <div class="progress-bar-container" style="height: 6px; margin-bottom: 14px;">
            <div class="progress-bar-fill" style="width: ${s.progress_pct}%;"></div>
          </div>

          <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 12px;">
            👨‍⚕️ PI: ${s.pi_name}
          </div>

          <button class="btn btn-outline btn-sm btn-block" style="margin-top: auto;">
            VIEW SITE DETAILS
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

async function openSiteDetailModal(city) {
  try {
    const res = await fetch(`/api/ayur/sites/${encodeURIComponent(city)}`);
    const data = await res.json();
    if (!data.success) return;
    const s = data.site;
    const trend = s.outcome_trend || [];

    const modalContent = document.getElementById('dynamic-modal-content');
    modalContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="badge badge-info">AIIA Clinical Center</span>
          <h3 style="margin-top: 6px; font-size: 20px;">📍 ${s.city} Trial Site</h3>
        </div>
        <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 13px; margin-bottom: 20px;">
        <div><strong>Hospital:</strong> ${s.hospital_name}</div>
        <div><strong>State:</strong> ${s.state}</div>
        <div><strong>Active Study Condition:</strong> <span style="color: var(--ayur-primary); font-weight: 700;">${s.condition}</span></div>
        <div><strong>Trial ID:</strong> ${s.trial_id}</div>
        <div><strong>Principal Investigator:</strong> ${s.pi_name}</div>
        <div><strong>Doctor Working at Site:</strong> ${s.doctor_name}</div>
        <div><strong>Trial Coordinator:</strong> ${s.coordinator_name}</div>
        <div><strong>Status:</strong> <span class="badge badge-success">${s.status}</span></div>
        <div><strong>Start Date:</strong> ${s.start_date}</div>
        <div><strong>Expected End Date:</strong> ${s.end_date}</div>
        <div><strong>Trial Duration:</strong> ${s.duration_weeks} Weeks</div>
        <div><strong>Participants:</strong> <strong>${s.participants_enrolled}</strong> / ${s.participants_target} (${s.progress_pct}%)</div>
      </div>

      <!-- RECORDED OUTCOME TREND / PROGRESS CHART -->
      <div style="background: var(--bg-canvas); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 18px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <strong>Recorded Outcome Trend / Progress (Demo Data)</strong>
          <span class="badge badge-neutral">Standardized Clinical Scoring</span>
        </div>

        <div style="display: flex; align-items: flex-end; gap: 20px; height: 120px; padding: 10px 0; border-bottom: 1px solid var(--border-medium);">
          ${trend.map(item => `
            <div style="flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end;">
              <div style="font-size: 11px; font-weight: 700; color: var(--ayur-primary); margin-bottom: 4px;">${item.score || item.value}</div>
              <div style="width: 100%; max-width: 40px; background: linear-gradient(180deg, var(--ayur-primary-light), var(--ayur-primary)); border-radius: 4px 4px 0 0; height: ${(item.score || item.value) * 1.2}px;"></div>
              <div style="font-size: 10px; color: var(--text-muted); margin-top: 6px;">${item.milestone || item.week}</div>
            </div>
          `).join('')}
        </div>
        <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">* Recorded outcome trend is synthesized demonstration telemetry for institutional protocol evaluation.</p>
      </div>

      <div style="background: #fffbeb; border: 1px solid #fde68a; padding: 12px; border-radius: 6px; font-size: 12px; color: #92400e; margin-bottom: 20px;">
        ⚠️ <strong>Site Pending Issues / Monitoring Remarks:</strong> ${s.pending_issues || 'Routine monitoring review pending.'}
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button class="btn btn-outline" onclick="closeDynamicModal()">Close</button>
        <button class="btn btn-primary" onclick="closeDynamicModal(); openStaffTrialDetailModal('${s.trial_id}')">Open Study Protocol</button>
      </div>
    `;

    document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  } catch (e) {
    showToast('Could not load site details', 'danger');
  }
}

// ============================================================
// 7. MODULE 4: TRIAL INFORMATION & [+ CREATE NEW TRIAL]
// ============================================================
async function renderTrialInfoView(container) {
  const res = await fetch('/api/ayur/trials');
  const data = await res.json();
  const trials = data.trials || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Ayurveda Clinical Protocols & Trials</h2>
        <p>Comprehensive protocol database with CDISC standard variable mapping</p>
      </div>
      <button class="btn btn-primary btn-sm" onclick="openCreateTrialModal()">+ CREATE NEW TRIAL</button>
    </div>

    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Trial ID</th>
            <th>Condition</th>
            <th>Intervention</th>
            <th>Hospital & City</th>
            <th>Principal Investigator</th>
            <th>Start / End Date</th>
            <th>Enrolled</th>
            <th>Regulatory</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${trials.map(t => `
            <tr>
              <td><span class="trial-id-badge">${t.trial_id}</span></td>
              <td><strong>${t.condition}</strong></td>
              <td>${t.intervention}</td>
              <td>${t.hospital_name} (${t.city})</td>
              <td>${t.pi_name}</td>
              <td style="font-size: 11.5px;">${t.start_date}<br><span class="text-muted">${t.end_date}</span></td>
              <td>${t.enrolled_participants}/${t.target_participants}</td>
              <td><span class="badge badge-success">${t.regulatory_status}</span></td>
              <td><span class="badge ${t.trial_status === 'Ongoing' ? 'badge-success' : 'badge-warning'}">${t.trial_status}</span></td>
              <td>
                <button class="btn btn-outline btn-xs" onclick="openStaffTrialDetailModal('${t.trial_id}')">View</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function openStaffTrialDetailModal(trialId) {
  try {
    const res = await fetch(`/api/ayur/trials/${trialId}`);
    const data = await res.json();
    if (!data.success) return;
    const t = data.trial;

    const modalContent = document.getElementById('dynamic-modal-content');
    modalContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="trial-id-badge">${t.trial_id}</span>
          <h3 style="margin-top: 6px; font-size: 20px;">${t.trial_name}</h3>
        </div>
        <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 13px; margin-bottom: 20px;">
        <div><strong>Condition:</strong> ${t.condition}</div>
        <div><strong>Ayurvedic Intervention:</strong> ${t.intervention}</div>
        <div><strong>Hospital / Facility:</strong> ${t.hospital_name}</div>
        <div><strong>City / State:</strong> ${t.city}, ${t.state}</div>
        <div><strong>Principal Investigator:</strong> ${t.pi_name}</div>
        <div><strong>Duration:</strong> ${t.duration_weeks} Weeks (${t.start_date} to ${t.end_date})</div>
        <div><strong>Target Sample:</strong> ${t.target_participants} Participants</div>
        <div><strong>Enrolled:</strong> ${t.enrolled_participants} (${t.progress_pct}%)</div>
        <div><strong>Ethics Approval:</strong> <span class="badge badge-success">${t.ethics_approval_status}</span></div>
        <div><strong>CTRI Registration:</strong> <span class="badge badge-success">${t.ctri_registration_status}</span></div>
        <div><strong>Regulatory Status:</strong> <span class="badge badge-success">${t.regulatory_status}</span></div>
        <div><strong>Trial Status:</strong> <span class="badge badge-info">${t.trial_status}</span></div>
      </div>

      <div style="background: var(--bg-canvas); padding: 14px; border-radius: 6px; border: 1px solid var(--border-light); margin-bottom: 16px;">
        <strong>Protocol Description:</strong>
        <p style="margin-top: 4px; font-size: 12.5px; color: var(--text-secondary);">${t.description}</p>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
        <div style="background: #f8fafc; border: 1px solid var(--border-light); padding: 12px; border-radius: 6px;">
          <strong style="font-size: 12px;">Diagnostic Inclusion Criteria:</strong>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${t.eligibility_criteria}</p>
        </div>
        <div style="background: #f8fafc; border: 1px solid var(--border-light); padding: 12px; border-radius: 6px;">
          <strong style="font-size: 12px;">Exclusion Criteria:</strong>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${t.exclusion_criteria}</p>
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 14px; border-top: 1px solid var(--border-light);">
        <span class="text-muted" style="font-size: 11.5px;">Enrolled Patient Cohort: ${t.patients ? t.patients.length : 0} registered subjects</span>
        <button class="btn btn-outline" onclick="closeDynamicModal()">Close</button>
      </div>
    `;

    document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  } catch (e) {
    showToast('Could not load trial details', 'danger');
  }
}

function openCreateTrialModal() {
  const modalContent = document.getElementById('dynamic-modal-content');
  modalContent.innerHTML = `
    <div class="modal-header">
      <div>
        <span class="badge badge-info">Protocol Planning</span>
        <h3 style="margin-top: 4px; font-size: 18px;">+ Create New Ayurvedic Clinical Trial</h3>
      </div>
      <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
    </div>

    <!-- OVERLAP WARNING PLACEHOLDER (INTELLIGENT DETECTION) -->
    <div id="trial-overlap-alert-box" class="overlap-warning-box" style="display: none;"></div>

    <form id="create-trial-form" onsubmit="handleCreateTrialSubmit(event)">
      <div class="form-row-grid">
        <div class="form-group">
          <label>Trial Name *</label>
          <input type="text" id="new-trial-name" class="form-input" placeholder="e.g. Randomized Clinical Evaluation of Rasayana in Arthritis" required>
        </div>
        <div class="form-group">
          <label>Trial ID *</label>
          <input type="text" id="new-trial-id" class="form-input" value="AYU-TRIAL-00${Math.floor(Math.random() * 90 + 10)}" required>
        </div>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>Condition / Illness *</label>
          <select id="new-trial-condition" class="form-select" required onchange="checkTrialOverlap()">
            <option value="Arthritis">Arthritis</option>
            <option value="Diabetes">Diabetes</option>
            <option value="Acne">Acne</option>
            <option value="Hypertension">Hypertension</option>
            <option value="Digestive Disorder">Digestive Disorder</option>
            <option value="Respiratory Disorders">Respiratory Disorders</option>
            <option value="Chronic Insomnia">Chronic Insomnia</option>
          </select>
        </div>
        <div class="form-group">
          <label>Ayurvedic Intervention *</label>
          <input type="text" id="new-trial-intervention" class="form-input" placeholder="e.g. Shallaki & Guggulu Extract 500mg BD" required>
        </div>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>City / Location *</label>
          <select id="new-trial-city" class="form-select" required onchange="checkTrialOverlap()">
            <option value="Mumbai">Mumbai</option>
            <option value="Delhi">Delhi</option>
            <option value="Kolkata">Kolkata</option>
            <option value="Kerala">Kerala</option>
            <option value="Lucknow">Lucknow</option>
            <option value="Noida">Noida</option>
            <option value="Jaipur">Jaipur</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Bengaluru">Bengaluru</option>
          </select>
        </div>
        <div class="form-group">
          <label>Hospital / Clinical Site *</label>
          <input type="text" id="new-trial-hospital" class="form-input" placeholder="e.g. AIIA Partner Clinical Hospital" required>
        </div>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>Principal Investigator *</label>
          <input type="text" id="new-trial-pi" class="form-input" placeholder="e.g. Dr. Ananya Sharma" required>
        </div>
        <div class="form-group">
          <label>Target Participants *</label>
          <input type="number" id="new-trial-target" class="form-input" value="100" min="10" max="1000" required>
        </div>
        <div class="form-group">
          <label>Duration (Weeks) *</label>
          <input type="number" id="new-trial-duration" class="form-input" value="12" min="1" max="104" required>
        </div>
      </div>

      <div class="form-group">
        <label>Trial Description & Protocol Synopsis</label>
        <textarea id="new-trial-desc" class="form-textarea" placeholder="Describe the therapeutic objectives and methodology..."></textarea>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>Ethics Approval Status</label>
          <select id="new-trial-ethics" class="form-select">
            <option value="Approved">Approved</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
        <div class="form-group">
          <label>CTRI Registration Status</label>
          <select id="new-trial-ctri" class="form-select">
            <option value="Registered">Registered</option>
            <option value="Submitted">Submitted</option>
          </select>
        </div>
        <div class="form-group">
          <label>Regulatory Status (NDCT 2019)</label>
          <select id="new-trial-reg" class="form-select">
            <option value="Approved">Approved</option>
            <option value="Under Review">Under Review</option>
          </select>
        </div>
      </div>

      <div class="form-actions" style="justify-content: flex-end;">
        <button type="button" class="btn btn-ghost" onclick="closeDynamicModal()">Cancel</button>
        <button type="submit" class="btn btn-primary" id="btn-submit-trial">Save & Register Trial</button>
      </div>
    </form>
  `;

  document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  checkTrialOverlap();
}

function checkTrialOverlap() {
  const city = document.getElementById('new-trial-city').value;
  const condition = document.getElementById('new-trial-condition').value;
  const alertBox = document.getElementById('trial-overlap-alert-box');

  // Overlap simulation
  if ((city === 'Kolkata' || city === 'Mumbai') && condition === 'Arthritis') {
    alertBox.innerHTML = `
      <strong>⚠️ Potential Overlap Detected:</strong>
      <p style="margin-top: 2px;">An active ${condition} trial already exists at ${city} Site 02. You may review and continue, or assign to an alternative clinical facility.</p>
    `;
    alertBox.style.display = 'block';
  } else if (city === 'Delhi' && condition === 'Diabetes') {
    alertBox.innerHTML = `
      <strong>⚠️ Potential Overlap Detected:</strong>
      <p style="margin-top: 2px;">An active Diabetes trial (AYU-TRIAL-002) is currently ongoing at Delhi Main Campus.</p>
    `;
    alertBox.style.display = 'block';
  } else {
    alertBox.style.display = 'none';
  }
}

async function handleCreateTrialSubmit(e) {
  e.preventDefault();

  const payload = {
    trial_name: document.getElementById('new-trial-name').value.trim(),
    trial_id: document.getElementById('new-trial-id').value.trim(),
    condition: document.getElementById('new-trial-condition').value,
    intervention: document.getElementById('new-trial-intervention').value.trim(),
    city: document.getElementById('new-trial-city').value,
    hospital_name: document.getElementById('new-trial-hospital').value.trim(),
    pi_name: document.getElementById('new-trial-pi').value.trim(),
    target_participants: document.getElementById('new-trial-target').value,
    duration_weeks: document.getElementById('new-trial-duration').value,
    description: document.getElementById('new-trial-desc').value.trim(),
    ethics_approval_status: document.getElementById('new-trial-ethics').value,
    ctri_registration_status: document.getElementById('new-trial-ctri').value,
    regulatory_status: document.getElementById('new-trial-reg').value
  };

  try {
    const res = await fetch('/api/ayur/trials/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Trial ${data.trial_id} created successfully!`, 'success');
      closeDynamicModal();
      switchStaffTab('trial-info');
    } else {
      showToast('Error creating trial', 'danger');
    }
  } catch (err) {
    showToast('Network error while saving trial', 'danger');
  }
}

// ============================================================
// 8. MODULE 5: PENDING APPROVALS
// ============================================================
async function renderApprovalsView(container) {
  const res = await fetch('/api/ayur/approvals');
  const data = await res.json();
  const approvals = data.approvals || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Institutional Ethics & Regulatory Approvals</h2>
        <p>Ethics Committees (IEC), CTRI, and CDSCO/NDCT Rules 2019 review workflow</p>
      </div>
    </div>

    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Approval ID</th>
            <th>Location / Site</th>
            <th>Trial Protocol</th>
            <th>Approval Type</th>
            <th>Status</th>
            <th>Submission Date</th>
            <th>Decision Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${approvals.map(a => `
            <tr>
              <td><span class="trial-id-badge">${a.approval_id}</span></td>
              <td><strong>${a.site}</strong></td>
              <td>${a.trial_id}</td>
              <td>${a.approval_type}</td>
              <td>
                <span class="badge ${a.status === 'APPROVED' ? 'badge-success' : a.status === 'PENDING' ? 'badge-warning' : 'badge-danger'}">
                  ${a.status}
                </span>
              </td>
              <td>${a.submission_date}</td>
              <td>${a.decision_date || 'Pending Review'}</td>
              <td>
                <button class="btn btn-outline btn-xs" onclick="openApprovalDecisionModal('${a.approval_id}', '${a.site}', '${a.approval_type}', '${a.status}')">
                  Review
                </button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function openApprovalDecisionModal(approvalId, site, type, status) {
  const modalContent = document.getElementById('dynamic-modal-content');
  modalContent.innerHTML = `
    <div class="modal-header">
      <div>
        <span class="badge badge-warning">Ethics Board Review</span>
        <h3 style="margin-top: 4px; font-size: 18px;">Review Approval: ${approvalId}</h3>
      </div>
      <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
    </div>

    <div style="font-size: 13px; margin-bottom: 16px;">
      <div><strong>Site:</strong> ${site}</div>
      <div><strong>Approval Category:</strong> ${type}</div>
      <div><strong>Current Status:</strong> <span class="badge ${status === 'APPROVED' ? 'badge-success' : status === 'PENDING' ? 'badge-warning' : 'badge-danger'}">${status}</span></div>
    </div>

    <form onsubmit="handleApprovalUpdateSubmit(event, '${approvalId}')">
      <div class="form-group">
        <label>Decision *</label>
        <select id="approval-decision-val" class="form-select" required>
          <option value="APPROVED" ${status === 'APPROVED' ? 'selected' : ''}>APPROVED</option>
          <option value="PENDING" ${status === 'PENDING' ? 'selected' : ''}>PENDING</option>
          <option value="REJECTED" ${status === 'REJECTED' ? 'selected' : ''}>REJECTED / ACTION REQUIRED</option>
        </select>
      </div>

      <div class="form-group">
        <label>Reviewer Remarks & Ethics Board Notes</label>
        <textarea id="approval-notes" class="form-textarea" placeholder="Enter protocol compliance remarks or conditions..."></textarea>
      </div>

      <div class="form-actions" style="justify-content: flex-end;">
        <button type="button" class="btn btn-ghost" onclick="closeDynamicModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">Submit Decision</button>
      </div>
    </form>
  `;

  document.getElementById('dynamic-modal-overlay').style.display = 'flex';
}

async function handleApprovalUpdateSubmit(e, approvalId) {
  e.preventDefault();
  const newStatus = document.getElementById('approval-decision-val').value;
  const notes = document.getElementById('approval-notes').value.trim();

  try {
    const res = await fetch('/api/ayur/approvals/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approval_id: approvalId,
        status: newStatus,
        notes,
        reviewed_by: STATE.currentUser ? STATE.currentUser.full_name : 'Ethics Committee Officer'
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Approval ${approvalId} updated to ${newStatus}`, 'success');
      closeDynamicModal();
      switchStaffTab('approvals');
    }
  } catch (err) {
    showToast('Error updating approval', 'danger');
  }
}

// ============================================================
// 9. MODULE 6: GCP GUIDELINES COMPLIANCE CHECKLIST
// ============================================================
async function renderGCPView(container) {
  const res = await fetch('/api/ayur/gcp');
  const data = await res.json();
  const items = data.items || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Good Clinical Practice (GCP) Guidelines Checklist</h2>
        <p>Operational monitoring module for GCP & Indian ICMR/AYUSH ethical guidelines</p>
      </div>
      <div class="badge ${data.percentage >= 80 ? 'badge-success' : 'badge-warning'}" style="font-size: 13px; padding: 6px 14px;">
        ${data.overall_status}
      </div>
    </div>

    <div class="active-trials-section-card" style="margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 700; font-size: 14px;">Overall GCP Compliance Score: ${data.percentage}%</span>
        <span class="text-muted" style="font-size: 12px;">${data.completed_items} of ${data.total_items} Guidelines Verified</span>
      </div>
      <div class="progress-bar-container" style="height: 12px;">
        <div class="progress-bar-fill" style="width: ${data.percentage}%;"></div>
      </div>
    </div>

    <div style="background: #ffffff; border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 20px;">
      <h4 style="font-size: 15px; margin-bottom: 16px;">GCP Compliance Checklist Items</h4>

      <div style="display: flex; flex-direction: column; gap: 14px;">
        ${items.map(i => `
          <div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 12px; background: var(--bg-canvas); border: 1px solid var(--border-light); border-radius: var(--radius-sm);">
            <div style="display: flex; gap: 12px; align-items: flex-start;">
              <input type="checkbox" style="width: 18px; height: 18px; margin-top: 2px; accent-color: var(--ayur-primary); cursor: pointer;" ${i.is_completed ? 'checked' : ''} onchange="toggleGCPCheckbox(${i.item_id}, this.checked)">
              <div>
                <div style="font-weight: 700; font-size: 13.5px; color: var(--text-primary);">${i.title}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">${i.description}</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">
                  Category: <strong>${i.category}</strong> • Last Reviewed: <strong>${i.last_reviewed_date}</strong> • Reviewed By: <strong>${i.reviewed_by}</strong>
                </div>
              </div>
            </div>
            <span class="badge ${i.is_completed ? 'badge-success' : 'badge-warning'}">
              ${i.is_completed ? '✓ Verified' : 'Pending Review'}
            </span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

async function toggleGCPCheckbox(itemId, isChecked) {
  try {
    const res = await fetch('/api/ayur/gcp/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: itemId,
        is_completed: isChecked ? 1 : 0,
        reviewed_by: STATE.currentUser ? STATE.currentUser.full_name : 'Dr. Research Admin'
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      // Update badge
      loadInitialStaffData();
      renderGCPView(document.getElementById('staff-main-content'));
    }
  } catch (err) {
    showToast('Error updating GCP item', 'danger');
  }
}

// ============================================================
// 10. MODULE 7: DOCTOR INFORMATION
// ============================================================
async function renderDoctorsView(container) {
  const res = await fetch('/api/ayur/doctors');
  const data = await res.json();
  const doctors = data.doctors || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Registered Ayurveda Doctors & Principal Investigators</h2>
        <p>Verified clinical investigators across participating AIIA medical centers</p>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px;">
      ${doctors.map(d => `
        <div class="site-card" onclick="openDoctorProfileModal('${d.doctor_id}')">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="width: 44px; height: 44px; border-radius: 50%; background: var(--ayur-primary-subtle); color: var(--ayur-primary); font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 15px;">
              ${d.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
            <div>
              <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">${d.name}</div>
              <div style="font-size: 11.5px; color: var(--text-muted);">${d.qualification}</div>
            </div>
          </div>

          <div style="font-size: 12px; display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px;">
            <div><strong>Specialization:</strong> ${d.specialization}</div>
            <div><strong>Experience:</strong> ${d.experience_years} Years</div>
            <div><strong>Current Site:</strong> 📍 ${d.current_site}</div>
            <div><strong>Assigned Trial:</strong> <span class="trial-id-badge">${d.trial_id}</span></div>
            <div><strong>Role:</strong> ${d.role}</div>
            <div><strong>Status:</strong> <span class="badge badge-success">${d.status}</span></div>
          </div>

          <button class="btn btn-outline btn-sm btn-block" style="margin-top: auto;">
            VIEW FULL PROFILE
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

async function openDoctorProfileModal(doctorId) {
  try {
    const res = await fetch(`/api/ayur/doctors/${doctorId}`);
    const data = await res.json();
    if (!data.success) return;
    const d = data.doctor;

    const modalContent = document.getElementById('dynamic-modal-content');
    modalContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="badge badge-info">${d.role}</span>
          <h3 style="margin-top: 6px; font-size: 20px;">${d.name}</h3>
        </div>
        <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 13px; margin-bottom: 20px;">
        <div><strong>Doctor ID:</strong> ${d.doctor_id}</div>
        <div><strong>Qualification:</strong> ${d.qualification}</div>
        <div><strong>Specialization:</strong> ${d.specialization}</div>
        <div><strong>Experience:</strong> ${d.experience_years} Years</div>
        <div><strong>Current Site:</strong> ${d.current_site}</div>
        <div><strong>Assigned Trial:</strong> ${d.trial_id}</div>
        <div><strong>Email:</strong> ${d.email}</div>
        <div><strong>Phone:</strong> ${d.phone}</div>
      </div>

      <div style="background: var(--bg-canvas); padding: 12px; border-radius: 6px; border: 1px solid var(--border-light); margin-bottom: 18px;">
        <strong>Clinical Biography & Research Focus:</strong>
        <p style="margin-top: 4px; font-size: 12.5px; color: var(--text-secondary);">${d.bio || 'Principal investigator overseeing clinical trials.'}</p>
      </div>

      <div style="margin-bottom: 16px;">
        <strong style="font-size: 13px;">Assigned Patients in Active Follow-Up (${d.assigned_patients ? d.assigned_patients.length : 0})</strong>
        <div style="margin-top: 8px; max-height: 160px; overflow-y: auto;">
          ${(d.assigned_patients && d.assigned_patients.length > 0) ? d.assigned_patients.map(p => `
            <div style="display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid var(--border-light); font-size: 12px;">
              <span><strong>${p.full_name}</strong> (${p.patient_id})</span>
              <span>${p.condition} • <span class="badge badge-info">${p.treatment_status}</span></span>
            </div>
          `).join('') : '<p class="text-muted" style="font-size: 12px;">No currently assigned patients.</p>'}
        </div>
      </div>

      <div style="display: flex; justify-content: flex-end;">
        <button class="btn btn-outline" onclick="closeDynamicModal()">Close</button>
      </div>
    `;

    document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  } catch (e) {
    showToast('Could not load doctor profile', 'danger');
  }
}

// ============================================================
// 11. MODULE 8: PATIENT INFORMATION & TREATMENT TIMELINE
// ============================================================
async function renderPatientsView(container) {
  const res = await fetch('/api/ayur/patients');
  const data = await res.json();
  const patients = data.patients || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Patient Management & Clinical Roster</h2>
        <p>Registered clinical trial participants under active protocol care</p>
      </div>
    </div>

    <div class="disclaimer-banner" style="margin-bottom: 18px;">
      <div class="disclaimer-icon">🔒</div>
      <div class="disclaimer-content">
        <strong>Authorized AIIA Clinical Staff Access Only</strong>
        <p>Patient medical details and visit timelines are confidential and accessible solely to qualified researchers.</p>
      </div>
    </div>

    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Patient ID</th>
            <th>Name</th>
            <th>Age / Gender</th>
            <th>Condition</th>
            <th>Location</th>
            <th>Assigned Trial</th>
            <th>Treatment Site</th>
            <th>Assigned Doctor</th>
            <th>Treatment Status</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${patients.map(p => `
            <tr>
              <td><span class="trial-id-badge">${p.patient_id}</span></td>
              <td><strong>${p.full_name}</strong></td>
              <td>${p.age} Y / ${p.gender}</td>
              <td>${p.condition}</td>
              <td>${p.area_city}</td>
              <td><span class="trial-id-badge">${p.assigned_trial_id}</span></td>
              <td>${p.treatment_site}</td>
              <td>${p.assigned_doctor_name}</td>
              <td><span class="badge badge-info">${p.treatment_status}</span></td>
              <td><span class="badge ${p.status === 'Active' ? 'badge-success' : 'badge-neutral'}">${p.status}</span></td>
              <td>
                <button class="btn btn-outline btn-xs" onclick="openPatientProfileModal('${p.patient_id}')">Profile</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function openPatientProfileModal(patientId) {
  try {
    const res = await fetch(`/api/ayur/patients/${patientId}`);
    const data = await res.json();
    if (!data.success) return;
    const p = data.patient;
    const timeline = p.treatment_timeline || [];

    const modalContent = document.getElementById('dynamic-modal-content');
    modalContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="badge badge-info">Participant Profile</span>
          <h3 style="margin-top: 6px; font-size: 20px;">${p.full_name} (${p.patient_id})</h3>
        </div>
        <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px; margin-bottom: 20px; background: var(--bg-canvas); padding: 14px; border-radius: 6px;">
        <div><strong>Age / Gender:</strong> ${p.age} Years / ${p.gender}</div>
        <div><strong>Condition:</strong> <span style="font-weight: 700; color: var(--ayur-primary);">${p.condition}</span></div>
        <div><strong>Registered City:</strong> ${p.area_city}, ${p.state}</div>
        <div><strong>Accessible Locations:</strong> ${p.accessible_locations}</div>
        <div><strong>Assigned Trial:</strong> ${p.assigned_trial_id}</div>
        <div><strong>Assigned Doctor:</strong> ${p.assigned_doctor_name}</div>
        <div><strong>Treatment Site:</strong> ${p.treatment_site}</div>
        <div><strong>Treatment Duration:</strong> ${p.treatment_duration_weeks} Weeks</div>
        <div><strong>Dose / Regimen:</strong> ${p.dosage_frequency}</div>
        <div><strong>Scheduled Visits:</strong> ${p.scheduled_visits} Scheduled</div>
      </div>

      <!-- VISUAL 8-STAGE TREATMENT TIMELINE -->
      <h4 style="font-size: 15px; margin-bottom: 14px;">Clinical Treatment Timeline & Visit Flow</h4>
      
      <div class="treatment-timeline-wrapper">
        <div class="timeline-stages-flow">
          ${timeline.map((stage, idx) => `
            <div class="timeline-stage-item ${stage.status === 'Completed' ? 'stage-completed' : stage.status === 'In Progress' ? 'stage-current' : ''}">
              <div class="stage-icon-circle">
                ${stage.status === 'Completed' ? '✓' : idx + 1}
              </div>
              <div class="stage-content-box">
                <div class="stage-title-line">
                  <span class="stage-title">${stage.stage_title}</span>
                  <span class="badge ${stage.status === 'Completed' ? 'badge-success' : stage.status === 'In Progress' ? 'badge-info' : 'badge-neutral'}">${stage.status}</span>
                </div>
                <div style="font-size: 11.5px; color: var(--text-muted);">
                  Date: <strong>${stage.date_recorded}</strong> • Clinician: <strong>${stage.assigned_doctor_name || p.assigned_doctor_name}</strong> • Regimen: <strong>${stage.dosage_frequency || p.dosage_frequency}</strong>
                </div>
                <div class="stage-notes">${stage.notes}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      ${p.adverse_events && p.adverse_events.length > 0 ? `
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 12px; margin-top: 16px;">
          <strong style="color: #991b1b; font-size: 12.5px;">⚠️ Recorded Safety Events for this Participant:</strong>
          ${p.adverse_events.map(ae => `
            <div style="font-size: 12px; margin-top: 4px; color: #7f1d1d;">
              • <strong>${ae.adverse_event}</strong> (Severity: ${ae.severity}) - Status: ${ae.status}
            </div>
          `).join('')}
        </div>
      ` : ''}

      <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
        <button class="btn btn-outline" onclick="closeDynamicModal()">Close</button>
      </div>
    `;

    document.getElementById('dynamic-modal-overlay').style.display = 'flex';
  } catch (e) {
    showToast('Could not load patient profile', 'danger');
  }
}

// ============================================================
// 12. MODULE 9: PHARMACOVIGILANCE & SAFETY SIGNALS
// ============================================================
async function renderPVView(container) {
  const [sumRes, evRes, sigRes] = await Promise.all([
    fetch('/api/ayur/pv/summary'),
    fetch('/api/ayur/pv/events'),
    fetch('/api/ayur/pv/signals')
  ]);
  const sumData = await sumRes.json();
  const evData = await evRes.json();
  const sigData = await sigRes.json();

  const summary = sumData.summary || {};
  const events = evData.events || [];
  const signals = sigData.signals || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Pharmacovigilance & Safety Monitoring</h2>
        <p>Real-time adverse event (AE/SAE) surveillance, signal detection, and regulatory escalation</p>
      </div>
      <button class="btn btn-primary btn-sm" onclick="openReportAEModal()">+ REPORT ADVERSE EVENT</button>
    </div>

    <!-- SUMMARY CARDS -->
    <div class="sketch-kpi-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 20px;">
      <div class="sketch-kpi-card">
        <span class="kpi-card-title">Total Adverse Events</span>
        <span class="kpi-stat-number" style="margin-top: 8px;">${summary.total_adverse_events || 0}</span>
      </div>
      <div class="sketch-kpi-card">
        <span class="kpi-card-title">Serious AE (SAE)</span>
        <span class="kpi-stat-number" style="margin-top: 8px; color: #dc2626;">${summary.serious_adverse_events || 0}</span>
      </div>
      <div class="sketch-kpi-card">
        <span class="kpi-card-title">Under Investigation</span>
        <span class="kpi-stat-number" style="margin-top: 8px; color: #d97706;">${summary.under_investigation || 0}</span>
      </div>
      <div class="sketch-kpi-card">
        <span class="kpi-card-title">Resolved Cases</span>
        <span class="kpi-stat-number" style="margin-top: 8px; color: #059669;">${summary.resolved_cases || 0}</span>
      </div>
    </div>

    <!-- SAFETY SIGNAL / PATTERN DETECTION BANNER -->
    ${signals.length > 0 ? `
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; border-radius: var(--radius-md); padding: 16px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
          <span style="font-size: 20px;">⚠️</span>
          <strong style="font-size: 14px; color: #92400e;">Potential Safety Signal Detected</strong>
          <span class="badge badge-warning">Automated Signal Detection</span>
        </div>
        <p style="font-size: 13px; color: #78350f; line-height: 1.5;">
          ${signals[0].recommendation}
        </p>
      </div>
    ` : ''}

    <!-- ADVERSE EVENTS TABLE -->
    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Report ID</th>
            <th>Patient</th>
            <th>Trial</th>
            <th>Condition</th>
            <th>Location</th>
            <th>Adverse Event</th>
            <th>Severity</th>
            <th>Suspected Treatment</th>
            <th>Date Reported</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${events.map(e => `
            <tr>
              <td><span class="trial-id-badge">${e.event_id}</span></td>
              <td><strong>${e.patient_name}</strong><br><span class="text-muted" style="font-size: 11px;">${e.patient_id}</span></td>
              <td>${e.trial_id}</td>
              <td>${e.condition}</td>
              <td>${e.location}</td>
              <td><strong>${e.adverse_event}</strong></td>
              <td>
                <span class="badge ${e.severity === 'Severe' ? 'badge-danger' : e.severity === 'Moderate' ? 'badge-warning' : 'badge-info'}">
                  ${e.severity}
                </span>
              </td>
              <td>${e.suspected_treatment}</td>
              <td>${e.date_reported}</td>
              <td>
                <span class="badge ${e.status === 'Under Investigation' ? 'badge-warning' : e.status === 'Resolved' ? 'badge-success' : 'badge-neutral'}">
                  ${e.status}
                </span>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function openReportAEModal() {
  const modalContent = document.getElementById('dynamic-modal-content');
  modalContent.innerHTML = `
    <div class="modal-header">
      <div>
        <span class="badge badge-danger">Pharmacovigilance Intake</span>
        <h3 style="margin-top: 4px; font-size: 18px;">+ Report Adverse Event / Safety Incident</h3>
      </div>
      <button class="modal-close-btn" onclick="closeDynamicModal()">✕</button>
    </div>

    <form id="report-ae-form" onsubmit="handleReportAESubmit(event)">
      <div class="form-row-grid">
        <div class="form-group">
          <label>Patient ID / Name *</label>
          <input type="text" id="ae-patient-name" class="form-input" placeholder="e.g. Ramlal Sharma (AYU-PAT-001)" required>
        </div>
        <div class="form-group">
          <label>Trial ID *</label>
          <select id="ae-trial-id" class="form-select" required>
            <option value="AYU-TRIAL-002">AYU-TRIAL-002 (Diabetes • Delhi)</option>
            <option value="AYU-TRIAL-001">AYU-TRIAL-001 (Arthritis • Mumbai)</option>
            <option value="AYU-TRIAL-003">AYU-TRIAL-003 (Acne • Kolkata)</option>
            <option value="AYU-TRIAL-004">AYU-TRIAL-004 (Hypertension • Kerala)</option>
          </select>
        </div>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>Adverse Event Symptom / Diagnosis *</label>
          <input type="text" id="ae-event-title" class="form-input" placeholder="e.g. Skin Rash / Allergic reaction" required>
        </div>
        <div class="form-group">
          <label>Severity Level *</label>
          <select id="ae-severity" class="form-select" required>
            <option value="Mild">Mild</option>
            <option value="Moderate">Moderate</option>
            <option value="Severe">Severe</option>
          </select>
        </div>
        <div class="form-group">
          <label>Serious Adverse Event (SAE)? *</label>
          <select id="ae-serious" class="form-select" required>
            <option value="No">No</option>
            <option value="Yes">Yes</option>
          </select>
        </div>
      </div>

      <div class="form-row-grid">
        <div class="form-group">
          <label>Suspected Ayurvedic Treatment / Formulation *</label>
          <input type="text" id="ae-treatment" class="form-input" placeholder="e.g. Ayurvedic Formulation Nisha Amalaki" required>
        </div>
        <div class="form-group">
          <label>Location *</label>
          <input type="text" id="ae-location" class="form-input" value="Delhi" required>
        </div>
      </div>

      <div class="form-group">
        <label>Description & Action Taken</label>
        <textarea id="ae-desc" class="form-textarea" placeholder="Detail clinical presentation, supportive therapy administered, and patient outcome..."></textarea>
      </div>

      <div class="form-actions" style="justify-content: flex-end;">
        <button type="button" class="btn btn-ghost" onclick="closeDynamicModal()">Cancel</button>
        <button type="submit" class="btn btn-primary" id="btn-submit-ae">Submit Safety Report</button>
      </div>
    </form>
  `;

  document.getElementById('dynamic-modal-overlay').style.display = 'flex';
}

async function handleReportAESubmit(e) {
  e.preventDefault();

  const payload = {
    patient_name: document.getElementById('ae-patient-name').value.trim(),
    trial_id: document.getElementById('ae-trial-id').value,
    adverse_event: document.getElementById('ae-event-title').value.trim(),
    severity: document.getElementById('ae-severity').value,
    serious: document.getElementById('ae-serious').value,
    suspected_treatment: document.getElementById('ae-treatment').value.trim(),
    location: document.getElementById('ae-location').value.trim(),
    action_taken: document.getElementById('ae-desc').value.trim(),
    reported_by: STATE.currentUser ? STATE.currentUser.full_name : 'Dr. Research Admin'
  };

  try {
    const res = await fetch('/api/ayur/pv/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast('Adverse event reported successfully!', 'success');
      closeDynamicModal();
      switchStaffTab('pv');
    }
  } catch (err) {
    showToast('Error filing safety report', 'danger');
  }
}

// ============================================================
// 13. MODULE 10: REPORTS
// ============================================================
async function renderReportsView(container) {
  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Clinical Trial & Governance Reports</h2>
        <p>Institutional summaries for AIIA Leadership, Ethics Committees, and Regulators</p>
      </div>
    </div>

    <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
      <button class="btn btn-outline btn-sm active" onclick="loadReportType('trial_progress', this)">1. Trial Progress</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('patient_enrollment', this)">2. Patient Enrollment</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('site_performance', this)">3. Site Performance</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('doctor_participation', this)">4. Doctor Participation</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('adverse_event', this)">5. Adverse Events</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('pending_approval', this)">6. Approvals</button>
      <button class="btn btn-outline btn-sm" onclick="loadReportType('gcp_compliance', this)">7. GCP Compliance</button>
    </div>

    <div id="report-content-area">
      <!-- Injected report table -->
    </div>
  `;

  loadReportType('trial_progress');
}

async function loadReportType(type, btnEl) {
  if (btnEl) {
    document.querySelectorAll('#staff-main-content .btn-sm').forEach(b => b.classList.remove('btn-primary'));
    btnEl.classList.add('btn-primary');
  }

  const area = document.getElementById('report-content-area');
  area.innerHTML = '<div style="padding: 30px; text-align:center;"><div class="badge badge-info">Generating Institutional Report...</div></div>';

  try {
    const res = await fetch(`/api/ayur/reports?type=${type}`);
    const data = await res.json();

    const cols = data.columns || [];
    const rows = data.rows || [];

    area.innerHTML = `
      <div class="active-trials-section-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div>
            <h4 style="font-size: 16px;">${data.report_title}</h4>
            <span class="text-muted" style="font-size: 11.5px;">Generated: ${data.generated_at} • Institution: ${data.institution}</span>
          </div>
          <div style="display: flex; gap: 10px;">
            <a href="/api/ayur/reports/export?type=${type}&format=csv" class="btn btn-outline btn-sm">
              📥 EXPORT CSV
            </a>
            <button class="btn btn-primary btn-sm" onclick="window.print()">
              🖨️ PRINT / PDF
            </button>
          </div>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                ${cols.map(c => `<th>${c}</th>`).join('')}
              </tr>
            </thead>
            <tbody>
              ${rows.map(r => `
                <tr>
                  ${cols.map(c => `<td>${r[c] !== undefined ? r[c] : ''}</td>`).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (e) {
    area.innerHTML = '<div style="color: red; padding: 20px;">Could not generate report.</div>';
  }
}

// ============================================================
// 14. MODULE 11: INTEROPERABILITY & AUDIT TRAIL
// ============================================================
async function renderInteropView(container) {
  const [interopRes, auditRes] = await Promise.all([
    fetch('/api/ayur/interop/demo'),
    fetch('/api/ayur/audit')
  ]);
  const interopData = await interopRes.json();
  const auditData = await auditRes.json();

  const auditEvents = auditData.audit_trail || [];

  container.innerHTML = `
    <div class="view-header-bar">
      <div class="view-title-group">
        <h2>Data Interoperability & Audit Trail</h2>
        <p>CDISC SDTM/ADaM mapping pipeline, HL7 FHIR ResearchStudy transformation, and immutable audit logs</p>
      </div>
    </div>

    <!-- PIPELINE VISUALIZATION -->
    <div class="active-trials-section-card" style="margin-bottom: 24px;">
      <div class="section-card-header">
        <span class="section-card-title">Visual Clinical Data Standards Pipeline</span>
        <span class="badge badge-info">Prototype Interoperability Demonstration</span>
      </div>

      <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 20px 0; text-align: center; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 140px; background: var(--bg-canvas); padding: 14px; border-radius: 8px; border: 1px solid var(--border-light);">
          <div style="font-size: 20px;">🏥</div>
          <strong style="font-size: 13px;">Hospital Data</strong>
          <div style="font-size: 11px; color: var(--text-muted);">AIIA EHR & Case Records</div>
        </div>
        <span style="font-size: 20px; color: var(--ayur-primary);">➔</span>
        
        <div style="flex: 1; min-width: 140px; background: var(--bg-canvas); padding: 14px; border-radius: 8px; border: 1px solid var(--border-light);">
          <div style="font-size: 20px;">🧬</div>
          <strong style="font-size: 13px;">FHIR Resource</strong>
          <div style="font-size: 11px; color: var(--text-muted);">HL7 FHIR R4 ResearchStudy</div>
        </div>
        <span style="font-size: 20px; color: var(--ayur-primary);">➔</span>

        <div style="flex: 1; min-width: 140px; background: var(--bg-canvas); padding: 14px; border-radius: 8px; border: 1px solid var(--border-light);">
          <div style="font-size: 20px;">⚙️</div>
          <strong style="font-size: 13px;">Mapping Layer</strong>
          <div style="font-size: 11px; color: var(--text-muted);">Semantic Concept Aligners</div>
        </div>
        <span style="font-size: 20px; color: var(--ayur-primary);">➔</span>

        <div style="flex: 1; min-width: 140px; background: var(--bg-canvas); padding: 14px; border-radius: 8px; border: 1px solid var(--border-light);">
          <div style="font-size: 20px;">📊</div>
          <strong style="font-size: 13px;">CDISC Dataset</strong>
          <div style="font-size: 11px; color: var(--text-muted);">SDTM TS / DM / AE Domains</div>
        </div>
      </div>
    </div>

    <!-- FHIR & CDISC PREVIEWS -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
      <div class="active-trials-section-card">
        <h4 style="font-size: 14px; margin-bottom: 10px;">HL7 FHIR R4 ResearchStudy JSON Preview</h4>
        <pre style="background: #1e293b; color: #38bdf8; padding: 14px; border-radius: 6px; font-size: 11px; max-height: 240px; overflow: auto;">${JSON.stringify(interopData.fhir_preview, null, 2)}</pre>
      </div>

      <div class="active-trials-section-card">
        <h4 style="font-size: 14px; margin-bottom: 10px;">CDISC SDTM Dataset Preview (TS/DM)</h4>
        <pre style="background: #1e293b; color: #4ade80; padding: 14px; border-radius: 6px; font-size: 11px; max-height: 240px; overflow: auto;">${JSON.stringify(interopData.cdisc_preview, null, 2)}</pre>
      </div>
    </div>

    <!-- IMMUTABLE AUDIT TRAIL -->
    <div class="active-trials-section-card">
      <div class="section-card-header">
        <span class="section-card-title">Immutable System Audit Trail & Traceability</span>
        <span class="badge badge-success">GCP Traceability</span>
      </div>

      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Audit ID</th>
              <th>User</th>
              <th>Action</th>
              <th>Module</th>
              <th>Previous Value</th>
              <th>New Value</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            ${auditEvents.map(a => `
              <tr>
                <td><span class="trial-id-badge">${a.audit_id}</span></td>
                <td><strong>${a.user_name}</strong></td>
                <td>${a.action}</td>
                <td><span class="badge badge-neutral">${a.module}</span></td>
                <td style="color: var(--text-muted); font-size: 11.5px;">${a.previous_value}</td>
                <td style="font-weight: 600; font-size: 11.5px;">${a.new_value}</td>
                <td style="font-size: 11.5px; white-space: nowrap;">${a.created_at}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ============================================================
// 15. GLOBAL SEARCH HANDLER
// ============================================================
let searchDebounceTimeout = null;

function handleGlobalSearch(query) {
  clearTimeout(searchDebounceTimeout);
  const dropdown = document.getElementById('global-search-dropdown');

  if (!query || query.trim().length < 2) {
    dropdown.style.display = 'none';
    return;
  }

  searchDebounceTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`/api/ayur/search?q=${encodeURIComponent(query.trim())}`);
      const data = await res.json();
      const results = data.results || {};

      const patients = results.patients || [];
      const doctors = results.doctors || [];
      const trials = results.trials || [];
      const sites = results.sites || [];

      const totalMatches = patients.length + doctors.length + trials.length + sites.length;

      if (totalMatches === 0) {
        dropdown.innerHTML = '<div style="padding: 12px; font-size: 12px; color: var(--text-muted); text-align:center;">No matching clinical records found.</div>';
        dropdown.style.display = 'block';
        return;
      }

      let html = '';

      if (patients.length > 0) {
        html += `
          <div class="search-category-group">
            <div class="search-cat-title">Patients (${patients.length})</div>
            ${patients.map(p => `
              <div class="search-result-item" onclick="openPatientProfileModal('${p.patient_id}'); closeSearchDropdown();">
                <span>👤 <strong>${p.full_name}</strong> (${p.patient_id})</span>
                <span class="badge badge-info">${p.condition} • ${p.area_city}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      if (doctors.length > 0) {
        html += `
          <div class="search-category-group">
            <div class="search-cat-title">Doctors (${doctors.length})</div>
            ${doctors.map(d => `
              <div class="search-result-item" onclick="openDoctorProfileModal('${d.doctor_id}'); closeSearchDropdown();">
                <span>👨‍⚕️ <strong>${d.name}</strong> (${d.specialization})</span>
                <span class="badge badge-neutral">${d.current_site}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      if (trials.length > 0) {
        html += `
          <div class="search-category-group">
            <div class="search-cat-title">Trials (${trials.length})</div>
            ${trials.map(t => `
              <div class="search-result-item" onclick="openStaffTrialDetailModal('${t.trial_id}'); closeSearchDropdown();">
                <span>🔬 <strong>${t.trial_id}</strong>: ${t.trial_name}</span>
                <span class="badge badge-success">${t.city}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      if (sites.length > 0) {
        html += `
          <div class="search-category-group">
            <div class="search-cat-title">Sites (${sites.length})</div>
            ${sites.map(s => `
              <div class="search-result-item" onclick="openSiteDetailModal('${s.city}'); closeSearchDropdown();">
                <span>📍 <strong>${s.city}</strong> (${s.hospital_name})</span>
                <span class="badge badge-info">${s.condition}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.style.display = 'block';
    } catch (e) {
      console.error(e);
    }
  }, 250);
}

function closeSearchDropdown() {
  const dropdown = document.getElementById('global-search-dropdown');
  if (dropdown) dropdown.style.display = 'none';
  const input = document.getElementById('global-search-input');
  if (input) input.value = '';
}

// Close search dropdown on outside click
document.addEventListener('click', (e) => {
  if (!e.target.closest('.global-search-container')) {
    closeSearchDropdown();
  }
  if (!e.target.closest('.notification-wrapper')) {
    const drawer = document.getElementById('notifications-drawer');
    if (drawer) drawer.style.display = 'none';
  }
});

// ============================================================
// 16. MODAL SYSTEM HELPERS
// ============================================================
function closeDynamicModal() {
  document.getElementById('dynamic-modal-overlay').style.display = 'none';
}

function handleModalBackdropClick(e) {
  if (e.target.id === 'dynamic-modal-overlay') {
    closeDynamicModal();
  }
}
