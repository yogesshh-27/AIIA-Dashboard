"""Legacy endpoint routes (CTMS, governance, export)."""

import io
import csv
import json
import urllib.parse

from fastapi import APIRouter
from fastapi.responses import Response

from . import db_service

router = APIRouter()


@router.get("/governance")
async def get_governance(scope: str = "aiia"):
    return db_service.get_governance_insights(scope=scope)


@router.get("/ctms/overview")
async def get_ctms_overview():
    return db_service.get_ctms_overview()


@router.get("/ctms/timelines")
async def get_ctms_timelines(
    search: str = "", status: str = "", page: int = 1, limit: int = 15,
):
    return db_service.get_ctms_timelines(
        search=search, status=status, page=page, limit=limit,
    )


@router.get("/ctms/recruitment")
async def get_ctms_recruitment(search: str = "", page: int = 1, limit: int = 15):
    return db_service.get_ctms_recruitment(search=search, page=page, limit=limit)


@router.get("/ctms/monitoring")
async def get_ctms_monitoring(
    search: str = "", status: str = "", page: int = 1, limit: int = 15,
):
    return db_service.get_ctms_monitoring(
        search=search, status=status, page=page, limit=limit,
    )


@router.get("/ctms/deviations")
async def get_ctms_deviations(
    search: str = "", severity: str = "", status: str = "",
    page: int = 1, limit: int = 15,
):
    return db_service.get_ctms_deviations(
        search=search, severity=severity, status=status, page=page, limit=limit,
    )


@router.get("/ctms/milestones")
async def get_ctms_milestones(
    search: str = "", status: str = "", overdue_only: bool = False,
    page: int = 1, limit: int = 15,
):
    return db_service.get_ctms_milestones(
        search=search, status=status, overdue_only=overdue_only,
        page=page, limit=limit,
    )


@router.get("/export")
async def export_trials(
    scope: str = "aiia", search: str = "", status: str = "",
    phase: str = "", trial_type: str = "", sponsor: str = "",
    thesis: str = "", year: str = "", date_from: str = "", date_to: str = "",
    sort_by: str = "registered_on", sort_dir: str = "desc",
    format: str = "csv",
):
    res = db_service.get_trials(
        scope=scope, search=search, status=status,
        phase=phase, trial_type=trial_type, sponsor=sponsor,
        thesis=thesis, year=year, date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_dir=sort_dir, page=1, limit=2000,
    )

    if format.lower() == "json":
        json_bytes = json.dumps(res["data"], indent=2, ensure_ascii=False).encode("utf-8")
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={
                "Content-Disposition": 'attachment; filename="aiia_trials_export.json"',
                "X-Export-Disclaimer": "Prototype mapping/export - AIIA Clinical Trial Intelligence",
            },
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "CTRI Number", "Public Title", "Scientific Title", "Recruitment Status",
            "Phase", "Type of Trial", "Target Sample Size", "Registration Date",
            "Primary Sponsor", "Principal Investigator", "Affiliation",
        ])
        for r in res["data"]:
            writer.writerow([
                r.get("CTRI_Number", ""), r.get("Public_Title", ""),
                r.get("Scientific_Title", ""), r.get("Recruitment_Status_India", ""),
                r.get("Phase", ""), r.get("Type_of_Trial", ""),
                r.get("Target_Sample_Size", ""), r.get("Registration_Date", ""),
                r.get("Primary_Sponsor", ""), r.get("PI_Name", ""),
                r.get("PI_Affiliation", ""),
            ])
        csv_bytes = output.getvalue().encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="aiia_trials_export.csv"'},
        )


# EDC routes
@router.get("/edc/crf/templates")
async def get_crf_templates():
    return db_service.get_crf_templates()


@router.get("/edc/entries")
async def get_edc_entries():
    # Placeholder for getting CRF entries
    return {"entries": []}
