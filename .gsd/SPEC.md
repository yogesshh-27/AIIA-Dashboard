# SPEC.md — Project Specification

> **Status**: `FINALIZED`
> **Project Name**: AYURCTMS v2.0
> **Subtitle**: Production-Grade Upgrade — Frontend & Backend Modernization
> **Predecessor**: v1.0 (archived in `.gsd/archive/v1.0/`)

## Vision
Elevate AYURCTMS from a functional prototype to an enterprise-grade, production-ready Clinical Trial Management System. This milestone focuses on 11 free, open-source upgrades across frontend and backend — adding interactive geospatial visualization, advanced clinical charts, WCAG accessibility compliance, FastAPI migration, WHO-standard pharmacovigilance algorithms, real-time WebSocket alerts, and offline-first PWA capabilities.

## Goals
1. **Backend Modernization**: Migrate from `http.server` to FastAPI with Pydantic validation, auto-generated Swagger docs, and async concurrency.
2. **Advanced Pharmacovigilance**: Implement WHO-standard PRR/ROR statistical disproportionality algorithms for safety signal detection.
3. **Real-Time Alerts**: WebSocket-based instant SAE push notifications to Safety Monitor dashboards.
4. **Interactive India Trial Map**: Leaflet.js + OpenStreetMap geospatial visualization with recruitment heatmaps and radius filters.
5. **Advanced Clinical Charts**: Recharts-powered KPI timelines, Dosha radar charts, and recruitment burn-down visualizations.
6. **GIGW 3.0 / WCAG 2.1 AA Accessibility**: Font resizer, high-contrast mode, screen reader support, keyboard navigation.
7. **Multi-Lingual Support**: i18next-based Hindi/English language switcher with browser SpeechRecognition voice search.
8. **PWA / Offline-First**: Service Workers + IndexedDB for field data collection at rural Ayush clinics.
9. **21 CFR Part 11 E-Signatures**: Dual-factor electronic signatures with Merkle tree cryptographic audit hash chain.
10. **PostgreSQL + Alembic**: Enterprise database migration with version-controlled schema changes.
11. **Background Worker Queue**: Celery/Redis for async PDF generation, CDISC exports, and scheduled CTRI scraping.

## Non-Goals (Out of Scope)
- TypeScript migration (deferred to v3.0 — not essential for functionality).
- Commercial cloud database hosting (PostgreSQL runs locally or on free tiers).
- Bhashini API integration (using free browser SpeechRecognition instead).
- Mobile native apps (PWA covers mobile needs).

## Users & Personas
- **Patient / Research Participant**: Discovers trials via interactive map, uses Hindi voice search.
- **Field Investigator (Rural)**: Records patient data offline via PWA, syncs when connected.
- **AIIA Clinical Staff**: Uses advanced charts and real-time safety alerts for decision-making.
- **Ethics Board / Regulator**: Verifies compliance via e-signatures and cryptographic audit trail.

## Constraints
- All tools and libraries must be **100% free and open-source**.
- Backward compatibility with existing v1.0 API contracts and data.
- Zero downtime migration — existing deployed site must remain functional.
- Python 3.10+ for backend, React 19 + Vite 8 for frontend.

## Success Criteria
- [x] FastAPI serves all 28+ existing endpoints with auto-generated `/docs` Swagger UI
- [x] PRR/ROR algorithms flag statistical safety signals from existing AE dataset
- [x] WebSocket connection pushes real-time SAE alerts to connected dashboards
- [x] Interactive India map renders 9 trial sites with click-to-filter functionality
- [x] Recharts renders at least 3 chart types (line, bar, radar) in DashboardView
- [x] WCAG 2.1 AA: font resizer, contrast toggle, and full keyboard navigation work
- [x] Hindi translation covers all UI labels and navigation elements
- [x] PWA installs on mobile and caches critical pages for offline access
- [x] E-signature workflow requires re-authentication before approving clinical records
- [x] All 74 tests continue to pass after upgrades (100% test success rate)
