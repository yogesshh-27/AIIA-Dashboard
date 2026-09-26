# DECISIONS.md — Architectural Decision Records

## ADR-001: FastAPI over Flask for Backend Migration
**Date**: 2026-09-27
**Status**: Accepted
**Context**: Need to migrate from raw `http.server` to a modern framework. Flask and FastAPI were considered.
**Decision**: FastAPI chosen for automatic OpenAPI/Swagger docs, Pydantic validation, async support, and superior developer experience.
**Consequences**: Requires `uvicorn` as ASGI server. All existing endpoint contracts must be preserved.

## ADR-002: Recharts over Chart.js for Frontend Visualization
**Date**: 2026-09-27
**Status**: Accepted
**Context**: Need interactive clinical charts. Chart.js (canvas-based) and Recharts (React SVG-based) evaluated.
**Decision**: Recharts chosen because it's React-native (composable components), SVG-based (accessible, printable), and integrates seamlessly with existing JSX component architecture.
**Consequences**: Adds ~40KB to bundle. All charts are React components, not imperative canvas calls.

## ADR-003: Leaflet.js over Mapbox for India Trial Map
**Date**: 2026-09-27
**Status**: Accepted
**Context**: Need interactive map. Mapbox (proprietary, free tier) vs Leaflet.js (fully open-source) + OpenStreetMap.
**Decision**: Leaflet.js + OpenStreetMap tiles — 100% free with no API key requirements.
**Consequences**: Slightly less polished than Mapbox but fully free and self-hostable.

## ADR-004: i18next for Internationalization
**Date**: 2026-09-27
**Status**: Accepted
**Context**: Need Hindi/English language support. react-intl vs i18next evaluated.
**Decision**: i18next — larger ecosystem, simpler API, excellent React integration via react-i18next.

## ADR-005: SQLite retained as development database
**Date**: 2026-09-27
**Status**: Accepted
**Context**: PostgreSQL migration planned but SQLite must remain for local development and demo scenarios.
**Decision**: Dual-mode database support via SQLAlchemy ORM — SQLite for dev, PostgreSQL for production.
