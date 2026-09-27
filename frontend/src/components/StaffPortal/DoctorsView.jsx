import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { FALLBACK_DATA } from '../../services/fallbackData';
import { Stethoscope, Mail, Phone, MapPin, Award, X, User } from 'lucide-react';

const INITIAL_DOCTORS = FALLBACK_DATA['/api/ayur/doctors']?.doctors || [];
const ALL_PATIENTS = FALLBACK_DATA['/api/ayur/patients']?.patients || [];

export default function DoctorsView() {
  const [doctors, setDoctors] = useState(INITIAL_DOCTORS);
  const [loading, setLoading] = useState(INITIAL_DOCTORS.length === 0);
  const [error, setError] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);

  useEffect(() => {
    async function loadDoctors() {
      try {
        if (doctors.length === 0) setLoading(true);
        const data = await api.getDoctors();
        if (data.doctors && data.doctors.length > 0) {
          setDoctors(data.doctors);
        }
      } catch (err) {
        if (doctors.length === 0) setError(err.message || 'Failed to load doctors');
      } finally {
        setLoading(false);
      }
    }
    loadDoctors();
  }, []);

  const handleOpenDoctor = async (doctor) => {
    // Open immediately with existing card data (0ms latency)
    setSelectedDoctor(doctor);
    try {
      const data = await api.getDoctorDetail(doctor.doctor_id || doctor.id);
      const detail = data?.doctor || data;
      if (detail && (detail.name || detail.doctor_id)) {
        setSelectedDoctor((prev) => ({ ...(prev || doctor), ...detail }));
      }
    } catch (err) {
      console.error('Failed to load extra doctor details:', err);
    }
  };

  // Find assigned patients for selected doctor
  const assignedPatients = selectedDoctor
    ? (selectedDoctor.assigned_patients && selectedDoctor.assigned_patients.length > 0
        ? selectedDoctor.assigned_patients
        : ALL_PATIENTS.filter((p) => p.assigned_trial_id === selectedDoctor.trial_id).slice(0, 5))
    : [];

  return (
    <div className="doctors-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Registered Ayurveda Doctors & Principal Investigators</h2>
          <p>Verified clinical investigators across participating AIIA medical centers</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500" style={{ padding: '32px', textAlign: 'center' }}>
          <div className="badge badge-info animate-pulse" style={{ padding: '8px 16px', fontSize: '13px' }}>
            Loading principal investigators directory...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger" style={{ padding: '10px 16px', fontSize: '13px' }}>{error}</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
          {doctors.map((d) => (
            <div
              key={d.doctor_id}
              className="site-card cursor-pointer hover:shadow-md transition"
              style={{
                display: 'flex',
                flexDirection: 'column',
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
                cursor: 'pointer'
              }}
              onClick={() => handleOpenDoctor(d)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
                <div
                  style={{
                    width: '46px',
                    height: '46px',
                    borderRadius: '50%',
                    background: 'var(--ayur-primary-subtle)',
                    color: 'var(--ayur-primary)',
                    fontWeight: 800,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '15px',
                    flexShrink: 0
                  }}
                >
                  {d.name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)', marginBottom: '2px' }}>
                    {d.name}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>{d.qualification}</div>
                </div>
              </div>

              <div style={{ fontSize: '12.5px', display: 'flex', flexDirection: 'column', gap: '7px', marginBottom: '16px' }}>
                <div>
                  <strong style={{ color: '#475569' }}>Specialization:</strong> {d.specialization}
                </div>
                <div>
                  <strong style={{ color: '#475569' }}>Experience:</strong> {d.experience_years} Years
                </div>
                <div>
                  <strong style={{ color: '#475569' }}>Current Site:</strong> 📍 {d.current_site}
                </div>
                <div>
                  <strong style={{ color: '#475569' }}>Assigned Trial:</strong> <span className="trial-id-badge">{d.trial_id}</span>
                </div>
                <div>
                  <strong style={{ color: '#475569' }}>Role:</strong> {d.role}
                </div>
                <div>
                  <strong style={{ color: '#475569' }}>Status:</strong> <span className="badge badge-success">{d.status}</span>
                </div>
              </div>

              <button
                type="button"
                className="btn btn-outline btn-sm"
                style={{
                  marginTop: 'auto',
                  width: '100%',
                  fontWeight: 600,
                  cursor: 'pointer',
                  borderColor: '#005944',
                  color: '#005944'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenDoctor(d);
                }}
              >
                VIEW FULL PROFILE
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Doctor Profile Modal */}
      {selectedDoctor && (
        <div
          className="modal-overlay"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px'
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setSelectedDoctor(null);
          }}
        >
          <div
            className="modal-card"
            style={{
              background: '#ffffff',
              borderRadius: '14px',
              padding: '24px',
              maxWidth: '600px',
              width: '100%',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              maxHeight: '90vh',
              overflowY: 'auto'
            }}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '14px' }}>
              <div>
                <span className="badge badge-info" style={{ fontSize: '11px', marginBottom: '6px' }}>{selectedDoctor.role || 'Principal Investigator'}</span>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#003d2e', margin: 0 }}>
                  {selectedDoctor.name}
                </h3>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  {selectedDoctor.qualification} • {selectedDoctor.specialization}
                </div>
              </div>
              <button
                type="button"
                className="btn btn-ghost btn-xs"
                style={{ cursor: 'pointer', color: '#64748b', padding: '4px', borderRadius: '6px' }}
                onClick={() => setSelectedDoctor(null)}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Metadata Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', fontSize: '12.5px', marginBottom: '16px' }}>
              <div>
                <strong style={{ color: '#475569' }}>Doctor ID:</strong> <span className="trial-id-badge">{selectedDoctor.doctor_id}</span>
              </div>
              <div>
                <strong style={{ color: '#475569' }}>Experience:</strong> {selectedDoctor.experience_years} Years
              </div>
              <div>
                <strong style={{ color: '#475569' }}>Current Site:</strong> 📍 {selectedDoctor.current_site}
              </div>
              <div>
                <strong style={{ color: '#475569' }}>Assigned Trial:</strong> <span className="trial-id-badge">{selectedDoctor.trial_id}</span>
              </div>
              <div>
                <strong style={{ color: '#475569' }}>Official Email:</strong> {selectedDoctor.email || `${selectedDoctor.doctor_id.toLowerCase()}@aiia.gov.in`}
              </div>
              <div>
                <strong style={{ color: '#475569' }}>Hospital Extension:</strong> {selectedDoctor.phone || '+91-11-29948601 (Ext 240)'}
              </div>
            </div>

            {/* Bio Box */}
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px', marginBottom: '16px', lineHeight: 1.5 }}>
              <strong style={{ color: '#1e293b', display: 'block', marginBottom: '4px' }}>Clinical Biography & Research Focus:</strong>
              <p style={{ color: '#475569', margin: 0 }}>
                {selectedDoctor.bio || 'Principal investigator and senior clinical specialist at AIIA overseeing patient enrollment, standard Ayurvedic therapeutic protocols, and GCP-compliant trial execution.'}
              </p>
            </div>

            {/* Assigned Patients Section */}
            <div style={{ marginBottom: '20px' }}>
              <strong style={{ fontSize: '13px', color: '#1e293b', display: 'block', marginBottom: '8px' }}>
                Assigned Trial Cohort Patients ({assignedPatients.length})
              </strong>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '160px', overflowY: 'auto' }}>
                {assignedPatients.length > 0 ? (
                  assignedPatients.map((p) => (
                    <div
                      key={p.patient_id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '12px'
                      }}
                    >
                      <span>
                        <strong style={{ color: '#0f172a' }}>{p.full_name}</strong> ({p.patient_id})
                      </span>
                      <span>
                        {p.condition} &nbsp;•&nbsp; <span className="badge badge-info" style={{ fontSize: '10px' }}>{p.treatment_status}</span>
                      </span>
                    </div>
                  ))
                ) : (
                  <p style={{ color: '#94a3b8', fontSize: '12px', fontStyle: 'italic', margin: 0 }}>No currently assigned patients in this cohort.</p>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '12px', borderTop: '1px solid #e2e8f0' }}>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                style={{ fontWeight: 600, cursor: 'pointer', padding: '6px 18px' }}
                onClick={() => setSelectedDoctor(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
