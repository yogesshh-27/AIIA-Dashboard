"""
AYURCTMS FastAPI Application
All India Institute of Ayurveda — Clinical Trial Management System

Replaces the legacy http.server-based server.py with a modern FastAPI application.
Provides auto-generated Swagger UI at /docs and ReDoc at /redoc.
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure root directory is on Python path for db_service import
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import db_service

# Import route modules
from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.trials import router as trials_router
from api.routes.patients import router as patients_router
from api.routes.doctors import router as doctors_router
from api.routes.pharmacovigilance import router as pv_router
from api.routes.compliance import router as compliance_router
from api.routes.interop import router as interop_router
from api.routes.reports import router as reports_router
from api.routes.audit import router as audit_router
from api.routes.documents import router as documents_router
from api.routes.ctri import router as ctri_router
from api.routes.search import router as search_router
from api.routes.legacy import router as legacy_router
from api.routes.privacy import router as privacy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup: initialize database indexes
    db_service.init_indexes()
    print("[OK] AYURCTMS FastAPI server started - database indexes initialized")
    yield
    # Shutdown
    print("[OK] AYURCTMS FastAPI server shutting down")


app = FastAPI(
    title="AYURCTMS — AIIA Clinical Trial Management System",
    description=(
        "Production-grade REST API for the All India Institute of Ayurveda "
        "Clinical Trial Management System. Provides patient trial matching, "
        "multi-site operations, pharmacovigilance, GCP compliance, FHIR/CDISC "
        "interoperability, and comprehensive audit trails."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "AIIA — Ministry of Ayush, Government of India",
        "url": "https://aiia.gov.in",
    },
    license_info={
        "name": "Government of India — Ministry of Ayush",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route modules
app.include_router(auth_router, prefix="/api", tags=["Authentication & RBAC"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard & Analytics"])
app.include_router(trials_router, prefix="/api", tags=["Trial Management"])
app.include_router(patients_router, prefix="/api", tags=["Patient Management"])
app.include_router(doctors_router, prefix="/api", tags=["Doctor Directory"])
app.include_router(pv_router, prefix="/api", tags=["Pharmacovigilance & Safety"])
app.include_router(compliance_router, prefix="/api", tags=["Compliance & GCP"])
app.include_router(interop_router, prefix="/api", tags=["Interoperability (FHIR/CDISC)"])
app.include_router(reports_router, prefix="/api", tags=["Reports & Export"])
app.include_router(audit_router, prefix="/api", tags=["Audit Trail"])
app.include_router(documents_router, prefix="/api", tags=["Document Repository"])
app.include_router(ctri_router, prefix="/api", tags=["CTRI Registry"])
app.include_router(search_router, prefix="/api", tags=["Search & Notifications"])
app.include_router(legacy_router, prefix="/api", tags=["Legacy Endpoints"])
app.include_router(privacy_router, prefix="/api", tags=["DPDP Privacy & Consent"])

from services.websocket_manager import ws_manager

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for instant SAE and clinical safety alerts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text('{"type":"pong"}')
    except (WebSocketDisconnect, Exception):
        ws_manager.disconnect(websocket)

# Serve React frontend from dist/ directory
dist_dir = os.path.join(ROOT_DIR, "dist")
if os.path.isdir(dist_dir):
    # Mount assets directory for static files (JS, CSS, images)
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Mount logos directory (from dist/logos or frontend/public/logos)
logos_dir = os.path.join(dist_dir, "logos")
if not os.path.isdir(logos_dir):
    logos_dir = os.path.join(ROOT_DIR, "frontend", "public", "logos")
if os.path.isdir(logos_dir):
    app.mount("/logos", StaticFiles(directory=logos_dir), name="logos")


@app.get("/favicon.svg", include_in_schema=False)
async def serve_favicon():
    for fav_path in [os.path.join(dist_dir, "favicon.svg"), os.path.join(ROOT_DIR, "frontend", "public", "favicon.svg")]:
        if os.path.isfile(fav_path):
            return FileResponse(fav_path, media_type="image/svg+xml")
    return Response(status_code=404)


@app.get("/manifest.json", include_in_schema=False)
async def serve_manifest():
    for m_path in [os.path.join(dist_dir, "manifest.json"), os.path.join(ROOT_DIR, "frontend", "public", "manifest.json")]:
        if os.path.isfile(m_path):
            return FileResponse(m_path, media_type="application/json")
    return Response(status_code=404)


@app.get("/health", include_in_schema=False)
@app.get("/healthz", include_in_schema=False)
async def health_check():
    """Health check endpoint for Render, orchestrators, and uptime monitors."""
    return {"status": "ok", "service": "AYURCTMS FastAPI Backend", "timestamp": "2026-09-27"}


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the React SPA index page."""
    dist_index = os.path.join(dist_dir, "index.html")
    if os.path.isfile(dist_index):
        return FileResponse(dist_index)
    legacy_index = os.path.join(ROOT_DIR, "index.html")
    if os.path.isfile(legacy_index):
        return FileResponse(legacy_index)
    from fastapi.responses import JSONResponse
    return JSONResponse({"status": "healthy", "service": "AYURCTMS FastAPI Backend", "docs": "/docs"}, status_code=200)


# Custom 404 handler: serve SPA for non-API routes, JSON error for API routes
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(StarletteHTTPException)
async def spa_exception_handler(request, exc):
    """For 404s on non-API paths, serve the SPA index.html (client-side routing)."""
    if exc.status_code == 404:
        path = request.url.path
        # API routes should return proper JSON 404
        if path.startswith("/api/"):
            return JSONResponse({"error": "Endpoint not found", "code": 404}, status_code=404)
        # Non-API 404s serve the SPA
        dist_index = os.path.join(dist_dir, "index.html")
        if os.path.isfile(dist_index):
            return FileResponse(dist_index)
    # All other HTTP exceptions
    return JSONResponse({"error": str(exc.detail), "code": exc.status_code}, status_code=exc.status_code)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("app_fastapi:app", host=host, port=port, reload=True)
