import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Users, Lock, X, Check, Clock, AlertTriangle, Calendar, FileText } from 'lucide-react';

export default function PatientsView() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientLoading, setPatientLoading] = useState(false);

  useEffect(() => {
    async function loadPatients() {
      try {
        setLoading(true);
        const data = await api.getPatients();
        setPatients(data.patients || []);
      } catch (err) {
        setError(err.message || 'Failed to load patients');
      } finally {
        setLoading(false);
      }
    }
    loadPatients();
  }, []);

  const handleOpenPatient = async (patientId) => {
    setPatientLoading(true);
    try {
      const data = await api.getPatientDetail(patientId);
      if (data.success && data.patient) {
        setSelectedPatient(data.patient);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setPatientLoading(false);
    }
  };

  return (
    <div className="patients-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Patient Management & Clinical Roster</h2>
          <p>Registered clinical trial participants under active protocol care</p>
        </div>
      </div>

      <div className="disclaimer-banner mb-4">
        <div className="disclaimer-icon">🔒</div>
        <div className="disclaimer-content">
          <strong>Authorized AIIA Clinical Staff Access Only</strong>
          <p>Patient medical details and visit timelines are confidential and accessible solely to qualified researchers under informed consent protocols.</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading patient records...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div className="table-responsive bg-white rounded-lg border shadow-xs">
          <table className="data-table">
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
              {patients.map((p) => (
                <tr key={p.patient_id}>
                  <td>
                    <span className="trial-id-badge">{p.patient_id}</span>
                  </td>
                  <td>
                    <strong>{p.full_name}</strong>
                  </td>
                  <td>
                    {p.age} Y / {p.gender}
                  </td>
                  <td>{p.condition}</td>
                  <td>{p.area_city}</td>
                  <td>
                    <span className="trial-id-badge">{p.assigned_trial_id}</span>
                  </td>
                  <td>{p.treatment_site}</td>
                  <td>{p.assigned_doctor_name}</td>
                  <td>
                    <span className="badge badge-info">{p.treatment_status}</span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        p.status === 'Active' ? 'badge-success' : 'badge-neutral'
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-outline btn-xs"
                      onClick={() => handleOpenPatient(p.patient_id)}
                    >
                      Timeline
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Patient Profile & 8-Stage Timeline Modal */}
      {selectedPatient && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="badge badge-info text-xs">Participant Profile & Longitudinal Flow</span>
                <h3 className="text-xl font-bold text-emerald-950 mt-1">
                  {selectedPatient.full_name} ({selectedPatient.patient_id})
                </h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedPatient(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs mb-4 bg-slate-50 p-3.5 rounded border">
              <div>
                <strong>Age / Gender:</strong> {selectedPatient.age} Years / {selectedPatient.gender}
              </div>
              <div>
                <strong>Condition:</strong>{' '}
                <span className="text-emerald-800 font-bold">{selectedPatient.condition}</span>
              </div>
              <div>
                <strong>City & State:</strong> {selectedPatient.area_city}, {selectedPatient.state}
              </div>
              <div>
                <strong>Accessible Locations:</strong> {selectedPatient.accessible_locations}
              </div>
              <div>
                <strong>Assigned Trial:</strong> {selectedPatient.assigned_trial_id}
              </div>
              <div>
                <strong>Assigned Doctor:</strong> {selectedPatient.assigned_doctor_name}
              </div>
              <div>
                <strong>Treatment Site:</strong> {selectedPatient.treatment_site}
              </div>
              <div>
                <strong>Treatment Duration:</strong> {selectedPatient.treatment_duration_weeks} Weeks
              </div>
              <div>
                <strong>Dose / Regimen:</strong> {selectedPatient.dosage_frequency}
              </div>
            </div>

            {/* VISUAL 8-STAGE TREATMENT TIMELINE */}
            <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Clock size={16} className="text-emerald-700" />
              <span>Clinical Treatment Timeline & Visit Flow (8 Stages)</span>
            </h4>

            <div className="treatment-timeline-wrapper">
              <div className="timeline-stages-flow">
                {(selectedPatient.treatment_timeline || []).map((stage, idx) => (
                  <div
                    key={idx}
                    className={`timeline-stage-item ${
                      stage.status === 'Completed'
                        ? 'stage-completed'
                        : stage.status === 'In Progress'
                        ? 'stage-current'
                        : ''
                    }`}
                  >
                    <div className="stage-icon-circle">
                      {stage.status === 'Completed' ? '✓' : idx + 1}
                    </div>
                    <div className="stage-content-box">
                      <div className="stage-title-line flex justify-between items-center">
                        <span className="stage-title font-bold text-xs">{stage.stage_title}</span>
                        <span
                          className={`badge text-[10px] ${
                            stage.status === 'Completed'
                              ? 'badge-success'
                              : stage.status === 'In Progress'
                              ? 'badge-info'
                              : 'badge-neutral'
                          }`}
                        >
                          {stage.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        Date: <strong>{stage.date_recorded}</strong> • Clinician:{' '}
                        <strong>
                          {stage.assigned_doctor_name || selectedPatient.assigned_doctor_name}
                        </strong>{' '}
                        • Regimen: <strong>{stage.dosage_frequency || selectedPatient.dosage_frequency}</strong>
                      </div>
                      <div className="stage-notes text-xs text-slate-700 mt-1 bg-slate-50 p-2 rounded border border-slate-100">
                        {stage.notes}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recorded Adverse Events for this patient if any */}
            {selectedPatient.adverse_events && selectedPatient.adverse_events.length > 0 && (
              <div className="bg-rose-50 border border-rose-200 rounded p-3 mt-4 text-xs text-rose-900">
                <strong className="block mb-1 text-rose-950 font-bold">
                  ⚠️ Recorded Safety Events for this Participant:
                </strong>
                {selectedPatient.adverse_events.map((ae, i) => (
                  <div key={i} className="mt-1">
                    • <strong>{ae.adverse_event}</strong> (Severity: {ae.severity}) - Status: {ae.status}
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end mt-4">
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedPatient(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
