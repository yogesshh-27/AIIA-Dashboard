import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Plus, Search, Filter, X, Shield, ExternalLink } from 'lucide-react';

export default function TrialInfoView({ onOpenCreateTrial }) {
  const [trials, setTrials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTrial, setSelectedTrial] = useState(null);
  const [search, setSearch] = useState('');

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

  const filtered = trials.filter(
    (t) =>
      t.trial_name?.toLowerCase().includes(search.toLowerCase()) ||
      t.condition?.toLowerCase().includes(search.toLowerCase()) ||
      t.intervention?.toLowerCase().includes(search.toLowerCase()) ||
      t.city?.toLowerCase().includes(search.toLowerCase()) ||
      t.trial_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="trial-info-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Ayurveda Clinical Protocols & Trials</h2>
          <p>Comprehensive protocol database with CDISC standard variable mapping</p>
        </div>
        <button
          className="btn btn-primary btn-sm flex items-center gap-1"
          onClick={onOpenCreateTrial}
        >
          <Plus size={14} />
          <span>+ CREATE NEW TRIAL</span>
        </button>
      </div>

      <div className="mb-4">
        <input
          type="text"
          className="form-input text-xs max-w-md"
          placeholder="Filter by trial ID, protocol name, condition or intervention..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading protocols and trial specifications...
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
              {filtered.map((t) => (
                <tr key={t.trial_id}>
                  <td>
                    <span className="trial-id-badge">{t.trial_id}</span>
                  </td>
                  <td>
                    <strong>{t.condition}</strong>
                  </td>
                  <td>{t.intervention}</td>
                  <td>
                    {t.hospital_name} ({t.city})
                  </td>
                  <td>{t.pi_name}</td>
                  <td style={{ fontSize: '11.5px' }}>
                    {t.start_date}
                    <br />
                    <span className="text-muted">{t.end_date}</span>
                  </td>
                  <td>
                    {t.enrolled_participants}/{t.target_participants}
                  </td>
                  <td>
                    <span className="badge badge-success">{t.regulatory_status || 'Approved'}</span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        t.trial_status === 'Ongoing' ? 'badge-success' : 'badge-warning'
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
                      View
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
                <span className="trial-id-badge text-xs">{selectedTrial.trial_id}</span>
                <h3 className="text-lg font-bold text-emerald-950 mt-1">
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

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div>
                <strong>Condition:</strong> {selectedTrial.condition}
              </div>
              <div>
                <strong>Ayurvedic Intervention:</strong> {selectedTrial.intervention}
              </div>
              <div>
                <strong>Hospital:</strong> {selectedTrial.hospital_name}
              </div>
              <div>
                <strong>City & State:</strong> {selectedTrial.city}, {selectedTrial.state}
              </div>
              <div>
                <strong>Principal Investigator:</strong> {selectedTrial.pi_name}
              </div>
              <div>
                <strong>Duration:</strong> {selectedTrial.duration_weeks} Weeks
              </div>
              <div>
                <strong>Target Sample:</strong> {selectedTrial.target_participants}
              </div>
              <div>
                <strong>Enrolled:</strong> {selectedTrial.enrolled_participants}
              </div>
              <div>
                <strong>Ethics Approval:</strong>{' '}
                <span className="badge badge-success">
                  {selectedTrial.ethics_approval_status || 'Approved'}
                </span>
              </div>
              <div>
                <strong>CTRI Status:</strong>{' '}
                <span className="badge badge-success">
                  {selectedTrial.ctri_registration_status || 'Registered'}
                </span>
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded border text-xs mb-3">
              <strong>Protocol Description:</strong>
              <p className="mt-1 text-slate-600">
                {selectedTrial.description ||
                  'Multicentric, randomized, double-blind clinical investigation adhering to GCP and NDCT Rules 2019.'}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div className="p-3 bg-white rounded border">
                <strong className="text-slate-700">Inclusion Criteria:</strong>
                <p className="mt-1 text-slate-600">
                  {selectedTrial.eligibility_criteria ||
                    'Age 18-65, confirmed clinical diagnosis, willing to sign informed consent.'}
                </p>
              </div>
              <div className="p-3 bg-white rounded border">
                <strong className="text-slate-700">Exclusion Criteria:</strong>
                <p className="mt-1 text-slate-600">
                  {selectedTrial.exclusion_criteria ||
                    'Severe systemic illness, pregnancy, participation in other trials within 30 days.'}
                </p>
              </div>
            </div>

            <div className="flex justify-end">
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
