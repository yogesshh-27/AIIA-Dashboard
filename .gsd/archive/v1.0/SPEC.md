# SPEC.md — Project Specification

> **Status**: `FINALIZED`
> **Project Name**: AYURCTMS
> **Subtitle**: AIIA Clinical Trial Management & Research Portal
> **Problem Statement ID**: 26046

## Vision
AYURCTMS is a real-time, cloud-based, GCP-compliant Clinical Trial Management System (CTMS) purpose-built for Ayurveda clinical research at the All India Institute of Ayurveda (AIIA). It bridges patient trial discovery with rigorous institutional governance—offering intelligent patient-location trial matching, multi-site operational tracking across India, doctor & participant lifecycle management with 8-stage treatment flows, integrated pharmacovigilance with automated safety signal detection, CTRI/NDCT Rules 2019 compliance, and CDISC/FHIR data interoperability.

## Goals
1. **Dual Entry Flow**: Distinct landing page experience separating public patient trial-discovery from authenticated AIIA research staff management.
2. **Patient Trial-Location Matching**: Clean intake form matching patients to recruiting Ayurvedic trials across 9 Indian cities without medical diagnosis overreach.
3. **Staff CTMS Portal**: Full operational suite following hand-drawn institutional dashboard layout: 3 top KPI cards (Doctors, Patients, PV), Active Trial progress tracking, interactive Sites/Locations explorer, and smart trial planning with overlap detection.
4. **Clinical Governance & Safety**: Interactive GCP compliance checklist, Pending Approvals workflow, dedicated Pharmacovigilance module with cluster signal detection, immutable audit trail, and CDISC/FHIR interoperability pipeline.
5. **Demonstration Dataset**: Realistic synthetic data featuring 10+ doctors, 25+ patients, 8+ trials, 9 sites, 10+ adverse events, approvals, and verified treatment flows (including Ramlal / AYU-002 / Skin Rash scenario).

## Non-Goals (Out of Scope)
- Commercial EHR / Hospital billing or inpatient bed management (the app is strictly for clinical trials).
- Automated AI medical diagnosis or claiming legal authority over regulatory approvals.
- Storing real unmasked patient identification data.

## Users & Personas
- **Patient / Research Participant**: Searches for nearby relevant clinical trials by condition and accessible locations.
- **AIIA Clinical Research Staff / Investigator**: Manages trial protocols, participants, doctor assignments, multi-site operations, safety event reporting, and GCP compliance.
- **Institutional Leadership / Auditor**: Inspects aggregated KPIs, multi-site progress, pharmacovigilance signals, and regulatory reports.

## Key Constraints & Standards
- Python standard HTTP server + SQLite backend with zero external runtime dependencies.
- Vanilla CSS + JavaScript with medical/research aesthetic (Deep Teal `#0d5c56`, Slate `#1e293b`, Soft Grey `#f8fafc`).
- Fully responsive across desktop, laptop, tablet, and mobile.
