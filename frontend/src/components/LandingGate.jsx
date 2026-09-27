import React from 'react';
import { ArrowRight, CheckCircle2, ShieldCheck, User } from 'lucide-react';

export default function LandingGate({ onSelectPatient, onSelectStaff }) {
  return (
    <div id="landing-gate" className="landing-gate-view">
      {/* Top Institutional Header */}
      <div className="landing-header">
        <div className="landing-brand">
          <img
            src="/logos/aiia-logo.svg"
            alt="All India Institute of Ayurveda"
            className="landing-brand-aiia-logo"
            width="56"
            height="56"
          />
          <div className="landing-brand-text">
            <div className="landing-brand-hindi">अखिल भारतीय आयुर्वेद संस्थान</div>
            <h1>ALL INDIA INSTITUTE OF AYURVEDA</h1>
            <p>An Autonomous Organization under the Ministry of Ayush, Govt. of India • AYURCTMS Portal</p>
          </div>
          <div className="landing-brand-divider" aria-hidden="true"></div>
          <img
            src="/logos/ayush-logo.svg"
            alt="Ministry of Ayush"
            className="landing-brand-ayush-logo"
            height="44"
          />
        </div>
        <div className="landing-official-badge">
          <span>🌿 Clinical Trial Management Portal</span>
        </div>
      </div>

      {/* Main Horizontal Layout: Image on Left, Logins on Right (divided up & down) */}
      <div className="landing-horizontal-layout">
        
        {/* LEFT COLUMN: HERO IMAGE & CLINICAL RESEARCH SHOWCASE */}
        <div className="landing-left-visual">
          <div className="landing-visual-card">
            <img
              src="/images/aiia_hero_research.jpg"
              alt="AIIA High-Tech Ayurvedic Clinical Science Laboratory"
              className="landing-visual-img"
            />
            <div className="landing-visual-overlay">
              <div className="landing-visual-top-badge">
                <span>🔬 AYURCTMS Evidence Platform</span>
              </div>

              <div className="landing-visual-badges">
                <span className="visual-badge badge-protocols">
                  🌿 75+ Standardized Ayurveda Protocols
                </span>
                <span className="visual-badge badge-sites">
                  🏛️ 9 Verified AIIA Clinical Research Sites
                </span>
                <span className="visual-badge badge-gcp">
                  📜 100% GCP & Rule 2 CTRI Compliant
                </span>
              </div>

              <p className="landing-visual-tagline">
                Advancing evidence-based Ayurvedic medicine through modern CDISC/FHIR informatics &amp; nation-wide multicentric clinical research.
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: PORTAL SELECTION (LOGINS DIVIDED UP AND DOWN) */}
        <div className="landing-right-portals">
          <div className="landing-title-block">
            <div className="portal-kicker">Ministry of Ayush • AYURCTMS</div>
            <h2>AIIA Clinical Trial Management &amp; Research Portal</h2>
            <p>
              A real-time, cloud-based, GCP-compliant Clinical Trial Management System (CTMS) for Ayurveda research,
              with CDISC/FHIR-interoperable data, role-based KPIs, and integrated ethics, regulatory and pharmacovigilance tracking.
            </p>
          </div>

          <div className="gate-selection-container">
            <div className="gate-selection-header">
              <h3 className="gate-prompt">Who are you?</h3>
              <p className="gate-subprompt">Select your portal to continue</p>
            </div>

            {/* STACKED LOGINS (DIVIDED UP AND DOWN) */}
            <div className="gate-cards-stack">
              
              {/* TOP CARD: PATIENT */}
              <div
                className="gate-card gate-card-horizontal gate-card-patient"
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
                  <div className="gate-card-header-row">
                    <span className="gate-badge">Public Access</span>
                    <span className="gate-direct-indicator">No Login Required</span>
                  </div>
                  <h4 className="gate-card-title">I'm a Patient</h4>
                  <p className="gate-card-desc">
                    Find suitable clinical trials and participating locations accessible to you across India.
                  </p>
                  <ul className="gate-card-features-inline">
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> Multi-location search</li>
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> Verified trial sites</li>
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> Direct coordinator contacts</li>
                  </ul>
                </div>
                <div className="gate-card-action-side">
                  <div className="action-btn-pill">
                    <span>Find Suitable Trials</span>
                    <ArrowRight size={16} className="arrow-icon ml-1.5" />
                  </div>
                </div>
              </div>

              {/* BOTTOM CARD: STAFF */}
              <div
                className="gate-card gate-card-horizontal gate-card-staff"
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
                  <div className="gate-card-header-row">
                    <span className="gate-badge staff-badge">Staff Login Required</span>
                    <span className="gate-direct-indicator staff-indicator">AIIA Credentials</span>
                  </div>
                  <h4 className="gate-card-title">I'm AIIA Authorized Staff</h4>
                  <p className="gate-card-desc">
                    Access CTMS operations: Trial management, doctor directories, patient tracking, pharmacovigilance, and ethics compliance.
                  </p>
                  <ul className="gate-card-features-inline">
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> Role-based KPI analytics</li>
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> Automated safety alerts</li>
                    <li><CheckCircle2 size={13} className="text-emerald-600 inline mr-1 flex-shrink-0" /> CDISC / FHIR data export</li>
                  </ul>
                </div>
                <div className="gate-card-action-side">
                  <div className="action-btn-pill staff-btn-pill">
                    <span>Staff Portal Login</span>
                    <ArrowRight size={16} className="arrow-icon ml-1.5" />
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>

      {/* Footer */}
      <div className="landing-footer">
        <span>GCP &amp; NDCT Rules 2019 Compliant Architecture</span>
        <span>•</span>
        <span>CDISC SDTM / HL7 FHIR R4 Interoperable</span>
        <span>•</span>
        <span>All India Institute of Ayurveda © 2026</span>
      </div>
    </div>
  );
}
