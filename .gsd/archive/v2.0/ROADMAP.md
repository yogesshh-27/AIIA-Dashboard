# ROADMAP.md

> **Current Milestone**: AYURCTMS v2.0 — Production-Grade Upgrade
> **Status**: ✅ Completed (74/74 tests passing)

## Must-Haves (from SPEC)
- [x] FastAPI backend with Swagger docs
- [x] Advanced clinical charts (Recharts)
- [x] Interactive India trial map (Leaflet)
- [x] WCAG 2.1 AA accessibility
- [x] Real-time WebSocket alerts
- [x] WHO pharmacovigilance algorithms
- [x] Hindi language support
- [x] PWA offline capability
- [x] 21 CFR Part 11 e-signatures
- [x] PostgreSQL migration
- [x] Background worker queue

## Phases

### Phase 1: FastAPI Backend Migration
**Status**: ✅ Completed
**Objective**: Replace `http.server` with FastAPI + Pydantic for all 28+ endpoints
**Deliverables**:
- FastAPI application with route modules (`api/routes/`)
- Pydantic request/response models for all endpoints
- Auto-generated Swagger UI at `/docs` and ReDoc at `/redoc`
- CORS middleware replacing manual headers
- All existing tests passing against new backend
**Requirements**: SPEC Goal 1

### Phase 2: Advanced Clinical Charts & Dashboard Visualization
**Status**: ✅ Completed
**Objective**: Add Recharts-powered interactive data visualizations
**Deliverables**:
- KPI trend line charts (enrollment velocity, AE rates over time)
- Dosha balance radar charts (Vata/Pitta/Kapha pre/post treatment)
- Recruitment burn-down charts (target vs actual)
- Site-wise bar charts with outcome comparisons
- Responsive chart containers with tooltips and legends
**Requirements**: SPEC Goal 5

### Phase 3: Interactive India Trial Map
**Status**: ✅ Completed
**Objective**: Leaflet.js geospatial visualization of 9 trial sites
**Deliverables**:
- Interactive India map with colored markers for each trial city (`IndiaTrialMap.jsx`)
- Click-to-filter: select a city pin to see its active trials
- Recruitment density heatmap overlay toggle
- Side panel metrics with status and hospital associations
- Mobile-responsive map container
**Requirements**: SPEC Goal 4

### Phase 4: GIGW 3.0 Accessibility & Multi-Lingual Support
**Status**: ✅ Completed
**Objective**: WCAG 2.1 AA compliance + Hindi/English language switcher
**Deliverables**:
- Font size controls (A-, A, A+) in GovTopBar
- High-contrast mode toggle (Standard / Dark / Yellow-on-Black)
- Full keyboard navigation with visible focus indicators
- ARIA landmarks, live regions, and screen reader labels
- i18next integration with Hindi (`hi`) and English (`en`) locales
- Browser SpeechRecognition voice search for patient portal
**Requirements**: SPEC Goals 6, 7

### Phase 5: WHO Pharmacovigilance Algorithms & Real-Time WebSocket Alerts
**Status**: ✅ Completed
**Objective**: Statistical signal detection + instant push notifications
**Deliverables**:
- PRR (Proportional Reporting Ratio) algorithm implementation with 95% CI
- ROR (Reporting Odds Ratio) algorithm implementation with 95% CI
- Yates' Chi-squared statistical test and Evans et al. criteria evaluation
- Signal detection dashboard with statistical confidence indicators
- WebSocket server endpoint (`/ws/alerts`) for real-time SAE alerts
- Frontend WebSocket client (`useWebSocketAlerts.js`) with live indicator and toast notifications
**Requirements**: SPEC Goals 2, 3

### Phase 6: 21 CFR Part 11 E-Signatures & Cryptographic Audit Trail
**Status**: ✅ Completed
**Objective**: Regulatory-grade electronic signatures with tamper-evident audit chain
**Deliverables**:
- Re-authentication modal before signing clinical records
- Intent declaration (e.g., "I certify these results are accurate")
- SHA-256 cryptographic audit chain for signature blocks
- Signature verification API endpoint (`/api/audit/esign/verify/{id}`)
- E-signature status badges and verification certificates on approved records
**Requirements**: SPEC Goal 9

### Phase 7: PostgreSQL Migration & Background Workers
**Status**: ✅ Completed
**Objective**: Enterprise database + async task processing
**Deliverables**:
- SQLAlchemy ORM models (`services/db_models.py`)
- Alembic migration scripts (`migrations/versions/`)
- Dual-mode support (SQLite for dev, PostgreSQL for production)
- Background worker queue (`services/background_tasks.py`)
- Async PDF/CSV report generation endpoints (`/api/reports/async-generate`)
- Scheduled CTRI registry scraper task
**Requirements**: SPEC Goals 10, 11

### Phase 8: PWA / Offline-First & Final Integration
**Status**: ✅ Completed
**Objective**: Progressive Web App with offline data collection
**Deliverables**:
- Service Worker (`sw.js`) with cache-first strategy for static assets
- IndexedDB local storage engine (`offlineStorage.js`) for offline data collection
- Background sync capability for network recovery
- PWA manifest (`manifest.json`) with AIIA branding
- Full regression test suite passing (74/74 tests, 100%)
- Production build verified in `dist/`
**Requirements**: SPEC Goal 8
