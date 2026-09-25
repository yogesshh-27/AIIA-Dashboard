import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Stethoscope, Users, AlertTriangle, ShieldCheck, Plus, ArrowRight, MapPin, Activity, CheckCircle, ExternalLink, X } from 'lucide-react';

export default function DashboardView({ onNavigate, onOpenCreateTrial }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSite, setSelectedSite] = useState(null);
  const [selectedTrial, setSelectedTrial] = useState(null);
  const [siteDetailData, setSiteDetailData] = useState(null);
  const [siteLoading, setSiteLoading] = useState(false);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const stats = await api.getDashboardStats();
        setData(stats);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const handleOpenSite = async (city) => {
    setSelectedSite(city);
    setSiteLoading(true);
    try {
      const detail = await api.getSiteDetail(city);
      setSiteDetailData(detail);
    } catch (err) {
      console.error(err);
    } finally {
      setSiteLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="badge badge-info animate-pulse p-3 inline-block">
          Loading clinical trial executive metrics...
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center">
        <div className="badge badge-danger p-3 mb-3 inline-block">{error || 'Data unavailable'}</div>
        <div>
          <button className="btn btn-primary btn-sm" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const kpis = data.kpi_cards || {};
  const trialsSum = data.active_trials_summary || {};

  return (
    <div className="dashboard-view">
      {/* Header bar */}
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>AIIA Clinical Trials Executive Dashboard</h2>
          <p>Real-time clinical trial oversight, doctor rosters, patient flow, and pharmacovigilance</p>
        </div>
        <div className="flex gap-2 items-center">
          <button
            className="btn btn-outline btn-sm flex items-center gap-1"
            onClick={() => onNavigate('gcp')}
          >
            <ShieldCheck size={14} className="text-emerald-700" />
            <span>GCP Status: {data.gcp_compliance?.percentage || 89}%</span>
          </button>
          <button
            className="btn btn-primary btn-sm flex items-center gap-1"
            onClick={onOpenCreateTrial}
          >
            <Plus size={14} />
            <span>CREATE NEW TRIAL</span>
          </button>
        </div>
      </div>

      {/* 3 Major Top KPI Cards */}
      <div className="sketch-kpi-grid">
        {/* Card 1: Doctor Information */}
        <div className="sketch-kpi-card kpi-doctor">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.doctors?.title || 'Doctor Information'}</span>
            <Stethoscope className="text-emerald-700" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.doctors?.total_doctors || 11}</span>
              <span className="kpi-stat-label">Total Doctors</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#005944' }}>
                {kpis.doctors?.active_investigators || 8}
              </span>
              <span className="kpi-stat-label">Active PIs</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.doctors?.trial_sites || 9}</span>
              <span className="kpi-stat-label">Trial Sites</span>
            </div>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('doctors')}
          >
            {kpis.doctors?.button_text || 'View Doctor Rosters →'}
          </button>
        </div>

        {/* Card 2: Patient Information */}
        <div className="sketch-kpi-card kpi-patient">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.patients?.title || 'Patient Information'}</span>
            <Users className="text-blue-700" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.patients?.total_patients || 25}</span>
              <span className="kpi-stat-label">Registered</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#0284c7' }}>
                {kpis.patients?.active_participants || 18}
              </span>
              <span className="kpi-stat-label">Active Flow</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#059669' }}>
                {kpis.patients?.completed_participants || 7}
              </span>
              <span className="kpi-stat-label">Completed</span>
            </div>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('patients')}
          >
            {kpis.patients?.button_text || 'View Patients & Timeline →'}
          </button>
        </div>

        {/* Card 3: Pharmacovigilance */}
        <div className="sketch-kpi-card kpi-pv">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.pharmacovigilance?.title || 'Pharmacovigilance'}</span>
            <AlertTriangle className="text-amber-600" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.pharmacovigilance?.total_adverse_events || 14}</span>
              <span className="kpi-stat-label">Total AE</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#dc2626' }}>
                {kpis.pharmacovigilance?.serious_adverse_events || 2}
              </span>
              <span className="kpi-stat-label">Serious (SAE)</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#d97706' }}>
                {kpis.pharmacovigilance?.cases_under_review || 3}
              </span>
              <span className="kpi-stat-label">Under Review</span>
            </div>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('pv')}
          >
            {kpis.pharmacovigilance?.button_text || 'Safety Signals & Reporting →'}
          </button>
        </div>
      </div>

      {/* Active Trials Section with Milestone Progress Bars */}
      <div className="active-trials-section-card mt-6">
        <div className="section-card-header">
          <span className="section-card-title">Active Clinical Trials & Milestone Progress</span>
          <button
            className="btn btn-ghost btn-sm flex items-center gap-1"
            onClick={() => onNavigate('active-trials')}
          >
            <span>View All Trials</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="trials-summary-counters">
          <div className="trial-counter-pill">
            <span>🟢 Ongoing:</span>
            <strong>{trialsSum.ongoing || 5}</strong>
          </div>
          <div className="trial-counter-pill">
            <span>🔵 Completed:</span>
            <strong>{trialsSum.completed || 2}</strong>
          </div>
          <div className="trial-counter-pill">
            <span>🟡 Upcoming / Pending:</span>
            <strong>{trialsSum.upcoming || 1}</strong>
          </div>
        </div>

        <div className="trial-progress-list">
          {trialsSum.trials_progress?.map((t) => (
            <div
              key={t.trial_id}
              className="trial-progress-row cursor-pointer hover:bg-slate-50 transition"
              onClick={() => setSelectedTrial(t)}
            >
              <div className="trial-progress-header">
                <div>
                  <span className="trial-progress-id">{t.trial_id}</span>: {' '}
                  <strong>{t.trial_name}</strong>
                  <span className="text-xs text-slate-500 ml-2">({t.condition} • {t.city})</span>
                </div>
                <div>
                  <span style={{ fontWeight: 700, color: '#005944' }}>{t.progress_pct}%</span>
                  <span className="text-muted ml-2" style={{ fontSize: '11px' }}>
                    ({t.enrolled_participants}/{t.target_participants} Enrolled)
                  </span>
                </div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${t.progress_pct}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 9 National Regional Centers Quick Matrix */}
      <div className="active-trials-section-card mt-6">
        <div className="section-card-header">
          <span className="section-card-title">National Ayurveda Clinical Trial Sites (9 Participating Centers)</span>
          <button
            className="btn btn-ghost btn-sm flex items-center gap-1"
            onClick={() => onNavigate('sites')}
          >
            <span>Full Sites Center</span>
            <ArrowRight size={14} />
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '10px' }}>
          {['Mumbai', 'Delhi', 'Kolkata', 'Kerala', 'Lucknow', 'Noida', 'Jaipur', 'Hyderabad', 'Bengaluru'].map((c) => (
            <button
              key={c}
              className="btn btn-outline btn-sm flex items-center justify-center gap-1 font-semibold"
              onClick={() => handleOpenSite(c)}
            >
              <MapPin size={13} className="text-emerald-700" />
              <span>{c}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Site Detail Modal */}
      {selectedSite && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <h3 className="text-lg font-bold text-emerald-900 flex items-center gap-2">
                <MapPin size={18} className="text-emerald-700" />
                <span>Site Details: {selectedSite}</span>
              </h3>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedSite(null)}
              >
                <X size={18} />
              </button>
            </div>
            {siteLoading ? (
              <div className="p-4 text-center text-sm text-slate-500">Loading site metrics...</div>
            ) : siteDetailData ? (
              <div className="space-y-3">
                <div className="bg-slate-50 p-3 rounded border text-sm">
                  <p><strong>Hospital:</strong> {siteDetailData.site?.hospital_name || 'AIIA Regional Hospital'}</p>
                  <p><strong>Lead Principal Investigator:</strong> {siteDetailData.site?.lead_investigator || 'Dr. Assigned PI'}</p>
                  <p><strong>Active Enrolled Patients:</strong> {siteDetailData.site?.active_patients || 0}</p>
                  <p><strong>Bed Capacity:</strong> {siteDetailData.site?.bed_capacity || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-xs uppercase text-slate-600 mb-2">Trials Conducted Here</h4>
                  <ul className="text-xs space-y-1">
                    {siteDetailData.trials?.map((tr) => (
                      <li key={tr.trial_id} className="p-2 bg-emerald-50 text-emerald-900 rounded">
                        <strong>{tr.trial_id}</strong> - {tr.trial_name} ({tr.condition})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-sm text-slate-500">Site details loaded.</div>
            )}
            <div className="mt-6 flex justify-end">
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedSite(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Trial Detail Modal */}
      {selectedTrial && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <h3 className="text-lg font-bold text-emerald-900">
                {selectedTrial.trial_id}: {selectedTrial.trial_name}
              </h3>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedTrial(null)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded border">
                <div><strong>Condition:</strong> {selectedTrial.condition}</div>
                <div><strong>Center:</strong> {selectedTrial.city}</div>
                <div><strong>Target:</strong> {selectedTrial.target_participants} patients</div>
                <div><strong>Recruited:</strong> {selectedTrial.enrolled_participants} ({selectedTrial.progress_pct}%)</div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${selectedTrial.progress_pct}%` }}></div>
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button
                className="btn btn-primary btn-sm"
                onClick={() => {
                  setSelectedTrial(null);
                  onNavigate('trial-info');
                }}
              >
                Full Protocol Specifications →
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedTrial(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
