# REQUIREMENTS.md — System Requirements Specification: AYURCTMS v3.0

| ID | Requirement | Description | SPEC Goal | Status |
|:---|:---|:---|:---|:---|
| **REQ-ALCOA-01** | ALCOA+ Audit Metrics | Compute 9 distinct ALCOA+ indices (Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available). | Goal 1 | ✅ Verified |
| **REQ-ALCOA-02** | ALCOA+ Certificate Generator | API endpoint returning a signed ALCOA+ data integrity verification certificate. | Goal 1 | ✅ Verified |
| **REQ-ABDM-01** | ABDM ABHA Verification | Mock sandbox ABHA verification and linking endpoint for clinical trial participants. | Goal 2 | ✅ Verified |
| **REQ-ABDM-02** | FHIR R4 Bundle Support | Generate FHIR R4 Bundles containing ResearchStudy, ResearchSubject, Condition, and MedicationStatement. | Goal 2 | ✅ Verified |
| **REQ-EDC-01** | EDC / HIS Ingest Connector | Standardized REST adapter accepting OpenClinica/REDCap JSON and Hospital Information System admission records. | Goal 2 | ✅ Verified |
| **REQ-PV-01** | MedDRA Coding Engine | Integrated 5-tier MedDRA dictionary hierarchy search (SOC, HLGT, HLT, PT, LLT) with Ayurvedic term cross-references. | Goal 3 | ✅ Verified |
| **REQ-PV-02** | Regulatory Timeline Engine | Statutory deadline calculator for SAE reporting (7-day fatal/life-threatening, 14-day other SAE, 30-day periodic). | Goal 3 | ✅ Verified |
| **REQ-PV-03** | E2B(R3) ICSR XML Export | Compliant XML safety report exporter for submission to NPvCC / PvPI / CDSCO. | Goal 3 | ✅ Verified |
| **REQ-DPDP-01** | DPDP Consent Management | Digital consent record creation with purpose specification, multilingual notice, and withdrawal tracking. | Goal 4 | ✅ Verified |
| **REQ-DPDP-02** | Data Principal Rights Queue | Processing pipeline for user requests: right to access, correction, erasure, and grievance redressal under DPDP 2023. | Goal 4 | ✅ Verified |
| **REQ-CDISC-01** | Complete SDTM Domains | Export structured SDTM domains: DM (Demographics), TS (Trial Summary), AE (Adverse Events), EX (Exposure), DS (Disposition), LB (Laboratory). | Goal 5 | ✅ Verified |
| **REQ-CDISC-02** | ADaM Dataset Export | Export ADSL (Subject-Level Analysis) and ADAE (Adverse Event Analysis) datasets. | Goal 5 | ✅ Verified |
| **REQ-CDISC-03** | Define-XML 2.0 Generator | Generate W3C-valid Define-XML 2.0 metadata file with stylesheet link. | Goal 5 | ✅ Verified |
| **REQ-UI-01** | Investigator Dashboard | Dedicated PI view featuring recruitment burn-down, subject visit windows, and protocol deviation resolution. | Goal 6 | ✅ Verified |
| **REQ-UI-02** | Ethics Committee Dashboard | Dedicated IEC view featuring protocol approval queue, 21 CFR Part 11 e-signatures, and GCP checklists. | Goal 6 | ✅ Verified |
| **REQ-UI-03** | NPvCC Safety Dashboard | Dedicated Safety Officer view featuring regulatory timeline countdowns, MedDRA coder, and PRR/ROR signal alerts. | Goal 6 | ✅ Verified |
| **REQ-UI-04** | Leadership Dashboard | Executive view featuring pan-India GIS map, portfolio KPIs, and institutional ALCOA+ compliance index. | Goal 6 | ✅ Verified |
| **REQ-SEC-01** | Security & Data Residency | CERT-In compliant security headers, CORS origin enforcement, and audit trail immutability. | Goal 7 | ✅ Verified |
