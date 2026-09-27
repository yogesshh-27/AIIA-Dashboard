import React, { useState } from 'react';
import { api } from '../services/api';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Search, RotateCcw, AlertTriangle, MapPin, Phone, Mail, Building, User, Calendar, CheckCircle2, Mic, MicOff } from 'lucide-react';

const CITIES = [
  'Mumbai', 'Delhi', 'Kolkata', 'Kerala', 'Lucknow', 'Noida', 'Jaipur', 'Hyderabad', 'Bengaluru'
];

const CONDITIONS = [
  'Arthritis', 'Diabetes', 'Hypertension', 'Psoriasis', 'Asthma',
  'Cognitive deficit disorders', 'Obesity', 'Skin disorders', 'Digestive disorders'
];

const CONDITION_ICONS = {
  'Arthritis': '🦴',
  'Diabetes': '🩸',
  'Hypertension': '🩺',
  'Psoriasis': '🌿',
  'Asthma': '🫁',
  'Cognitive deficit disorders': '🧠',
  'Obesity': '⚖️',
  'Skin disorders': '✨',
  'Digestive disorders': '🧪'
};

export default function PatientPortal({ onBackToGate, onStaffLoginClick, onOpenStaffLogin }) {
  const handleStaffLogin = onOpenStaffLogin || onStaffLoginClick;
  const { t } = useTranslation();
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
  const [isListening, setIsListening] = useState(false);
  const [speechNotice, setSpeechNotice] = useState('');

  const startVoiceSearch = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechNotice('Voice search is not supported in this browser.');
      return;
    }
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      setIsListening(true);
      setSpeechNotice('Listening... Speak a health condition or city (e.g. "Diabetes", "Mumbai")');

      recognition.onresult = (event) => {
        const text = event.results[0][0].transcript.toLowerCase();
        setIsListening(false);
        setSpeechNotice(`Recognized: "${event.results[0][0].transcript}"`);

        const matchedCond = CONDITIONS.find(c => text.includes(c.toLowerCase()));
        if (matchedCond) {
          setFormData(prev => ({ ...prev, condition: matchedCond }));
        }

        const matchedCity = CITIES.find(c => text.includes(c.toLowerCase()));
        if (matchedCity) {
          setFormData(prev => ({
            ...prev,
            selectedCities: prev.selectedCities.includes(matchedCity) ? prev.selectedCities : [...prev.selectedCities, matchedCity]
          }));
        }
      };

      recognition.onerror = () => {
        setIsListening(false);
        setSpeechNotice('Voice input cancelled or timed out.');
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (e) {
      setIsListening(false);
      setSpeechNotice('Voice recognition error.');
    }
  };

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
            <img
              src="/logos/aiia-logo.svg"
              alt="AIIA Logo"
              className="patient-portal-logo-img"
              width="32"
              height="32"
            />
            <span className="brand-text">AYURCTMS • Patient Trial Matching Portal</span>
          </div>
        </div>
        <div className="patient-header-right">
          <button className="btn btn-outline btn-sm" onClick={handleStaffLogin}>
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

          {/* VISUAL 3-STEP MATCHING STEPPER */}
          <div className="matching-stepper" style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            marginBottom: '22px',
            flexWrap: 'wrap'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: '#f0fdf4',
              border: '1px solid #bbf7d0',
              padding: '6px 14px',
              borderRadius: '9999px',
              color: '#15803d',
              fontWeight: 700,
              fontSize: '12px'
            }}>
              <span style={{ background: '#15803d', color: '#ffffff', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>1</span>
              <span>Patient Profile</span>
            </div>
            <span style={{ color: '#94a3b8', fontWeight: 'bold' }}>→</span>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: formData.selectedCities.length > 0 ? '#f0fdf4' : '#f8fafc',
              border: formData.selectedCities.length > 0 ? '1px solid #bbf7d0' : '1px solid #e2e8f0',
              padding: '6px 14px',
              borderRadius: '9999px',
              color: formData.selectedCities.length > 0 ? '#15803d' : '#64748b',
              fontWeight: 700,
              fontSize: '12px'
            }}>
              <span style={{ background: formData.selectedCities.length > 0 ? '#15803d' : '#94a3b8', color: '#ffffff', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>2</span>
              <span>City Locations ({formData.selectedCities.length})</span>
            </div>
            <span style={{ color: '#94a3b8', fontWeight: 'bold' }}>→</span>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: matches ? '#f0fdf4' : '#f8fafc',
              border: matches ? '1px solid #bbf7d0' : '1px solid #e2e8f0',
              padding: '6px 14px',
              borderRadius: '9999px',
              color: matches ? '#15803d' : '#64748b',
              fontWeight: 700,
              fontSize: '12px'
            }}>
              <span style={{ background: matches ? '#15803d' : '#94a3b8', color: '#ffffff', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>3</span>
              <span>Matching Trials {matches ? `(${matches.length})` : ''}</span>
            </div>
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
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label htmlFor="p-condition">{t('patient.condition', 'Target Health Condition / Area of Interest')} *</label>
                  <button
                    type="button"
                    onClick={startVoiceSearch}
                    className={`btn btn-sm ${isListening ? 'btn-danger' : 'btn-outline'}`}
                    style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', padding: '3px 8px' }}
                    aria-label="Activate voice search"
                  >
                    {isListening ? <MicOff size={13} className="animate-spin" /> : <Mic size={13} className="text-emerald-700" />}
                    <span>{isListening ? t('patient.listening', 'Listening...') : t('patient.voiceSearch', 'Voice Search')}</span>
                  </button>
                </div>
                {speechNotice && (
                  <div
                    style={{
                      fontSize: '11.5px',
                      color: isListening ? '#b45309' : '#047857',
                      background: isListening ? '#fef3c7' : '#d1fae5',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      marginBottom: '8px'
                    }}
                    role="status"
                    aria-live="polite"
                  >
                    {speechNotice}
                  </div>
                )}
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

                {/* AYURVEDIC CONDITION GRAPHIC CHIPS */}
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '10px' }}>
                  {CONDITIONS.map((cond) => {
                    const isSelected = formData.condition === cond;
                    return (
                      <button
                        key={cond}
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, condition: cond }))}
                        style={{
                          background: isSelected ? '#005944' : '#f8fafc',
                          color: isSelected ? '#ffffff' : '#334155',
                          border: isSelected ? '1px solid #005944' : '1px solid #cbd5e1',
                          borderRadius: '8px',
                          padding: '5px 11px',
                          fontSize: '11.5px',
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          boxShadow: isSelected ? '0 2px 6px rgba(0, 89, 68, 0.25)' : 'none',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <span style={{ fontSize: '13px' }}>{CONDITION_ICONS[cond] || '🌿'}</span>
                        <span>{cond}</span>
                      </button>
                    );
                  })}
                </div>
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
                    <div className="trial-card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="trial-id-badge">{trial.trial_id || 'TRIAL'}</span>
                        <span style={{ fontSize: '10.5px', fontWeight: 700, background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', borderRadius: '4px', padding: '1px 7px', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                          🌿 Verified AIIA Protocol
                        </span>
                      </div>
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
