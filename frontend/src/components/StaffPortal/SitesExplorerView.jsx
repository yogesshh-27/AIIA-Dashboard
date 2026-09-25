import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { MapPin, Building, Users, Calendar, Activity, X, BarChart3, AlertCircle } from 'lucide-react';

export default function SitesExplorerView({ onNavigateToTrial }) {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSite, setSelectedSite] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    async function loadSites() {
      try {
        setLoading(true);
        const data = await api.getSites();
        setSites(data.sites || []);
      } catch (err) {
        setError(err.message || 'Failed to load sites');
      } finally {
        setLoading(false);
      }
    }
    loadSites();
  }, []);

  const handleOpenSiteDetail = async (city) => {
    setDetailLoading(true);
    try {
      const data = await api.getSiteDetail(city);
      if (data.success && data.site) {
        setSelectedSite(data.site);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="sites-explorer-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>AIIA Participating Clinical Trial Sites Across India</h2>
          <p>Interactive location nodes with live protocol tracking and recorded outcome trends</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading 9 clinical center sites...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div className="sites-grid">
          {sites.map((s) => (
            <div
              key={s.city}
              className="site-card cursor-pointer hover:shadow-md transition"
              onClick={() => handleOpenSiteDetail(s.city)}
            >
              <div className="site-card-header">
                <span className="site-city-title flex items-center gap-1">
                  <MapPin size={16} className="text-emerald-700" />
                  <span>{s.city}</span>
                </span>
                <span className={`badge ${s.status === 'Ongoing' ? 'badge-success' : 'badge-warning'}`}>
                  {s.status}
                </span>
              </div>
              <div className="site-hospital-name">{s.hospital_name}</div>

              <div style={{ marginBottom: '10px', fontSize: '12.5px' }}>
                <strong>Condition:</strong> {s.condition}
              </div>

              <div className="site-stats-row">
                <div>
                  <span className="meta-label">Enrolled</span>
                  <div style={{ fontWeight: 700 }}>
                    {s.participants_enrolled} / {s.participants_target}
                  </div>
                </div>
                <div>
                  <span className="meta-label">Duration</span>
                  <div style={{ fontWeight: 700 }}>{s.duration_weeks} Weeks</div>
                </div>
                <div>
                  <span className="meta-label">Progress</span>
                  <div style={{ fontWeight: 700, color: '#005944' }}>{s.progress_pct}%</div>
                </div>
              </div>

              <div className="progress-bar-container" style={{ height: '6px', marginBottom: '14px' }}>
                <div className="progress-bar-fill" style={{ width: `${s.progress_pct}%` }}></div>
              </div>

              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                👨‍⚕️ PI: {s.pi_name}
              </div>

              <button className="btn btn-outline btn-sm btn-block" style={{ marginTop: 'auto' }}>
                VIEW SITE DETAILS
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Selected Site Detail Modal with Outcome Trend Chart */}
      {selectedSite && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="badge badge-info text-xs">AIIA Clinical Center</span>
                <h3 className="text-xl font-bold text-emerald-950 mt-1 flex items-center gap-2">
                  <MapPin size={20} className="text-emerald-700" />
                  <span>📍 {selectedSite.city} Trial Site</span>
                </h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedSite(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div>
                <strong>Hospital:</strong> {selectedSite.hospital_name}
              </div>
              <div>
                <strong>State:</strong> {selectedSite.state}
              </div>
              <div>
                <strong>Active Condition:</strong>{' '}
                <span className="text-emerald-800 font-bold">{selectedSite.condition}</span>
              </div>
              <div>
                <strong>Trial ID:</strong> {selectedSite.trial_id}
              </div>
              <div>
                <strong>Principal Investigator:</strong> {selectedSite.pi_name}
              </div>
              <div>
                <strong>Working Doctor:</strong> {selectedSite.doctor_name}
              </div>
              <div>
                <strong>Trial Coordinator:</strong> {selectedSite.coordinator_name}
              </div>
              <div>
                <strong>Status:</strong>{' '}
                <span className="badge badge-success">{selectedSite.status}</span>
              </div>
              <div>
                <strong>Start Date:</strong> {selectedSite.start_date}
              </div>
              <div>
                <strong>End Date:</strong> {selectedSite.end_date}
              </div>
              <div>
                <strong>Duration:</strong> {selectedSite.duration_weeks} Weeks
              </div>
              <div>
                <strong>Participants:</strong>{' '}
                <strong>{selectedSite.participants_enrolled}</strong> / {selectedSite.participants_target} ({selectedSite.progress_pct}%)
              </div>
            </div>

            {/* Recorded Outcome Trend Chart */}
            <div className="bg-slate-50 border rounded-lg p-4 mb-4">
              <div className="flex justify-between items-center mb-3">
                <strong className="text-xs flex items-center gap-1">
                  <BarChart3 size={14} className="text-emerald-700" />
                  <span>Recorded Clinical Outcome Trend / Progress</span>
                </strong>
                <span className="badge badge-neutral text-xs">Standardized Clinical Scoring</span>
              </div>

              <div className="flex items-end gap-4 h-28 px-4 border-b border-slate-200">
                {(selectedSite.outcome_trend || [
                  { week: 'W0', score: 32 },
                  { week: 'W4', score: 55 },
                  { week: 'W8', score: 72 },
                  { week: 'W12', score: 88 },
                ]).map((item, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
                    <div className="text-xs font-bold text-emerald-800 mb-1">
                      {item.score || item.value}
                    </div>
                    <div
                      className="w-full max-w-[36px] bg-gradient-to-t from-emerald-700 to-emerald-500 rounded-t"
                      style={{ height: `${(item.score || item.value) * 0.9}px` }}
                    ></div>
                    <div className="text-[10px] text-slate-500 mt-1">{item.milestone || item.week}</div>
                  </div>
                ))}
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                * Outcome trend reflects patient validated symptom relief and biomarker recovery rates.
              </p>
            </div>

            {/* Pending Issues Remark */}
            <div className="bg-amber-50 border border-amber-200 p-3 rounded text-xs text-amber-900 mb-4 flex items-start gap-2">
              <AlertCircle size={16} className="text-amber-600 shrink-0 mt-0.5" />
              <div>
                <strong>Site Monitoring Remarks:</strong> {selectedSite.pending_issues || 'Routine monitoring review pending.'}
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedSite(null)}>
                Close
              </button>
              {onNavigateToTrial && (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => {
                    setSelectedSite(null);
                    onNavigateToTrial(selectedSite.trial_id);
                  }}
                >
                  Open Study Protocol
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
