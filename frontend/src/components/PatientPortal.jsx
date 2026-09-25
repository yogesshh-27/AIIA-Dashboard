import React, { useState } from 'react';
import { api } from '../services/api';
import { ArrowLeft, Search, RotateCcw, AlertTriangle, MapPin, Phone, Mail, Building, User, Calendar, CheckCircle2 } from 'lucide-react';

const CITIES = [
  'Mumbai', 'Delhi', 'Kolkata', 'Kerala', 'Lucknow', 'Noida', 'Jaipur', 'Hyderabad', 'Bengaluru'
];

const CONDITIONS = [
  'Arthritis', 'Diabetes', 'Hypertension', 'Psoriasis', 'Asthma',
  'Cognitive deficit disorders', 'Obesity', 'Skin disorders', 'Digestive disorders'
];

export default function PatientPortal({ onBackToGate, onStaffLoginClick }) {
  const [formData, setFormData] = useState({
    fullname: '',
    age: '',
    gender: '',
    condition: 'Arthritis',
    selectedCities: ['Mumbai', 'Delhi'],
    distancePref: 'Within City (< 25 km)',
    accessibility: '',
  });

  const [matches, setMatches] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleCity = (city) => {
    setFormData((prev) => {
      const exists = prev.selectedCities.includes(city);
      const updated = exists
        ? prev.selectedCities.filter((c) => c !== city)
        : [...prev.selectedCities, city];
      return { ...prev, selectedCities: updated };
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (formData.selectedCities.length === 0) {
      setError('Please select at least one accessible city/location.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const res = await api.matchPatientTrial({
        condition: formData.condition,
        accessible_locations: formData.selectedCities,
        distance_pref: formData.distancePref,
      });

      if (res.success) {
        setMatches(res.results || []);
        setTimeout(() => {
          document.getElementById('patient-results-area')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } else {
        setError(res.message || 'No matching trials found.');
      }
    } catch (err) {
      setError('Could not connect to matching engine. Please verify backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      fullname: '',
      age: '',
      gender: '',
      condition: 'Arthritis',
      selectedCities: ['Mumbai', 'Delhi'],
      distancePref: 'Within City (< 25 km)',
      accessibility: '',
    });
    setMatches(null);
    setError('');
  };

  return (
    <div className="patient-portal-view">
      <header className="patient-header">
        <div className="patient-header-left">
          <button className="btn btn-outline btn-sm" onClick={onBackToGate}>
            <ArrowLeft size={14} className="inline mr-1" />
            Back to Portal Selection
          </button>
          <div className="brand-inline">
            <span className="brand-pill">AIIA</span>
            <span className="brand-text">AYURCTMS • Patient Trial Matching Portal</span>
          </div>
        </div>
        <div className="patient-header-right">
          <button className="btn btn-outline btn-sm" onClick={onStaffLoginClick}>
            AIIA Staff Login
          </button>
        </div>
      </header>

      <main className="patient-main-container">
        {/* INTAKE FORM */}
        <section className="patient-intake-section">
          <div className="section-hero">
            <h2>Find a Suitable Clinical Trial</h2>
            <p>Tell us a little about yourself so we can identify trial locations that may be accessible to you.</p>
          </div>

          <div className="patient-card form-card">
            <form onSubmit={handleSearch}>
              <div className="form-row-grid">
                <div className="form-group">
                  <label htmlFor="p-fullname">Full Name *</label>
                  <input
                    type="text"
                    id="p-fullname"
                    className="form-input"
                    placeholder="e.g. Ramesh Kumar"
                    required
                    value={formData.fullname}
                    onChange={(e) => setFormData({ ...formData, fullname: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="p-age">Age *</label>
                  <input
                    type="number"
                    id="p-age"
                    className="form-input"
                    min="1"
                    max="120"
                    placeholder="e.g. 45"
                    required
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="p-gender">Gender *</label>
                  <select
                    id="p-gender"
                    className="form-select"
                    required
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="p-condition">Target Health Condition / Area of Interest *</label>
                <select
                  id="p-condition"
                  className="form-select"
                  required
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                >
                  {CONDITIONS.map((cond) => (
                    <option key={cond} value={cond}>
                      {cond}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label-bold">
                  Accessible Participating Cities across India (Select all that apply) *
                </label>
                <div className="location-pills-grid">
                  {CITIES.map((city) => {
                    const checked = formData.selectedCities.includes(city);
                    return (
                      <label key={city} className="location-pill">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleCity(city)}
                        />
                        <span>{city}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="form-row-grid">
                <div className="form-group">
                  <label htmlFor="p-distance">Distance Preference</label>
                  <select
                    id="p-distance"
                    className="form-select"
                    value={formData.distancePref}
                    onChange={(e) => setFormData({ ...formData, distancePref: e.target.value })}
                  >
                    <option value="Within City (< 25 km)">Within City (&lt; 25 km)</option>
                    <option value="Neighboring District (< 50 km)">Neighboring District (&lt; 50 km)</option>
                    <option value="Willing to Travel Any Distance">Willing to Travel Any Distance</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="p-accessibility">Accessibility Requirements (Optional)</label>
                  <input
                    type="text"
                    id="p-accessibility"
                    className="form-input"
                    placeholder="e.g. Wheelchair access, Weekend visits..."
                    value={formData.accessibility}
                    onChange={(e) => setFormData({ ...formData, accessibility: e.target.value })}
                  />
                </div>
              </div>

              {error && (
                <div className="login-error" style={{ marginTop: '10px' }}>
                  {error}
                </div>
              )}

              <div className="form-actions">
                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                  <Search size={16} className="inline mr-2" />
                  <span>{loading ? 'Finding Trials...' : 'Find Suitable Clinical Trials'}</span>
                </button>
                <button type="button" className="btn btn-ghost" onClick={handleReset}>
                  <RotateCcw size={14} className="inline mr-1" />
                  Reset Form
                </button>
              </div>
            </form>
          </div>
        </section>

        {/* RESULTS SECTION */}
        {matches && (
          <section className="patient-results-section" id="patient-results-area">
            <div className="results-header-bar">
              <div>
                <h3>Matching Clinical Trial Locations</h3>
                <p className="results-subtitle">
                  Found {matches.length} potentially relevant trial site{matches.length === 1 ? '' : 's'} matching your criteria
                </p>
              </div>
            </div>

            {/* MANDATORY DISCLAIMER BOX */}
            <div className="disclaimer-banner">
              <div className="disclaimer-icon">⚠️</div>
              <div className="disclaimer-content">
                <strong>Potentially Relevant Trial Disclaimer</strong>
                <p>
                  Final eligibility will be determined strictly by the authorized AIIA clinical research team 
                  following institutional protocol, ethical committee approval, and formal informed consent procedures.
                </p>
              </div>
            </div>

            {matches.length === 0 ? (
              <div className="empty-state-box">
                <p>No active trials currently recruiting for the selected condition in your chosen locations.</p>
              </div>
            ) : (
              <div className="trial-cards-grid">
                {matches.map((trial, idx) => (
                  <div key={idx} className="trial-match-card">
                    <div className="trial-card-header">
                      <span className="trial-id-badge">{trial.trial_id || 'TRIAL'}</span>
                      <span className="badge badge-success">Recruiting</span>
                    </div>

                    <h4 className="trial-condition-title">{trial.trial_name || trial.condition}</h4>

                    <div className="trial-meta-grid">
                      <div className="trial-meta-item">
                        <span className="meta-label">Location / City</span>
                        <span className="meta-value flex items-center gap-1">
                          <MapPin size={13} className="text-emerald-700" />
                          {trial.location || trial.city}
                        </span>
                      </div>
                      <div className="trial-meta-item">
                        <span className="meta-label">Hospital Center</span>
                        <span className="meta-value flex items-center gap-1">
                          <Building size={13} className="text-emerald-700" />
                          {trial.hospital_name || 'AIIA Clinical Center'}
                        </span>
                      </div>
                      <div className="trial-meta-item">
                        <span className="meta-label">Principal Investigator</span>
                        <span className="meta-value flex items-center gap-1">
                          <User size={13} className="text-emerald-700" />
                          {trial.doctor_name || trial.pi_name || 'Investigator'}
                        </span>
                      </div>
                      <div className="trial-meta-item">
                        <span className="meta-label">Study Duration</span>
                        <span className="meta-value flex items-center gap-1">
                          <Calendar size={13} className="text-emerald-700" />
                          {trial.duration_weeks ? `${trial.duration_weeks} Weeks` : 'Standard Protocol'}
                        </span>
                      </div>
                    </div>

                    <div className="distance-info-tag">
                      <strong>Accessibility:</strong> Direct trial coordinator contact available • Wheelchair accessible site
                    </div>

                    <div className="trial-card-footer flex justify-between items-center pt-3 border-t border-slate-200">
                      <div className="contact-details text-xs text-slate-600">
                        <div>📞 Contact: <strong>+91 11 26950401</strong></div>
                        <div>✉️ Email: <strong>trials@aiia.gov.in</strong></div>
                      </div>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => alert(`Inquiry initiated for Trial ${trial.trial_id}. Please contact the AIIA Clinical Trial Coordination Office at +91 11 26950401 or trials@aiia.gov.in with reference ${trial.trial_id}.`)}
                      >
                        Inquire at Site →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
