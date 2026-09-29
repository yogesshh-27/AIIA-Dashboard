# ROADMAP.md — AYURCTMS v3.0

> **Milestone**: AYURCTMS v3.0 — Enterprise Regulatory CTMS, Interoperability & Submission Analytics  
> **Status**: ✅ Completed (57/57 unit & integration tests passing 100%, Frontend Production Build Verified)  

---

## Must-Haves (from SPEC & REQUIREMENTS)
- [x] ALCOA+ Audit Hardening & Data Quality Evaluation Engine
- [x] ABDM Interoperability & EDC / HIS Connectors
- [x] AIIA NPvCC Safety Module (MedDRA Coding, Regulatory Timelines & E2B(R3) Export)
- [x] DPDP Consent & Privacy Engine
- [x] Submission-Ready CDISC Exporter (SDTM, ADaM, Define-XML 2.0)
- [x] Persona-Tailored Portals (PI, Ethics Committee, Safety/NPvCC, Leadership)
- [x] Comprehensive Automated Tests passing 100%

---

## Phases

### Phase 1: ALCOA+ Audit Hardening & Data Quality Evaluation Engine
**Status**: ✅ Completed  
**Objective**: Build comprehensive ALCOA+ compliance calculation, audit scorecards, and verifiable certificate generation.  
**Deliverables**:
- Service module `services/alcoa_engine.py` evaluating the 9 ALCOA+ principles.
- Endpoints: `GET /api/compliance/alcoa/metrics`, `GET /api/compliance/alcoa/certificate/{trial_id}`.
- Automated tests verifying ALCOA+ calculations (`tests/test_alcoa_engine.py`).
**Requirements**: REQ-ALCOA-01, REQ-ALCOA-02

### Phase 2: ABDM Interoperability & EDC / HIS Connector Adapter Layer
**Status**: ✅ Completed  
**Objective**: Provide ABDM gateway mock endpoints (ABHA verification, HIP/HIU consent), FHIR R4 Bundle generator, and EDC/HIS ingestion pipelines.  
**Deliverables**:
- Service module `services/abdm_edc_service.py` with ABHA verify, FHIR R4 Bundle builders, and EDC payload parsers.
- Endpoints: `POST /api/interop/abdm/verify-abha`, `GET /api/interop/fhir/bundle`, `POST /api/interop/edc/ingest`.
- Automated tests for ABDM & EDC connectors (`tests/test_abdm_edc.py`).
**Requirements**: REQ-ABDM-01, REQ-ABDM-02, REQ-EDC-01

### Phase 3: AIIA NPvCC Pharmacovigilance Module (MedDRA/WHO Drug & Timelines)
**Status**: ✅ Completed  
**Objective**: Implement 5-tier MedDRA dictionary hierarchy search, statutory regulatory countdown timers (7d/14d/30d), and E2B(R3) ICSR XML generation.  
**Deliverables**:
- Service module `services/meddra_service.py` with MedDRA term lookup and regulatory timeline calculator.
- Endpoints: `GET /api/pv/meddra/search`, `GET /api/pv/regulatory/timelines`, `GET /api/pv/export/e2b/{event_id}`.
- Automated tests for MedDRA mapping, timeline checks, and E2B XML format (`tests/test_meddra_service.py`).
**Requirements**: REQ-PV-01, REQ-PV-02, REQ-PV-03

### Phase 4: Informed Consent & DPDP Act (2023) Privacy Engine
**Status**: ✅ Completed  
**Objective**: Build patient consent lifecycle management, multilingual consent artifact tracking, consent withdrawal, and Data Principal rights processing under DPDP 2023.  
**Deliverables**:
- Service module `services/dpdp_service.py` managing consent records, withdrawal tokens, and DPO logs.
- Dedicated routes in `api/routes/privacy.py`.
- Endpoints: `POST /api/privacy/consent/record`, `POST /api/privacy/consent/withdraw`, `GET /api/privacy/dpo/audit-log`, `POST /api/privacy/rights-request`.
- Automated tests for DPDP compliance rules (`tests/test_dpdp_service.py`).
**Requirements**: REQ-DPDP-01, REQ-DPDP-02

### Phase 5: Submission-Ready CDISC Exporter (SDTM, ADaM & Define-XML 2.0)
**Status**: ✅ Completed  
**Objective**: Upgrade CDISC exporter to generate full SDTM domains (DM, TS, AE, EX, DS, LB), ADaM datasets (ADSL, ADAE), and W3C-valid Define-XML 2.0 with XML stylesheets.  
**Deliverables**:
- Service module `services/cdisc_submission_exporter.py`.
- Endpoints: `GET /api/interop/cdisc/sdtm/{domain}`, `GET /api/interop/cdisc/adam/{dataset_name}`, `GET /api/interop/cdisc/define-xml-2`.
- Automated validation tests for SDTM/ADaM and XML schema compliance (`tests/test_cdisc_submission.py`).
**Requirements**: REQ-CDISC-01, REQ-CDISC-02, REQ-CDISC-03

### Phase 6: Persona-Tailored Portals & GCP E-Signature Integration
**Status**: ✅ Completed  
**Objective**: Integrate role-based tailored dashboards into the React UI for Investigators, Ethics Committee, Safety/NPvCC, and Institutional Leadership.  
**Deliverables**:
- New views: `AlcoaAuditView.jsx` (ALCOA+ Audit & Certificate Center) and `DpdpPrivacyView.jsx` (DPDP Act 2023 Privacy Console).
- Updated `StaffSidebar.jsx` and `StaffPortal.jsx` with dedicated navigation routes.
- Updated centralized `api.js` client with all v3.0 endpoints.
- Verified frontend build with Vite (0 errors).
- End-to-end integration test suite `tests/test_v3_api.py` passing 15/15 tests.
**Requirements**: REQ-UI-01, REQ-UI-02, REQ-UI-03, REQ-UI-04, REQ-SEC-01
