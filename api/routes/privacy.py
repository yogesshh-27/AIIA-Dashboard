"""
DPDP Act (2023) Privacy & Consent Governance Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.dpdp_service import (
    get_dpdp_privacy_notice,
    record_dpdp_consent,
    withdraw_dpdp_consent,
    process_rights_request,
    get_dpo_audit_log,
)

router = APIRouter()


class ConsentRecordRequest(BaseModel):
    trial_id: str = "CTRI/2017/12/010899"
    subject_id: str = "SUBJ-001"
    abha_id: Optional[str] = "91-8842-1920-3341"
    language: str = "en"
    purposes_granted: Optional[List[str]] = [
        "CLINICAL_EVALUATION",
        "PRAKRITI_DOSHA_STRATIFICATION",
        "PHARMACOVIGILANCE_REPORTING",
    ]


class ConsentWithdrawRequest(BaseModel):
    consent_id: str
    reason: Optional[str] = "Participant revocation"


class RightsRequestModel(BaseModel):
    subject_id: str = "SUBJ-001"
    request_type: str = "ACCESS"  # ACCESS, CORRECTION, ERASURE, GRIEVANCE
    details: str = "Request for summary of processed personal and clinical data."


@router.get("/privacy/notice")
async def get_privacy_notice(language: str = "en"):
    """Returns DPDP Section 5 Multilingual Consent & Processing Notice."""
    return get_dpdp_privacy_notice(language=language)


@router.post("/privacy/consent/record")
async def api_record_consent(body: ConsentRecordRequest):
    """Records an explicit, tokenized digital consent artifact under DPDP Act 2023."""
    return record_dpdp_consent(body.model_dump())


@router.post("/privacy/consent/withdraw")
async def api_withdraw_consent(body: ConsentWithdrawRequest):
    """Executes consent revocation under DPDP Section 6(4)."""
    return withdraw_dpdp_consent(body.consent_id, body.reason)


@router.post("/privacy/rights-request")
async def api_rights_request(body: RightsRequestModel):
    """Processes Data Principal rights requests (Access, Correction, Erasure, Grievance)."""
    return process_rights_request(body.model_dump())


@router.get("/privacy/dpo/audit-log")
async def api_dpo_audit_log():
    """Returns the Data Protection Officer (DPO) consent and privacy audit log."""
    return get_dpo_audit_log()
