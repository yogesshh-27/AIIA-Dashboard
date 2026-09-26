// Centralized API client for AYURCTMS backend
const RAW_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
let activeBaseUrl = localStorage.getItem('ayurctms_active_api_url') || RAW_URL;

// Auto-fallback candidates across standard Render domains to prevent 404s/timeouts
const CANDIDATES = [
  activeBaseUrl,
  RAW_URL,
  'https://aiia-dashboard.onrender.com',
  'https://aiia-dashboard-api.onrender.com',
  ''
].filter((val, idx, arr) => val !== undefined && arr.indexOf(val) === idx);

async function fetchJSON(url, options = {}) {
  let lastErr = null;
  for (const base of CANDIDATES) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 12000);
      const res = await fetch(`${base}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {}),
        },
        signal: controller.signal,
        ...options,
      });
      clearTimeout(timer);

      if (res.status === 404 && base) {
        // Subdomain mismatch or not found, proceed to next candidate
        continue;
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        throw new Error(err.message || err.error || `HTTP ${res.status}`);
      }

      if (base !== activeBaseUrl) {
        activeBaseUrl = base;
        try { localStorage.setItem('ayurctms_active_api_url', base); } catch {}
      }
      return await res.json();
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error('Backend server is waking up or temporarily unreachable.');
}

export const api = {
  // Auth
  loginStaff: (staff_id, password) =>
    fetchJSON('/api/ayur/auth/login', {
      method: 'POST',
      body: JSON.stringify({ staff_id, password }),
    }),

  // Patient Matching
  matchPatientTrial: (criteria) =>
    fetchJSON('/api/ayur/patient/match', {
      method: 'POST',
      body: JSON.stringify(criteria),
    }),

  // Dashboard Stats
  getDashboardStats: () => fetchJSON('/api/ayur/dashboard/stats'),

  // Sites
  getSites: () => fetchJSON('/api/ayur/sites'),
  getSiteDetail: (city) => fetchJSON(`/api/ayur/sites/${encodeURIComponent(city)}`),

  // Trials
  getTrials: () => fetchJSON('/api/ayur/trials'),
  createTrial: (trialData) =>
    fetchJSON('/api/ayur/trials/create', {
      method: 'POST',
      body: JSON.stringify(trialData),
    }),

  // Doctors
  getDoctors: () => fetchJSON('/api/ayur/doctors'),
  getDoctorDetail: (id) => fetchJSON(`/api/ayur/doctors/${id}`),

  // Patients
  getPatients: () => fetchJSON('/api/ayur/patients'),
  getPatientDetail: (id) => fetchJSON(`/api/ayur/patients/${id}`),

  // Pharmacovigilance
  getPvSummary: () => fetchJSON('/api/ayur/pv/summary'),
  getSafetySignals: () => fetchJSON('/api/ayur/pv/signals'),
  getAdverseEvents: () => fetchJSON('/api/ayur/pv/events'),
  reportAdverseEvent: (aeData) =>
    fetchJSON('/api/ayur/pv/report', {
      method: 'POST',
      body: JSON.stringify(aeData),
    }),

  // Approvals & Governance
  getApprovals: () => fetchJSON('/api/ayur/approvals'),
  updateApproval: (data) =>
    fetchJSON('/api/ayur/approvals/update', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // GCP Checklist
  getGcpChecklist: () => fetchJSON('/api/ayur/gcp'),
  toggleGcpItem: (data) =>
    fetchJSON('/api/ayur/gcp/toggle', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Reports
  getReportData: (type = 'trial_progress') =>
    fetchJSON(`/api/ayur/reports?type=${type}`),

  // Global Search
  globalSearch: (query) =>
    fetchJSON(`/api/ayur/search?q=${encodeURIComponent(query)}`),

  // Interoperability (FHIR & CDISC)
  getInteropDemo: () => fetchJSON('/api/ayur/interop/demo'),

  // 21 CFR Part 11 Electronic Signatures
  executeEsignature: (data) =>
    fetchJSON('/api/audit/esign', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  verifyEsignature: (sigId) => fetchJSON(`/api/audit/esign/verify/${sigId}`),
  getRecordSignature: (type, id) => fetchJSON(`/api/audit/esign/record/${type}/${id}`),

  // CTRI Extractor Registry Dataset
  getCTRIExtractorTrials: () => fetchJSON('/api/ctri-extractor/trials?limit=100'),

  // Audit Trail
  getAuditTrail: () => fetchJSON('/api/ayur/audit'),
};
