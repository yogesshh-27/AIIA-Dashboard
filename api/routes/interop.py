"""Interoperability (FHIR R4 & CDISC SDTM) routes."""

from fastapi import APIRouter
from fastapi.responses import Response, JSONResponse
from typing import Dict, Any

from . import db_service

router = APIRouter()


@router.get("/ayur/interop/demo")
async def get_ayur_interop_demo():
    return db_service.get_ayur_interop_demo()


@router.get("/cdisc")
async def search_cdisc(search: str = "", limit: int = 50):
    return db_service.search_cdisc_concepts(search=search, limit=limit)


@router.get("/interop/cdisc/overview")
async def get_cdisc_overview():
    return db_service.get_cdisc_overview()


@router.get("/interop/cdisc/mapping")
async def get_cdisc_mappings():
    return db_service.get_cdisc_mappings()


@router.get("/interop/cdisc/export")
async def export_cdisc(format: str = "sdtm", trial_id: str = None):
    fmt = format.lower()
    if fmt == "sdtm":
        return db_service.export_cdisc_sdtm(trial_id=trial_id)
    elif fmt == "adam":
        return db_service.export_cdisc_adam(trial_id=trial_id)
    elif fmt == "define_xml":
        xml_data = db_service.export_cdisc_define_xml(trial_id=trial_id)
        return Response(
            content=xml_data.encode("utf-8"),
            media_type="application/xml",
            headers={"Content-Disposition": 'attachment; filename="define_xml_demonstration.xml"'},
        )
    return JSONResponse({"error": f"Unsupported export format '{fmt}'"}, status_code=400)


@router.get("/interop/fhir/study")
async def get_fhir_study(trial_id: str = None):
    return db_service.get_fhir_research_study(trial_id=trial_id)


@router.post("/interop/fhir/validate")
async def validate_fhir(body: Dict[str, Any]):
    return db_service.validate_fhir_research_study(body)
