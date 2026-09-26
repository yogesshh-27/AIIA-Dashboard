"""Audit Trail routes."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from . import db_service, get_auth_context, check_permission

router = APIRouter()


class AuditLogRequest(BaseModel):
    user: Optional[str] = None
    role: Optional[str] = None
    action: str = "USER_ACTION"
    entity: str = "GeneralEntity"
    entity_id: str = "N/A"
    previous_value: str = ""
    new_value: str = ""


class TamperDemoRequest(BaseModel):
    event_id: str = "EVT-0003"
    malicious_value: str = "Tampered enrollment count (UNAUTHORIZED_MUTATION)"


@router.get("/ayur/audit")
async def get_ayur_audit_trail():
    return db_service.get_ayur_audit_trail()


@router.get("/audit/chain")
async def get_audit_chain(
    page: int = 1, limit: int = 20, search: str = "", role: str = ""
):
    return db_service.get_audit_chain(
        page=page, limit=limit, search=search, role_filter=role
    )


@router.get("/audit/verify")
async def verify_audit_chain():
    return db_service.verify_audit_chain()


@router.post("/audit/log")
async def log_audit_event(body: AuditLogRequest, request: Request):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    perm_err = check_permission(auth, "audit:write", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)

    res = db_service.log_audit_event(
        user_name=body.user or auth["user_name"],
        role=body.role or auth["role"],
        action=body.action, entity=body.entity,
        entity_id=body.entity_id, previous_value=body.previous_value,
        new_value=body.new_value,
        ip_address=request.client.host if request.client else "127.0.0.1",
        device_metadata=request.headers.get("User-Agent", "WebBrowser")[:120],
    )
    return res


@router.post("/audit/tamper-demo")
async def tamper_demo(body: TamperDemoRequest, request: Request):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    perm_err = check_permission(auth, "audit:admin", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)
    return db_service.tamper_audit_event_demo(body.event_id, body.malicious_value)


@router.post("/audit/restore-demo")
async def restore_demo(request: Request):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    perm_err = check_permission(auth, "audit:admin", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)
    return db_service.restore_audit_chain_demo()


# ============================================================
# 21 CFR PART 11 ELECTRONIC SIGNATURES
# ============================================================
from services.esignature_service import sign_record, verify_signature, get_record_signature


class ESignatureRequest(BaseModel):
    record_type: str = "approval"
    record_id: str
    signer_name: str
    signer_role: str = "Ethics Reviewer"
    intent: str = "I hereby certify that I have reviewed this clinical trial documentation and approve it in accordance with GCP and 21 CFR Part 11."
    reauth_password: str


@router.post("/audit/esign")
async def execute_esignature(body: ESignatureRequest):
    """Executes a 21 CFR Part 11 compliant re-authenticated electronic signature."""
    res = sign_record(
        record_type=body.record_type,
        record_id=body.record_id,
        signer_name=body.signer_name,
        signer_role=body.signer_role,
        intent=body.intent,
        reauth_password=body.reauth_password
    )
    if not res.get("success"):
        return JSONResponse(res, status_code=401)
    return res


@router.get("/audit/esign/verify/{signature_id}")
async def verify_record_signature(signature_id: str):
    """Cryptographically verifies a 21 CFR Part 11 signature hash."""
    return verify_signature(signature_id)


@router.get("/audit/esign/record/{record_type}/{record_id}")
async def get_record_signature_details(record_type: str, record_id: str):
    """Retrieves e-signature details for an audited clinical record."""
    sig = get_record_signature(record_type, record_id)
    if not sig:
        return {"has_signature": False, "signature": None}
    return {"has_signature": True, "signature": sig}
