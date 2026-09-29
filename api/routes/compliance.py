"""Compliance & GCP routes."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

from . import db_service, get_auth_context

router = APIRouter()


class ApprovalUpdateRequest(BaseModel):
    approval_id: Optional[str] = None
    status: str = "Approved"
    notes: str = "Reviewed by ethics/regulatory board."
    reviewed_by: str = "Ethics Committee Officer"


class GcpToggleRequest(BaseModel):
    item_id: int = 1
    is_completed: int = 1
    reviewed_by: str = "Dr. Research Admin"


class AlertStatusRequest(BaseModel):
    status: str = "Acknowledged"
    user: Optional[str] = None


@router.get("/ayur/approvals")
async def get_ayur_approvals(
    site: str = "", type: str = "", status: str = ""
):
    return db_service.get_ayur_approvals(
        site=site, approval_type=type, status=status
    )


@router.post("/ayur/approvals/update")
async def update_ayur_approval(body: ApprovalUpdateRequest):
    return db_service.update_ayur_approval(
        body.approval_id, body.status, body.notes, body.reviewed_by
    )


@router.get("/ayur/gcp")
async def get_ayur_gcp_checklist():
    return db_service.get_ayur_gcp_checklist()


@router.post("/ayur/gcp/toggle")
async def toggle_gcp_item(body: GcpToggleRequest):
    return db_service.toggle_ayur_gcp_item(
        body.item_id, body.is_completed, body.reviewed_by
    )


@router.get("/compliance/overview")
async def get_compliance_overview():
    return db_service.get_compliance_overview()


@router.get("/compliance/data-quality")
async def get_data_quality(scope: str = "aiia"):
    return db_service.calculate_data_quality_audit(scope=scope)


@router.get("/alerts")
async def get_alerts(
    category: str = "", severity: str = "", status: str = "",
    search: str = "", page: int = 1, limit: int = 15,
):
    return db_service.get_alerts(
        category=category, severity=severity, status=status,
        search=search, page=page, limit=limit,
    )


@router.post("/alerts/{alert_id}/status")
async def update_alert_status(alert_id: int, body: AlertStatusRequest, request: Request):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    from . import check_permission
    from fastapi.responses import JSONResponse
    perm_err = check_permission(auth, "alerts:write", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)

    user_name = body.user or auth["user_name"]
    res = db_service.update_alert_status(alert_id, body.status, user_name)
    db_service.log_audit_event(
        user_name=user_name, role=auth["role"],
        action="UPDATE_ALERT_STATUS", entity="Alert",
        entity_id=str(alert_id), previous_value="Active",
        new_value=body.status,
        ip_address=request.client.host if request.client else "127.0.0.1",
    )
    return res


# ============================================================
# ALCOA+ REGULATORY DATA INTEGRITY ENDPOINTS
# ============================================================
from services.alcoa_engine import evaluate_alcoa_principles, generate_alcoa_certificate

@router.get("/compliance/alcoa/metrics")
async def get_alcoa_metrics(scope: str = "aiia", trial_id: Optional[str] = None):
    """Evaluates 9 ALCOA+ principles for clinical trials and audit logs."""
    return evaluate_alcoa_principles(scope=scope, trial_id=trial_id)


@router.get("/compliance/alcoa/certificate/{trial_id:path}")
async def get_alcoa_certificate(trial_id: str):
    """Generates a cryptographically signed ALCOA+ Data Integrity Certificate."""
    return generate_alcoa_certificate(trial_id=trial_id)

