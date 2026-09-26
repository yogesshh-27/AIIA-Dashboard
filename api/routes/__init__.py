"""Shared dependencies and utilities for all route modules."""

import os
import sys
from typing import Dict, Any, Optional
from fastapi import Header, Request
from pydantic import BaseModel

# Ensure root directory is on Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import db_service


def get_auth_context(
    authorization: str = Header("", alias="Authorization"),
    x_session_token: str = Header("", alias="X-Session-Token"),
    x_active_role: str = Header("", alias="X-Active-Role"),
    request: Request = None,
) -> Dict[str, Any]:
    """Extract active user, role, and permissions from headers or token."""
    token = ""
    if authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if not token:
        token = x_session_token
    if not token and request:
        token = request.query_params.get("token", "")

    session = db_service.get_session(token) if token else None
    demo_role = x_active_role.strip()

    if session:
        active_role = demo_role if demo_role else session.get("role_name", "Administrator")
        user_name = session.get("full_name", session.get("username", "Authenticated User"))
        user_id = session.get("user_id", 1)
        perms = session.get("permissions", ["*"])
    elif demo_role:
        active_role = demo_role
        user_name = f"Demo User ({demo_role})"
        user_id = 1
        roles = db_service.get_roles()
        role_dict = next((r for r in roles if r["name"] == active_role), None)
        perms = role_dict["permissions"] if role_dict else ["*"]
    else:
        active_role = "Administrator"
        user_name = "Prof. (Dr.) Tanuja Nesari"
        user_id = 1
        perms = ["*"]

    return {
        "token": token or "demo-session-token",
        "user_id": user_id,
        "user_name": user_name,
        "role": active_role,
        "permissions": perms,
        "is_authenticated": True,
    }


def check_permission(auth: Dict[str, Any], permission_code: str, method: str = "GET") -> Optional[Dict]:
    """Check if the user has permission. Returns error dict if unauthorized, None if OK."""
    role = auth["role"]
    if role == "Regulator / Read-only" and method in ("POST", "PUT", "DELETE", "PATCH"):
        return {
            "error": "Forbidden: Read-Only Access",
            "message": f"Role '{role}' is restricted to authorized read-only audit access. All modifying actions are prohibited.",
            "role": role,
            "required_permission": permission_code,
        }
    if not db_service.has_permission(role, permission_code):
        return {
            "error": "Forbidden",
            "message": f"Role '{role}' is not authorized to perform action '{permission_code}'. Server-side RBAC restriction enforced.",
            "role": role,
            "required_permission": permission_code,
        }
    return None
