# ROADMAP.md

> **Current Milestone**: AYURCTMS v1.0 Production Prototype
> **Status**: Completed

## Phases

### Phase 1: Data Model & Synthetic Clinical Seed Engine
**Status**: ✅ Completed
- SQLite database schema & seed scripts for AYURCTMS (`doctors`, `patients`, `ayur_trials`, `trial_sites`, `approvals`, `gcp_checklist`, `patient_treatments`, `patient_visits`, `ayur_adverse_events`, `safety_signals`, `ayur_notifications`, `ayur_audit_trail`).
- Seeded 11 doctors, 25 patients, 8 trials, 9 sites across India, adverse events (including Ramlal Sharma / AYU-002 / Skin Rash cluster), 5 approvals, GCP checklist.

### Phase 2: Backend REST Services & Clinical Intelligence Endpoints
**Status**: ✅ Completed
- Patient trial-location matching algorithm with accessibility scoring.
- Authentication service (`AIIA001` / `AIIA@123`).
- Overlap detection for new trial planning.
- Pharmacovigilance safety signal detection engine.
- GCP checklist status manager, Report generator (CSV/PDF), and Global search engine.

### Phase 3: Modern Responsive Frontend UI & Interaction Flow
**Status**: ✅ Completed
- Landing page gate ("Who are you?" with Patient vs AIIA Authorized Staff cards).
- Patient trial-matching flow with recommendation cards and detail modal.
- Staff login screen with demo credentials.
- Staff dashboard with 3 top KPI cards (Doctors, Patients, PV), Active trial progress bars, interactive Sites/Locations explorer (Mumbai, Delhi, Kolkata, Kerala, Lucknow, Noida, Jaipur, Hyderabad, Bengaluru).
- Complete operational modules: Trials, New Trial Planning with Overlap Warning, Pending Approvals, GCP Checklist, Doctor Directory, Patient Profiles with 8-Stage Treatment Timeline, Pharmacovigilance & Safety Signals, Reports, Interoperability (FHIR/CDISC), and Audit Trail.

### Phase 4: Quality Assurance & Backend Verification
**Status**: ✅ Completed
- Comprehensive automated test suite for all AYURCTMS backend endpoints and logic (`tests/test_ayur_ctms.py` and `tests/test_compliance.py`).
- 9 core backend requirements fully audited and verified.

### Phase 5: Modern React Ecosystem Migration
**Status**: ✅ Completed
- Scaffolded and configured modern Vite + React application in `frontend/` with Lucide Icons.
- Configured development proxy forwarding `/api` to backend Python server (`http://127.0.0.1:8000`).
- Created modular React components:
  - `GovTopBar`: GIGW Government of India & Ministry of Ayush Identity strip with accessibility controls and tricolor ribbon.
  - `LandingGate`: Dual-path entry portal (Patient vs AIIA Staff) with official institute branding.
  - `PatientPortal`: Clinical trial discovery and location matching with accessibility filters and mandatory disclaimers.
  - `StaffAuthModal`: Staff authentication with quick demo credentials and persona selection.
  - `StaffPortal`: Complete operational CTMS interface with sidebar navigation, sticky header, global search, and notification center.
  - `DashboardView`: Hero KPI cards (Doctors, Patients, PV), active trial velocity, and recruitment summaries.
  - `SitesExplorerView`: Multi-center city cards across 9 regions with outcome trend charts.
  - `ActiveTrialsView`: Protocol directory with enrollment progress and details modal.
  - `TrialInfoView` & `CreateTrialModal`: Trial registry with Intelligent Overlap Warning engine.
  - `PatientsView`: Patient roster and 8-stage longitudinal clinical treatment timeline (Ramlal Sharma).
  - `PharmacovigilanceView`: Safety signal detection, AE cluster alerts, and expedited SAE reporting modal.
  - `ApprovalsView`: Ethics Committee & DCGI review workflow.
  - `GcpChecklistView`: Interactive 8-point Good Clinical Practice auditor checklist with verification stamps.
  - `ReportsView`: Live report data generator with 7 institutional report types and CSV export.
  - `InteropView`: Interactive HL7 FHIR R4 & CDISC SDTM dataset pipeline demonstrator with immutable audit trail.
  - `CtriExplorerView`: CTRI registry database browser (75 trials) with verified official record links.
- Built production bundle (`npm run build`) targeting `dist/` and integrated with Python backend server.
- Verified all 67 test suites pass with 100% success rate.
