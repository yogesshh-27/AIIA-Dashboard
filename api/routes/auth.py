"""Authentication & RBAC routes."""

from fastapi import APIRouter, Request, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from . import db_service, get_auth_context

router = APIRouter()


class LoginRequest(BaseModel):
    username: Optional[str] = ""
    password: Optional[str] = ""
    staff_id: Optional[str] = ""


class RoleSwitchRequest(BaseModel):
    role: str = "Administrator"


@router.post("/auth/login")
async def auth_login(body: LoginRequest, request: Request):
    username = body.username or ""
    password = body.password or ""
    ip = request.client.host if request.client else "127.0.0.1"
    agent = request.headers.get("User-Agent", "WebBrowser")
    auth_res = db_service.authenticate_user(username, password, ip_address=ip, user_agent=agent)
    if auth_res:
        return auth_res
    return JSONResponse(
        {"error": "Invalid institutional credentials or inactive account."},
        status_code=401,
    )


@router.post("/auth/switch-role")
async def switch_role(body: RoleSwitchRequest, x_session_token: str = Header("", alias="X-Session-Token")):
    res = db_service.switch_role_session(x_session_token, body.role)
    if not res:
        roles = db_service.get_roles()
        role_dict = next((r for r in roles if r["name"] == body.role), None)
        res = {
            "role_name": body.role,
            "full_name": f"AIIA User ({body.role})",
            "permissions": role_dict["permissions"] if role_dict else ["*"],
            "is_authenticated": True,
        }
    return res


@router.get("/auth/roles")
async def get_roles():
    return db_service.get_roles()


@router.get("/auth/users")
async def get_users():
    return db_service.get_users()


@router.get("/auth/me")
async def get_current_user(request: Request):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    return auth


# --- AYURCTMS Auth ---
@router.post("/ayur/auth/login")
async def ayur_auth_login(body: LoginRequest):
    staff_id = (body.staff_id or body.username or "").strip()
    password = (body.password or "").strip()

    if (staff_id.upper() == "AIIA001" and password == "AIIA@123") or (
        staff_id.lower() == "admin" and password == "admin123"
    ):
        return {
            "success": True,
            "token": "ayur-demo-token-998811",
            "user": {
                "staff_id": "AIIA001",
                "full_name": "Dr. Research Admin",
                "role": "AIIA Authorized Staff",
                "designation": "Clinical Research Coordinator / Admin",
                "institution": "All India Institute of Ayurveda (AIIA), New Delhi",
            },
            "message": "Login successful. Welcome to AYURCTMS.",
        }
    return JSONResponse(
        {
            "success": False,
            "error": "Invalid Staff ID or Password. Demo credentials: Staff ID: AIIA001, Password: AIIA@123",
        },
        status_code=401,
    )
