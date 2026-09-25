import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { AlertTriangle, Plus, ShieldAlert, CheckCircle, X, Search, FileDown } from 'lucide-react';

export default function PharmacovigilanceView({ currentUser }) {
  const [summary, setSummary] = useState({});
  const [events, setEvents] = useState([]);
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const [aeForm, setAeForm] = useState({
    patient_name: '',
    trial_id: 'AYU-TRIAL-002',
    condition: 'Diabetes',
    location: 'Delhi',
    adverse_event: '',
    severity: 'Mild',
    suspected_treatment: 'Ashwagandha Capsule 500mg',
    action_taken: 'Dose held temporarily, symptomatic antihistamine prescribed.',
    outcome: 'Recovering',
    status: 'Under Investigation',
  });

  const loadPvData = async () => {
    try {
      setLoading(true);
      const [sumRes, evRes, sigRes] = await Promise.all([
        api.getPvSummary(),
        api.getAdverseEvents(),
        api.getSafetySignals(),
      ]);
      setSummary(sumRes.summary || {});
      setEvents(evRes.events || []);
      setSignals(sigRes.signals || []);
    } catch (err) {
      setError(err.message || 'Failed to load pharmacovigilance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPvData();
  }, []);

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.reportAdverseEvent({
        ...aeForm,
        reported_by: currentUser?.full_name || 'Dr. Clinical Pharmacologist',
      });
      if (res.success) {
        setToast({ type: 'success', text: `Adverse event reported successfully!` });
        setShowReportModal(false);
        setAeForm({
          patient_name: '',
          trial_id: 'AYU-TRIAL-002',
          condition: 'Diabetes',
          location: 'Delhi',
          adverse_event: '',
          severity: 'Mild',
          suspected_treatment: 'Ashwagandha Capsule 500mg',
          action_taken: '',
          outcome: 'Recovering',
          status: 'Under Investigation',
        });
        await loadPvData();
      }
    } catch (err) {
      setToast({ type: 'error', text: err.message || 'Failed to report event' });
    } finally {
      setSubmitting(false);
      setTimeout(() => setToast(null), 4000);
    }
  };

  return (
    <div className="pv-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Pharmacovigilance & Safety Monitoring</h2>
          <p>Real-time adverse event (AE/SAE) surveillance, signal detection, and regulatory escalation</p>
        </div>
        <button
          className="btn btn-primary btn-sm flex items-center gap-1"
          onClick={() => setShowReportModal(true)}
        >
          <Plus size={14} />
          <span>+ REPORT ADVERSE EVENT</span>
        </button>
      </div>

      {toast && (
        <div
          className={`p-3 rounded text-xs mb-4 ${
            toast.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border border-emerald-300'
              : 'bg-rose-50 text-rose-900 border border-rose-300'
          }`}
        >
          {toast.text}
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="sketch-kpi-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '20px' }}>
        <div className="sketch-kpi-card">
          <span className="kpi-card-title">Total Adverse Events</span>
          <span className="kpi-stat-number" style={{ marginTop: '8px' }}>
            {summary.total_adverse_events || 0}
          </span>
        </div>
        <div className="sketch-kpi-card">
          <span className="kpi-card-title">Serious AE (SAE)</span>
          <span className="kpi-stat-number" style={{ marginTop: '8px', color: '#dc2626' }}>
            {summary.serious_adverse_events || 0}
          </span>
        </div>
        <div className="sketch-kpi-card">
          <span className="kpi-card-title">Under Investigation</span>
          <span className="kpi-stat-number" style={{ marginTop: '8px', color: '#d97706' }}>
            {summary.under_investigation || 0}
          </span>
        </div>
        <div className="sketch-kpi-card">
          <span className="kpi-card-title">Resolved Cases</span>
          <span className="kpi-stat-number" style={{ marginTop: '8px', color: '#059669' }}>
            {summary.resolved_cases || 0}
          </span>
        </div>
      </div>

      {/* SAFETY SIGNAL / PATTERN DETECTION BANNER */}
      {signals.length > 0 && (
        <div className="bg-amber-50 border border-amber-300 border-l-4 border-l-amber-500 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-1.5">
            <AlertTriangle className="text-amber-600" size={20} />
            <strong className="text-amber-900 text-sm">Potential Safety Signal Detected</strong>
            <span className="badge badge-warning text-[10px]">Automated Signal Detection</span>
          </div>
          <p className="text-xs text-amber-900 leading-relaxed">
            {signals[0].recommendation ||
              'Multiple localized rash events observed in AYU-002 (Ashwagandha formulation). Cluster evaluation recommended by Data Safety Monitoring Board (DSMB).'}
          </p>
        </div>
      )}

      {/* Adverse Events Table */}
      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading adverse events registry...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div className="table-responsive bg-white rounded-lg border shadow-xs">
          <table className="data-table">
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
              {events.map((e) => (
                <tr key={e.event_id}>
                  <td>
                    <span className="trial-id-badge">{e.event_id}</span>
                  </td>
                  <td>
                    <strong>{e.patient_name}</strong>
                    <br />
                    <span className="text-muted" style={{ fontSize: '11px' }}>
                      {e.patient_id}
                    </span>
                  </td>
                  <td>{e.trial_id}</td>
                  <td>{e.condition}</td>
                  <td>{e.location}</td>
                  <td>
                    <strong>{e.adverse_event}</strong>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        e.severity === 'Severe'
                          ? 'badge-danger'
                          : e.severity === 'Moderate'
                          ? 'badge-warning'
                          : 'badge-info'
                      }`}
                    >
                      {e.severity}
                    </span>
                  </td>
                  <td>{e.suspected_treatment}</td>
                  <td>{e.date_reported}</td>
                  <td>
                    <span
                      className={`badge ${
                        e.status === 'Under Investigation'
                          ? 'badge-warning'
                          : e.status === 'Resolved'
                          ? 'badge-success'
                          : 'badge-neutral'
                      }`}
                    >
                      {e.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Report AE Modal */}
      {showReportModal && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="badge badge-danger text-xs">Pharmacovigilance Intake</span>
                <h3 className="text-lg font-bold text-slate-900 mt-1">
                  + Report Adverse Event / Safety Incident
                </h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setShowReportModal(false)}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleReportSubmit} className="space-y-3 text-xs">
              <div className="form-row-grid">
                <div className="form-group">
                  <label className="font-semibold">Patient Name / ID *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Ramlal Sharma (AYU-PAT-001)"
                    value={aeForm.patient_name}
                    onChange={(e) => setAeForm({ ...aeForm, patient_name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="font-semibold">Trial Protocol *</label>
                  <select
                    className="form-select"
                    value={aeForm.trial_id}
                    onChange={(e) => setAeForm({ ...aeForm, trial_id: e.target.value })}
                    required
                  >
                    <option value="AYU-TRIAL-002">AYU-TRIAL-002 (Diabetes • Delhi)</option>
                    <option value="AYU-TRIAL-001">AYU-TRIAL-001 (Arthritis • Mumbai)</option>
                    <option value="AYU-TRIAL-003">AYU-TRIAL-003 (Acne • Kolkata)</option>
                    <option value="AYU-TRIAL-004">AYU-TRIAL-004 (Hypertension • Kerala)</option>
                  </select>
                </div>
              </div>

              <div className="form-row-grid">
                <div className="form-group">
                  <label className="font-semibold">Adverse Event Symptom *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Mild Pruritic Erythematous Skin Rash"
                    value={aeForm.adverse_event}
                    onChange={(e) => setAeForm({ ...aeForm, adverse_event: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="font-semibold">Severity Grade *</label>
                  <select
                    className="form-select"
                    value={aeForm.severity}
                    onChange={(e) => setAeForm({ ...aeForm, severity: e.target.value })}
                    required
                  >
                    <option value="Mild">Mild (Grade 1)</option>
                    <option value="Moderate">Moderate (Grade 2)</option>
                    <option value="Severe">Severe (Grade 3 - SAE)</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="font-semibold">Suspected Herbal / Botanical Formulation</label>
                <input
                  type="text"
                  className="form-input"
                  value={aeForm.suspected_treatment}
                  onChange={(e) => setAeForm({ ...aeForm, suspected_treatment: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="font-semibold">Clinical Action Taken & Management</label>
                <textarea
                  className="form-textarea"
                  rows={2}
                  value={aeForm.action_taken}
                  onChange={(e) => setAeForm({ ...aeForm, action_taken: e.target.value })}
                  placeholder="e.g. Discontinued formulation, prescribed antihistamine..."
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t">
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setShowReportModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit Safety Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
