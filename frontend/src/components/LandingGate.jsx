import React from 'react';
import { User, ShieldCheck, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react';

export default function LandingGate({ onSelectPatient, onSelectStaff }) {
  return (
    <div id="landing-gate" className="landing-gate-view">
      <div className="landing-header">
        <div className="landing-brand">
          <div className="landing-emblem" aria-label="AIIA Logo">AIIA</div>
          <div className="landing-brand-text">
            <div className="landing-brand-hindi">अखिल भारतीय आयुर्वेद संस्थान</div>
            <h1>ALL INDIA INSTITUTE OF AYURVEDA</h1>
            <p>An Autonomous Organization under the Ministry of Ayush, Govt. of India • AYURCTMS Portal</p>
          </div>
        </div>
        <div className="landing-official-badge">
          <span>🌿 Clinical Trial Management Portal</span>
        </div>
      </div>

      <div className="landing-hero-content">
        <div className="landing-title-block">
          <h2>AIIA Clinical Trial Management & Research Portal</h2>
          <p>
            A real-time, cloud-based, GCP-compliant Clinical Trial Management System (CTMS) for Ayurveda research, 
            with CDISC/FHIR-interoperable data, role-based KPIs, and integrated ethics, regulatory and pharmacovigilance tracking.
          </p>
        </div>

        <div className="gate-selection-container">
          <h3 className="gate-prompt">Who are you?</h3>
          <p className="gate-subprompt">Select your portal to continue</p>

          <div className="gate-cards-grid">
            {/* CARD 1: PATIENT */}
            <div
              className="gate-card gate-card-patient"
              onClick={onSelectPatient}
              tabIndex={0}
              role="button"
              aria-label="Patient Portal"
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelectPatient()}
            >
              <div className="gate-card-icon-wrapper">
                <span className="gate-icon">👤</span>
              </div>
              <div className="gate-card-body">
                <span className="gate-badge">Public Access</span>
                <h4 className="gate-card-title">I'm a Patient</h4>
                <p className="gate-card-desc">
                  Find suitable clinical trials and participating locations accessible to you across India.
                </p>
                <ul className="gate-card-features">
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> Multi-location accessibility search</li>
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> Verified Ayurvedic trial sites</li>
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> Direct trial coordinator contacts</li>
                </ul>
              </div>
              <div className="gate-card-action">
                <span>Find Suitable Trials</span>
                <ArrowRight size={16} className="arrow-icon ml-1" />
              </div>
            </div>

            {/* CARD 2: STAFF */}
            <div
              className="gate-card gate-card-staff"
              onClick={onSelectStaff}
              tabIndex={0}
              role="button"
              aria-label="AIIA Authorized Staff Portal"
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelectStaff()}
            >
              <div className="gate-card-icon-wrapper staff-icon-wrapper">
                <span className="gate-icon">🔒</span>
              </div>
              <div className="gate-card-body">
                <span className="gate-badge staff-badge">Staff Login Required</span>
                <h4 className="gate-card-title">I'm AIIA Authorized Staff</h4>
                <p className="gate-card-desc">
                  Access CTMS operations: Trial management, doctor directories, patient tracking, pharmacovigilance, and ethics compliance.
                </p>
                <ul className="gate-card-features">
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> Role-based KPI analytics & GCP oversight</li>
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> Automated safety signal detection</li>
                  <li><CheckCircle2 size={14} className="text-emerald-600 inline mr-1" /> CDISC / FHIR data interoperability</li>
                </ul>
              </div>
              <div className="gate-card-action staff-action">
                <span>Staff Portal Login</span>
                <ArrowRight size={16} className="arrow-icon ml-1" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="landing-footer">
        <span>GCP & NDCT Rules 2019 Compliant Architecture</span>
        <span>•</span>
        <span>CDISC SDTM / HL7 FHIR R4 Interoperable</span>
        <span>•</span>
        <span>All India Institute of Ayurveda © 2026</span>
      </div>
    </div>
  );
}
