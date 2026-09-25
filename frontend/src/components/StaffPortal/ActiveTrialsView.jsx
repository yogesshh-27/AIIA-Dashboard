import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Activity, Plus, Search, Filter, ExternalLink, X, MapPin, Calendar, UserCheck } from 'lucide-react';

export default function ActiveTrialsView({ onOpenCreateTrial }) {
  const [trials, setTrials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedTrial, setSelectedTrial] = useState(null);

  useEffect(() => {
    async function loadTrials() {
      try {
        setLoading(true);
        const data = await api.getTrials();
        setTrials(data.trials || []);
      } catch (err) {
        setError(err.message || 'Failed to load trials');
      } finally {
        setLoading(false);
      }
    }
    loadTrials();
  }, []);

  const filtered = trials.filter((t) => {
    const matchesSearch =
      t.trial_name?.toLowerCase().includes(search.toLowerCase()) ||
      t.condition?.toLowerCase().includes(search.toLowerCase()) ||
      t.city?.toLowerCase().includes(search.toLowerCase()) ||
      t.trial_id?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || t.trial_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="active-trials-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Active Clinical Trials Directory</h2>
          <p>Multi-center Ayurveda clinical trials across India with live enrollment tracking</p>
        </div>
        <button
          className="btn btn-primary btn-sm flex items-center gap-1"
          onClick={onOpenCreateTrial}
        >
          <Plus size={14} />
          <span>CREATE NEW TRIAL</span>
        </button>
      </div>

      {/* Filter and search bar */}
      <div className="flex flex-wrap gap-3 items-center justify-between mb-4 bg-white p-3 rounded-lg border shadow-xs">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            className="form-input text-xs"
            placeholder="Search by ID, condition, city or protocol title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-400" />
          <select
            className="form-select text-xs"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Completed">Completed</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading active trials...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div className="table-responsive bg-white rounded-lg border shadow-xs">
          <table className="data-table">
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
              {filtered.map((t) => (
                <tr key={t.trial_id}>
                  <td>
                    <span className="trial-id-badge">{t.trial_id}</span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 700 }}>{t.condition}</div>
                    <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                      {t.trial_name}
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{t.city}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      {t.hospital_name}
                    </div>
                  </td>
                  <td>{t.pi_name}</td>
                  <td>{t.duration_weeks} Wks</td>
                  <td>
                    <strong>{t.enrolled_participants}</strong> / {t.target_participants}
                  </td>
                  <td>
                    <div style={{ width: '80px' }}>
                      <div style={{ fontSize: '11px', fontWeight: 700, marginBottom: '2px' }}>
                        {t.progress_pct}%
                      </div>
                      <div className="progress-bar-container" style={{ height: '6px' }}>
                        <div
                          className="progress-bar-fill"
                          style={{ width: `${t.progress_pct}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        t.trial_status === 'Ongoing'
                          ? 'badge-success'
                          : t.trial_status === 'Completed'
                          ? 'badge-info'
                          : 'badge-warning'
                      }`}
                    >
                      {t.trial_status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-outline btn-xs"
                      onClick={() => setSelectedTrial(t)}
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Trial Detail Modal */}
      {selectedTrial && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="trial-id-badge text-xs mr-2">{selectedTrial.trial_id}</span>
                <h3 className="text-lg font-bold text-emerald-900 inline">
                  {selectedTrial.trial_name}
                </h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedTrial(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded border">
                <div>
                  <span className="text-slate-500 block">Condition / Indication:</span>
                  <strong className="text-sm">{selectedTrial.condition}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Clinical Center:</span>
                  <strong className="text-sm">
                    {selectedTrial.city} ({selectedTrial.hospital_name})
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Principal Investigator:</span>
                  <strong className="text-sm">{selectedTrial.pi_name}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Study Duration:</span>
                  <strong className="text-sm">{selectedTrial.duration_weeks} Weeks</strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Recruitment Target:</span>
                  <strong className="text-sm">
                    {selectedTrial.enrolled_participants} of {selectedTrial.target_participants} enrolled
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Trial Phase:</span>
                  <strong className="text-sm">{selectedTrial.phase || 'Phase II / III'}</strong>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block mb-1">Recruitment Completion:</span>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${selectedTrial.progress_pct}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-3 bg-emerald-50 rounded border border-emerald-200">
                <span className="font-semibold text-emerald-950 block mb-1">
                  Ayurvedic Intervention & Formulation:
                </span>
                <p className="text-emerald-900">
                  {selectedTrial.intervention ||
                    'Standardized Ayurvedic botanical extract formulation administered twice daily under supervised clinical protocol.'}
                </p>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
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
