# ROADMAP.md

> **Current Milestone**: AYURCTMS v2.0 — Production-Grade Upgrade
> **Status**: In Progress

## Must-Haves (from SPEC)
- [ ] FastAPI backend with Swagger docs
- [ ] Advanced clinical charts (Recharts)
- [ ] Interactive India trial map (Leaflet)
- [ ] WCAG 2.1 AA accessibility
- [ ] Real-time WebSocket alerts
- [ ] WHO pharmacovigilance algorithms
- [ ] Hindi language support
- [ ] PWA offline capability
- [ ] 21 CFR Part 11 e-signatures
- [ ] PostgreSQL migration
- [ ] Background worker queue

## Phases

### Phase 1: FastAPI Backend Migration
**Status**: ⬜ Not Started
**Objective**: Replace `http.server` with FastAPI + Pydantic for all 28+ endpoints
**Deliverables**:
- FastAPI application with route modules
- Pydantic request/response models for all endpoints
- Auto-generated Swagger UI at `/docs`
- CORS middleware replacing manual headers
- All 67 existing tests passing against new backend
**Requirements**: SPEC Goal 1

### Phase 2: Advanced Clinical Charts & Dashboard Visualization
**Status**: ⬜ Not Started
**Objective**: Add Recharts-powered interactive data visualizations
**Deliverables**:
- KPI trend line charts (enrollment velocity, AE rates over time)
- Dosha balance radar charts (Vata/Pitta/Kapha pre/post treatment)
- Recruitment burn-down charts (target vs actual)
- Site-wise bar charts with outcome comparisons
- Responsive chart containers with tooltips and legends
**Requirements**: SPEC Goal 5

### Phase 3: Interactive India Trial Map
**Status**: ⬜ Not Started
**Objective**: Leaflet.js geospatial visualization of 9 trial sites
**Deliverables**:
- Interactive India map with colored markers for each trial city
- Click-to-filter: select a city pin to see its active trials
- Recruitment density heatmap overlay toggle
- Patient radius filter (25km / 50km / 100km from clicked location)
- Mobile-responsive map container
**Requirements**: SPEC Goal 4

### Phase 4: GIGW 3.0 Accessibility & Multi-Lingual Support
**Status**: ⬜ Not Started
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
**Status**: ⬜ Not Started
**Objective**: Statistical signal detection + instant push notifications
**Deliverables**:
- PRR (Proportional Reporting Ratio) algorithm implementation
- ROR (Reporting Odds Ratio) algorithm implementation
- Signal detection dashboard with statistical confidence indicators
- WebSocket server endpoint for real-time SAE alerts
- Frontend WebSocket client with toast notification system
- Auto-reconnect and connection status indicator
**Requirements**: SPEC Goals 2, 3

### Phase 6: 21 CFR Part 11 E-Signatures & Cryptographic Audit Trail
**Status**: ⬜ Not Started
**Objective**: Regulatory-grade electronic signatures with tamper-evident audit chain
**Deliverables**:
- Re-authentication modal before signing clinical records
- Intent declaration (e.g., "I certify these results are accurate")
- Merkle tree hash chain for audit trail entries
- Signature verification API endpoint
- E-signature status badges on approved records
**Requirements**: SPEC Goal 9

### Phase 7: PostgreSQL Migration & Background Workers
**Status**: ⬜ Not Started
**Objective**: Enterprise database + async task processing
**Deliverables**:
- SQLAlchemy ORM models replacing raw SQL
- Alembic migration scripts (SQLite → PostgreSQL)
- Dual-mode support (SQLite for dev, PostgreSQL for production)
- Celery + Redis worker setup for background tasks
- Async PDF report generation
- Scheduled CTRI registry scraper (daily cron)
**Requirements**: SPEC Goals 10, 11

### Phase 8: PWA / Offline-First & Final Integration
**Status**: ⬜ Not Started
**Objective**: Progressive Web App with offline data collection
**Deliverables**:
- Service Worker with cache-first strategy for static assets
- IndexedDB local storage for offline form submissions
- Background sync: auto-upload when connection restored
- PWA manifest with AIIA branding (icons, splash screen)
- Install prompt for mobile devices
- Full regression test suite (all 67+ tests passing)
- Production build and deployment
**Requirements**: SPEC Goal 8
