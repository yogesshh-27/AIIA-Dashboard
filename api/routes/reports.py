"""Reports & Export routes."""

import io
import csv

from fastapi import APIRouter, Request
from fastapi.responses import Response

from . import db_service, get_auth_context

router = APIRouter()


@router.get("/ayur/reports")
async def get_ayur_reports(type: str = "trial_progress"):
    return db_service.get_ayur_report_data(report_type=type)


@router.get("/ayur/reports/export")
async def export_ayur_report(type: str = "trial_progress", format: str = "csv"):
    rep_data = db_service.get_ayur_report_data(report_type=type)
    if format.lower() == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        cols = rep_data.get("columns", [])
        writer.writerow(cols)
        for row in rep_data.get("rows", []):
            writer.writerow([row.get(c, "") for c in cols])
        csv_bytes = out.getvalue().encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="AYURCTMS_{type.upper()}_REPORT.csv"'},
        )
    return rep_data


@router.get("/reports/data")
async def get_report_data(type: str = "portfolio"):
    return _get_report_by_type(type)


@router.get("/reports/export")
async def export_report(type: str = "portfolio", format: str = "csv", request: Request = None):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", "") if request else "",
        x_session_token=request.headers.get("X-Session-Token", "") if request else "",
        x_active_role=request.headers.get("X-Active-Role", "") if request else "",
        request=request,
    )
    fmt = format.lower()
    if fmt in ("pdf", "html"):
        html_content = db_service.generate_report_printable_html(
            type,
            generated_by=auth.get("user_name", "Prof. (Dr.) Tanuja Nesari"),
            role=auth.get("role", "Administrator"),
        )
        return Response(content=html_content.encode("utf-8"), media_type="text/html")
    else:
        csv_content = db_service.generate_report_csv(type)
        return Response(
            content=csv_content.encode("utf-8"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="AIIA_{type.upper()}_REPORT.csv"'},
        )


@router.get("/reports/{report_type}")
async def get_report_by_type(report_type: str):
    return _get_report_by_type(report_type)


def _get_report_by_type(rep_type: str):
    rep_type = rep_type.strip().lower()
    dispatch = {
        "portfolio": db_service.get_report_portfolio,
        "recruitment": db_service.get_report_recruitment,
        "compliance": db_service.get_report_compliance,
        "safety": db_service.get_report_safety,
        "data_quality": db_service.get_report_data_quality,
        "data-quality": db_service.get_report_data_quality,
        "audit": db_service.get_report_audit,
    }
    handler = dispatch.get(rep_type)
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": f"Unknown report type '{rep_type}'"}, status_code=400)


# ============================================================
# BACKGROUND WORKER QUEUE ENDPOINTS
# ============================================================
import uuid
from fastapi import BackgroundTasks
from services.background_tasks import (
    async_generate_clinical_report,
    async_sync_ctri_registry,
    get_job_status
)


@router.post("/reports/async-generate")
async def trigger_async_report(background_tasks: BackgroundTasks, type: str = "trial_progress"):
    """Enqueues async report generation task into background worker queue."""
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    background_tasks.add_task(async_generate_clinical_report, job_id, type, {})
    return {
        "success": True,
        "job_id": job_id,
        "status": "QUEUED",
        "message": f"Async report task for '{type}' enqueued to worker queue."
    }


@router.post("/reports/async-sync-ctri")
async def trigger_async_ctri_sync(background_tasks: BackgroundTasks):
    """Enqueues scheduled CTRI clinical registry scraper job."""
    job_id = f"ctri-{uuid.uuid4().hex[:8]}"
    background_tasks.add_task(async_sync_ctri_registry, job_id)
    return {
        "success": True,
        "job_id": job_id,
        "status": "QUEUED",
        "message": "CTRI registry sync worker job enqueued."
    }


@router.get("/reports/job/{job_id}")
async def check_job_status(job_id: str):
    """Polls execution progress of a background worker task."""
    return get_job_status(job_id)
