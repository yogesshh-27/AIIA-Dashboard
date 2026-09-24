# ROADMAP.md

> **Current Milestone**: AYURCTMS v1.0 Production Prototype
> **Status**: In Progress

## Phases

### Phase 1: Data Model & Synthetic Clinical Seed Engine
**Status**: 🚀 In Progress
- SQLite database schema & seed scripts for AYURCTMS (`doctors`, `patients`, `ayur_trials`, `trial_sites`, `approvals`, `gcp_checklist`, `patient_treatments`, `patient_visits`, `ayur_adverse_events`, `safety_signals`, `ayur_notifications`, `ayur_audit_trail`).
- Seed 10+ doctors, 25+ patients, 8+ trials, 9 sites across India, 10+ adverse events (including Ramlal / AYU-002 / Skin Rash), 5 approvals, GCP checklist.

### Phase 2: Backend REST Services & Clinical Intelligence Endpoints
**Status**: ⬜ Pending
- Patient trial-location matching algorithm with accessibility scoring.
- Authentication service (Mock `AIIA001` / `AIIA@123`).
- Overlap detection for new trial planning.
- Pharmacovigilance safety signal detection engine.
- GCP checklist status manager, Report generator (CSV/PDF), and Global search engine.

### Phase 3: Modern Responsive Frontend UI & Interaction Flow
**Status**: ⬜ Pending
- Landing page gate ("Who are you?" with Patient vs AIIA Authorized Staff cards).
- Patient trial-matching flow with recommendation cards and detail modal.
- Staff login screen with demo credentials.
- Staff dashboard with 3 top KPI cards (Doctors, Patients, PV), Active trial progress bars, interactive Sites/Locations explorer (Mumbai, Delhi, Kolkata, Kerala, Lucknow, Noida, Jaipur, Hyderabad, Bengaluru).
- Complete operational modules: Trials, New Trial Planning with Overlap Warning, Pending Approvals, GCP Checklist, Doctor Directory, Patient Profiles with 8-Stage Treatment Timeline, Pharmacovigilance & Safety Signals, Reports, Interoperability (FHIR/CDISC), and Audit Trail.

### Phase 4: Quality Assurance, Verification & Final Polish
**Status**: ⬜ Pending
- Comprehensive automated test suite for all AYURCTMS backend endpoints and logic.
- Browser subagent visual verification of patient flow, staff dashboard, and all modules.
- Final documentation and walkthrough.
