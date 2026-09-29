# SPEC.md — Project Specification: AYURCTMS v3.0

> **Status**: `FINALIZED`  
> **Project Name**: AYURCTMS v3.0 (Enterprise Regulatory CTMS & Interoperability)  
> **Subtitle**: CDISC Submission Datasets, ABDM/EDC Interoperability, DPDP Privacy & NPvCC Pharmacovigilance  
> **Predecessor**: v2.0 (archived in `.gsd/archive/v2.0/`)  

---

## 1. Vision
Transform AYURCTMS from an operational clinical dashboard into an enterprise-grade, regulatory-evaluable Clinical Trial Management System (CTMS) for the **All India Institute of Ayurveda (AIIA)** and the **Ministry of Ayush**. 

v3.0 provides:
1. **Real-Time Portfolio & Per-Study Drill-Down** with verifiable ALCOA+ data integrity indices.
2. **HL7 FHIR R4 & ABDM Interoperability** with bidirectional EDC (OpenClinica / REDCap) and Hospital Information System (e-Hospital / Ayush HIS) connectors.
3. **Institutional NPvCC Pharmacovigilance Module** featuring MedDRA/WHO Drug hierarchical coding, automated 7/14/30-day regulatory timeline countdowns, and E2B(R3) ICSR export.
4. **DPDP Act (2023) Consent & Privacy Controls** covering digital multilingual consent artifacts, revocation lifecycles, and Data Principal rights.
5. **Submission-Ready CDISC Datasets** covering full SDTM domains (DM, TS, AE, EX, DS, LB), ADaM datasets (ADSL, ADAE), and Define-XML 2.0 with XML stylesheets.
6. **Tailored Persona Dashboards** for Principal Investigators, Ethics Committees, Pharmacovigilance Officers, and Institutional Leadership.
7. **Cloud Data Residency & CERT-In / ISO 27001 Security Hardening**.

---

## 2. Goals

1. **ALCOA+ Data Integrity & Audit Hardening**: Formalize Attributable, Legible, Contemporaneous, Original, and Accurate (+ Complete, Consistent, Enduring, Available) compliance metrics across all trial records, backed by SHA-256 hash chaining and automated integrity scorecards.
2. **ABDM & EDC / HIS Interoperability**: Implement Ayushman Bharat Digital Mission (ABDM) Milestone 1/2/3 scaffolding (ABHA verification, HIP/HIU data bridge) and FHIR R4 clinical trial resources (`ResearchStudy`, `ResearchSubject`, `Condition`, `MedicationStatement`), alongside JSON ingest connectors for OpenClinica/REDCap EDC and hospital HIS.
3. **AIIA NPvCC Safety Module & MedDRA Coding**: Expand the pharmacovigilance engine with a 5-level MedDRA ontology search (SOC, HLGT, HLT, PT, LLT), WHO Drug dictionary structure, automated regulatory timeline trackers (7-day fatal/life-threatening SAE, 14-day non-fatal SAE, 30-day periodic), and E2B(R3) XML export.
4. **DPDP Compliance & Consent Governance**: Build a dedicated privacy module implementing the Digital Personal Data Protection Act (2023) requirements: dynamic informed consent logging, multilingual notices, withdrawal mechanisms, Data Principal access/correction/erasure requests, and DPO audit logs.
5. **Submission-Ready CDISC Exporter**: Extend existing prototypes to generate complete, structured SDTM datasets (TS, DM, AE, EX, DS, LB), ADaM analysis datasets (ADSL, ADAE), and W3C-valid Define-XML 2.0 metadata with XSL stylesheet support.
6. **Persona-Specific Dashboards**: Deliver tailored views in the web portal for:
   - **Investigators**: Trial recruitment velocity, visit windows, protocol deviation logging.
   - **Ethics Committee (IEC)**: Clearance review queue, 21 CFR Part 11 e-signature approvals, GCP checklists.
   - **Pharmacovigilance (NPvCC)**: PRR/ROR signal alerts, regulatory countdown clock, SAE triage inbox.
   - **Institutional Leadership**: Portfolio overview, GIS multi-center spread, recruitment forecast, audit summaries.
7. **CERT-In / ISO 27001 Cloud Security Profile**: Enforce strict HTTP security headers, data residency configuration, RBAC privilege boundaries, and automated vulnerability scanning.

---

## 3. Non-Goals (Out of Scope for v3.0)
- Commercial proprietary MedDRA license server integration (standardized local open ontology tables and synthetic hierarchies will be provided).
- Live CDAC / NHA production ABDM gateway credentials (sandbox-compliant mock client and gateway interface will be implemented).
- Direct SAS proprietary binary XPT file compilers (datasets will export in standard CDISC JSON, CSV, and Define-XML 2.0 formats).

---

## 4. Users & Personas
- **Principal Investigator (PI)**: Manages site recruitment, tracks visits within window, logs deviations, signs clinical approvals.
- **Ethics Committee (IEC) Member**: Reviews study protocols, inspects informed consent templates, conducts 21 CFR Part 11 e-signatures on clearances.
- **NPvCC Safety Officer**: Codes adverse events with MedDRA terms, monitors PRR/ROR statistical signals, files E2B(R3) safety reports within statutory timelines.
- **Institutional Director / Ayush Leadership**: Monitors pan-India trial progress, reviews recruitment burn-down, audits compliance scores.
- **Data Protection Officer (DPO)**: Audits consent compliance, processes Data Principal rights requests under DPDP.

---

## 5. Constraints
- Zero breaking changes to existing 28+ v2.0 endpoints and React 18/19 components.
- 100% free, open-source dependencies without commercial vendor lock-in.
- Dual SQLite (local dev) / PostgreSQL (production) database compatibility.
- Local git commits only; strictly **no remote push**.

---

## 6. Success Criteria
- [ ] ALCOA+ audit score calculated per trial and system-wide with downloadable compliance certificate.
- [ ] ABDM ABHA verification, consent artifact models, and FHIR R4 ResearchStudy/ResearchSubject endpoints functional.
- [ ] EDC/HIS ingestion adapter successfully parses and maps external trial payloads.
- [ ] MedDRA search returns SOC -> PT terms; 7-day/14-day regulatory countdown displays active urgency.
- [ ] E2B(R3) ICSR XML report generated for serious adverse events.
- [ ] DPDP consent lifecycle records creation, consent revocation, and Data Principal rights logs.
- [ ] CDISC exporter produces SDTM (DM, TS, AE, EX, DS), ADaM (ADSL, ADAE), and valid Define-XML 2.0.
- [ ] 4 tailored persona dashboard views fully accessible in the Staff Portal.
- [ ] Comprehensive automated test suite passes with 100% success rate.
