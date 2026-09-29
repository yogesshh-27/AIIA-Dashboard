"""Interoperability (FHIR R4 & CDISC SDTM) routes."""

from fastapi import APIRouter
from fastapi.responses import Response, JSONResponse
from typing import Dict, Any, Optional, List

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


# ============================================================
# ABDM & EDC / HIS INTEROPERABILITY ENDPOINTS
# ============================================================
from services.abdm_edc_service import (
    verify_abha_id,
    generate_fhir_r4_bundle,
    ingest_edc_payload,
    get_abdm_gateway_status,
)
from pydantic import BaseModel


class AbhaVerifyRequest(BaseModel):
    abha_id: str


class EdcIngestRequest(BaseModel, extra="allow"):
    source_system: str = "OpenClinica"
    trial_id: Optional[str] = "CTRI/2017/12/010899"
    subject_id: Optional[str] = "SUBJ-001"
    event_type: Optional[str] = "VISIT_DAY_14"


@router.post("/interop/abdm/verify-abha")
async def api_verify_abha(body: AbhaVerifyRequest):
    """Verifies ABHA ID format and resolves mock sandbox demographic profile."""
    return verify_abha_id(body.abha_id)


@router.get("/interop/abdm/status")
async def api_abdm_status():
    """Returns ABDM M1/M2/M3 Interoperability conformance readiness."""
    return get_abdm_gateway_status()


@router.get("/interop/fhir/bundle")
async def get_fhir_bundle(trial_id: str = None):
    """Generates an HL7 FHIR R4 Bundle uniting ResearchStudy, Patient, Condition, and Medication."""
    return generate_fhir_r4_bundle(trial_id=trial_id)


@router.post("/interop/edc/ingest")
async def api_ingest_edc(body: EdcIngestRequest):
    """Standardized Ingest Adapter for OpenClinica, REDCap, and Hospital Information Systems."""
    payload = body.model_dump()
    return ingest_edc_payload(body.source_system, payload)


# ============================================================
# SUBMISSION-READY CDISC EXPORT (SDTM, ADAM, DEFINE-XML 2.0)
# ============================================================
from services.cdisc_submission_exporter import (
    get_sdtm_domain_dataset,
    get_adam_dataset,
    generate_define_xml_2_0,
)

@router.get("/interop/cdisc/sdtm/{domain}")
async def api_get_sdtm(domain: str, trial_id: Optional[str] = None):
    """Generates standardized SDTM tabulation dataset for domain (TS, DM, AE, EX, DS, LB)."""
    return get_sdtm_domain_dataset(domain=domain, trial_id=trial_id)


@router.get("/interop/cdisc/adam/{dataset_name}")
async def api_get_adam(dataset_name: str, trial_id: Optional[str] = None):
    """Generates standardized ADaM analysis dataset (ADSL, ADAE)."""
    return get_adam_dataset(dataset_name=dataset_name, trial_id=trial_id)


@router.get("/interop/cdisc/define-xml-2")
async def api_get_define_xml_2(trial_id: Optional[str] = None):
    """Generates W3C-valid Define-XML 2.0 metadata with stylesheet link."""
    xml_data = generate_define_xml_2_0(trial_id=trial_id)
    return Response(
        content=xml_data.encode("utf-8"),
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="Define_XML_2_0.xml"'},
    )


