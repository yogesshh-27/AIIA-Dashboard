// Centralized API client for AYURCTMS backend
const BASE_URL = '';

async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      throw new Error(err.message || err.error || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API call failed for ${url}:`, error);
    throw error;
  }
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

  // CTRI Extractor Registry Dataset
  getCTRIExtractorTrials: () => fetchJSON('/api/ctri-extractor/trials?limit=100'),

  // Audit Trail
  getAuditTrail: () => fetchJSON('/api/ayur/audit'),
};
