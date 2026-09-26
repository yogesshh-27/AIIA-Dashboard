"""Search & Notification routes."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from . import db_service

router = APIRouter()


class NotificationReadRequest(BaseModel):
    notification_id: int = 1


class AssistantQueryRequest(BaseModel):
    query: str


@router.get("/ayur/search")
async def global_search(q: str = "", search: str = ""):
    query = q or search
    return db_service.global_ayur_search(query)


@router.get("/ayur/notifications")
async def get_notifications():
    return db_service.get_ayur_notifications()


@router.post("/ayur/notifications/read")
async def mark_notification_read(body: NotificationReadRequest):
    return db_service.mark_ayur_notification_read(body.notification_id)


@router.post("/assistant/query")
async def assistant_query(body: AssistantQueryRequest, request: Request):
    if not body.query.strip():
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Empty query"}, status_code=400)

    from . import get_auth_context
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    ans = db_service.query_trial_assistant(body.query)
    db_service.log_audit_event(
        user_name=auth["user_name"], role=auth["role"],
        action="ASSISTANT_QUERY", entity="TrialAssistant",
        entity_id=ans.get("intent", "QUERY"),
        previous_value="", new_value=body.query[:100],
        ip_address=request.client.host if request.client else "127.0.0.1",
    )
    return ans
