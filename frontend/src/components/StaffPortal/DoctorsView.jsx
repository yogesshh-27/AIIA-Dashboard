import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Stethoscope, Mail, Phone, MapPin, Award, X, User } from 'lucide-react';

export default function DoctorsView() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);

  useEffect(() => {
    async function loadDoctors() {
      try {
        setLoading(true);
        const data = await api.getDoctors();
        setDoctors(data.doctors || []);
      } catch (err) {
        setError(err.message || 'Failed to load doctors');
      } finally {
        setLoading(false);
      }
    }
    loadDoctors();
  }, []);

  const handleOpenDoctor = async (doctorId) => {
    try {
      const data = await api.getDoctorDetail(doctorId);
      if (data.success && data.doctor) {
        setSelectedDoctor(data.doctor);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="doctors-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Registered Ayurveda Doctors & Principal Investigators</h2>
          <p>Verified clinical investigators across participating AIIA medical centers</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading principal investigators directory...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
          {doctors.map((d) => (
            <div
              key={d.doctor_id}
              className="site-card cursor-pointer hover:shadow-md transition"
              onClick={() => handleOpenDoctor(d.doctor_id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div
                  style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '50%',
                    background: 'var(--ayur-primary-subtle)',
                    color: 'var(--ayur-primary)',
                    fontWeight: 800,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '15px',
                  }}
                >
                  {d.name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                    {d.name}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>{d.qualification}</div>
                </div>
              </div>

              <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '14px' }}>
                <div>
                  <strong>Specialization:</strong> {d.specialization}
                </div>
                <div>
                  <strong>Experience:</strong> {d.experience_years} Years
                </div>
                <div>
                  <strong>Current Site:</strong> 📍 {d.current_site}
                </div>
                <div>
                  <strong>Assigned Trial:</strong> <span className="trial-id-badge">{d.trial_id}</span>
                </div>
                <div>
                  <strong>Role:</strong> {d.role}
                </div>
                <div>
                  <strong>Status:</strong> <span className="badge badge-success">{d.status}</span>
                </div>
              </div>

              <button className="btn btn-outline btn-sm btn-block" style={{ marginTop: 'auto' }}>
                VIEW FULL PROFILE
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Doctor Profile Modal */}
      {selectedDoctor && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="badge badge-info text-xs">{selectedDoctor.role}</span>
                <h3 className="text-xl font-bold text-emerald-950 mt-1">{selectedDoctor.name}</h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedDoctor(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div>
                <strong>Doctor ID:</strong> {selectedDoctor.doctor_id}
              </div>
              <div>
                <strong>Qualification:</strong> {selectedDoctor.qualification}
              </div>
              <div>
                <strong>Specialization:</strong> {selectedDoctor.specialization}
              </div>
              <div>
                <strong>Experience:</strong> {selectedDoctor.experience_years} Years
              </div>
              <div>
                <strong>Current Site:</strong> {selectedDoctor.current_site}
              </div>
              <div>
                <strong>Assigned Trial:</strong> {selectedDoctor.trial_id}
              </div>
              <div>
                <strong>Email:</strong> {selectedDoctor.email}
              </div>
              <div>
                <strong>Phone:</strong> {selectedDoctor.phone}
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded border text-xs mb-4">
              <strong className="text-slate-800">Clinical Biography & Research Focus:</strong>
              <p className="mt-1 text-slate-600">
                {selectedDoctor.bio || 'Principal investigator overseeing clinical trials and patient safety.'}
              </p>
            </div>

            <div className="mb-4">
              <strong className="text-xs text-slate-800">
                Assigned Patients in Active Follow-Up ({selectedDoctor.assigned_patients ? selectedDoctor.assigned_patients.length : 0})
              </strong>
              <div className="mt-2 max-h-36 overflow-y-auto space-y-1">
                {selectedDoctor.assigned_patients && selectedDoctor.assigned_patients.length > 0 ? (
                  selectedDoctor.assigned_patients.map((p) => (
                    <div
                      key={p.patient_id}
                      className="flex justify-between p-2 bg-slate-50 border rounded text-xs"
                    >
                      <span>
                        <strong>{p.full_name}</strong> ({p.patient_id})
                      </span>
                      <span>
                        {p.condition} • <span className="badge badge-info">{p.treatment_status}</span>
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400 text-xs italic">No currently assigned patients.</p>
                )}
              </div>
            </div>

            <div className="flex justify-end">
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedDoctor(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
